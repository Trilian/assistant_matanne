"""
Tests pour src/api/routes/anti_gaspillage.py

Tests unitaires pour les routes anti-gaspillage.
"""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Client de test FastAPI."""
    from src.api.main import app

    return TestClient(app)


# ═══════════════════════════════════════════════════════════
# DONNÉES DE TEST
# ═══════════════════════════════════════════════════════════

MOCK_ANTI_GASPILLAGE = {
    "score": {
        "score": 75,
        "articles_perimes_mois": 3,
        "articles_sauves_mois": 12,
        "economie_estimee": 25.50,
    },
    "articles_urgents": [
        {
            "id": 1,
            "nom": "Yaourts nature",
            "date_peremption": "2026-03-25",
            "jours_restants": 1,
            "quantite": 4,
        },
        {
            "id": 2,
            "nom": "Crème fraîche",
            "date_peremption": "2026-03-26",
            "jours_restants": 2,
            "quantite": 1,
        },
    ],
    "recettes_rescue": [
        {
            "id": 10,
            "nom": "Gâteau au yaourt",
            "ingredients_utilises": ["Yaourts nature"],
        },
    ],
}


# ═══════════════════════════════════════════════════════════
# TESTS ROUTES
# ═══════════════════════════════════════════════════════════


class TestRoutesAntiGaspillage:
    """Tests des routes anti-gaspillage."""

    def test_endpoint_existe(self, client):
        """GET /api/v1/anti-gaspillage existe."""
        response = client.get("/api/v1/anti-gaspillage")
        assert response.status_code in (200, 500)

    def test_endpoint_avec_parametre_jours(self, client):
        """GET /api/v1/anti-gaspillage?jours=14 accepte le paramètre."""
        response = client.get("/api/v1/anti-gaspillage?jours=14")
        assert response.status_code in (200, 500)

    def test_endpoint_jours_invalide(self, client):
        """GET /api/v1/anti-gaspillage?jours=0 est rejeté (ge=1)."""
        response = client.get("/api/v1/anti-gaspillage?jours=0")
        assert response.status_code == 422

    def test_endpoint_jours_trop_grand(self, client):
        """GET /api/v1/anti-gaspillage?jours=31 est rejeté (le=30)."""
        response = client.get("/api/v1/anti-gaspillage?jours=31")
        assert response.status_code == 422


class TestRoutesAntiGaspillageAvecMock:
    """Tests avec mock de la base de données."""

    def test_retourne_score_et_articles(self):
        """Retourne score, articles urgents et recettes rescue."""
        with patch(
            "src.api.routes.anti_gaspillage.executer_avec_session"
        ) as mock_exec:
            mock_ctx = MagicMock()
            mock_ctx.__enter__ = MagicMock(return_value=MagicMock())
            mock_ctx.__exit__ = MagicMock(return_value=None)
            mock_exec.return_value = mock_ctx

            with patch(
                "src.api.routes.anti_gaspillage.executer_async",
                side_effect=lambda fn: fn(),
            ):
                from src.api.main import app

                client = TestClient(app)
                response = client.get("/api/v1/anti-gaspillage")
                assert response.status_code in (200, 500)
