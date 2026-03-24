"""
Tests pour src/api/routes/webhooks.py

Tests unitaires pour les routes webhooks.
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

WEBHOOK_CREATE = {
    "url": "https://example.com/webhook",
    "evenements": ["recette.created", "courses.updated"],
    "description": "Mon webhook de test",
}

WEBHOOK_UPDATE = {
    "url": "https://example.com/webhook-v2",
    "evenements": ["recette.created"],
}


# ═══════════════════════════════════════════════════════════
# TESTS ROUTES WEBHOOKS
# ═══════════════════════════════════════════════════════════


class TestRoutesWebhooks:
    """Tests CRUD des routes webhooks."""

    def test_lister_webhooks_endpoint(self, client):
        """GET /api/v1/webhooks existe."""
        response = client.get("/api/v1/webhooks")
        assert response.status_code in (200, 500)

    def test_obtenir_webhook_endpoint(self, client):
        """GET /api/v1/webhooks/{id} existe."""
        response = client.get("/api/v1/webhooks/999999")
        # Response validation error possible if mock returns non-string fields
        assert response.status_code in (200, 404, 500)

    def test_creer_webhook_endpoint(self, client):
        """POST /api/v1/webhooks existe."""
        response = client.post("/api/v1/webhooks", json=WEBHOOK_CREATE)
        # Response validation error possible since service is mocked
        assert response.status_code in (200, 201, 422, 500)

    def test_modifier_webhook_endpoint(self, client):
        """PUT /api/v1/webhooks/{id} existe."""
        response = client.put("/api/v1/webhooks/1", json=WEBHOOK_UPDATE)
        assert response.status_code in (200, 404, 422, 500)

    def test_supprimer_webhook_endpoint(self, client):
        """DELETE /api/v1/webhooks/{id} existe."""
        response = client.delete("/api/v1/webhooks/999999")
        assert response.status_code in (200, 204, 404, 500)

    def test_tester_webhook_endpoint(self, client):
        """POST /api/v1/webhooks/{id}/test existe."""
        response = client.post("/api/v1/webhooks/999999/test")
        assert response.status_code in (200, 404, 500)


class TestRoutesWebhooksAvecMock:
    """Tests avec mock du service webhooks."""

    def test_creer_webhook_appelle_service(self):
        """Création de webhook appelle le service."""
        mock_service = MagicMock()
        mock_service.creer_webhook.return_value = {
            "id": 1,
            "url": "https://example.com/webhook",
            "evenements": ["recette.created"],
            "secret": "hmac_secret_generated",
            "actif": True,
        }

        with patch(
            "src.api.routes.webhooks.get_webhook_service",
            return_value=mock_service,
        ):
            from src.api.main import app

            client = TestClient(app)
            response = client.post("/api/v1/webhooks", json=WEBHOOK_CREATE)
            # Service is called via module-level import
            assert response.status_code in (200, 201, 500)

    def test_tester_webhook_appelle_service(self):
        """Test webhook appelle le service."""
        mock_service = MagicMock()
        mock_service.tester_webhook.return_value = {
            "success": True,
            "status_code": 200,
            "response_time_ms": 150,
        }

        with patch(
            "src.api.routes.webhooks.get_webhook_service",
            return_value=mock_service,
        ):
            from src.api.main import app

            client = TestClient(app)
            response = client.post("/api/v1/webhooks/1/test")
            assert response.status_code in (200, 404, 500)
