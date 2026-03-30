"""Tests pour ResumeFamilleIAService — résumé hebdomadaire famille IA."""

from datetime import date
from unittest.mock import MagicMock, patch

import pytest

from src.services.dashboard.resume_famille_ia import (
    ResumeFamilleIAService,
    ResumeHebdoIAResponse,
)


class TestResumeHebdoIAResponse:
    def test_creation_vide(self):
        r = ResumeHebdoIAResponse()
        assert r.resume == ""
        assert r.points_attention == []
        assert r.recommandations == []
        assert r.score_semaine == 0

    def test_creation_complete(self):
        r = ResumeHebdoIAResponse(
            resume="Semaine bien remplie",
            points_attention=["Stocks bas"],
            recommandations=["Planifier les repas"],
            score_semaine=75,
        )
        assert r.score_semaine == 75
        assert len(r.points_attention) == 1

    def test_score_validation(self):
        with pytest.raises(Exception):
            ResumeHebdoIAResponse(score_semaine=150)
        with pytest.raises(Exception):
            ResumeHebdoIAResponse(score_semaine=-5)


class TestResumeFamilleIAService:
    @patch("src.services.dashboard.resume_famille_ia.obtenir_client_ia")
    def test_init(self, mock_ia):
        service = ResumeFamilleIAService()
        assert service is not None

    @patch("src.services.dashboard.resume_famille_ia.obtenir_contexte_db")
    @patch("src.services.dashboard.resume_famille_ia.obtenir_client_ia")
    def test_collecter_contexte_structure(self, mock_ia, mock_db):
        """Vérifie que le contexte a la bonne structure même sans données."""
        service = ResumeFamilleIAService()

        # Mock DB context retournant des résultats vides
        mock_session = MagicMock()
        mock_session.__enter__ = MagicMock(return_value=mock_session)
        mock_session.__exit__ = MagicMock(return_value=False)

        # Tous les .scalar() retournent 0
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.scalar.return_value = 0
        mock_session.query.return_value = mock_query

        mock_db.return_value = mock_session

        contexte = service._collecter_contexte(date(2026, 3, 15))

        assert "periode" in contexte
        assert "planning" in contexte
        assert "inventaire" in contexte
        assert "budget" in contexte
        assert contexte["periode"]["debut"] is not None
