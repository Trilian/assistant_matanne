"""Tests pour les services Dashboard — agrégation, anomalies, bien-être, points."""

# pyright: reportUnknownParameterType=false, reportMissingParameterType=false, reportPrivateUsage=false

from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from src.services.dashboard.anomalies_financieres import (
    MoisRef,
    ResumeAnomaliesIA,
    ServiceAnomaliesFinancieres,
)
from src.services.dashboard.score_bienetre import ScoreBienEtreService


# ═══════════════════════════════════════════════════════════
# TESTS ANOMALIES FINANCIÈRES
# ═══════════════════════════════════════════════════════════


class TestMoisRef:
    def test_creation(self):
        m = MoisRef(annee=2026, mois=3)
        assert m.annee == 2026
        assert m.mois == 3


class TestResumeAnomaliesIA:
    def test_creation_vide(self):
        r = ResumeAnomaliesIA()
        assert r.resume == ""
        assert r.recommandations == []

    def test_creation_complete(self):
        r = ResumeAnomaliesIA(
            resume="Augmentation notable des courses",
            recommandations=["Comparer les prix", "Planifier les repas"],
        )
        assert len(r.recommandations) == 2


class TestServiceAnomaliesFinancieres:
    @patch("src.services.dashboard.anomalies_financieres.obtenir_client_ia")
    def test_mois_precedents_mars(self, mock_ia):
        refs = ServiceAnomaliesFinancieres._mois_precedents(date(2026, 3, 15))
        assert refs[0].annee == 2026 and refs[0].mois == 3  # courant
        assert refs[1].annee == 2026 and refs[1].mois == 2  # N-1
        assert refs[2].annee == 2026 and refs[2].mois == 1  # N-2

    @patch("src.services.dashboard.anomalies_financieres.obtenir_client_ia")
    def test_mois_precedents_janvier_rollover(self, mock_ia):
        """Janvier doit remonter à décembre N-1 et novembre N-1."""
        refs = ServiceAnomaliesFinancieres._mois_precedents(date(2026, 1, 10))
        assert refs[0].annee == 2026 and refs[0].mois == 1
        assert refs[1].annee == 2025 and refs[1].mois == 12
        assert refs[2].annee == 2025 and refs[2].mois == 11

    @patch("src.services.dashboard.anomalies_financieres.obtenir_client_ia")
    def test_mois_precedents_fevrier_rollover(self, mock_ia):
        refs = ServiceAnomaliesFinancieres._mois_precedents(date(2026, 2, 1))
        assert refs[1].annee == 2026 and refs[1].mois == 1
        assert refs[2].annee == 2025 and refs[2].mois == 12

    @patch("src.services.dashboard.anomalies_financieres.obtenir_client_ia")
    def test_normaliser_categorie_courses(self, mock_ia):
        svc = ServiceAnomaliesFinancieres
        assert svc._normaliser_categorie("Courses alimentaires") == "courses"
        assert svc._normaliser_categorie("Supermarche") == "courses"
        assert svc._normaliser_categorie("epicerie") == "courses"

    @patch("src.services.dashboard.anomalies_financieres.obtenir_client_ia")
    def test_normaliser_categorie_energie(self, mock_ia):
        svc = ServiceAnomaliesFinancieres
        assert svc._normaliser_categorie("electricité") == "energie"
        assert svc._normaliser_categorie("Gaz naturel") == "energie"
        assert svc._normaliser_categorie("chauffage") == "energie"

    @patch("src.services.dashboard.anomalies_financieres.obtenir_client_ia")
    def test_normaliser_categorie_loisirs(self, mock_ia):
        svc = ServiceAnomaliesFinancieres
        assert svc._normaliser_categorie("Loisirs") == "loisirs"
        assert svc._normaliser_categorie("restaurant") == "loisirs"
        assert svc._normaliser_categorie("Jeux vidéo") == "loisirs"

    @patch("src.services.dashboard.anomalies_financieres.obtenir_client_ia")
    def test_normaliser_categorie_autre(self, mock_ia):
        svc = ServiceAnomaliesFinancieres
        assert svc._normaliser_categorie(None) == "autre"
        assert svc._normaliser_categorie("") == "autre"
        assert svc._normaliser_categorie("impôts") == "impôts"


# ═══════════════════════════════════════════════════════════
# TESTS SCORE BIEN-ÊTRE
# ═══════════════════════════════════════════════════════════


class TestScoreBienEtreService:
    def test_nutri_points_mapping(self):
        """Vérifie la table de correspondance Nutri-score."""
        from src.services.dashboard.score_bienetre import _NUTRI_POINTS

        assert _NUTRI_POINTS["A"] == 5
        assert _NUTRI_POINTS["E"] == 1
        assert len(_NUTRI_POINTS) == 5
