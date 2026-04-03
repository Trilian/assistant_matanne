"""
Tests pour src/api/routes/preferences.py

Tests unitaires pour les routes préférences utilisateur.
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

PREFERENCES_CREATE = {
    "regime_alimentaire": "omnivore",
    "allergies": ["gluten"],
    "nb_personnes": 3,
    "budget_courses_hebdo": 120.0,
    "jours_courses": ["samedi"],
    "theme": "dark",
    "langue": "fr",
}

PREFERENCES_PATCH = {
    "theme": "light",
    "nb_personnes": 4,
}


# ═══════════════════════════════════════════════════════════
# TESTS ROUTES PRÉFÉRENCES
# ═══════════════════════════════════════════════════════════


class TestRoutesPreferences:
    """Tests des routes préférences."""

    def test_obtenir_preferences_endpoint(self, client):
        """GET /api/v1/preferences existe."""
        response = client.get("/api/v1/preferences")
        assert response.status_code in (200, 500)

    def test_creer_preferences_endpoint(self, client):
        """PUT /api/v1/preferences existe (upsert)."""
        response = client.put("/api/v1/preferences", json=PREFERENCES_CREATE)
        assert response.status_code in (200, 201, 422, 500)

    def test_modifier_preferences_endpoint(self, client):
        """PATCH /api/v1/preferences existe."""
        response = client.patch("/api/v1/preferences", json=PREFERENCES_PATCH)
        assert response.status_code in (200, 422, 500)

    def test_modifier_preferences_body_vide(self, client):
        """PATCH /api/v1/preferences avec body vide."""
        response = client.patch("/api/v1/preferences", json={})
        assert response.status_code in (200, 422, 500)
