"""Tests unitaires pour `InnovationsService`."""

from __future__ import annotations

from unittest.mock import patch


class TestInnovationsServiceUnit:
    """Tests unitaires pour InnovationsService."""

    def test_evaluer_niveau_excellent(self):
        from src.services.ia_avancee.service_central import InnovationsService

        with patch.object(InnovationsService, "__init__", lambda x: None):
            service = InnovationsService()
            assert service._evaluer_niveau(85) == "excellent"

    def test_evaluer_niveau_attention(self):
        from src.services.ia_avancee.service_central import InnovationsService

        with patch.object(InnovationsService, "__init__", lambda x: None):
            service = InnovationsService()
            assert service._evaluer_niveau(30) == "attention"

    def test_generer_conseils_score_faible(self):
        from src.services.ia_avancee.service_central import InnovationsService
        from src.services.ia_avancee.types_central import DimensionBienEtre

        with patch.object(InnovationsService, "__init__", lambda x: None):
            service = InnovationsService()
            dimensions = [
                DimensionBienEtre(nom="Sport", score=30, detail="Activité insuffisante"),
                DimensionBienEtre(nom="Nutrition", score=90, detail="Excellent"),
            ]
            conseils = service._generer_conseils(dimensions)
            assert len(conseils) >= 1
            assert "sport" in conseils[0].lower()
