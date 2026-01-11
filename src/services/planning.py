"""
Service Planning Unifié (REFACTORING v2.2 - PRO)

✅ Héritage de BaseAIService (rate limiting + cache auto)
✅ Utilisation de PlanningAIMixin (contextes métier)
✅ Fix: Import RateLimitIA depuis src.core.ai
"""

import logging
from datetime import date, timedelta

from pydantic import BaseModel
from sqlalchemy.orm import joinedload

from src.core.ai import obtenir_client_ia
from src.core.cache import Cache
from src.core.database import obtenir_contexte_db
from src.core.errors import gerer_erreurs
from src.core.models import Planning, Repas
from src.services.base_ai_service import BaseAIService, PlanningAIMixin
from src.services.types import BaseService

logger = logging.getLogger(__name__)


class PlanningService(BaseService[Planning], BaseAIService, PlanningAIMixin):
    """
    Service complet pour le planning hebdomadaire.

    ✅ Héritage multiple :
    - BaseService → CRUD optimisé
    - BaseAIService → IA avec rate limiting auto
    - PlanningAIMixin → Contextes métier planning
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

    @gerer_erreurs(afficher_dans_ui=False, valeur_fallback=None)
    def get_planning_complet(self, planning_id: int) -> dict | None:
        """Récupère un planning avec tous ses repas."""
        cache_key = f"planning_full_{planning_id}"
        cached = Cache.obtenir(cache_key, ttl=self.cache_ttl)
        if cached:
            return cached

        with obtenir_contexte_db() as db:
            planning = (
                db.query(Planning)
                .options(joinedload(Planning.repas).joinedload(Repas.recette))
                .filter(Planning.id == planning_id)
                .first()
            )

            if not planning:
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
                "semaine_debut": planning.semaine_debut,
                "semaine_fin": planning.semaine_fin,
                "actif": planning.actif,
                "genere_par_ia": planning.genere_par_ia,
                "repas_par_jour": repas_par_jour,
            }

            Cache.definir(
                cache_key,
                result,
                ttl=self.cache_ttl,
                dependencies=[f"planning_{planning_id}", "plannings"],
            )

            return result

    @gerer_erreurs(afficher_dans_ui=True, valeur_fallback=None)
    async def generer_planning_ia(
        self, semaine_debut: date, preferences: dict | None = None
    ) -> Planning | None:
        """
        Génère un planning hebdomadaire avec l'IA.

        ✅ Rate limiting AUTO
        ✅ Cache AUTO
        Code réduit de 70 lignes → 25 lignes ! 🚀
        """
        # 🎯 Utilisation du Mixin pour contexte planning
        context = self.build_planning_context(
            config=preferences or {}, semaine_debut=semaine_debut.strftime("%d/%m/%Y")
        )

        semaine_fin = semaine_debut + timedelta(days=6)

        prompt = self.build_json_prompt(
            context=context,
            task="Génère un planning hebdomadaire complet (lundi à dimanche)",
            json_schema='[{"jour": str, "dejeuner": str, "diner": str}]',
            constraints=[
                "Un repas par type (déjeuner, dîner) par jour",
                "Équilibré et varié sur la semaine",
                "Adapter selon configuration foyer",
            ],
        )

        class JourPlanning(BaseModel):
            jour: str
            dejeuner: str
            diner: str

        planning_data = await self.call_with_list_parsing(
            prompt=prompt,
            item_model=JourPlanning,
            system_prompt=self.build_system_prompt(
                role="Planificateur de repas familial",
                expertise=["Organisation repas", "Équilibre nutritionnel"],
            ),
            max_items=7,
        )

        if not planning_data:
            return None

        # Créer planning en DB
        with obtenir_contexte_db() as db:
            planning = Planning(
                nom=f"Planning semaine {semaine_debut.strftime('%d/%m')}",
                semaine_debut=semaine_debut,
                semaine_fin=semaine_fin,
                actif=True,
                genere_par_ia=True,
            )
            db.add(planning)
            db.flush()

            for idx, jour_data in enumerate(planning_data):
                date_jour = semaine_debut + timedelta(days=idx)

                repas_dej = Repas(
                    planning_id=planning.id,
                    date_repas=date_jour,
                    type_repas="déjeuner",
                    notes=jour_data.dejeuner,
                )
                db.add(repas_dej)

                repas_din = Repas(
                    planning_id=planning.id,
                    date_repas=date_jour,
                    type_repas="dîner",
                    notes=jour_data.diner,
                )
                db.add(repas_din)

            db.commit()
            db.refresh(planning)

        logger.info(f"✅ Planning IA généré pour semaine du {semaine_debut}")
        return planning


planning_service = PlanningService()

__all__ = ["PlanningService", "planning_service"]
