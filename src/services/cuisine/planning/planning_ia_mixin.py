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
                        "type_repas": "déjeuner" if idx % 2 == 0 else "dîner",
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
                            "type_repas": "déjeuner" if idx % 2 == 0 else "dîner",
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
  {{"jour": "Lundi", "dejeuner": "Pâtes carbonara", "diner": "Salade niçoise"}},
  {{"jour": "Mardi", "dejeuner": "Riz et poulet", "diner": "Soupe de légumes"}}
]}}

RULES:
1. Return ONLY valid JSON array with exactly 7 items (one per day)
2. jour values: Lundi, Mardi, Mercredi, Jeudi, Vendredi, Samedi, Dimanche
3. dejeuner and diner: recipe names or meal descriptions (3-50 chars)
4. Ensure variety throughout the week
5. Adapt to family preferences and dietary restrictions
6. No explanations, no text, ONLY JSON"""

        logger.info(f"🤖 Generating AI weekly plan starting {semaine_debut}")

        # Appel IA avec auto rate limiting & parsing
        planning_data = self.call_with_list_parsing_sync(
            prompt=prompt,
            item_model=JourPlanning,
            system_prompt="Return ONLY valid JSON. No text before or after JSON. Never use markdown code blocks.",
            max_items=7,
            temperature=0.5,
            max_tokens=2000,
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

            # Déjeuner
            repas_dej = Repas(
                planning_id=planning.id,
                date_repas=date_jour,
                type_repas="déjeuner",
                notes=jour_data.dejeuner,
            )
            db.add(repas_dej)

            # Dîner
            repas_din = Repas(
                planning_id=planning.id,
                date_repas=date_jour,
                type_repas="dîner",
                notes=jour_data.diner,
            )
            db.add(repas_din)

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
