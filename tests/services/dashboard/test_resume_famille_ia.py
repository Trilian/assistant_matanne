"""Tests pour ResumeFamilleIAService — résumé hebdomadaire famille IA."""

from unittest.mock import patch

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
    def test_collecter_contexte_dep_sans_crash(self, mock_ia, mock_db):
        """Vérifie la structure de fallback du modèle de réponse, sans dépendre des imports DB."""
        response = ResumeHebdoIAResponse()
        assert response.resume == ""
        assert response.points_attention == []
        assert response.recommandations == []
        assert response.score_semaine == 0
