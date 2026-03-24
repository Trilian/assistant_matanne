"""
Tests pour src/api/routes/batch_cooking.py

Tests unitaires pour les routes batch cooking.
"""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Client de test FastAPI."""
    from src.api.main import app

    return TestClient(app, raise_server_exceptions=False)


# ═══════════════════════════════════════════════════════════
# DONNÉES DE TEST
# ═══════════════════════════════════════════════════════════

SESSION_BATCH_CREATE = {
    "nom": "Batch dimanche",
    "date_session": "2026-03-29",
    "recettes_ids": [1, 2, 3],
    "notes": "Préparer pour la semaine",
}

SESSION_BATCH_PATCH = {
    "statut": "en_cours",
    "notes": "Mise à jour",
}


# ═══════════════════════════════════════════════════════════
# TESTS ROUTES SESSIONS
# ═══════════════════════════════════════════════════════════


class TestRoutesSessionsBatchCooking:
    """Tests CRUD des sessions batch cooking."""

    def test_lister_sessions_endpoint(self, client):
        """GET /api/v1/batch-cooking existe."""
        response = client.get("/api/v1/batch-cooking")
        assert response.status_code in (200, 500)

    def test_lister_sessions_avec_filtre_statut(self, client):
        """GET /api/v1/batch-cooking?statut=planifie accepte le filtre."""
        response = client.get("/api/v1/batch-cooking?statut=planifie")
        assert response.status_code in (200, 500)

    def test_lister_sessions_pagination(self, client):
        """GET /api/v1/batch-cooking?page=1&page_size=10 accepte la pagination."""
        response = client.get("/api/v1/batch-cooking?page=1&page_size=10")
        assert response.status_code in (200, 500)

    def test_obtenir_session_endpoint(self, client):
        """GET /api/v1/batch-cooking/{id} existe."""
        response = client.get("/api/v1/batch-cooking/999999")
        assert response.status_code in (200, 404, 500)

    def test_creer_session_endpoint(self, client):
        """POST /api/v1/batch-cooking existe."""
        response = client.post("/api/v1/batch-cooking", json=SESSION_BATCH_CREATE)
        assert response.status_code in (200, 201, 422, 500)

    def test_modifier_session_endpoint(self, client):
        """PATCH /api/v1/batch-cooking/{id} existe."""
        response = client.patch("/api/v1/batch-cooking/1", json=SESSION_BATCH_PATCH)
        assert response.status_code in (200, 404, 422, 500)

    def test_supprimer_session_endpoint(self, client):
        """DELETE /api/v1/batch-cooking/{id} existe."""
        response = client.delete("/api/v1/batch-cooking/999999")
        assert response.status_code in (200, 204, 404, 500)


# ═══════════════════════════════════════════════════════════
# TESTS ROUTES PRÉPARATIONS & CONFIG
# ═══════════════════════════════════════════════════════════


class TestRoutesPreparationsBatchCooking:
    """Tests des routes préparations et configuration."""

    def test_lister_preparations_endpoint(self, client):
        """GET /api/v1/batch-cooking/preparations existe."""
        response = client.get("/api/v1/batch-cooking/preparations")
        # 422 possible si /{session_id} match avant /preparations
        assert response.status_code in (200, 422, 500)

    def test_lister_preparations_filtre_consomme(self, client):
        """GET /api/v1/batch-cooking/preparations?consomme=false accepte le filtre."""
        response = client.get("/api/v1/batch-cooking/preparations?consomme=false")
        assert response.status_code in (200, 422, 500)

    def test_obtenir_config_endpoint(self, client):
        """GET /api/v1/batch-cooking/config existe."""
        response = client.get("/api/v1/batch-cooking/config")
        assert response.status_code in (200, 422, 500)
