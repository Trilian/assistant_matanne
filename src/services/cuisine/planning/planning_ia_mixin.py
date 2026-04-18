"""
Mixin IA pour la génération de plannings.

Contient les méthodes de génération IA extraites de ServicePlanning:
- generer_planning_ia: Génération complète d'un planning hebdomadaire via Mistral AI
- suggerer_recettes_equilibrees: Suggestions de recettes équilibrées par jour

Ces méthodes utilisent BaseAIService (via MRO) pour l'appel IA avec
rate limiting et cache automatiques.
"""

import logging
from datetime import date, timedelta
from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.core.caching import obtenir_cache
from src.core.date_utils.helpers import obtenir_noms_jours_semaine
from src.core.decorators import avec_gestion_erreurs, avec_session_db
from src.core.models import Planning, Repas
from src.core.monitoring import chronometre
from src.services.core.event_bus_mixin import emettre_evenement_simple

from .nutrition import determine_protein_type
from .types import JourPlanning, ParametresEquilibre, RecetteEnrichieIA

logger = logging.getLogger(__name__)

# Constituants structurels implicites : mappe un motif (sous-chaîne du nom du plat) vers
# les féculents redondants à annuler. Utilisé par _nettoyer_feculents_constitutifs.
# Ex : « Gratin dauphinois » → ne pas mettre « Pommes de terre » en féculent.
_FECULENTS_CONSTITUTIFS_PAR_PLAT: list[tuple[str, frozenset[str]]] = [
    # Plats à base de pommes de terre
    ("gratin dauphinois", frozenset({"pomme de terre", "pommes de terre", "patate", "patates"})),
    ("tartiflette",       frozenset({"pomme de terre", "pommes de terre", "patate"})),
    ("hachis parmentier", frozenset({"pomme de terre", "pommes de terre", "purée", "puree"})),
    ("gnocchi",           frozenset({"gnocchi", "pomme de terre", "pommes de terre"})),
    # Plats à base de riz
    ("risotto",  frozenset({"riz", "risotto"})),
    ("paella",   frozenset({"riz", "riz à la paella"})),
    # Plats à base de pâtes
    ("lasagne",  frozenset({"lasagne", "lasagnes", "pâtes", "pates"})),
    # Plats à base de pâte brisée / feuilletée
    ("quiche",       frozenset({"pâte brisée", "pate brisee", "pâte feuilletée", "pate feuilletee", "pâte", "pate"})),
    ("tarte salée",  frozenset({"pâte brisée", "pate brisee", "pâte feuilletée", "pate feuilletee", "pâte", "pate"})),
    ("tourte",       frozenset({"pâte brisée", "pate brisee", "pâte feuilletée", "pate feuilletee", "pâte", "pate"})),
    ("flamiche",     frozenset({"pâte brisée", "pate brisee", "pâte feuilletée", "pate feuilletee"})),
    # Plats à base de polenta / maïs
    ("polenta", frozenset({"polenta", "maïs", "mais"})),
    # Légumineuses en plat principal : féculent + protéine simultanément
    ("lentille",    frozenset({"lentille", "lentilles"})),
    ("pois chiche", frozenset({"pois chiche", "pois chiches"})),
    ("dal",         frozenset({"dal", "dahl"})),
    # Recettes contenant pommes de terre comme féculent explicite dans leur nom
    # (ex : « Omelette aux champignons et pommes de terre »)
    ("pommes de terre", frozenset({"riz", "semoule", "pâtes", "pates", "quinoa", "boulgour", "bulgur"})),
    ("pomme de terre",  frozenset({"riz", "semoule", "pâtes", "pates", "quinoa", "boulgour", "bulgur"})),
]


# Mots de cuisine génériques et articles/prépositions courts à exclure
# du matching mot-à-mot dans _nettoyer_si_inclus_dans_nom
_MOTS_CUISINE_STOP: frozenset[str] = frozenset({
    # Articles et prépositions courants français de 3 lettres
    "aux", "les", "des", "par", "sur", "son", "ses", "mes", "ton", "tes",
    # Méthodes de cuisson (non discriminantes pour identifier un ingrédient)
    "vapeur", "sauté", "sautée", "sautés", "sautées",
    "grillé", "grillée", "grillés", "grillées",
    "cuit", "cuite", "cuits", "cuites",
    "poêlé", "poêlée", "poêlés", "poêlées",
    "rôti", "rôtie", "rôtis", "rôties",
    # Qualificatifs génériques
    "frais", "fraîche", "fraîches", "nature", "maison", "saison",
    "léger", "légère",
})

# Mots-aliments courts (< 4 caractères) à traiter comme significatifs malgré leur longueur
_MOTS_COURTS_ALIMENTS: frozenset[str] = frozenset({
    "riz", "blé", "ble", "soja", "dal",
})


class PlanningIAGenerationMixin:
    """
    Mixin contenant les méthodes de génération IA pour le planning.

    Dépendances MRO:
    - BaseAIService → call_with_list_parsing_sync, rate limiting
    - PlanningAIMixin → build_planning_context (contexte métier)

    Usage:
        class ServicePlanning(BaseService, BaseAIService, PlanningAIMixin, PlanningIAGenerationMixin):
            ...
    """

    # ═══════════════════════════════════════════════════════════
    # HELPERS INTERNES
    # ═══════════════════════════════════════════════════════════

    @staticmethod
    def _trouver_ou_creer_recette(db: Session, nom: str, categorie: str = "Plat") -> int:
        """Retourne l'id d'une recette existante (lookup insensible à la casse)
        ou crée un stub minimal si elle n'existe pas encore."""
        from src.core.models.recettes import Recette

        recette = db.query(Recette).filter(func.lower(Recette.nom) == nom.lower()).first()
        if recette is None:
            recette = Recette(nom=nom, temps_preparation=30, categorie=categorie)
            db.add(recette)
            db.flush()
        return recette.id

    @staticmethod
    def _trouver_recette_seule(db: Session, nom: str) -> int | None:
        """Retourne l'id d'une recette existante ou None si non trouvée (sans créer de stub).
        Utilisé pour les repas « Reste » afin d'éviter la création d'une fausse recette."""
        from src.core.models.recettes import Recette

        recette = db.query(Recette).filter(func.lower(Recette.nom) == nom.lower()).first()
        return recette.id if recette else None

    @staticmethod
    def _corriger_restes_insuffisants(planning_data: list) -> list:
        """Corrige un planning où l'IA a généré trop peu de restes.

        Si le nombre de déjeuners marqués 'reste' est < 3, cherche les dîners compatibles
        (en sauce, mijoté, gratin…) et convertit automatiquement le déjeuner du lendemain
        en reste, en héritant des accompagnements du dîner source.
        """
        _JOURS = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
        # Mots-clés indiquant un plat réchauffable
        _MOTS_COMPATIBLES = {
            "basquaise", "bourguignon", "blanquette", "daube", "ragoût", "cocotte",
            "osso buco", "tajine", "curry", "korma", "tikka", "masala", "colombo",
            "rôti", "rotisserie", "gratin", "lasagnes", "moussaka", "parmentier",
            "risotto", "soupe", "velouté", "potage", "minestrone", "mijoté",
            "boulettes", "wok", "poêlée", "sauce", "crumble", "pot-au-feu",
            "poulet basquaise", "blanquette", "navarin", "pot au feu",
        }
        # Mots-clés excluant un plat (non réchauffable)
        _MOTS_INCOMPATIBLES = {
            "grillé", "grillée", "vapeur", "poché", "pochée", "omelette",
            "salade", "tartare", "carpaccio", "sashimi",
        }

        nb_restes = sum(1 for j in planning_data if j.dejeuner_est_reste)
        if nb_restes >= 3:
            return planning_data

        logger.info(
            f"⚠️ Planning IA : {nb_restes} reste(s) seulement — correction auto (objectif ≥ 3)"
        )

        for idx in range(1, len(planning_data)):
            if nb_restes >= 4:
                break
            jour = planning_data[idx]
            prev = planning_data[idx - 1]

            if jour.dejeuner_est_reste:
                continue

            diner_lower = (prev.diner or "").lower()
            est_compatible = any(mot in diner_lower for mot in _MOTS_COMPATIBLES)
            est_incompatible = any(mot in diner_lower for mot in _MOTS_INCOMPATIBLES)

            if est_compatible and not est_incompatible:
                jour_nom = _JOURS[idx - 1] if idx - 1 < len(_JOURS) else prev.jour
                jour.dejeuner = prev.diner
                jour.dejeuner_est_reste = True
                jour.dejeuner_reste_source = f"dîner de {jour_nom}"
                jour.dejeuner_legumes = prev.diner_legumes
                jour.dejeuner_feculents = prev.diner_feculents
                jour.dejeuner_proteine_accompagnement = prev.diner_proteine_accompagnement
                nb_restes += 1
                logger.info(
                    f"✅ Reste injecté : {jour.jour} déjeuner → '{prev.diner}' "
                    f"({jour.dejeuner_reste_source})"
                )

        if nb_restes < 3:
            logger.warning(
                f"⚠️ Correction restes : seulement {nb_restes} reste(s) atteint(s) "
                f"— pas assez de dîners compatibles dans ce planning."
            )

        return planning_data

    @staticmethod
    def _nettoyer_feculents_constitutifs(valeur: str | None, nom_recette: str) -> str | None:
        """Nullifie un féculent qui est le constituant structurel du plat.

        Complète `_nettoyer_si_inclus_dans_nom` qui ne couvre que les sous-chaînes
        littérales. Ici on gère les cas sémantiques : « Pommes de terre » pour un
        « Gratin dauphinois », « Pâte brisée » pour une « Quiche lorraine », etc.
        """
        if not valeur or not nom_recette:
            return valeur
        nom_lower = nom_recette.lower()
        valeur_lower = valeur.lower().strip()
        for pattern, feculents_redondants in _FECULENTS_CONSTITUTIFS_PAR_PLAT:
            if pattern in nom_lower and any(token in valeur_lower for token in feculents_redondants):
                logger.debug(
                    "[planning] Féculent constitutif '%s' supprimé de '%s' (pattern '%s')",
                    valeur,
                    nom_recette,
                    pattern,
                )
                return None
        return valeur

    @staticmethod
    def _est_plat_propre_feculent(nom_recette: str) -> bool:
        """True si le plat est lui-même son propre féculent (quiche, gratin, risotto…).

        Utilisé pour ignorer le fallback \"Riz vapeur\" qui serait incohérent dans ce cas :
        si l'IA a correctement laissé feculents=null per Rule 17, on ne doit pas l'écraser.
        """
        if not nom_recette:
            return False
        nom_lower = nom_recette.lower()
        return any(pattern in nom_lower for pattern, _ in _FECULENTS_CONSTITUTIFS_PAR_PLAT)

    @staticmethod
    def _nettoyer_si_inclus_dans_nom(valeur: str | None, nom_recette: str) -> str | None:
        """Retourne None si `valeur` est déjà présent (en tout ou en partie significative)
        dans le nom de la recette.

        Évite les doublons comme :
        - « Semoule » dans « Agneau rôti aux légumes de saison, semoule »
        - « Riz basmati » dans « Dinde aux courgettes et riz »
        - « Courgettes sautées » dans « Dinde aux courgettes et riz »
        - « Petits pois vapeur » dans « Poulet curry aux petits pois et riz »
        - « Poêlée de légumes » dans « Poulet sauté aux légumes printaniers »
        """
        if not valeur or not nom_recette:
            return valeur
        nom_lower = nom_recette.lower()
        valeur_lower = valeur.lower().strip()
        # 1. Correspondance exacte (sous-chaîne littérale)
        if valeur_lower in nom_lower:
            return None
        # 2. Matching par mot significatif :
        #    - mots ≥ 4 caractères OU mots-aliments courts spécifiques (riz, blé…)
        #    - hors mots génériques de cuisine / articles / prépositions
        mots = valeur_lower.replace("-", " ").replace("'", " ").split()
        mots_significatifs = [
            m for m in mots
            if (len(m) >= 4 or m in _MOTS_COURTS_ALIMENTS)
            and m not in _MOTS_CUISINE_STOP
        ]
        if mots_significatifs and any(mot in nom_lower for mot in mots_significatifs):
            return None
        return valeur

    # ═══════════════════════════════════════════════════════════
    # SUGGESTIONS ÉQUILIBRÉES
    # ═══════════════════════════════════════════════════════════

    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def suggerer_recettes_equilibrees(
        self,
        semaine_debut: date,
        parametres: ParametresEquilibre,
        type_repas: str = "dejeuner",
        db: Session | None = None,
    ) -> list[dict]:
        """Suggère des recettes équilibrées pour chaque jour.

        Retourne 3 options par jour avec score d'équilibre.
        Utilise les fonctions pures de planning.utils.

        Args:
            semaine_debut: Date de début de semaine
            parametres: Contraintes d'équilibre
            type_repas: Type de repas cible ("dejeuner" ou "diner"). Défaut "dejeuner".
            db: Database session

        Returns:
            List de dicts {jour, type_repas, suggestions: [{nom, description, raison}]}
        """
        from src.core.models import Recette

        # Utiliser planning.utils pour les jours de la semaine
        jours_semaine = obtenir_noms_jours_semaine()
        suggestions_globales = []

        for idx, jour_name in enumerate(jours_semaine):
            jour_lower = jour_name.lower()
            date_jour = semaine_debut + timedelta(days=idx)

            # Utiliser planning.utils pour déterminer le type de protéine
            type_proteine, raison_jour = determine_protein_type(
                jour_lower,
                poisson_jours=parametres.poisson_jours,
                viande_rouge_jours=parametres.viande_rouge_jours,
                vegetarien_jours=parametres.vegetarien_jours,
                poisson_blanc_jours=parametres.poisson_blanc_jours,
                poisson_gras_jours=parametres.poisson_gras_jours,
            )

            # Requête base pour récupérer 3 recettes de ce type
            query = db.query(Recette).filter(Recette.est_equilibre)

            # Filtrer par type de protéine (poisson_blanc et poisson_gras → filtre sur "poisson")
            if type_proteine in ("poisson", "poisson_blanc", "poisson_gras"):
                query = query.filter(Recette.type_proteines.ilike("%poisson%"))
            elif type_proteine == "viande_rouge":
                query = query.filter(Recette.type_proteines.ilike("%viande%"))
            elif type_proteine == "vegetarien":
                query = query.filter(Recette.est_vegetarien)

            # Exclure les ingrédients interdits
            for ingredient_exc in parametres.ingredients_exclus:
                # Filtre basique (devrait utiliser une vraie relation en prod)
                query = query.filter(~Recette.description.ilike(f"%{ingredient_exc}%"))

            # Récupérer 3 suggestions
            recettes = query.limit(3).all()

            suggestions_jour = []
            for recette in recettes:
                suggestions_jour.append(
                    {
                        "id": recette.id,
                        "nom": recette.nom,
                        "description": recette.description,
                        "temps_total": (recette.temps_preparation or 0)
                        + (recette.temps_cuisson or 0),
                        "type_repas": type_repas,
                        "raison": raison_jour,
                        "type_proteines": recette.type_proteines,
                    }
                )

            # Si pas assez, ajouter des recettes équilibrées quelconques
            if len(suggestions_jour) < 3:
                autres = (
                    db.query(Recette)
                    .filter(Recette.id.notin_([s["id"] for s in suggestions_jour]))
                    .limit(3 - len(suggestions_jour))
                    .all()
                )

                for recette in autres:
                    suggestions_jour.append(
                        {
                            "id": recette.id,
                            "nom": recette.nom,
                            "description": recette.description,
                            "temps_total": (recette.temps_preparation or 0)
                            + (recette.temps_cuisson or 0),
                            "type_repas": type_repas,
                            "raison": "📝 Alternative équilibrée",
                            "type_proteines": getattr(recette, "type_proteines", "mixte"),
                        }
                    )

            suggestions_globales.append(
                {
                    "jour": jour_name,
                    "jour_index": idx,
                    "date": date_jour.isoformat(),
                    "raison_jour": raison_jour,
                    "suggestions": suggestions_jour[:3],
                }
            )

        logger.info(f"✅ Generated {len(suggestions_globales)} days of balanced suggestions")
        return suggestions_globales

    # ═══════════════════════════════════════════════════════════
    # GÉNÉRATION IA PLANNING HEBDOMADAIRE
    # ═══════════════════════════════════════════════════════════

    @avec_gestion_erreurs(default_return=None)
    @chronometre("ia.planning.generer", seuil_alerte_ms=15000)
    @avec_session_db
    def generer_planning_ia(
        self,
        semaine_debut: date,
        preferences: dict[str, Any] | None = None,
        db: Session | None = None,
    ) -> Planning | None:
        """Génère un planning hebdomadaire avec l'IA.

        Generates a complete weekly meal plan using Mistral AI.
        Includes breakfast/lunch/dinner organization.

        Args:
            semaine_debut: Start date of the week (Monday)
            preferences: Optional preferences dict for meal types, dietary restrictions, etc.
            db: Database session (injected by @avec_session_db)

        Returns:
            Planning object with generated meals, or None if generation fails
        """
        # Utilisation du Mixin pour contexte planning
        context = self.build_planning_context(
            config=preferences or {},
            semaine_debut=semaine_debut.strftime("%d/%m/%Y"),
        )

        prefs = preferences or {}
        legumes_souhaites: list[str] = prefs.get("legumes_souhaites", [])
        feculents_souhaites: list[str] = prefs.get("feculents_souhaites", [])
        plats_souhaites: list[str] = prefs.get("plats_souhaites", [])
        autoriser_restes: bool = prefs.get("autoriser_restes", True)
        recettes_favorites: list[dict] = prefs.get("recettes_favorites", [])

        # Préférences nutritionnelles — injectées depuis UserPreferences par la route
        nb_poisson_blanc: int = int(prefs.get("nb_poisson_blanc", 1))
        nb_poisson_gras: int = int(prefs.get("nb_poisson_gras", 1))
        viande_rouge_max: int = int(prefs.get("viande_rouge_max", 2))
        nb_vegetarien: int = int(prefs.get("nb_vegetarien", 1))
        jules_present: bool = bool(prefs.get("jules_present", True))
        jules_age_mois: int = int(prefs.get("jules_age_mois", 19))
        robots: list[str] = prefs.get("robots", [])
        aliments_favoris: list[str] = prefs.get("aliments_favoris", [])
        saison_actuelle: str = prefs.get("saison_actuelle", "printemps")

        semaine_fin = semaine_debut + timedelta(days=6)

        # Construire prompt ultra-direct (comme pour recettes)
        legumes_section = (
            f"\nLÉGUMES À PRIVILÉGIER CETTE SEMAINE (forte préférence — essaie d'inclure chacun dans 2-3 préparations différentes) :\n"
            + "\n".join(f"- {v}" for v in legumes_souhaites)
            if legumes_souhaites
            else ""
        )
        feculents_section = (
            f"\nFÉCULENTS À PRIVILÉGIER CETTE SEMAINE (forte préférence — utilise-les en priorité pour les champs feculents) :\n"
            + "\n".join(f"- {f}" for f in feculents_souhaites)
            if feculents_souhaites
            else ""
        )
        plats_section = (
            f"\nPLATS À INCLURE CETTE SEMAINE — OBLIGATION (voir règle 11) :\n"
            + "\n".join(f"- {p}" for p in plats_souhaites)
            if plats_souhaites
            else ""
        )

        # Stratégie 4 portions : dîners en sauce/gratin/soupe → midi du lendemain
        if autoriser_restes:
            restes_section = (
                "\nSTRATÉGIE 4 PORTIONS — MINIMUM OBLIGATOIRE 3 MIDIS RESTES SUR 7 :\n"
                "Pour TOUT dîner en sauce, gratin, soupe, lasagnes, cocotte, tajine, ragoût, rôti, "
                "risotto, curry, korma, wok, poêlée, mijoté, boulettes, hachis parmentier, "
                "pot-au-feu, gratin de légumes, crumble salé, poulet basquaise, blanquette — "
                "cuisiner 4 portions (2 adultes + Jules + 1 extra). "
                "La portion extra DEVIENT OBLIGATOIREMENT le déjeuner du LENDEMAIN : "
                "dejeuner_est_reste=true, dejeuner_reste_source=\"dîner de [JOUR]\". "
                "MINIMUM OBLIGATOIRE : au moins 3 des 6 déjeuners (Mardi→Dimanche) DOIVENT être des restes — "
                "c'est une contrainte non négociable, pas une suggestion. "
                "STRATÉGIE : choisis INTENTIONNELLEMENT 3 à 4 de tes dîners parmi les plats compatibles restes. "
                "NON ÉLIGIBLES aux restes (ne jamais mettre est_reste=true) : poisson grillé, poisson vapeur, "
                "salade, omelette, tartare, carpaccio — plats frais non réchauffables."
            )
        else:
            restes_section = (
                "\nPORTIONS : Pas de restes réchauffés. Chaque repas doit être une préparation fraîche."
            )

        recettes_section = (
            f"\nRECETTES FAVORITES À RÉUTILISER (l'utilisateur les apprécie — réintègre-en au moins 2 dans la semaine si elles s'y prêtent) :\n"
            + "\n".join(
                f"- {r['nom']} (préparé {r.get('frequence', 1)} fois)" for r in recettes_favorites
            )
            if recettes_favorites
            else ""
        )

        # Bloc OMS dynamique selon préférences utilisateur (basé sur des nombres, pas des jours fixes)
        poisson_blanc_ligne = (
            f"- POISSON BLANC : exactement {nb_poisson_blanc} repas AU TOTAL sur la semaine — cabillaud, merlu, colin, sole, bar, lieu noir, daurade SONT TOUS DU POISSON BLANC et comptent ENSEMBLE dans ce quota de {nb_poisson_blanc}. Choisir {nb_poisson_blanc} espèce(s) MAXIMUM sur toute la semaine."
            if nb_poisson_blanc > 0
            else "- Pas de poisson blanc cette semaine"
        )
        poisson_gras_ligne = (
            f"- POISSON GRAS : exactement {nb_poisson_gras} repas AU TOTAL (saumon, maquereau, sardines, hareng, truite saumonée — comptent ensemble) — oméga-3 essentiels OMS"
            if nb_poisson_gras > 0
            else ""
        )
        poisson_lines = "\n".join(filter(None, [poisson_blanc_ligne, poisson_gras_ligne]))
        vegetarien_ligne = (
            f"- Minimum {nb_vegetarien} repas VÉGÉTARIEN ou légumineuses cette semaine (lentilles, pois chiches, haricots, œufs, tofu)"
            if nb_vegetarien > 0
            else ""
        )
        oms_section = f"""
ÉQUILIBRE NUTRITIONNEL HEBDOMADAIRE (recommandations OMS — OBLIGATOIRE) :
{poisson_lines}
- Maximum {viande_rouge_max} repas de viande rouge sur toute la semaine (bœuf, veau, agneau) — réduction risque cardiovasculaire OMS
{vegetarien_ligne}
- Reste des jours: volaille préférée (poulet, dinde, pintade, canard)
- Ne jamais mettre 2 fois le même ingrédient principal à 2 repas consécutifs (déjeuner ou dîner)
- Varier les féculents : alterner pâtes, riz, pommes de terre, semoule, légumineuses"""

        # Section robots cuisine disponibles
        robots_section = (
            f"\nROBOTS CUISINE DISPONIBLES (adapter les recettes pour utiliser ces équipements si pertinent) :\n"
            + "\n".join(f"- {r}" for r in robots)
            if robots
            else ""
        )

        # Section aliments favoris
        favoris_section = (
            f"\nALIMENTS FAVORIS (inclure fréquemment si possible — au moins 2-3 fois dans la semaine) :\n"
            + "\n".join(f"- {a}" for a in aliments_favoris)
            if aliments_favoris
            else ""
        )

        # Section Jules si présent dans la famille
        jules_section = (
            f"""
JULES ({jules_age_mois} mois — mange les mêmes plats adaptés) :
- Noms de plats COURTS et SIMPLES — un seul nom sans parenthèses, sans précisions entre parenthèses, sans suffixes. Exemples corrects: "Bœuf bourguignon", "Carottes vapeur", "Salade verte". JAMAIS: "Carottes (mixées pour Jules)", "(sans sel)", "(sans piment)", "(version bébé)"
- Jules mange la même chose adaptée : sans sel ajouté, sans alcool même en sauce, sans épices fortes, textures adaptées si nécessaire — but NEVER mention these adaptations in the field values
- POISSON CRU INTERDIT pour Jules — ne jamais planifier tartare, carpaccio, sashimi, gravlax un jour où Jules mange. Toujours choisir du poisson CUIT (vapeur, grillé, poché)
- À éviter également : marinades alcoolisées, piments, moutarde forte
- Jules ne mange PAS d'entrée — inclure impérativement un légume dans diner_legumes/dejeuner_legumes pour chaque repas"""
            if jules_present
            else ""
        )

        # Section saison
        saison_labels = {"printemps": "printemps", "ete": "été", "automne": "automne", "hiver": "hiver"}
        saison_label = saison_labels.get(saison_actuelle, saison_actuelle)
        # Plats de saison par saison — guide l'IA vers des plats cohérents avec la météo
        plats_saison_notes = {
            "printemps": "Privilégier plats légers : poulet grillé, poisson vapeur, sautés de légumes printaniers. Éviter les plats d'hiver lourds (gratin dauphinois, tartiflette, bœuf bourguignon, raclette, fondue, pot-au-feu, cassoulet).",
            "ete": "Plats froids, grillades, salades composées. Éviter les plats chauds lourds (gratins, rôtis braisés, cuisses confites).",
            "automne": "Plats mijotés légers, soupes, roasted vegetables. Les plats de type bourguignon et ragoût sont acceptables en fin d'automne.",
            "hiver": "Plats mijotés, gratins, cocottes, soupes réconfortantes — toute la gamme hivernale est appropriée.",
        }
        saison_section = (
            f"\nSAISON ACTUELLE : {saison_label.upper()}\n"
            f"{plats_saison_notes.get(saison_actuelle, '')}"
        )

        # Section ingrédients interdits (allergies)
        allergies: list[str] = prefs.get("allergies", [])
        allergies_section = (
            f"\nINGRÉDIENTS INTERDITS — NE JAMAIS UTILISER dans aucun plat (allergie/intolérance) :\n"
            + "\n".join(f"- {a}" for a in allergies)
            if allergies
            else ""
        )

        prompt = f"""GENERATE A 7-DAY MEAL PLAN (MONDAY-SUNDAY) IN JSON FORMAT ONLY.

CONTEXT:
{context}{saison_section}{oms_section}{jules_section}{allergies_section}{robots_section}{favoris_section}{legumes_section}{feculents_section}{plats_section}{restes_section}{recettes_section}

OUTPUT ONLY THIS JSON STRUCTURE (no other text, no markdown, no code blocks):
{{"items": [
  {{
    "jour": "Lundi",
    "petit_dejeuner": "Tartines beurre confiture",
    "petit_dejeuner_est_recette": false,
    "dejeuner": "Pâtes carbonara",
    "dejeuner_entree": "Salade verte",
    "dejeuner_entree_est_recette": false,
    "dejeuner_laitage": "Yaourt nature",
    "dejeuner_legumes": "Haricots verts vapeur",
    "dejeuner_feculents": "Pâtes",
    "dejeuner_dessert": "Tarte aux pommes",
    "dejeuner_dessert_est_recette": true,
    "dejeuner_proteine_accompagnement": null,
    "dejeuner_est_reste": false,
    "dejeuner_reste_source": null,
    "gouter": "Pain au chocolat",
    "gouter_est_recette": false,
    "gouter_laitage": "Yaourt nature",
    "gouter_fruit": "Pomme",
    "gouter_gateau": "Cake maison",
    "diner": "Filet de colin sauce citronnée",
    "diner_entree": null,
    "diner_entree_est_recette": false,
    "diner_laitage": "Fromage",
    "diner_legumes": "Courgettes sautées",
    "diner_feculents": "Riz vapeur",
    "diner_dessert": null,
    "diner_dessert_est_recette": false,
    "diner_proteine_accompagnement": null,
    "diner_est_reste": false,
    "diner_reste_source": null
  }}
]}}

RULES:
1. Return ONLY valid JSON with exactly 7 items (one per day: Lundi→Dimanche)
2. dejeuner and diner (le PLAT principal): ONLY the main dish/recipe name — NEVER include sides, accompaniments, or ingredients in this field. Correct: "Poulet curry", "Filet de saumon", "Gratin dauphinois". FORBIDDEN: "Poulet curry, riz basmati, carottes vapeur" or "Saumon avec haricots verts". Sides go ONLY in legumes/feculents fields. Max 40 chars, no parentheses.
3. petit_dejeuner: TOUJOURS un petit-déjeuner français classique — tartines, pain, céréales, viennoiseries, yaourt, fruit, jus. En semaine: texte court simple (tartines beurre, céréales lait, pain confiture, yaourt fruit). Le week-end: peut être est_recette=true pour des préparations spéciales (crêpes, gaufres, pain perdu, pancakes, granola maison). ABSOLUMENT INTERDIT dans petit_dejeuner: omelette, œufs brouillés, œufs sur le plat, quiche, tout plat salé cuisiné — ce sont des plats de repas, PAS des petits-déjeuners.
4. entree/dessert: optional — include only if the meal complexity warrants it; est_recette=true only if real preparation steps needed
5. laitage: text only (yaourt, fromage blanc, fromage, petits-suisses...) — never est_recette
6. gouter: MANDATORY — always a non-null short text representing the cereal product (pain, biscuit, cake...). Never leave null. gouter_laitage MANDATORY (yaourt, fromage frais, fromage blanc...). gouter_fruit MANDATORY — whole fruit (pomme, poire, banane, raisin, clémentine...) OR compote (compote pomme, compote poire...) — NEVER a juice. gouter_gateau MANDATORY — same as gouter: a healthy cereal/biscuit product (cake maison, galette avoine, biscuit complet, pain d'épices, tartines, pain au chocolat...). gouter and gouter_gateau should match.
7. PROTEINS — strictly follow the OMS balance section above: MAX {nb_poisson_blanc}x TOTAL white fish (bar, merlu, lieu noir, cabillaud, sole = ALL are white fish — they share ONE common quota of {nb_poisson_blanc}), {nb_poisson_gras}x fatty fish total, max {viande_rouge_max}x red meat total for the whole week, min {nb_vegetarien}x vegetarian, other days=poultry. ALL white fish species together count as ONE pool: if nb_poisson_blanc=1 you can have cabillaud OR bar OR merlu — only ONE species total, NOT one of each. Same rule for fatty fish. Spread each protein type throughout the week, never two consecutive identical proteins.
8. 4-PORTIONS STRATEGY (MANDATORY MINIMUM: 3 LUNCHES MUST BE LEFTOVERS) — for sauces/gratins/soups/stews/lasagnes/risottos/currys/woks/poêlées/cocottes/tajines/mijotés/rôtis/boulettes: set dejeuner_est_reste=true the NEXT DAY with dejeuner_reste_source="dîner de [JOUR]". MANDATORY: at least 3 of the 6 lunches (Mardi→Dimanche) MUST be leftovers — NOT optional. Plan your dinners intentionally: choose at least 3-4 dinner dishes that ARE reheatable. CRITICAL: dejeuner_reste_source MUST reference the IMMEDIATELY PREVIOUS day — never a future day, never the same day. Example: Mardi's lunch can only reference "dîner de Lundi", NEVER "dîner de Mercredi" or later. Mercredi's lunch → "dîner de Mardi". IMPORTANT: A reste of a viande rouge dish still counts as 1 viande rouge occurrence in your max {viande_rouge_max} total — plan accordingly. ABSOLUTE RULES FOR RESTES: (a) NEVER set est_reste=true without a non-null reste_source — if you cannot name a real previous meal as the source, set est_reste=false; (b) diner_est_reste MUST ALWAYS be false — dinners are ALWAYS fresh preparations, NEVER leftovers. This field is permanently banned from ever being true in this app; (c) NEVER set any est_reste=true on Dimanche diner (last meal of the week — no identifiable source). RISOTTO STAYS RULE: for RESTES of dishes like risotto, quiche, gratin — feculents=null (the dish already contains its own starch — adding "Riz vapeur" or similar is FORBIDDEN).
9. null is valid ONLY for entree, laitage, dessert, reste_source, proteine_accompagnement. For RESTES (dejeuner_est_reste=true or diner_est_reste=true): copy legumes, feculents AND proteine_accompagnement from the original dish — do NOT return null for legumes/feculents. Example: if the source was 'Bœuf bourguignon' with legumes='Poêlée de légumes' and feculents='Pâtes', the reste must also have legumes='Poêlée de légumes' and feculents='Pâtes'. For all other meals (non-restes): legumes and feculents are MANDATORY (never null) — fill them with what is in the dish — EXCEPT when the ingredient is already literally named in the dish (e.g. if dejeuner="Agneau rôti aux légumes, semoule" then feculents=null because "semoule" is already in the name; if dejeuner="Omelette aux poivrons et pommes de terre" then legumes=null AND feculents=null). CRITICAL VEGETABLE EXCEPTION: If a vegetable or ingredient is ALREADY IN THE DISH NAME, you MUST NOT repeat it in the legumes field. Instead use a DIFFERENT vegetable. EXAMPLES: 'Risotto aux asperges' → legumes=null OR legumes='Salade verte' — ABSOLUTELY FORBIDDEN: legumes='Asperges vapeur'. 'Dinde aux champignons' → legumes MUST NOT be 'Champignons sautés' — use 'Haricots verts', 'Brocoli', 'Courgettes' instead. 'Bœuf haché aux poivrons' → legumes MUST NOT be 'Poivrons grillés' — use 'Salade verte', 'Haricots verts', 'Courgettes' instead. 'Poulet aux courgettes' → legumes must NOT be 'Courgettes sautées' — use 'Haricots verts' or 'Salade' instead. General rule: NEVER put a variant of the SAME ingredient in both the dish name AND the legumes field.
10. No explanations, no text, ONLY JSON
11. MANDATORY — PLATS À INCLURE: every dish listed in the "PLATS À INCLURE" section MUST appear at least once as dejeuner or diner. Do NOT ignore them.
12. PNNS4 ASSIETTE ÉQUILIBRÉE — for every dejeuner and diner that is NOT a reste AND NOT a dish-as-starch (see Rule 17), the meal MUST include BOTH:
    a) legumes field: ≥ half the plate (haricots verts, courgettes sautées, brocoli vapeur, carottes, épinards, poêlée de légumes...) — NEVER null
    b) feculents field: ~1/4 of the plate (riz, pâtes, pommes de terre, semoule, quinoa...) — NEVER null
    EXCEPTION: for dishes that ARE their own starch (see Rule 17), set feculents=null and legumes=side vegetable. NEVER leave legumes null except when the vegetable is literally in the dish name (see Rule 9).
13. NO DISH REPETITION — Never plan the exact same main dish (dejeuner or diner) more than once across the 7 days. This includes CONCEPTUALLY IDENTICAL dishes with slightly different names: 'Rôti de poulet aux herbes' and 'Poulet rôti aux légumes' are BOTH roasted chicken — only ONE per week. 'Filet de saumon grillé' and 'Pavé de saumon' are BOTH salmon — only ONE per week. Rule: same protein + same cooking method = forbidden repetition. Vary BOTH the protein source AND the cooking technique throughout the week.
14. PROTEIN MANDATORY — every dejeuner and diner MUST contain a protein source. If the main dish has NO visible protein in its name, you MUST fill proteine_accompagnement. MANDATORY EXAMPLES: 'Gratin dauphinois' → proteine_accompagnement='Jambon blanc' (NEVER null); 'Tarte aux poireaux' → 'Lardons' or 'Saumon poché'; 'Risotto aux légumes' → 'Crevettes sautées' or 'Blanc de poulet'; 'Ratatouille' → 'Blanc de poulet grillé'; 'Soupe de légumes' → 'Pain complet fromage' or 'Œuf dur'; 'Poêlée de légumes' → 'Blanc de dinde'. Rule: a dish with no animal or legume protein keyword in its name ALWAYS needs proteine_accompagnement. For restes, copy proteine_accompagnement from the source dish. Never plan a meal with zero protein across all fields.
15. ABSOLUTE FORBIDDEN INGREDIENTS — Ingredients listed in "INGRÉDIENTS INTERDITS" are STRICTLY BANNED in EVERY field without ANY exception: dejeuner, diner, entree, legumes, feculents, dessert, petit_dejeuner, laitage, gouter_fruit, gouter_gateau, proteine_accompagnement, and ALL other fields. The ban EXTENDS to all preparations containing that ingredient (if 'concombre' is forbidden → 'concombre à la crème', 'salade de concombre', 'tzatziki' are ALL forbidden — same for champignons, marrons, etc.). There is NO exception. This is the most critical rule.
16. ENTREE NEVER DUPLICATES LEGUMES — dejeuner_entree and dejeuner_legumes (and their diner_ equivalents) MUST contain different dishes or vegetables. If entree is 'Salade de carottes', legumes MUST be a different vegetable ('Haricots verts', 'Brocoli vapeur'...). Having the same or equivalent value in both fields is FORBIDDEN.
17. DISH-AS-STARCH: feculents=null WHEN THE DISH IS ITS OWN STARCH — Never list as féculent an ingredient that is the structural base of the dish itself. Set feculents=null in these cases:
    - 'Quiche lorraine' / 'Quiche aux poireaux': feculents=null (pâte brisée IS the dish — FORBIDDEN: feculents='Pâte brisée')
    - 'Tarte salée': feculents=null (same reason)
    - 'Gratin dauphinois': feculents=null (pommes de terre ARE the dish — FORBIDDEN: feculents='Pommes de terre')
    - 'Tartiflette' / 'Hachis parmentier': feculents=null (pommes de terre = dish base)
    - 'Risotto': feculents=null (riz IS the risotto — FORBIDDEN: feculents='Riz' or feculents='Quinoa')
    - This applies to ALL risotto variants: 'Risotto aux asperges', 'Risotto aux champignons', 'Risotto aux fruits de mer' — ALL → feculents=null regardless of the accompanying vegetable or ingredient
    - 'Lasagnes': feculents=null (pasta IS the structure)
    - 'Lentilles à la tomate' / 'Dal' / 'Pois chiches' / 'Salade de lentilles' / 'Soupe de lentilles' / 'Lentilles vinaigrette': feculents=null (toutes les préparations à base de légumineuses = féculent+protéine combinés — JAMAIS ajouter riz ou autre féculent en accompagnement)
    In ALL these cases: legumes MUST be filled with a vegetable side (e.g. 'Salade verte', 'Haricots verts', 'Épinards') — NEVER another cold salad alongside a lentil salad (e.g. 'Carottes râpées' with 'Salade de lentilles' = FORBIDDEN, both are cold salads — use a COOKED vegetable instead: 'Haricots verts', 'Brocoli vapeur', 'Courgettes sautées').
    PROTEIN CHECK: quiche, tarte salée, gratin, risotto, lasagnes have no obvious standalone protein → ALWAYS fill proteine_accompagnement (see Rule 14 examples).
18. VEGETABLE COHERENCE — legumes MUST make culinary sense with the main dish. Think like a real chef:
    - Roast chicken (poulet rôti) → haricots verts, petits pois, carottes glacées, haricots plats, ratatouille
    - Grilled fish (poisson grillé, filet de cabillaud, lieu noir) → haricots verts, courgettes, épinards vapeur, fenouil braisé
    - Beef stew (bœuf bourguignon, daube) → carottes, champignons, navets (these ARE part of the dish — note: add them to legumes only if not already in dish components)
    - Pot-au-feu → carottes, navets, poireaux (these are IN the dish — legumes='Légumes du bouillon' or 'Salade verte en entrée')
    - Pasta (pâtes bolognaise, carbonara, pesto) → salade verte, courgettes sautées — NEVER put a heavy steamed vegetable with pasta that already has a rich sauce
    - Mediterranean dishes (ratatouille, poulet basquaise, moussaka) → salade verte or tomatoes — AVOID Nordic/Northern vegetables (choux de Bruxelles, endives)
    - ABSOLUTELY FORBIDDEN incoherent pairings: 'Épinards' with 'Poulet basquaise'; 'Choux de Bruxelles' with 'Filet de sole meunière'; 'Carottes vapeur' with 'Moules marinières' (maritime dish needs maritime vegetables: fenouil, céleri)
    - If the requested legumes list (LÉGUMES À INCLURE) conflicts with the dish, still use them but match them to the MOST coherent dish available that week."""

        logger.info(f"🤖 Generating AI weekly plan starting {semaine_debut}")

        # Appel IA avec auto rate limiting & parsing
        # use_cache=False : chaque génération doit produire un planning UNIQUE (pas de réponse recyclée)
        planning_data = self.call_with_list_parsing_sync(
            prompt=prompt,
            item_model=JourPlanning,
            system_prompt="Return ONLY valid JSON. No text before or after JSON. Never use markdown code blocks.",
            max_items=7,
            temperature=0.5,
            max_tokens=3000,
            use_cache=False,
        )

        # Log de debug pour voir la réponse
        if not planning_data:
            logger.warning(
                f"⚠️ Aucune donnée IA reçue pour le planning {semaine_debut} — l'appel Mistral n'a pas produit de résultat parsable."
            )
            from src.core.exceptions import ErreurServiceIA

            raise ErreurServiceIA(
                "Aucune donnée retournée par Mistral pour la génération du planning",
                message_utilisateur="L'IA n'a pas pu générer le planning. Vérifiez la clé Mistral ou réessayez.",
            )

        # Garde : Mistral doit retourner exactement 7 jours
        if len(planning_data) < 7:
            jours_manquants = 7 - len(planning_data)
            logger.error(
                f"⛔ Planning IA incomplet : {len(planning_data)}/7 jours reçus "
                f"({jours_manquants} jour(s) manquant(s)) — semaine {semaine_debut}"
            )
            from src.core.exceptions import ErreurServiceIA

            raise ErreurServiceIA(
                f"Planning IA incomplet : {len(planning_data)} jours seulement (7 attendus)",
                message_utilisateur="L'IA n'a pas généré les 7 jours du planning. Réessayez.",
            )

        # Planning IA réussi
        logger.info(f"✅ Generated planning with {len(planning_data)} days using AI")

        # Correction auto si l'IA a généré trop peu de restes (< 3)
        if autoriser_restes:
            planning_data = self._corriger_restes_insuffisants(planning_data)

        # Archiver les plannings existants de la même semaine pour éviter les doublons.
        # (brouillons orphelins laissés par des générations précédentes)
        semaine_fin = semaine_debut + timedelta(days=6)
        db.query(Planning).filter(
            Planning.semaine_debut == semaine_debut,
            Planning.etat.notin_(["archive"]),
        ).update({"etat": "archive"}, synchronize_session=False)

        # Créer planning en DB
        # etat="brouillon" : le planning généré doit être validé par l'utilisateur
        # avant d'être activé (cf. route POST /{id}/valider).
        planning = Planning(
            nom=f"Planning {semaine_debut.strftime('%d/%m/%Y')}",
            semaine_debut=semaine_debut,
            semaine_fin=semaine_fin,
            etat="brouillon",
            genere_par_ia=True,
        )
        db.add(planning)
        db.flush()

        # Créer repas pour chaque jour
        from src.services.planning.nutrition import (
            analyser_distribution_proteines_semaine,
            evaluer_equilibre_repas,
        )

        _JOURS_IDX = {
            "lundi": 0, "mardi": 1, "mercredi": 2, "jeudi": 3,
            "vendredi": 4, "samedi": 5, "dimanche": 6,
        }
        repas_generes: list[Repas] = []

        for idx, jour_data in enumerate(planning_data):
            date_jour = semaine_debut + timedelta(days=idx)

            # Petit-déjeuner (optionnel selon ce que l'IA a fourni)
            if jour_data.petit_dejeuner:
                recette_pdj_id = (
                    self._trouver_ou_creer_recette(db, jour_data.petit_dejeuner, "Petit-déjeuner")
                    if jour_data.petit_dejeuner_est_recette
                    else None
                )
                db.add(
                    Repas(
                        planning_id=planning.id,
                        date_repas=date_jour,
                        type_repas="petit_dejeuner",
                        notes=jour_data.petit_dejeuner,
                        recette_id=recette_pdj_id,
                    )
                )

            # Correction : un reste le lundi (idx=0) est impossible — pas de dîner précédent.
            if jour_data.dejeuner_est_reste and idx == 0:
                logger.warning(
                    f"⚠️ L'IA a marqué le déjeuner du {jour_data.jour} (1er jour, idx=0) comme reste "
                    f"(impossible : pas de repas précédent) — est_reste forcé à False."
                )
                jour_data.dejeuner_est_reste = False
                jour_data.dejeuner_reste_source = None
            # Les dîners sont TOUJOURS des préparations fraîches — jamais des restes réchauffés.
            # L'IA confond parfois « ce dîner va produire des restes » avec « ce dîner EST un reste ».
            # On force diner_est_reste=False systématiquement.
            if jour_data.diner_est_reste:
                logger.warning(
                    f"⚠️ L'IA a marqué le dîner de {jour_data.jour} comme reste "
                    f"(diner_est_reste doit toujours être False) — forcé à False."
                )
                jour_data.diner_est_reste = False
                jour_data.diner_reste_source = None

            # Cohérence reste_source : vérifier que la référence est antérieure au jour courant.
            # Si elle pointe vers un jour futur ou identique, désactiver le flag reste
            # (persistance d'une donnée invalide évitée).
            for _flag_attr, _source_attr in [
                ("dejeuner_est_reste", "dejeuner_reste_source"),
                ("diner_est_reste", "diner_reste_source"),
            ]:
                _est_reste = getattr(jour_data, _flag_attr)
                _champ_source = getattr(jour_data, _source_attr)
                if _est_reste and _champ_source:
                    src_lower = _champ_source.lower()
                    for _jour_nom, _jour_idx in _JOURS_IDX.items():
                        if _jour_nom in src_lower and _jour_idx >= idx:
                            logger.warning(
                                f"⚠️ reste_source incohérent jour idx={idx} : "
                                f"{_champ_source!r} référence un jour futur ou identique "
                                f"— {_flag_attr} forcé à False."
                            )
                            setattr(jour_data, _flag_attr, False)
                            setattr(jour_data, _source_attr, None)
                            break

            # Guard complémentaire : est_reste=True mais reste_source=None.
            # L'IA peut omettre la source (le check de cohérence sur le nom de jour
            # ne se déclenche que si _champ_source est non-null).
            for _flag_attr, _source_attr in [
                ("dejeuner_est_reste", "dejeuner_reste_source"),
                ("diner_est_reste", "diner_reste_source"),
            ]:
                if getattr(jour_data, _flag_attr) and not getattr(jour_data, _source_attr):
                    logger.warning(
                        f"⚠️ {_flag_attr}=True mais {_source_attr}=None pour {jour_data.jour} "
                        f"— reste sans source identifiable → est_reste forcé à False."
                    )
                    setattr(jour_data, _flag_attr, False)

            # Légumes/féculents : pour les restes, héritage depuis le dîner de la veille ;
            # pour les repas normaux, fallback générique si l'IA n'a rien fourni.
            if not jour_data.dejeuner_legumes:
                if jour_data.dejeuner_est_reste and idx > 0:
                    jour_data.dejeuner_legumes = planning_data[idx - 1].diner_legumes or "Légumes de saison"
                else:
                    jour_data.dejeuner_legumes = "Légumes de saison"
            if not jour_data.dejeuner_feculents:
                if jour_data.dejeuner_est_reste and idx > 0:
                    # Héritage depuis la source ; ne pas appliquer "Riz vapeur" si le
                    # reste est lui-même un plat propre-féculent (risotto, quiche…).
                    _héritage_dej = planning_data[idx - 1].diner_feculents
                    if _héritage_dej:
                        jour_data.dejeuner_feculents = _héritage_dej
                    elif not self._est_plat_propre_feculent(jour_data.dejeuner):
                        jour_data.dejeuner_feculents = "Riz vapeur"
                    # else: reste d'un plat propre-féculent → feculents reste None
                elif not self._est_plat_propre_feculent(jour_data.dejeuner):
                    # Ne pas appliquer de fallback si le plat EST déjà son propre féculent
                    # (quiche, gratin dauphinois, risotto…) — feculents=null est intentionnel
                    jour_data.dejeuner_feculents = "Riz vapeur"
            # Éviter la duplication quand légumes/féculents sont déjà dans le nom du plat
            # (ex : « Semoule » dans « Agneau rôti aux légumes de saison, semoule »)
            jour_data.dejeuner_legumes = self._nettoyer_si_inclus_dans_nom(
                jour_data.dejeuner_legumes, jour_data.dejeuner
            )
            jour_data.dejeuner_feculents = self._nettoyer_si_inclus_dans_nom(
                jour_data.dejeuner_feculents, jour_data.dejeuner
            )
            # Nettoyage sémantique : constituants structurels du plat (gratin→PDT, quiche→pâte…)
            jour_data.dejeuner_feculents = self._nettoyer_feculents_constitutifs(
                jour_data.dejeuner_feculents, jour_data.dejeuner
            )

            # Déjeuner — pour un reste : lookup seul (pas de création de recette stub) ;
            # pour un repas normal : lookup ou création.
            if jour_data.dejeuner_est_reste:
                recette_dej_id = self._trouver_recette_seule(db, jour_data.dejeuner)
            else:
                recette_dej_id = self._trouver_ou_creer_recette(db, jour_data.dejeuner, "Plat")
            entree_dej_recette_id = (
                self._trouver_ou_creer_recette(db, jour_data.dejeuner_entree, "Entrée")
                if jour_data.dejeuner_entree and jour_data.dejeuner_entree_est_recette
                else None
            )
            dessert_dej_recette_id = (
                self._trouver_ou_creer_recette(db, jour_data.dejeuner_dessert, "Dessert")
                if jour_data.dejeuner_dessert and jour_data.dejeuner_dessert_est_recette
                else None
            )
            # Héritage protéine accompagnement pour les restes
            if jour_data.dejeuner_est_reste and not jour_data.dejeuner_proteine_accompagnement and idx > 0:
                jour_data.dejeuner_proteine_accompagnement = planning_data[idx - 1].diner_proteine_accompagnement

            repas_dej = Repas(
                planning_id=planning.id,
                date_repas=date_jour,
                type_repas="dejeuner",
                notes=jour_data.dejeuner,
                recette_id=recette_dej_id,
                entree=jour_data.dejeuner_entree,
                entree_recette_id=entree_dej_recette_id,
                laitage=jour_data.dejeuner_laitage,
                legumes=jour_data.dejeuner_legumes,
                feculents=jour_data.dejeuner_feculents,
                dessert=jour_data.dejeuner_dessert,
                dessert_recette_id=dessert_dej_recette_id,
                proteine_accompagnement=jour_data.dejeuner_proteine_accompagnement,
                est_reste=jour_data.dejeuner_est_reste,
                reste_description=jour_data.dejeuner_reste_source,
            )
            score_dej = evaluer_equilibre_repas(repas_dej)
            repas_dej.score_equilibre = score_dej["score_equilibre"]
            repas_dej.alertes_equilibre = score_dej["alertes_equilibre"] or None
            if score_dej["score_equilibre"] == 0:
                logger.warning(
                    f"⚠️ Déjeuner du {date_jour} a un score d'équilibre de 0 "
                    f"— alertes : {score_dej.get('alertes_equilibre', [])}"
                )
            db.add(repas_dej)
            repas_generes.append(repas_dej)

            # Goûter (obligatoire — fallback si l'IA a quand même renvoyé null)
            if not jour_data.gouter:
                jour_data.gouter = "Fruit de saison"
            if jour_data.gouter:
                recette_gouter_id = (
                    self._trouver_ou_creer_recette(db, jour_data.gouter, "Goûter")
                    if jour_data.gouter_est_recette
                    else None
                )
                db.add(
                    Repas(
                        planning_id=planning.id,
                        date_repas=date_jour,
                        type_repas="gouter",
                        notes=jour_data.gouter,
                        recette_id=recette_gouter_id,
                        laitage=jour_data.gouter_laitage,
                        fruit=jour_data.gouter_fruit,
                        fruit_gouter=jour_data.gouter_fruit,
                        gateau_gouter=jour_data.gouter_gateau,
                    )
                )

            # Légumes/féculents pour le dîner : pour les restes, héritage depuis le dîner
            # de la veille (source la plus probable pour un reste du soir) ; sinon fallback générique.
            if not jour_data.diner_legumes:
                if jour_data.diner_est_reste and idx > 0:
                    jour_data.diner_legumes = planning_data[idx - 1].diner_legumes or "Légumes de saison"
                else:
                    jour_data.diner_legumes = "Légumes de saison"
            if not jour_data.diner_feculents:
                if jour_data.diner_est_reste and idx > 0:
                    _héritage_din = planning_data[idx - 1].diner_feculents
                    if _héritage_din:
                        jour_data.diner_feculents = _héritage_din
                    elif not self._est_plat_propre_feculent(jour_data.diner):
                        jour_data.diner_feculents = "Riz vapeur"
                elif not self._est_plat_propre_feculent(jour_data.diner):
                    # Ne pas appliquer de fallback si le plat EST déjà son propre féculent
                    # (quiche, gratin dauphinois, risotto…) — feculents=null est intentionnel
                    jour_data.diner_feculents = "Riz vapeur"
            # Éviter la duplication quand légumes/féculents sont déjà dans le nom du plat
            jour_data.diner_legumes = self._nettoyer_si_inclus_dans_nom(
                jour_data.diner_legumes, jour_data.diner
            )
            jour_data.diner_feculents = self._nettoyer_si_inclus_dans_nom(
                jour_data.diner_feculents, jour_data.diner
            )
            # Nettoyage sémantique : constituants structurels du plat (gratin→PDT, quiche→pâte…)
            jour_data.diner_feculents = self._nettoyer_feculents_constitutifs(
                jour_data.diner_feculents, jour_data.diner
            )

            # Dîner — pour un reste : lookup seul (pas de création de recette stub) ;
            # pour un repas normal : lookup ou création.
            if jour_data.diner_est_reste:
                recette_din_id = self._trouver_recette_seule(db, jour_data.diner)
            else:
                recette_din_id = self._trouver_ou_creer_recette(db, jour_data.diner, "Plat")
            entree_din_recette_id = (
                self._trouver_ou_creer_recette(db, jour_data.diner_entree, "Entrée")
                if jour_data.diner_entree and jour_data.diner_entree_est_recette
                else None
            )
            dessert_din_recette_id = (
                self._trouver_ou_creer_recette(db, jour_data.diner_dessert, "Dessert")
                if jour_data.diner_dessert and jour_data.diner_dessert_est_recette
                else None
            )
            # Héritage protéine accompagnement pour les restes dîner (source = dîner de la veille)
            if jour_data.diner_est_reste and not jour_data.diner_proteine_accompagnement and idx > 0:
                jour_data.diner_proteine_accompagnement = planning_data[idx - 1].diner_proteine_accompagnement

            repas_din = Repas(
                planning_id=planning.id,
                date_repas=date_jour,
                type_repas="diner",
                notes=jour_data.diner,
                recette_id=recette_din_id,
                entree=jour_data.diner_entree,
                entree_recette_id=entree_din_recette_id,
                laitage=jour_data.diner_laitage,
                legumes=jour_data.diner_legumes,
                feculents=jour_data.diner_feculents,
                dessert=jour_data.diner_dessert,
                dessert_recette_id=dessert_din_recette_id,
                proteine_accompagnement=jour_data.diner_proteine_accompagnement,
                est_reste=jour_data.diner_est_reste,
                reste_description=jour_data.diner_reste_source,
            )
            score_din = evaluer_equilibre_repas(repas_din)
            repas_din.score_equilibre = score_din["score_equilibre"]
            repas_din.alertes_equilibre = score_din["alertes_equilibre"] or None
            if score_din["score_equilibre"] == 0:
                logger.warning(
                    f"⚠️ Dîner du {date_jour} a un score d'équilibre de 0 "
                    f"— alertes : {score_din.get('alertes_equilibre', [])}"
                )
            db.add(repas_din)
            repas_generes.append(repas_din)

        # Vérification hebdomadaire de la distribution des protéines (OMS)
        bilan_proteines = analyser_distribution_proteines_semaine(
            repas_generes, nb_vegetarien_min=nb_vegetarien
        )
        if bilan_proteines.alertes:
            logger.warning(
                f"⚠️ Planning {semaine_debut} — déséquilibre protéique détecté : "
                f"{bilan_proteines.alertes}"
            )
            logger.info(
                f"   Compteurs protéines : {bilan_proteines.compteurs} "
                f"| Score semaine : {bilan_proteines.score_semaine}/100"
            )
        else:
            logger.info(
                f"✅ Distribution protéines OK — score semaine : {bilan_proteines.score_semaine}/100"
            )

        db.commit()
        db.refresh(planning)

        emettre_evenement_simple(
            "planning.modifie",
            {"planning_id": planning.id, "semaine": str(semaine_debut), "action": "genere_ia"},
            source="planning_ia",
        )

        # Invalider cache
        obtenir_cache().invalidate(pattern="planning")

        logger.info(f"✅ Generated AI planning for week starting {semaine_debut}")

        return planning

    # ═══════════════════════════════════════════════════════════
    # ENRICHISSEMENT DES RECETTES STUBS
    # ═══════════════════════════════════════════════════════════

    def enrichir_recettes_stub_planning(self, planning_id: int) -> None:
        """Enrichit en arrière-plan les recettes stubs créées lors de la génération.

        Appelé après ``generer_planning_ia`` via BackgroundTasks : interroge l'IA
        pour obtenir les étapes et ingrédients des recettes qui n'ont encore aucune
        étape enregistrée.

        Args:
            planning_id: ID du planning dont les recettes stubs sont à enrichir.
        """
        try:
            from src.core.db import obtenir_contexte_db
            from src.core.models import EtapeRecette, Ingredient, RecetteIngredient, Repas
            from src.core.models.recettes import Recette

            with obtenir_contexte_db() as session:
                # Collecter tous les recette_id liés au planning
                repas_list = session.query(Repas).filter(Repas.planning_id == planning_id).all()
                recette_ids: set[int] = set()
                for r in repas_list:
                    for rid in (r.recette_id, r.entree_recette_id, r.dessert_recette_id):
                        if rid is not None:
                            recette_ids.add(rid)

                if not recette_ids:
                    return

                # Filtrer celles sans étapes (stubs) — stocker (id, nom) pour éviter les objets détachés
                stubs_data: list[tuple[int, str]] = []
                for recette in session.query(Recette).filter(Recette.id.in_(recette_ids)).all():
                    has_etapes = (
                        session.query(EtapeRecette)
                        .filter(EtapeRecette.recette_id == recette.id)
                        .first()
                    ) is not None
                    if not has_etapes:
                        stubs_data.append((recette.id, recette.nom))

            if not stubs_data:
                logger.debug("[planning] Aucune recette stub à enrichir pour planning %d", planning_id)
                return

            self._enrichir_stubs_data(stubs_data, context=f"planning {planning_id}")

        except Exception as exc:
            logger.warning(
                "[planning] Enrichissement stubs ignoré pour planning %d: %s",
                planning_id,
                exc,
                exc_info=True,
            )

    # ═══════════════════════════════════════════════════════════
    # HELPERS SHARED: appel IA + sauvegarde + enrichissement global
    # ═══════════════════════════════════════════════════════════

    def _enrichir_stubs_data(self, stubs_data: list[tuple[int, str]], context: str = "") -> int:
        """Appel IA + sauvegarde étapes/ingrédients pour une liste de stubs ``(id, nom)``.

        Args:
            stubs_data: Tuples ``(id, nom)`` des recettes à enrichir.
            context:    Libellé pour les logs (ex: ``"planning 42"``, ``"global"``).

        Returns:
            Nombre de recettes effectivement enrichies.
        """
        from src.core.db import obtenir_contexte_db
        from src.core.models import EtapeRecette, Ingredient, RecetteIngredient
        from src.core.models.recettes import Recette

        noms = [nom for _, nom in stubs_data]
        logger.info("[planning] Enrichissement IA de %d recette(s) [%s]: %s", len(noms), context, noms)

        # ── Batcher par 3 pour limiter la taille des réponses Mistral ──────────
        BATCH_SIZE = 3
        total_count = 0
        for batch_start in range(0, len(stubs_data), BATCH_SIZE):
            batch = stubs_data[batch_start : batch_start + BATCH_SIZE]
            total_count += self._enrichir_batch(batch, context=context)

        return total_count

    @staticmethod
    def _safe_quantite(v: object) -> float:
        """Convertit *v* en float, retourne 1.0 si la valeur n'est pas numérique.

        Gère les valeurs renvoyées par Mistral comme ``"au goût"``, ``"QS"``,
        ``None``, ``""`` etc. qui ne peuvent pas être passées à ``float()``.
        """
        try:
            return float(v)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            return 1.0

    def _enrichir_batch(self, stubs_data: list[tuple[int, str]], context: str = "") -> int:
        """Enrichit un batch de ≤3 recettes via un seul appel Mistral."""
        from src.core.db import obtenir_contexte_db
        from src.core.models import EtapeRecette, Ingredient, RecetteIngredient
        from src.core.models.recettes import Recette

        noms = [nom for _, nom in stubs_data]
        liste_noms = "\n".join(f"{i + 1}. {nom}" for i, nom in enumerate(noms))
        prompt = f"""For each recipe listed below, generate practical cooking steps and main ingredients.

OUTPUT ONLY THIS JSON (no other text, no markdown, no code blocks):
{{"items": [
  {{
    "nom": "Pâtes carbonara",
    "temps_preparation": 10,
    "temps_cuisson": 15,
    "portions": 4,
    "difficulte": "facile",
    "ingredients": [{{"nom": "spaghetti", "quantite": 400, "unite": "g"}}, {{"nom": "lardons", "quantite": 200, "unite": "g"}}, {{"nom": "oeufs", "quantite": 3, "unite": "pièce"}}],
    "etapes": ["Faire bouillir l'eau salée et cuire les spaghetti al dente.", "Faire revenir les lardons à sec dans une poêle.", "Mélanger les oeufs battus avec le parmesan.", "Égoutter les pâtes, hors du feu mélanger avec les lardons puis la sauce oeufs-parmesan."]
  }}
]}}

RULES:
1. Return ONLY valid JSON — no text before or after
2. One item per recipe, in the SAME ORDER as the input list
3. etapes: array of French strings, 3-8 steps each, describing the actual cooking process
4. ingredients: array of {{nom, quantite, unite}}, 3-12 items
5. Keep nom identical to the input recipe name
6. No explanations, ONLY JSON

Recipes to enrich:
{liste_noms}"""

        enriched = self.call_with_list_parsing_sync(
            prompt=prompt,
            item_model=RecetteEnrichieIA,
            system_prompt="Return ONLY valid JSON. No text before or after JSON.",
            max_items=len(noms),
            use_cache=False,
            temperature=0.3,
            max_tokens=4000,
        )

        if not enriched:
            logger.warning("[planning] Aucune donnée IA reçue pour l'enrichissement [%s]", context)
            return 0

        stubs_by_nom = {nom.lower(): rid for rid, nom in stubs_data}
        stubs_ids_ordered = [rid for rid, _ in stubs_data]
        with obtenir_contexte_db() as session:
            count = 0
            matched_ids: set[int] = set()
            for enriched_idx, recette_ia in enumerate(enriched):
                stub_id = stubs_by_nom.get(recette_ia.nom.lower())
                if stub_id is None:
                    for nom_key, rid in stubs_by_nom.items():
                        if recette_ia.nom.lower() in nom_key or nom_key in recette_ia.nom.lower():
                            stub_id = rid
                            break
                # Fallback positionnel : Mistral a retourné les items dans le même ordre
                if stub_id is None and enriched_idx < len(stubs_ids_ordered):
                    candidate = stubs_ids_ordered[enriched_idx]
                    if candidate not in matched_ids:
                        stub_id = candidate
                        logger.debug(
                            "[planning] Fallback positionnel idx=%d → recette_id=%d (%s→%s)",
                            enriched_idx, candidate, stubs_data[enriched_idx][1], recette_ia.nom,
                        )
                if stub_id is None:
                    continue
                matched_ids.add(stub_id)

                db_recette = session.get(Recette, stub_id)
                if db_recette is None:
                    continue

                if recette_ia.temps_preparation:
                    db_recette.temps_preparation = recette_ia.temps_preparation
                if recette_ia.temps_cuisson:
                    db_recette.temps_cuisson = recette_ia.temps_cuisson
                if recette_ia.portions:
                    db_recette.portions = recette_ia.portions
                if recette_ia.difficulte:
                    db_recette.difficulte = recette_ia.difficulte

                # Supprimer les étapes et ingrédients existants avant d'insérer ceux de l'IA
                session.query(EtapeRecette).filter(EtapeRecette.recette_id == stub_id).delete()
                session.query(RecetteIngredient).filter(RecetteIngredient.recette_id == stub_id).delete()

                for idx, texte in enumerate(recette_ia.etapes, start=1):
                    texte = texte.strip()
                    if texte:
                        session.add(
                            EtapeRecette(
                                recette_id=stub_id,
                                ordre=idx,
                                description=texte,
                            )
                        )

                for ing_data in recette_ia.ingredients:
                    nom_ing = (ing_data.get("nom") or "").strip()
                    if not nom_ing:
                        continue
                    db_ingredient = (
                        session.query(Ingredient).filter(Ingredient.nom == nom_ing).first()
                    )
                    if db_ingredient is None:
                        db_ingredient = Ingredient(
                            nom=nom_ing,
                            unite=ing_data.get("unite") or "pièce",
                        )
                        session.add(db_ingredient)
                        session.flush()
                    session.add(
                        RecetteIngredient(
                            recette_id=stub_id,
                            ingredient_id=db_ingredient.id,
                            quantite=self._safe_quantite(ing_data.get("quantite")),
                            unite=ing_data.get("unite") or db_ingredient.unite,
                        )
                    )

                count += 1

            session.commit()
            logger.info("[planning] ✅ %d recette(s) enrichie(s) [%s]", count, context)
            return count

    def enrichir_recettes_stubs_global(self, recette_ids: list[int] | None = None) -> int:
        """Enrichit via l'IA toutes les recettes sans étapes (ou celles de ``recette_ids``).

        Peut être appelé depuis une route admin pour réparer des stubs existants
        sans avoir à régénérer un planning.

        Args:
            recette_ids: IDs à traiter. Si ``None``, toutes les recettes sans étape.

        Returns:
            Nombre de recettes enrichies.
        """
        try:
            from src.core.db import obtenir_contexte_db
            from src.core.models import EtapeRecette
            from src.core.models.recettes import Recette

            with obtenir_contexte_db() as session:
                query = session.query(Recette)
                if recette_ids:
                    query = query.filter(Recette.id.in_(recette_ids))
                stubs_data: list[tuple[int, str]] = []
                for recette in query.all():
                    has_etapes = (
                        session.query(EtapeRecette)
                        .filter(EtapeRecette.recette_id == recette.id)
                        .first()
                    ) is not None
                    if not has_etapes:
                        stubs_data.append((recette.id, recette.nom))

            if not stubs_data:
                logger.info("[planning] Aucune recette stub à enrichir (global)")
                return 0

            return self._enrichir_stubs_data(
                stubs_data, context=f"global ({len(stubs_data)} recettes)"
            )

        except Exception as exc:
            logger.warning("[planning] Enrichissement stubs global échoué: %s", exc, exc_info=True)
            return 0
