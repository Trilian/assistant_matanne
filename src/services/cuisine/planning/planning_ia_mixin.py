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
from .types import JourPlanning, ParametresEquilibre

logger = logging.getLogger(__name__)


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
    def _trouver_ou_creer_recette(db: Session, nom: str) -> int:
        """Retourne l'id d'une recette existante (lookup insensible à la casse)
        ou crée un stub minimal si elle n'existe pas encore."""
        from src.core.models.recettes import Recette

        recette = db.query(Recette).filter(func.lower(Recette.nom) == nom.lower()).first()
        if recette is None:
            recette = Recette(
                nom=nom,
                temps_preparation=30,
                source="ia_planning",
            )
            db.add(recette)
            db.flush()
        return recette.id

    # ═══════════════════════════════════════════════════════════
    # SUGGESTIONS ÉQUILIBRÉES
    # ═══════════════════════════════════════════════════════════

    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def suggerer_recettes_equilibrees(
        self,
        semaine_debut: date,
        parametres: ParametresEquilibre,
        db: Session | None = None,
    ) -> list[dict]:
        """Suggère des recettes équilibrées pour chaque jour.

        Retourne 3 options par jour avec score d'équilibre.
        Utilise les fonctions pures de planning.utils.

        Args:
            semaine_debut: Date de début de semaine
            parametres: Contraintes d'équilibre
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
            )

            # Requête base pour récupérer 3 recettes de ce type
            query = db.query(Recette).filter(Recette.est_equilibre)

            # Filtrer par type de protéine
            if type_proteine == "poisson":
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
                        "type_repas": "dejeuner" if idx % 2 == 0 else "diner",
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
                            "type_repas": "dejeuner" if idx % 2 == 0 else "diner",
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

        semaine_fin = semaine_debut + timedelta(days=6)

        # Construire prompt ultra-direct (comme pour recettes)
        prompt = f"""GENERATE A 7-DAY MEAL PLAN (MONDAY-SUNDAY) IN JSON FORMAT ONLY.

CONTEXT:
{context}

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
    "dejeuner_dessert": "Tarte aux pommes",
    "dejeuner_dessert_est_recette": true,
    "gouter": "Pain au chocolat",
    "gouter_est_recette": false,
    "diner": "Salade niçoise",
    "diner_entree": null,
    "diner_entree_est_recette": false,
    "diner_laitage": "Fromage",
    "diner_dessert": "Fruit de saison",
    "diner_dessert_est_recette": false
  }}
]}}

RULES:
1. Return ONLY valid JSON with exactly 7 items (one per day: Lundi→Dimanche)
2. dejeuner and diner (le PLAT principal): always a real recipe name to cook (3-50 chars)
3. petit_dejeuner: simple text on weekdays (tartines, céréales, fruit), can be est_recette=true on weekend (crêpes, gaufres...)
4. entree/dessert: optional — include only if the meal complexity warrants it; est_recette=true only if real preparation steps needed
5. laitage: text only (yaourt, fromage blanc, fromage, petits-suisses...) — never est_recette
6. gouter: simple text (pain au chocolat, fruit, yaourt...), est_recette=true only for real preparations
7. Ensure variety throughout the week — alternate proteins (fish Mon/Thu, red meat Tue, vegetarian Wed, poultry Fri)
8. null is valid for optional fields
9. No explanations, no text, ONLY JSON"""

        logger.info(f"🤖 Generating AI weekly plan starting {semaine_debut}")

        # Appel IA avec auto rate limiting & parsing
        planning_data = self.call_with_list_parsing_sync(
            prompt=prompt,
            item_model=JourPlanning,
            system_prompt="Return ONLY valid JSON. No text before or after JSON. Never use markdown code blocks.",
            max_items=7,
            temperature=0.5,
            max_tokens=3000,
        )

        # Log de debug pour voir la réponse
        if not planning_data:
            logger.warning(f"⚠️ Aucune donnée IA reçue pour le planning {semaine_debut} — l'appel Mistral n'a pas produit de résultat parsable.")
            from src.core.exceptions import ErreurServiceIA
            raise ErreurServiceIA(
                "Aucune donnée retournée par Mistral pour la génération du planning",
                message_utilisateur="L'IA n'a pas pu générer le planning. Vérifiez la clé Mistral ou réessayez.",
            )

        # Planning IA réussi
        logger.info(f"✅ Generated planning with {len(planning_data)} days using AI")

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
        for idx, jour_data in enumerate(planning_data):
            date_jour = semaine_debut + timedelta(days=idx)

            # Petit-déjeuner (optionnel selon ce que l'IA a fourni)
            if jour_data.petit_dejeuner:
                recette_pdj_id = (
                    self._trouver_ou_creer_recette(db, jour_data.petit_dejeuner)
                    if jour_data.petit_dejeuner_est_recette
                    else None
                )
                db.add(Repas(
                    planning_id=planning.id,
                    date_repas=date_jour,
                    type_repas="petit_dejeuner",
                    notes=jour_data.petit_dejeuner,
                    recette_id=recette_pdj_id,
                ))

            # Déjeuner — plat = toujours une recette stub
            recette_dej_id = self._trouver_ou_creer_recette(db, jour_data.dejeuner)
            entree_dej_recette_id = (
                self._trouver_ou_creer_recette(db, jour_data.dejeuner_entree)
                if jour_data.dejeuner_entree and jour_data.dejeuner_entree_est_recette
                else None
            )
            dessert_dej_recette_id = (
                self._trouver_ou_creer_recette(db, jour_data.dejeuner_dessert)
                if jour_data.dejeuner_dessert and jour_data.dejeuner_dessert_est_recette
                else None
            )
            db.add(Repas(
                planning_id=planning.id,
                date_repas=date_jour,
                type_repas="dejeuner",
                notes=jour_data.dejeuner,
                recette_id=recette_dej_id,
                entree=jour_data.dejeuner_entree,
                entree_recette_id=entree_dej_recette_id,
                laitage=jour_data.dejeuner_laitage,
                dessert=jour_data.dejeuner_dessert,
                dessert_recette_id=dessert_dej_recette_id,
            ))

            # Goûter (optionnel)
            if jour_data.gouter:
                recette_gouter_id = (
                    self._trouver_ou_creer_recette(db, jour_data.gouter)
                    if jour_data.gouter_est_recette
                    else None
                )
                db.add(Repas(
                    planning_id=planning.id,
                    date_repas=date_jour,
                    type_repas="gouter",
                    notes=jour_data.gouter,
                    recette_id=recette_gouter_id,
                ))

            # Dîner — plat = toujours une recette stub
            recette_din_id = self._trouver_ou_creer_recette(db, jour_data.diner)
            entree_din_recette_id = (
                self._trouver_ou_creer_recette(db, jour_data.diner_entree)
                if jour_data.diner_entree and jour_data.diner_entree_est_recette
                else None
            )
            dessert_din_recette_id = (
                self._trouver_ou_creer_recette(db, jour_data.diner_dessert)
                if jour_data.diner_dessert and jour_data.diner_dessert_est_recette
                else None
            )
            db.add(Repas(
                planning_id=planning.id,
                date_repas=date_jour,
                type_repas="diner",
                notes=jour_data.diner,
                recette_id=recette_din_id,
                entree=jour_data.diner_entree,
                entree_recette_id=entree_din_recette_id,
                laitage=jour_data.diner_laitage,
                dessert=jour_data.diner_dessert,
                dessert_recette_id=dessert_din_recette_id,
            ))

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
