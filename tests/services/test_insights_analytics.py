"""
Tests unitaires pour InsightsAnalyticsService.

Couvre: génération d'insights famille, narrative IA.
"""

import pytest
from unittest.mock import Mock, patch
from contextlib import contextmanager

from src.services.dashboard.insights_analytics import (
    InsightsAnalyticsService,
    InsightsFamille,
    TendanceModule,
)


class TestInsightsAnalyticsService:
    """Tests pour le service Insights & Analytics."""

    @pytest.fixture
    def service(self):
        return InsightsAnalyticsService()

    @patch("src.services.dashboard.insights_analytics.obtenir_contexte_db")
    def test_generer_insights_basique(self, mock_db, service):
        """Génération d'insights basique sans données en base."""
        mock_session = Mock()
        mock_session.query.return_value.filter.return_value.all.return_value = []
        mock_session.query.return_value.filter.return_value.scalar.return_value = 0

        @contextmanager
        def _ctx():
            yield mock_session

        mock_db.return_value = _ctx()

        service.call_with_dict_parsing_sync = Mock(
            return_value={
                "resume": "Bonne semaine familiale !",
                "points_forts": ["Régularité des repas"],
                "axes_amelioration": ["Plus de variété"],
            }
        )

        # Contourner le cache pour le test
        result = InsightsAnalyticsService.generer_insights_famille.__wrapped__(service, periode_mois=1)
        assert isinstance(result, InsightsFamille)
        assert result.periode_jours == 30

    def test_generer_narrative_ia(self, service):
        """Génération de narrative IA à partir d'insights."""
        insights = InsightsFamille(
            repas_planifies=14,
            repas_cuisines=12,
            taux_realisation_repas=85.7,
            routines_actives=3,
            meilleur_streak=7,
        )
        service.call_with_dict_parsing_sync = Mock(
            return_value={
                "resume": "Super semaine ! 85% de réalisation.",
                "points_forts": ["Régularité"],
                "axes_amelioration": ["Varier les légumes"],
            }
        )
        result = service._generer_narrative(insights)
        assert "Super semaine" in result
        assert len(insights.points_forts) > 0

    def test_generer_narrative_ia_none(self, service):
        """IA retourne None → résumé vide."""
        insights = InsightsFamille()
        service.call_with_dict_parsing_sync = Mock(return_value=None)
        result = service._generer_narrative(insights)
        assert result == ""
