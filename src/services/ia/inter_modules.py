"""
Service Inter-Modules — Bridges entre modules.

Connecte les modules via l'event bus et des helpers métier pour :
- B5.1: Récolte jardin → Recettes semaine suivante
- B5.2: Budget anomalie → Notification proactive
- B5.3: Documents expirés → Dashboard alerte
- B5.5: Entretien récurrent → Planning unifié
- B5.6: Voyages → Inventaire (déstockage)
- B5.7: Anniversaire proche → Suggestions cadeaux IA
- B5.8: Météo → Entretien maison
- Consolidation inter_modules: entretien → artisans, récolte → stock, anniversaire → menu, jalon → journal
"""

import importlib
import logging
from datetime import date, timedelta
from pathlib import Path

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.core.decorators import avec_gestion_erreurs, avec_session_db
from src.services.core.events.bus import EvenementDomaine
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)

_CATALOGUE_BRIDGES_LABELS: dict[str, dict[str, str]] = {
    "src.services.utilitaires.inter_modules.inter_module_dashboard_actions": {
        "groupe": "utilitaires",
        "flux": "Dashboard → Actions rapides",
    },
    "src.services.utilitaires.inter_modules.inter_module_chat_event_bus": {
        "groupe": "utilitaires",
        "flux": "Chat IA → Event Bus",
    },
    "src.services.utilitaires.inter_modules.inter_module_chat_contexte": {
        "groupe": "utilitaires",
        "flux": "Chat → Contexte multi-modules",
    },
    "src.services.famille.inter_module_weekend_courses": {
        "groupe": "famille",
        "flux": "Weekend → Courses",
    },
    "src.services.famille.inter_module_voyages_budget": {
        "groupe": "famille",
        "flux": "Voyages → Budget",
    },
    "src.services.famille.inter_module_meteo_activites": {
        "groupe": "famille",
        "flux": "Météo → Activités",
    },
    "src.services.famille.inter_module_documents_calendrier": {
        "groupe": "famille",
        "flux": "Documents → Calendrier",
    },
    "src.services.cuisine.inter_module_saison_menu": {
        "groupe": "cuisine",
        "flux": "Saison → Menu",
    },
    "src.services.maison.inter_modules.inter_module_jardin_entretien": {
        "groupe": "maison",
        "flux": "Jardin → Entretien",
    },
    "src.services.maison.inter_modules.inter_module_entretien_courses": {
        "groupe": "maison",
        "flux": "Entretien → Courses",
    },
    "src.services.maison.inter_modules.inter_module_charges_energie": {
        "groupe": "maison",
        "flux": "Charges → Énergie",
    },
}


def _humaniser_segment(segment: str) -> str:
    """Formate un segment de nom de bridge pour l'UI admin."""
    return segment.replace("_", " ").strip().capitalize()


def _lister_modules_legacy_inter_modules() -> list[str]:
    """Découvre automatiquement les wrappers legacy `inter_module_*.py`."""
    racine_services = Path(__file__).resolve().parents[1]
    racine_repo = racine_services.parents[1]
    modules: list[str] = []

    for fichier in sorted(racine_services.rglob("inter_module_*.py")):
        if fichier.name == "__init__.py":
            continue
        relatif = fichier.relative_to(racine_repo).with_suffix("")
        modules.append(".".join(relatif.parts))

    return modules


def _construire_definition_catalogue(module: str) -> dict[str, str]:
    """Construit la définition d'un bridge pour le catalogue consolidé."""
    if module in _CATALOGUE_BRIDGES_LABELS:
        return {**_CATALOGUE_BRIDGES_LABELS[module], "module": module}

    parties = module.split(".")
    groupe = parties[2] if len(parties) > 2 else "autres"
    nom_bridge = parties[-1].removeprefix("inter_module_")
    morceaux = [morceau for morceau in nom_bridge.split("_") if morceau]

    source = _humaniser_segment(morceaux[0]) if morceaux else "Bridge"
    cible = _humaniser_segment("_".join(morceaux[1:])) if len(morceaux) > 1 else "Actions"

    return {
        "groupe": groupe,
        "flux": f"{source} → {cible}",
        "module": module,
    }


class BridgesInterModulesService:
    """Service de inter_modules inter-modules."""

    def _detecter_metiers_depuis_tache(self, tache: object) -> list[str]:
        """Déduit les métiers d'artisans à partir d'une tâche d'entretien."""
        contenu = " ".join(
            str(getattr(tache, champ, "") or "")
            for champ in ("nom", "description", "categorie", "piece")
        ).lower()

        correspondances = {
            "plombier": ["plomb", "fuite", "robinet", "canalisation", "wc", "eau"],
            "plombier-chauffagiste": ["chaudiere", "chauffage", "radiateur", "chauffe-eau"],
            "électricien": ["electric", "prise", "tableau", "lum", "ampoule", "disjonct"],
            "couvreur": ["toit", "toiture", "gouttiere", "gouttière"],
            "menuisier": ["porte", "fenetre", "fenêtre", "volet", "placard"],
            "peintre": ["peinture", "mur", "plafond"],
            "serrurier": ["serrure", "verrou", "porte bloquee", "porte bloquée"],
            "jardinier": ["jardin", "haie", "pelouse", "taille", "arbre"],
        }

        metiers = [
            metier
            for metier, mots_cles in correspondances.items()
            if any(mot in contenu for mot in mots_cles)
        ]
        return metiers or ["artisan multi-services"]

    def _prioriser_artisans(self, artisans: list[object]) -> list[object]:
        """Ordonne les artisans recommandés par pertinence."""
        return sorted(
            artisans,
            key=lambda artisan: (
                not bool(getattr(artisan, "recommande", True)),
                -(getattr(artisan, "note", 0) or 0),
                str(getattr(artisan, "nom", "")).lower(),
            ),
        )

    def obtenir_catalogue_consolidation(self) -> dict[str, object]:
        """Expose l'état consolidé des inter_modules legacy et canoniques."""
        definitions = [
            _construire_definition_catalogue(module)
            for module in _lister_modules_legacy_inter_modules()
        ]

        items: list[dict[str, object]] = []
        for definition in definitions:
            importable = True
            erreur_import: str | None = None
            try:
                importlib.import_module(str(definition["module"]))
            except Exception as exc:  # pragma: no cover - info d'audit uniquement
                importable = False
                erreur_import = exc.__class__.__name__

            items.append({
                **definition,
                "statut": "consolide",
                "mode": "compat_legacy",
                "disponible": True,
                "importable": importable,
                "verification_import": "ok" if importable else f"warning:{erreur_import}",
            })

        total = len(items)
        groupes = sorted({str(item["groupe"]) for item in items})
        warnings_import = sum(1 for item in items if not item["importable"])

        return {
            "resume": {
                "total_legacy": total,
                "consolides": total,
                "reste_a_traiter": 0,
                "groupes": groupes,
                "warnings_import": warnings_import,
                "statut": "termine",
            },
            "items": items,
        }

    # ── B5.1: Récolte jardin → Suggestions recettes ────────

    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def recolte_vers_recettes(self, element_nom: str, db: Session | None = None) -> list[dict]:
        """Cherche des recettes utilisant un ingrédient récolté au jardin.

        Args:
            element_nom: Nom de l'élément récolté (tomate, basilic, etc.)

        Returns:
            Liste de recettes correspondantes
        """
        from src.core.models.recettes import Recette, Ingredient

        recettes = (
            db.query(Recette)
            .join(Ingredient, Ingredient.recette_id == Recette.id)
            .filter(Ingredient.nom.ilike(f"%{element_nom}%"))
            .limit(10)
            .all()
        )

        return [
            {
                "id": r.id,
                "nom": r.nom,
                "description": r.description,
                "temps_total": r.temps_total,
            }
            for r in recettes
        ]

    # ── B5.3: Documents expirés → Dashboard alerte ─────────

    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def documents_expires_alertes(self, jours_avant: int = 30, db: Session | None = None) -> list[dict]:
        """Liste les documents qui expirent bientôt ou sont déjà expirés.

        Args:
            jours_avant: Nombre de jours avant expiration pour alerter

        Returns:
            Liste de documents avec statut expiration
        """
        from src.core.models import DocumentFamille

        seuil = date.today() + timedelta(days=jours_avant)

        documents = (
            db.query(DocumentFamille)
            .filter(
                DocumentFamille.actif.is_(True),
                DocumentFamille.date_expiration.isnot(None),
                DocumentFamille.date_expiration <= seuil,
            )
            .order_by(DocumentFamille.date_expiration)
            .all()
        )

        return [
            {
                "id": d.id,
                "titre": d.titre,
                "categorie": d.categorie,
                "membre_famille": d.membre_famille,
                "date_expiration": str(d.date_expiration),
                "jours_restants": d.jours_avant_expiration,
                "est_expire": d.est_expire,
                "niveau": "critique" if d.est_expire else (
                    "urgent" if d.jours_avant_expiration and d.jours_avant_expiration <= 7 else "attention"
                ),
            }
            for d in documents
        ]

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def entretien_echoue_vers_artisans(
        self,
        tache_id: int,
        db: Session | None = None,
    ) -> dict:
        """Propose des artisans adaptés pour une tâche d'entretien en échec."""
        from src.core.models.abonnements import Artisan
        from src.core.models.habitat import TacheEntretien

        tache = db.query(TacheEntretien).filter(TacheEntretien.id == tache_id).first()
        if not tache:
            return {}

        metiers = self._detecter_metiers_depuis_tache(tache)
        artisans: list[Artisan] = []
        for metier in metiers:
            artisans.extend(
                db.query(Artisan).filter(Artisan.metier.ilike(f"%{metier}%")).all()
            )

        if not artisans and "artisan multi-services" not in metiers:
            artisans = db.query(Artisan).filter(Artisan.metier.ilike("%multi%")).all()

        artisans_uniques = list({artisan.id: artisan for artisan in artisans}.values())
        artisans_tries = self._prioriser_artisans(artisans_uniques)

        return {
            "tache": {
                "id": tache.id,
                "nom": tache.nom,
                "categorie": tache.categorie,
                "piece": tache.piece,
            },
            "metiers_recommandes": metiers,
            "artisans": [
                {
                    "id": artisan.id,
                    "nom": artisan.nom,
                    "entreprise": artisan.entreprise,
                    "metier": artisan.metier,
                    "specialite": artisan.specialite,
                    "telephone": artisan.telephone,
                    "email": artisan.email,
                    "note": artisan.note,
                    "recommande": artisan.recommande,
                }
                for artisan in artisans_tries[:5]
            ],
            "nb_artisans": len(artisans_tries),
        }

    # ── B5.5: Entretien récurrent → Planning unifié ─────────

    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def entretien_planning_unifie(self, nb_jours: int = 7, db: Session | None = None) -> list[dict]:
        """Récupère les tâches d'entretien planifiées pour les N prochains jours.

        Returns:
            Liste de tâches avec dates et priorités
        """
        from src.core.models import TacheEntretien

        seuil = date.today() + timedelta(days=nb_jours)
        aujourd_hui = date.today()

        taches = (
            db.query(TacheEntretien)
            .filter(
                TacheEntretien.prochaine_fois <= seuil,
                TacheEntretien.fait.is_(False),
            )
            .order_by(TacheEntretien.prochaine_fois)
            .all()
        )

        return [
            {
                "id": t.id,
                "nom": t.nom,
                "prochaine_fois": str(t.prochaine_fois),
                "en_retard": t.prochaine_fois < aujourd_hui if t.prochaine_fois else False,
                "jours_restants": (t.prochaine_fois - aujourd_hui).days if t.prochaine_fois else None,
                "type": "entretien",
            }
            for t in taches
        ]

    # ── B5.2: Budget anomalie → Notification ────────────────

    def verifier_anomalies_budget_et_notifier(self) -> list[dict]:
        """Vérifie les anomalies budgétaires et émet des événements.

        Returns:
            Liste des anomalies détectées
        """
        from src.services.ia.prevision_budget import obtenir_service_prevision_budget
        from src.services.core.events import obtenir_bus

        service = obtenir_service_prevision_budget()
        anomalies = service.detecter_anomalies_budget(seuil_pct=80)

        bus = obtenir_bus()
        for anomalie in anomalies:
            bus.emettre("budget.depassement", {
                "categorie": anomalie["categorie"],
                "depense": anomalie["depense"],
                "budget_ref": anomalie["budget_ref"],
                "pourcentage": anomalie["pourcentage"],
                "niveau": anomalie["niveau"],
            })

        return anomalies

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def recolte_vers_stock_inventaire(
        self,
        element_id: int,
        quantite: float = 1.0,
        emplacement: str = "Frigo",
        db: Session | None = None,
    ) -> dict:
        """Ajoute automatiquement une récolte jardin à l'inventaire."""
        from src.core.models import ArticleInventaire, ElementJardin, Ingredient

        element = db.query(ElementJardin).filter(ElementJardin.id == element_id).first()
        if not element:
            return {}

        ingredient = (
            db.query(Ingredient)
            .filter(func.lower(Ingredient.nom) == element.nom.lower())
            .first()
        )

        if ingredient is None:
            categorie = "Légumes"
            if "fruit" in (element.type or "").lower():
                categorie = "Fruits"
            ingredient = Ingredient(nom=element.nom, categorie=categorie, unite="pcs")
            db.add(ingredient)
            db.flush()

        article = (
            db.query(ArticleInventaire)
            .filter(ArticleInventaire.ingredient_id == ingredient.id)
            .first()
        )

        quantite_ajoutee = max(0.1, quantite)
        action = "mise_a_jour"
        if article:
            article.quantite = float(article.quantite or 0) + quantite_ajoutee
            article.emplacement = article.emplacement or emplacement
        else:
            article = ArticleInventaire(
                ingredient_id=ingredient.id,
                quantite=quantite_ajoutee,
                quantite_min=1.0,
                emplacement=emplacement,
            )
            db.add(article)
            action = "creation"

        db.commit()
        db.refresh(article)

        return {
            "element_id": element.id,
            "element_nom": element.nom,
            "ingredient_id": ingredient.id,
            "article_inventaire_id": article.id,
            "quantite_ajoutee": quantite_ajoutee,
            "quantite_totale": float(article.quantite or 0),
            "emplacement": article.emplacement,
            "action": action,
        }

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def anniversaire_vers_menu_festif(
        self,
        jours_horizon: int = 14,
        db: Session | None = None,
    ) -> dict:
        """Suggère un menu festif pour l'anniversaire le plus proche."""
        from src.core.models import AnniversaireFamille
        from src.core.models.recettes import Recette

        anniversaires = sorted(
            [a for a in db.query(AnniversaireFamille).all() if 0 <= a.jours_restants <= jours_horizon],
            key=lambda anniversaire: anniversaire.jours_restants,
        )
        if not anniversaires:
            return {}

        cible = anniversaires[0]
        recettes = (
            db.query(Recette)
            .filter(
                func.lower(Recette.nom).contains("gateau")
                | func.lower(Recette.nom).contains("gâteau")
                | func.lower(Recette.nom).contains("tarte")
                | func.lower(Recette.categorie).contains("dessert")
            )
            .limit(6)
            .all()
        )

        suggestions = [
            {
                "id": recette.id,
                "nom": recette.nom,
                "categorie": recette.categorie,
                "type_repas": recette.type_repas,
                "temps_total": recette.temps_total,
            }
            for recette in recettes
        ]
        if not suggestions:
            suggestions = [
                {"id": None, "nom": "Gâteau maison festif", "categorie": "Dessert", "type_repas": "dessert", "temps_total": 90},
                {"id": None, "nom": "Buffet apéritif familial", "categorie": "Plat", "type_repas": "dîner", "temps_total": 45},
            ]

        return {
            "anniversaire": {
                "id": cible.id,
                "nom_personne": cible.nom_personne,
                "jours_restants": cible.jours_restants,
                "age": cible.age,
            },
            "menu_festif": suggestions,
        }

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def jalon_vers_evenement_familial(
        self,
        jalon_id: int,
        db: Session | None = None,
    ) -> dict:
        """Crée un événement familial à partir d'un jalon Jules."""
        from src.core.models.famille import EvenementFamilial, Jalon, ProfilEnfant

        jalon = db.query(Jalon).filter(Jalon.id == jalon_id).first()
        if not jalon:
            return {}

        enfant = db.query(ProfilEnfant).filter(ProfilEnfant.id == jalon.child_id).first()
        titre = f"Jalon Jules: {jalon.titre}"

        evenement = (
            db.query(EvenementFamilial)
            .filter(
                EvenementFamilial.titre == titre,
                EvenementFamilial.date_evenement == jalon.date_atteint,
                EvenementFamilial.type_evenement == "jalon_jules",
            )
            .first()
        )

        if evenement is None:
            evenement = EvenementFamilial(
                titre=titre,
                date_evenement=jalon.date_atteint,
                type_evenement="jalon_jules",
                recurrence="unique",
                notes=jalon.description or jalon.notes,
                participants=[enfant.name] if enfant else ["Jules"],
            )
            db.add(evenement)
            db.commit()
            db.refresh(evenement)

        return {
            "jalon_id": jalon.id,
            "evenement_id": evenement.id,
            "titre": evenement.titre,
            "date_evenement": evenement.date_evenement.isoformat(),
        }

    @avec_gestion_erreurs(default_return={})
    def energie_hc_hp_vers_planning_machines(self) -> dict:
        """IM-5: Propose la meilleure fenêtre HC/HP pour lancer les machines."""
        from src.services.maison.inter_modules.inter_module_energie_cuisine import (
            obtenir_service_energie_cuisine_interaction,
        )

        service = obtenir_service_energie_cuisine_interaction()
        recommandations = service.obtenir_suggestions_heures_creuses()
        return {
            "interaction": "IM-5",
            "description": "Tarif HC/HP vers planning machines",
            **recommandations,
        }

    # ── B5.8: Météo → Entretien maison ──────────────────────

    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def meteo_vers_entretien(self, conditions_meteo: dict, db: Session | None = None) -> list[dict]:
        """Génère des alertes entretien basées sur les conditions météo.

        Args:
            conditions_meteo: Dict avec temperature, vent, precipitations

        Returns:
            Liste d'alertes avec conseils
        """
        alertes = []
        temp = conditions_meteo.get("temperature", 15)
        vent = conditions_meteo.get("vent_kmh", 0)
        pluie = conditions_meteo.get("precipitations_mm", 0)

        if temp <= 0:
            alertes.append({
                "type": "gel",
                "message": "🥶 Gel annoncé ! Protéger les plantes, purger les tuyaux extérieurs.",
                "priorite": "haute",
                "domaine": "jardin",
            })
        if temp >= 35:
            alertes.append({
                "type": "canicule",
                "message": "🌡️ Canicule ! Arroser le jardin tôt/tard, fermer les volets.",
                "priorite": "haute",
                "domaine": "jardin",
            })
        if vent >= 80:
            alertes.append({
                "type": "vent_fort",
                "message": "💨 Vent fort ! Rentrer les meubles de jardin, vérifier les fixations.",
                "priorite": "moyenne",
                "domaine": "exterieur",
            })
        if pluie >= 50:
            alertes.append({
                "type": "pluie_forte",
                "message": "🌧️ Pluie forte ! Vérifier les gouttières et évacuations.",
                "priorite": "moyenne",
                "domaine": "maison",
            })

        return alertes

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def generer_courses_auto_depuis_planning(
        self,
        planning_id: int,
        semaine_debut: date | str | None = None,
        db: Session | None = None,
    ) -> dict:
        """I1: génère automatiquement une liste de courses depuis un planning validé."""
        from sqlalchemy import func

        from src.core.models import (
            ArticleCourses,
            ArticleInventaire,
            Ingredient,
            ListeCourses,
            Planning,
        )
        from src.core.models.planning import Repas
        from src.core.models.recettes import RecetteIngredient

        planning = db.query(Planning).filter(Planning.id == planning_id).first()
        if not planning:
            return {}

        if isinstance(semaine_debut, str) and semaine_debut:
            try:
                semaine_ref = date.fromisoformat(semaine_debut)
            except ValueError:
                semaine_ref = planning.semaine_debut
        else:
            semaine_ref = semaine_debut or planning.semaine_debut

        nom_liste = f"Courses auto planning #{planning.id} ({semaine_ref.isoformat()})"
        liste = (
            db.query(ListeCourses)
            .filter(
                ListeCourses.nom == nom_liste,
                ListeCourses.archivee.is_(False),
            )
            .order_by(ListeCourses.id.desc())
            .first()
        )
        if liste is None:
            liste = ListeCourses(nom=nom_liste, archivee=False, etat="brouillon")
            db.add(liste)
            db.flush()

        repas_list = db.query(Repas).filter(Repas.planning_id == planning.id).all()
        recette_ids: set[int] = set()
        for repas in repas_list:
            for recette_id in (
                repas.recette_id,
                repas.entree_recette_id,
                repas.dessert_recette_id,
                repas.dessert_jules_recette_id,
            ):
                if recette_id:
                    recette_ids.add(recette_id)

        if not recette_ids:
            return {
                "planning_id": planning.id,
                "liste_id": liste.id,
                "nb_articles": 0,
                "articles_en_stock": 0,
                "message": "Aucune recette liée au planning validé.",
            }

        ingredients = (
            db.query(
                RecetteIngredient.ingredient_id,
                func.sum(RecetteIngredient.quantite).label("quantite_totale"),
                Ingredient.nom,
                Ingredient.categorie,
                Ingredient.unite,
            )
            .join(Ingredient, Ingredient.id == RecetteIngredient.ingredient_id)
            .filter(RecetteIngredient.recette_id.in_(recette_ids))
            .group_by(
                RecetteIngredient.ingredient_id,
                Ingredient.nom,
                Ingredient.categorie,
                Ingredient.unite,
            )
            .all()
        )

        nb_articles = 0
        articles_en_stock = 0

        for row in ingredients:
            quantite_voulue = float(row.quantite_totale or 1)
            inventaire = (
                db.query(ArticleInventaire)
                .filter(ArticleInventaire.ingredient_id == row.ingredient_id)
                .order_by(ArticleInventaire.quantite.desc())
                .first()
            )
            quantite_en_stock = float(getattr(inventaire, "quantite", 0) or 0)
            if quantite_en_stock >= quantite_voulue:
                articles_en_stock += 1
                continue

            quantite_a_acheter = max(0.1, quantite_voulue - quantite_en_stock)
            article = (
                db.query(ArticleCourses)
                .filter(
                    ArticleCourses.liste_id == liste.id,
                    ArticleCourses.ingredient_id == row.ingredient_id,
                    ArticleCourses.achete.is_(False),
                )
                .first()
            )

            if article:
                article.quantite_necessaire = float(article.quantite_necessaire or 0) + quantite_a_acheter
                if not article.rayon_magasin:
                    article.rayon_magasin = row.categorie or "Autre"
                nb_articles += 1
                continue

            db.add(
                ArticleCourses(
                    liste_id=liste.id,
                    ingredient_id=row.ingredient_id,
                    quantite_necessaire=quantite_a_acheter,
                    rayon_magasin=row.categorie or "Autre",
                    priorite="moyenne",
                    suggere_par_ia=False,
                    notes=f"Ajout automatique depuis le planning #{planning.id}",
                )
            )
            nb_articles += 1

        db.commit()
        db.refresh(liste)

        return {
            "planning_id": planning.id,
            "liste_id": liste.id,
            "nom_liste": liste.nom,
            "nb_articles": nb_articles,
            "articles_en_stock": articles_en_stock,
            "semaine_debut": semaine_ref.isoformat() if semaine_ref else None,
            "message": f"{nb_articles} article(s) ajoutés à la liste auto.",
        }

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def synchroniser_entretien_termine_vers_fiche(
        self,
        tache_id: int,
        db: Session | None = None,
    ) -> dict:
        """I5: met à jour la fiche d'entretien après validation d'une tâche."""
        from src.core.models.habitat import TacheEntretien
        from src.core.models.maison_extensions import EntretienSaisonnier

        tache = db.query(TacheEntretien).filter(TacheEntretien.id == tache_id).first()
        if not tache:
            return {}

        date_realisation = tache.derniere_fois or date.today()
        tokens = [mot for mot in (tache.nom or "").lower().replace("-", " ").split() if len(mot) >= 4]
        fiches = db.query(EntretienSaisonnier).all()
        fiches_cibles = [
            fiche
            for fiche in fiches
            if fiche.nom and any(token in fiche.nom.lower() for token in tokens)
        ]

        if not fiches_cibles:
            mois = date_realisation.month
            if mois in {12, 1, 2}:
                saison = "hiver"
            elif mois in {3, 4, 5}:
                saison = "printemps"
            elif mois in {6, 7, 8}:
                saison = "ete"
            else:
                saison = "automne"

            categorie = (tache.categorie or "entretien").lower()
            if categorie not in {"chauffage", "plomberie", "toiture", "jardin", "piscine", "securite"}:
                categorie = "securite" if "secur" in categorie else "jardin" if "jardin" in categorie else "chauffage"

            fiche = EntretienSaisonnier(
                nom=tache.nom,
                categorie=categorie,
                saison=saison,
                frequence="annuel",
                alerte_active=True,
            )
            db.add(fiche)
            db.flush()
            fiches_cibles = [fiche]

        correspondance_frequences = {
            "hebdomadaire": 7,
            "mensuel": 30,
            "trimestriel": 90,
            "semestriel": 180,
            "annuel": 365,
        }

        for fiche in fiches_cibles:
            fiche.date_derniere_realisation = date_realisation
            fiche.fait_cette_annee = date_realisation.year == date.today().year
            nb_jours = correspondance_frequences.get((fiche.frequence or "annuel").lower(), 365)
            fiche.date_prochaine = date_realisation + timedelta(days=nb_jours)
            note_auto = f"Mis à jour automatiquement depuis la tâche #{tache.id} ({tache.nom})"
            fiche.notes = note_auto if not fiche.notes else f"{fiche.notes}\n{note_auto}"

        db.commit()

        return {
            "tache_id": tache.id,
            "nb_fiches_mises_a_jour": len(fiches_cibles),
            "date_realisation": date_realisation.isoformat(),
            "message": f"{len(fiches_cibles)} fiche(s) d'entretien synchronisée(s).",
        }

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def pre_remplir_planning_depuis_batch(
        self,
        session_id: int,
        db: Session | None = None,
    ) -> dict:
        """I6: marque les repas du planning comme déjà préparés après un batch cooking."""
        from sqlalchemy import or_

        from src.core.models import SessionBatchCooking
        from src.core.models.planning import Repas

        session_batch = db.query(SessionBatchCooking).filter(SessionBatchCooking.id == session_id).first()
        if not session_batch:
            return {}

        recette_ids = [int(recette_id) for recette_id in (session_batch.recettes_selectionnees or []) if recette_id]
        if not session_batch.planning_id or not recette_ids:
            return {
                "session_id": session_batch.id,
                "planning_id": session_batch.planning_id,
                "nb_repas_mis_a_jour": 0,
                "message": "Aucun repas à pré-remplir pour cette session.",
            }

        repas = (
            db.query(Repas)
            .filter(Repas.planning_id == session_batch.planning_id)
            .filter(
                or_(
                    Repas.recette_id.in_(recette_ids),
                    Repas.entree_recette_id.in_(recette_ids),
                    Repas.dessert_recette_id.in_(recette_ids),
                    Repas.dessert_jules_recette_id.in_(recette_ids),
                )
            )
            .all()
        )

        note_batch = f"Préparé en batch le {(session_batch.date_session or date.today()).isoformat()}"
        nb_mis_a_jour = 0
        for repas_item in repas:
            repas_item.prepare = True
            if note_batch not in (repas_item.notes or ""):
                repas_item.notes = note_batch if not repas_item.notes else f"{repas_item.notes}\n{note_batch}"
            nb_mis_a_jour += 1

        db.commit()

        return {
            "session_id": session_batch.id,
            "planning_id": session_batch.planning_id,
            "nb_repas_mis_a_jour": nb_mis_a_jour,
            "message": f"{nb_mis_a_jour} repas pré-rempli(s) depuis le batch.",
        }

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def appliquer_feedback_recette_sur_suggestions(
        self,
        recette_id: int,
        *,
        note: int | None = None,
        feedback: str | None = None,
        user_id: str | None = None,
        commentaire: str | None = None,
        db: Session | None = None,
    ) -> dict:
        """I10: convertit le feedback recette en signal exploitable pour les suggestions."""
        from src.core.models import Recette
        from src.core.models.user_preferences import RetourRecette

        recette = db.query(Recette).filter(Recette.id == recette_id).first()
        if not recette:
            return {}

        feedback_normalise = (feedback or "").strip().lower()
        if feedback_normalise not in {"like", "dislike", "neutral"}:
            if note is not None and int(note) <= 2:
                feedback_normalise = "dislike"
            elif note is not None and int(note) >= 4:
                feedback_normalise = "like"
            else:
                feedback_normalise = "neutral"

        utilisateur = user_id or "system"
        retour = (
            db.query(RetourRecette)
            .filter(RetourRecette.user_id == utilisateur, RetourRecette.recette_id == recette_id)
            .first()
        )
        if retour is None:
            retour = RetourRecette(user_id=utilisateur, recette_id=recette_id, feedback=feedback_normalise)
            db.add(retour)
        else:
            retour.feedback = feedback_normalise

        if note is not None:
            retour.contexte = f"note={int(note)}/5"
        if commentaire:
            retour.notes = commentaire[:1000]

        db.commit()

        poids = {"like": 2, "neutral": 0, "dislike": -3}[feedback_normalise]
        return {
            "recette_id": recette_id,
            "user_id": utilisateur,
            "feedback": feedback_normalise,
            "poids_suggestion": poids,
            "exclure_des_suggestions": feedback_normalise == "dislike",
        }

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def integrer_budget_mensuel_dans_rapport(
        self,
        *,
        mois: int | None = None,
        annee: int | None = None,
        db: Session | None = None,
    ) -> dict:
        """I4: résume le budget du mois pour l'injecter dans le rapport famille."""
        from src.core.models.famille import BudgetFamille

        aujourd_hui = date.today()
        mois_cible = mois or aujourd_hui.month
        annee_cible = annee or aujourd_hui.year

        lignes = (
            db.query(BudgetFamille)
            .filter(
                func.extract("month", BudgetFamille.date) == mois_cible,
                func.extract("year", BudgetFamille.date) == annee_cible,
            )
            .all()
        )
        total = round(sum(float(ligne.montant or 0) for ligne in lignes), 2)
        repartition: dict[str, float] = {}
        for ligne in lignes:
            categorie = ligne.categorie or "autre"
            repartition[categorie] = round(repartition.get(categorie, 0.0) + float(ligne.montant or 0), 2)

        return {
            "mois": mois_cible,
            "annee": annee_cible,
            "total_depenses": total,
            "nb_lignes": len(lignes),
            "repartition": repartition,
        }

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def resumer_depenses_retour_voyage(
        self,
        voyage_id: int | None = None,
        db: Session | None = None,
    ) -> dict:
        """I9: produit un résumé synthétique du budget d'un voyage terminé."""
        from src.core.models.voyage import Voyage

        query = db.query(Voyage)
        if voyage_id is not None:
            query = query.filter(Voyage.id == voyage_id)
        else:
            query = query.filter(Voyage.statut.in_(["termine", "terminé", "en_cours"]))

        voyage = query.order_by(Voyage.date_retour.desc()).first()
        if not voyage:
            return {}

        budget_prevu = float(voyage.budget_prevu or 0)
        budget_reel = float(voyage.budget_reel or 0)
        ecart = round(budget_reel - budget_prevu, 2)
        return {
            "voyage_id": voyage.id,
            "titre": voyage.titre,
            "destination": voyage.destination,
            "budget_prevu": budget_prevu,
            "budget_reel": budget_reel,
            "ecart_budget": ecart,
            "statut": voyage.statut,
        }

    # ═══════════════════════════════════════════════════════════
    # P3 — BRIDGES INTER-MODULES ENRICHIS
    # ═══════════════════════════════════════════════════════════

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def terroir_vers_recettes(self, localisation: str | None = None, db: Session | None = None) -> dict:
        """P3-A1: Suggère des recettes régionales basées sur la localisation du foyer."""
        from src.core.models.habitat_projet import CritereImmoHabitat
        from src.core.models.recettes import Recette

        # Déterminer la localisation
        region = localisation
        if not region:
            critere = db.query(CritereImmoHabitat).filter(CritereImmoHabitat.actif.is_(True)).first()
            if critere and critere.villes:
                region = critere.villes[0] if isinstance(critere.villes, list) else str(critere.villes)
            elif critere and critere.departements:
                dep = critere.departements[0] if isinstance(critere.departements, list) else str(critere.departements)
                region = dep

        if not region:
            region = "France"

        # Chercher des recettes avec catégorie/nom/description régionale
        recettes = (
            db.query(Recette)
            .filter(
                Recette.categorie.ilike(f"%{region}%")
                | Recette.nom.ilike(f"%{region}%")
                | Recette.description.ilike(f"%{region}%")
            )
            .limit(10)
            .all()
        )

        recettes_liste = [
            {
                "id": r.id,
                "nom": r.nom,
                "categorie": r.categorie or "",
                "temps_preparation": r.temps_preparation,
            }
            for r in recettes
        ]

        return {
            "localisation": region,
            "region": region,
            "recettes_suggerees": recettes_liste,
            "nb_recettes": len(recettes_liste),
        }

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def budget_unifie(self, mois: int | None = None, annee: int | None = None, db: Session | None = None) -> dict:
        """P3-A2: Agrège budget famille + charges maison en vue unifiée."""
        from src.core.models.famille import BudgetFamille
        from src.core.models.finances import DepenseMaison

        aujourd_hui = date.today()
        mois_cible = mois or aujourd_hui.month
        annee_cible = annee or aujourd_hui.year

        # Budget famille
        lignes_famille = (
            db.query(BudgetFamille)
            .filter(
                func.extract("month", BudgetFamille.date) == mois_cible,
                func.extract("year", BudgetFamille.date) == annee_cible,
            )
            .all()
        )
        details_famille: dict[str, float] = {}
        for ligne in lignes_famille:
            cat = ligne.categorie or "autre"
            details_famille[cat] = round(details_famille.get(cat, 0.0) + float(ligne.montant or 0), 2)
        total_famille = round(sum(details_famille.values()), 2)

        # Charges maison
        lignes_maison = (
            db.query(DepenseMaison)
            .filter(
                DepenseMaison.mois == mois_cible,
                DepenseMaison.annee == annee_cible,
            )
            .all()
        )
        details_maison: dict[str, float] = {}
        for ligne in lignes_maison:
            cat = ligne.categorie or "autre"
            details_maison[cat] = round(details_maison.get(cat, 0.0) + float(ligne.montant or 0), 2)
        total_maison = round(sum(details_maison.values()), 2)

        # Évolution vs mois précédent
        mois_prec = mois_cible - 1 if mois_cible > 1 else 12
        annee_prec = annee_cible if mois_cible > 1 else annee_cible - 1
        total_prec_famille = float(
            db.query(func.coalesce(func.sum(BudgetFamille.montant), 0))
            .filter(
                func.extract("month", BudgetFamille.date) == mois_prec,
                func.extract("year", BudgetFamille.date) == annee_prec,
            )
            .scalar()
        )
        total_prec_maison = float(
            db.query(func.coalesce(func.sum(DepenseMaison.montant), 0))
            .filter(DepenseMaison.mois == mois_prec, DepenseMaison.annee == annee_prec)
            .scalar()
        )
        total_prec = total_prec_famille + total_prec_maison
        total_unifie = round(total_famille + total_maison, 2)
        evolution_pct = round(((total_unifie - total_prec) / total_prec) * 100, 1) if total_prec > 0 else None

        return {
            "mois": mois_cible,
            "annee": annee_cible,
            "total_famille": total_famille,
            "total_maison": total_maison,
            "total_unifie": total_unifie,
            "details_famille": [{"categorie": k, "montant": v} for k, v in sorted(details_famille.items())],
            "details_maison": [{"categorie": k, "montant": v} for k, v in sorted(details_maison.items())],
            "evolution_pct": evolution_pct,
        }

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def impact_demenagement(self, scenario_id: int, db: Session | None = None) -> dict:
        """P3-A3: Évalue l'impact familial d'un scénario de déménagement."""
        from src.core.models.famille import ActiviteFamille, ProfilEnfant
        from src.core.models.habitat_projet import CritereScenarioHabitat, ScenarioHabitat

        scenario = db.query(ScenarioHabitat).filter(ScenarioHabitat.id == scenario_id).first()
        if not scenario:
            return {"erreur": "Scénario introuvable"}

        # Charger les données famille
        enfants = db.query(ProfilEnfant).filter(ProfilEnfant.actif.is_(True)).all()
        activites = db.query(ActiviteFamille).limit(20).all()
        criteres = (
            db.query(CritereScenarioHabitat)
            .filter(CritereScenarioHabitat.scenario_id == scenario_id)
            .all()
        )

        impacts = []
        # Impact sur les enfants
        for enfant in enfants:
            age_mois = None
            if enfant.date_of_birth:
                delta = date.today() - enfant.date_of_birth
                age_mois = delta.days // 30
            impacts.append({
                "domaine": "enfant",
                "sujet": enfant.name,
                "detail": f"Changement d'environnement pour {enfant.name}"
                + (f" ({age_mois} mois)" if age_mois else ""),
                "severite": "moyenne",
            })

        # Impact sur les activités
        for act in activites:
            impacts.append({
                "domaine": "activite",
                "sujet": act.titre if hasattr(act, "titre") else str(act),
                "detail": "Activité potentiellement à réorganiser après déménagement",
                "severite": "faible",
            })

        # Score global basé sur les critères
        notes = [float(c.note) for c in criteres if c.note is not None]
        score_global = round(sum(notes) / len(notes), 1) if notes else None

        return {
            "scenario_nom": scenario.nom,
            "impacts": impacts,
            "score_global": score_global,
            "recommandation": "Scénario favorable" if score_global and score_global >= 7 else "À évaluer en détail",
            "details": {
                "budget_estime": float(scenario.budget_estime) if scenario.budget_estime else None,
                "surface_m2": float(scenario.surface_finale_m2) if scenario.surface_finale_m2 else None,
                "nb_chambres": scenario.nb_chambres,
                "avantages": scenario.avantages or [],
                "inconvenients": scenario.inconvenients or [],
            },
        }

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def widget_veille_immo(self, db: Session | None = None) -> dict:
        """P3-A4: Données pour le widget veille immobilière du dashboard."""
        from src.core.models.habitat_projet import AnnonceHabitat

        # 5 dernières annonces
        annonces = (
            db.query(AnnonceHabitat)
            .order_by(AnnonceHabitat.id.desc())
            .limit(5)
            .all()
        )
        nb_total = db.query(func.count(AnnonceHabitat.id)).scalar() or 0

        annonces_liste = [
            {
                "id": a.id,
                "titre": a.titre or "",
                "prix": float(a.prix) if a.prix else 0,
                "surface_m2": float(a.surface_m2) if a.surface_m2 else None,
                "ville": a.ville or "",
                "score_pertinence": float(a.score_pertinence) if a.score_pertinence else None,
                "url_source": a.url_source,
            }
            for a in annonces
        ]

        # Prix moyen
        prix_moyen_val = db.query(func.avg(AnnonceHabitat.prix)).scalar()
        prix_moyen = round(float(prix_moyen_val), 0) if prix_moyen_val else None

        return {
            "dernieres_annonces": annonces_liste,
            "nb_annonces_total": nb_total,
            "prix_moyen": prix_moyen,
            "tendance_prix_pct": None,
        }

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def widget_saison_jardin(self, db: Session | None = None) -> dict:
        """P3-A5: Données saisonnières du jardin pour le widget dashboard."""
        from src.core.models.maison import ElementJardin

        aujourd_hui = date.today()
        mois = aujourd_hui.month
        saison_map = {1: "hiver", 2: "hiver", 3: "printemps", 4: "printemps", 5: "printemps",
                      6: "été", 7: "été", 8: "été", 9: "automne", 10: "automne",
                      11: "automne", 12: "hiver"}
        saison = saison_map[mois]

        # Éléments actifs du jardin
        plantes = (
            db.query(ElementJardin)
            .filter(ElementJardin.statut != "retire")
            .all()
        )

        activites = []
        prochaines_recoltes = []

        for plante in plantes:
            # Déterminer le type d'activité selon la saison et le statut
            if plante.statut == "plante" or plante.statut == "actif":
                activites.append({
                    "element": plante.nom,
                    "type_activite": "arrosage",
                    "priorite": "haute" if saison in ("été", "printemps") else "normale",
                    "conseil": f"Arroser {plante.nom} régulièrement" if saison == "été" else "",
                })

            # Récolte prévue
            if plante.date_recolte_prevue and plante.date_recolte_prevue >= aujourd_hui:
                jours_restants = (plante.date_recolte_prevue - aujourd_hui).days
                prochaines_recoltes.append({
                    "element": plante.nom,
                    "date_recolte": plante.date_recolte_prevue.isoformat(),
                    "jours_restants": jours_restants,
                })

        prochaines_recoltes.sort(key=lambda x: x["jours_restants"])

        return {
            "saison": saison,
            "activites": activites,
            "nb_plantes_actives": len(plantes),
            "prochaines_recoltes": prochaines_recoltes[:5],
        }

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def activites_jules_potager(self, db: Session | None = None) -> dict:
        """P3-A6: Suggère des activités jardinage adaptées à Jules."""
        from src.core.models.famille import ProfilEnfant
        from src.core.models.maison import ElementJardin

        # Trouver Jules
        jules = db.query(ProfilEnfant).filter(ProfilEnfant.actif.is_(True)).first()
        age_mois = None
        if jules and jules.date_of_birth:
            delta = date.today() - jules.date_of_birth
            age_mois = delta.days // 30

        # Plantes actives du jardin
        plantes = (
            db.query(ElementJardin)
            .filter(ElementJardin.statut != "retire")
            .all()
        )
        plantes_noms = [p.nom for p in plantes]

        # Générer des activités adaptées à l'âge
        activites = []
        for plante in plantes:
            if plante.statut in ("plante", "actif"):
                activites.append({
                    "activite": f"Arroser {plante.nom}",
                    "difficulte": "facile",
                    "duree_minutes": 10,
                    "description": f"Arroser doucement {plante.nom} avec un petit arrosoir",
                })
            if plante.date_recolte_prevue and plante.date_recolte_prevue <= date.today() + timedelta(days=7):
                activites.append({
                    "activite": f"Récolter {plante.nom}",
                    "difficulte": "facile",
                    "duree_minutes": 15,
                    "description": f"Cueillir {plante.nom} ensemble — montrer les couleurs et les formes",
                })

        # Activités génériques adaptées
        activites.append({
            "activite": "Observer les insectes",
            "difficulte": "facile",
            "duree_minutes": 10,
            "description": "Chercher et observer les insectes dans le jardin",
        })

        return {
            "activites": activites,
            "plantes_disponibles": plantes_noms,
            "age_jules_mois": age_mois,
        }

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def verifier_stock_recette(self, recette_id: int, db: Session | None = None) -> dict:
        """P3-B3: Vérifie le stock pour une recette et retourne les manquants."""
        from src.core.models.inventaire import ArticleInventaire
        from src.core.models.recettes import Ingredient, Recette, RecetteIngredient

        recette = db.query(Recette).filter(Recette.id == recette_id).first()
        if not recette:
            return {"recette_id": recette_id, "erreur": "Recette introuvable"}

        liens = (
            db.query(RecetteIngredient, Ingredient)
            .join(Ingredient, RecetteIngredient.ingredient_id == Ingredient.id)
            .filter(RecetteIngredient.recette_id == recette_id)
            .all()
        )

        ingredients_ok = []
        ingredients_manquants = []

        for lien, ing in liens:
            nom_normalise = (ing.nom or "").strip().lower()
            stock = (
                db.query(ArticleInventaire)
                .filter(ArticleInventaire.ingredient_id == ing.id)
                .first()
            )
            item = {"nom": ing.nom, "quantite_requise": lien.quantite, "unite": lien.unite}
            if stock and stock.quantite > 0:
                item["en_stock"] = True
                item["quantite_stock"] = float(stock.quantite)
                ingredients_ok.append(item)
            else:
                item["en_stock"] = False
                ingredients_manquants.append(item)

        nb_total = len(liens)
        nb_ok = len(ingredients_ok)
        taux = round((nb_ok / nb_total) * 100, 1) if nb_total > 0 else 0

        return {
            "recette_id": recette_id,
            "recette_nom": recette.nom,
            "ingredients_ok": ingredients_ok,
            "ingredients_manquants": ingredients_manquants,
            "taux_couverture": taux,
        }


# ═══════════════════════════════════════════════════════════
# EVENT HANDLERS (subscribers)
# ═══════════════════════════════════════════════════════════


def _on_jardin_recolte(event: EvenementDomaine) -> None:
    """Handler: Quand une récolte jardin est validée → suggérer des recettes."""
    try:
        nom = event.data.get("nom", "")
        if not nom:
            return

        service = obtenir_service_bridges()
        recettes = service.recolte_vers_recettes(nom)

        if recettes:
            logger.info(
                f"🌱→🍽️ Récolte '{nom}' → {len(recettes)} recette(s) trouvée(s): "
                f"{', '.join(r['nom'] for r in recettes[:3])}"
            )
            # Émettre un événement pour notification
            from src.services.core.events import obtenir_bus
            obtenir_bus().emettre("bridge.recolte_recettes", {
                "ingredient": nom,
                "recettes": recettes[:5],
                "nb_recettes": len(recettes),
            })
    except Exception as e:
        logger.warning(f"Erreur bridge récolte→recettes: {e}")


def _on_budget_modifie(event: EvenementDomaine) -> None:
    """Handler: Quand le budget est modifié → vérifier les anomalies."""
    try:
        service = obtenir_service_bridges()
        anomalies = service.verifier_anomalies_budget_et_notifier()
        if anomalies:
            logger.info(f"💰 {len(anomalies)} anomalie(s) budget détectée(s)")
    except Exception as e:
        logger.warning(f"Erreur bridge budget→notification: {e}")


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


@service_factory("bridges_inter_modules", tags={"inter_modules"})
def obtenir_service_bridges() -> BridgesInterModulesService:
    """Factory singleton."""
    return BridgesInterModulesService()



def enregistrer_bridges_subscribers() -> None:
    """Enregistre tous les subscribers de inter_modules inter-modules dans le bus."""
    from src.services.core.events import obtenir_bus

    bus = obtenir_bus()
    bus.souscrire("jardin.recolte", _on_jardin_recolte)
    bus.souscrire("budget.modifie", _on_budget_modifie)

    logger.info("✅ Bridges inter-modules enregistrés (jardin→recettes, budget→notification)")
