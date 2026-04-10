"""
Service Insights & Analytics familiaux.

Agrège les données de tous les modules sur une période donnée
et génère un rapport analytique avec tendances et comparaisons.
Page "Ma famille en chiffres".
"""

from __future__ import annotations

import logging
from datetime import date, timedelta
from typing import Any

from pydantic import BaseModel, Field

from src.core.db import obtenir_contexte_db
from src.core.decorators import avec_cache
from src.services.core.base import BaseAIService
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


class TendanceModule(BaseModel):
    """Tendance d'un module sur la période analysée."""

    module: str = Field("", description="Nom du module")
    valeur_actuelle: float = 0.0
    valeur_precedente: float = 0.0
    variation_pct: float = 0.0
    tendance: str = Field("stable", description="hausse, baisse, stable")
    detail: str = ""


class InsightsFamille(BaseModel):
    """Insights analytiques complets de la famille."""

    periode_jours: int = 30
    # Cuisine
    repas_planifies: int = 0
    repas_cuisines: int = 0
    taux_realisation_repas: float = 0.0
    recettes_favorites: list[str] = Field(default_factory=list)
    # Budget
    depenses_totales: float = 0.0
    budget_par_categorie: dict[str, float] = Field(default_factory=dict)
    # Routines
    routines_actives: int = 0
    taux_completion_routines: float = 0.0
    meilleur_streak: int = 0
    # Jardin
    recoltes_count: int = 0
    plantes_actives: int = 0
    # Tendances
    tendances: list[TendanceModule] = Field(default_factory=list)
    # IA narrative
    resume_ia: str = ""
    points_forts: list[str] = Field(default_factory=list)
    axes_amelioration: list[str] = Field(default_factory=list)


class InsightsAnalyticsService(BaseAIService):
    """Service d'analytics familiaux avec narrative IA."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(
            cache_prefix="insights_analytics",
            default_ttl=3600,
            default_temperature=0.5,
            service_name="insights_analytics",
            **kwargs,
        )

    @avec_cache(ttl=3600)
    def generer_insights_famille(self, periode_mois: int = 1) -> InsightsFamille:
        """Génère les insights analytiques de la famille sur une période.

        Args:
            periode_mois: Nombre de mois à analyser (1, 3, 6, 12).

        Returns:
            InsightsFamille avec métriques, tendances et narrative IA.
        """
        periode_jours = periode_mois * 30
        date_debut = date.today() - timedelta(days=periode_jours)
        date_fin = date.today()
        date_precedente = date_debut - timedelta(days=periode_jours)

        insights = InsightsFamille(periode_jours=periode_jours)

        try:
            self._collecter_metriques_cuisine(insights, date_debut, date_fin, date_precedente)
        except Exception:
            logger.warning("Collecte métriques cuisine échouée", exc_info=True)

        try:
            self._collecter_metriques_routines(insights, date_debut, date_fin)
        except Exception:
            logger.warning("Collecte métriques routines échouée", exc_info=True)

        try:
            self._collecter_metriques_jardin(insights, date_debut, date_fin)
        except Exception:
            logger.warning("Collecte métriques jardin échouée", exc_info=True)

        # Générer la narrative IA
        try:
            insights.resume_ia = self._generer_narrative(insights)
        except Exception:
            logger.warning("Génération narrative IA échouée", exc_info=True)
            insights.resume_ia = "Analyse temporairement indisponible."

        return insights

    def _collecter_metriques_cuisine(
        self,
        insights: InsightsFamille,
        date_debut: date,
        date_fin: date,
        date_precedente: date,
    ) -> None:
        """Collecte les métriques du module cuisine."""
        with obtenir_contexte_db() as session:
            from sqlalchemy import func

            from src.core.models import Planning, Repas

            # Repas planifiés sur la période
            plannings = (
                session.query(Planning)
                .filter(Planning.date_debut >= date_debut, Planning.date_debut <= date_fin)
                .all()
            )
            planning_ids = [p.id for p in plannings]

            if planning_ids:
                insights.repas_planifies = int(
                    session.query(func.count(Repas.id))
                    .filter(Repas.planning_id.in_(planning_ids))
                    .scalar()
                    or 0
                )
                insights.repas_cuisines = int(
                    session.query(func.count(Repas.id))
                    .filter(
                        Repas.planning_id.in_(planning_ids),
                        Repas.statut == "cuisine",
                    )
                    .scalar()
                    or 0
                )
                if insights.repas_planifies > 0:
                    insights.taux_realisation_repas = round(
                        insights.repas_cuisines / insights.repas_planifies * 100,
                        1,
                    )

            # Période précédente pour tendance
            plannings_prec = (
                session.query(Planning)
                .filter(Planning.date_debut >= date_precedente, Planning.date_debut < date_debut)
                .all()
            )
            nb_prec = 0
            if plannings_prec:
                p_ids_prec = [p.id for p in plannings_prec]
                nb_prec = int(
                    session.query(func.count(Repas.id))
                    .filter(Repas.planning_id.in_(p_ids_prec))
                    .scalar()
                    or 0
                )

            if nb_prec > 0:
                var = round((insights.repas_planifies - nb_prec) / nb_prec * 100, 1)
                insights.tendances.append(
                    TendanceModule(
                        module="cuisine",
                        valeur_actuelle=float(insights.repas_planifies),
                        valeur_precedente=float(nb_prec),
                        variation_pct=var,
                        tendance="hausse" if var > 5 else ("baisse" if var < -5 else "stable"),
                        detail=f"{insights.repas_planifies} repas planifiés vs {nb_prec} précédemment",
                    )
                )

    def _collecter_metriques_routines(
        self,
        insights: InsightsFamille,
        date_debut: date,
        date_fin: date,
    ) -> None:
        """Collecte les métriques du module routines."""
        with obtenir_contexte_db() as session:
            from src.core.models.famille import Routine

            routines = session.query(Routine).filter(Routine.actif.is_(True)).all()
            insights.routines_actives = len(routines)

            if routines:
                streaks = [r.streak_actuel or 0 for r in routines]
                insights.meilleur_streak = max(streaks) if streaks else 0

                # Taux de complétion approximatif
                total_completions = sum(r.nb_completions or 0 for r in routines)
                jours = (date_fin - date_debut).days or 1
                insights.taux_completion_routines = round(
                    min(total_completions / (len(routines) * jours) * 100, 100.0),
                    1,
                )

    def _collecter_metriques_jardin(
        self,
        insights: InsightsFamille,
        date_debut: date,
        date_fin: date,
    ) -> None:
        """Collecte les métriques du module jardin."""
        with obtenir_contexte_db() as session:
            from sqlalchemy import func

            from src.core.models.temps_entretien import ActionPlante, PlanteJardin

            insights.plantes_actives = int(session.query(func.count(PlanteJardin.id)).scalar() or 0)
            insights.recoltes_count = int(
                session.query(func.count(ActionPlante.id))
                .filter(
                    ActionPlante.type_action == "recolte",
                    ActionPlante.date_action >= date_debut,
                    ActionPlante.date_action <= date_fin,
                )
                .scalar()
                or 0
            )

    def _generer_narrative(self, insights: InsightsFamille) -> str:
        """Génère un résumé narratif IA des insights."""
        prompt = f"""Génère un résumé bienveillant des statistiques familiales :

- Repas planifiés : {insights.repas_planifies}, cuisinés : {insights.repas_cuisines} ({insights.taux_realisation_repas}%)
- Routines actives : {insights.routines_actives}, meilleur streak : {insights.meilleur_streak} jours
- Complétion routines : {insights.taux_completion_routines}%
- Jardin : {insights.plantes_actives} plantes, {insights.recoltes_count} récoltes
- Tendances : {[t.model_dump() for t in insights.tendances]}

Résume en 3-4 phrases positives avec 2-3 points forts et 1-2 axes d'amélioration.
Réponds en JSON : {{"resume": "...", "points_forts": ["..."], "axes_amelioration": ["..."]}}"""

        system_prompt = (
            "Tu es un coach familial bienveillant. "
            "Tu commentes les statistiques de façon encourageante et constructive."
        )

        result = self.call_with_dict_parsing_sync(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.5,
        )

        if result:
            insights.points_forts = result.get("points_forts", [])
            insights.axes_amelioration = result.get("axes_amelioration", [])
            return result.get("resume", "")

        return ""


@service_factory("insights_analytics", tags={"ia", "dashboard"})
def get_insights_analytics_service() -> InsightsAnalyticsService:
    """Factory pour le service d'insights analytics."""
    return InsightsAnalyticsService()
