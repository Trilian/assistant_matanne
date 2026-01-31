"""
Service Planning Unifié (REFACTORING PHASE 2)

✅ Utilise @with_db_session et @with_cache (Phase 1)
✅ Validation Pydantic centralisée
✅ Type hints complets pour meilleur IDE support
✅ Services testables sans Streamlit
"""

import logging
from datetime import date, timedelta
from typing import Any

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session, joinedload

from src.core.ai import obtenir_client_ia
from src.core.cache import Cache
from src.core.database import obtenir_contexte_db
from src.core.decorators import with_db_session, with_cache, with_error_handling
from src.core.errors_base import ErreurNonTrouve
from src.core.models import Planning, Repas
from src.services.base_ai_service import BaseAIService, PlanningAIMixin
from src.services.types import BaseService

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════
# SCHÉMAS PYDANTIC
# ═══════════════════════════════════════════════════════════

class JourPlanning(BaseModel):
    """Jour du planning généré par l'IA"""
    jour: str = Field(..., min_length=6, max_length=10)
    dejeuner: str = Field(..., min_length=3)
    diner: str = Field(..., min_length=3)


# ═══════════════════════════════════════════════════════════
# SERVICE PLANNING UNIFIÉ
# ═══════════════════════════════════════════════════════════


class PlanningService(BaseService[Planning], BaseAIService, PlanningAIMixin):
    """
    Service complet pour le planning hebdomadaire.

    ✅ Héritage multiple :
    - BaseService → CRUD optimisé
    - BaseAIService → IA avec rate limiting auto
    - PlanningAIMixin → Contextes métier planning

    Fonctionnalités:
    - CRUD optimisé avec cache
    - Génération IA planning hebdomadaire
    - Gestion repas par jour
    """

    def __init__(self):
        BaseService.__init__(self, Planning, cache_ttl=1800)
        BaseAIService.__init__(
            self,
            client=obtenir_client_ia(),
            cache_prefix="planning",
            default_ttl=1800,
            default_temperature=0.7,
            service_name="planning",
        )

    # ═══════════════════════════════════════════════════════════
    # SECTION 1: CRUD & PLANNING (REFACTORED)
    # ═══════════════════════════════════════════════════════════

    @with_cache(ttl=1800, key_func=lambda self, pid=None: f"planning_active")
    @with_error_handling(default_return=None)
    @with_db_session
    def get_planning(self, planning_id: int | None = None, db: Session | None = None) -> Planning | None:
        """Get the active or specified planning with eager loading of meals.

        Args:
            planning_id: Specific planning ID, or None to get active planning
            db: Database session (injected by @with_db_session)

        Returns:
            Planning object with repas eagerly loaded, or None if not found
        """
        if planning_id:
            planning = (
                db.query(Planning)
                .options(
                    joinedload(Planning.repas).joinedload(Repas.recette)
                )
                .filter(Planning.id == planning_id)
                .first()
            )
        else:
            planning = (
                db.query(Planning)
                .options(
                    joinedload(Planning.repas).joinedload(Repas.recette)
                )
                .filter(Planning.actif == True)
                .first()
            )
        
        if not planning:
            logger.debug(f"ℹ️ Planning not found")
            return None
        
        return planning

    @with_cache(ttl=1800, key_func=lambda self, pid: f"planning_full_{pid}")
    @with_error_handling(default_return=None)
    @with_db_session
    def get_planning_complet(self, planning_id: int, db: Session | None = None) -> dict[str, Any] | None:
        """Récupère un planning avec tous ses repas.

        Retrieves complete planning with all meals organized by day.
        Results are cached for 30 minutes.

        Args:
            planning_id: ID of the planning to retrieve
            db: Database session (injected by @with_db_session)

        Returns:
            Dict with planning data and meals organized by date, or None if not found
        """
        planning = (
            db.query(Planning)
            .options(
                joinedload(Planning.repas).joinedload(Repas.recette)
            )
            .filter(Planning.id == planning_id)
            .first()
        )

        if not planning:
            logger.warning(f"⚠️ Planning {planning_id} not found")
            return None

        repas_par_jour = {}
        for repas in planning.repas:
            jour_str = repas.date_repas.strftime("%Y-%m-%d")
            if jour_str not in repas_par_jour:
                repas_par_jour[jour_str] = []

            repas_par_jour[jour_str].append(
                {
                    "id": repas.id,
                    "type_repas": repas.type_repas,
                    "recette_id": repas.recette_id,
                    "recette_nom": repas.recette.nom if repas.recette else None,
                    "prepare": repas.prepare,
                    "notes": repas.notes,
                }
            )

        result = {
            "id": planning.id,
            "nom": planning.nom,
            "semaine_debut": planning.semaine_debut.isoformat(),
            "semaine_fin": planning.semaine_fin.isoformat(),
            "actif": planning.actif,
            "genere_par_ia": planning.genere_par_ia,
            "repas_par_jour": repas_par_jour,
        }

        logger.info(f"✅ Retrieved planning {planning_id} with {len(repas_par_jour)} days")
        return result

    # ═══════════════════════════════════════════════════════════
    # SECTION 2: GÉNÉRATION IA (REFACTORED)
    # ═══════════════════════════════════════════════════════════

    @with_cache(
        ttl=3600,
        key_func=lambda self, semaine_debut, preferences=None: f"planning_ia_{semaine_debut.isoformat()}",
    )
    @with_error_handling(default_return=None)
    @with_db_session
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
            db: Database session (injected by @with_db_session)

        Returns:
            Planning object with generated meals, or None if generation fails
        """
        # Utilisation du Mixin pour contexte planning
        context = self.build_planning_context(
            config=preferences or {},
            semaine_debut=semaine_debut.strftime("%d/%m/%Y"),
        )

        semaine_fin = semaine_debut + timedelta(days=6)

        # Construire prompt
        prompt = self.build_json_prompt(
            context=context,
            task="Generate a complete weekly meal plan (Monday to Sunday)",
            json_schema='[{"jour": str, "dejeuner": str, "diner": str}]',
            constraints=[
                "One meal per type (lunch, dinner) per day",
                "Balanced and varied throughout the week",
                "Adapt to household configuration",
                "Consider seasonal ingredients",
                "Family-friendly recipes",
            ],
        )

        logger.info(f"🤖 Generating AI weekly plan starting {semaine_debut}")

        # Appel IA avec auto rate limiting & parsing
        planning_data = self.call_with_list_parsing_sync(
            prompt=prompt,
            item_model=JourPlanning,
            system_prompt=self.build_system_prompt(
                role="Family meal planner",
                expertise=[
                    "Meal organization",
                    "Nutritional balance",
                    "Seasonal cooking",
                    "Family preferences",
                ],
                rules=[
                    "Respect dietary restrictions",
                    "Balance flavors across week",
                    "Minimize repeated meals",
                    "Consider preparation time",
                ],
            ),
            max_items=7,
        )

        # Log de debug pour voir la réponse
        if not planning_data:
            logger.warning(f"⚠️ Failed to generate planning for {semaine_debut} - no data returned")
            logger.debug(f"Checking if we can create default planning instead...")
            
            # Créer un planning par défaut avec des repas simples
            planning = Planning(
                nom=f"Planning {semaine_debut.strftime('%d/%m/%Y')}",
                semaine_debut=semaine_debut,
                semaine_fin=semaine_fin,
                actif=True,
                genere_par_ia=False,  # Non généré par IA car fallback
            )
            db.add(planning)
            db.flush()

            # Créer repas par défaut (simplement lundi à dimanche)
            jours_semaine = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
            for idx, jour_name in enumerate(jours_semaine):
                date_jour = semaine_debut + timedelta(days=idx)
                
                repas = Repas(
                    planning_id=planning.id,
                    date_repas=date_jour,
                    type_repas="dejeuner",
                    notes=f"Repas du {jour_name} - À remplir manuellement",
                )
                db.add(repas)
            
            db.commit()
            logger.info(f"✅ Created default planning for {semaine_debut} with 7 days")
            return planning
        
        # Planning IA réussi
        logger.info(f"✅ Generated planning with {len(planning_data)} days using AI")

        # Créer planning en DB
        planning = Planning(
            nom=f"Planning {semaine_debut.strftime('%d/%m/%Y')}",
            semaine_debut=semaine_debut,
            semaine_fin=semaine_fin,
            actif=True,
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

        # Invalider cache
        Cache.invalider(pattern="planning")

        logger.info(f"✅ Generated AI planning for week starting {semaine_debut}")
        return planning


# INSTANCE SINGLETON - LAZY LOADING
_planning_service = None

def get_planning_service() -> PlanningService:
    """Get or create the global PlanningService instance."""
    global _planning_service
    if _planning_service is None:
        _planning_service = PlanningService()
    return _planning_service

planning_service = None

__all__ = ["PlanningService", "planning_service", "get_planning_service"]
