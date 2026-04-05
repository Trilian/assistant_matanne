"""Tests admin dédiés aux routes legacy d'innovations."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def admin_headers():
    """Headers d'authentification admin avec JWT valide."""
    from src.api.auth import creer_token_acces

    token = creer_token_acces(
        user_id="admin-1",
        email="admin@test.local",
        role="admin",
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def client(app):
    """Client sync local pour les routes admin sync."""
    with TestClient(app) as c:
        yield c


class TestAdminResetModule:
    """Tests pour POST /api/v1/admin/reset-module."""

    def test_reset_module_preview(self, client, admin_headers):
        with patch("src.core.config.obtenir_parametres") as mock_params:
            mock_params.return_value = type("Params", (), {"ENV": "test"})()
            response = client.post(
                "/api/v1/admin/reset-module",
                json={"module": "courses", "confirmer": False},
                headers=admin_headers,
            )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "preview"
        assert "listes_courses" in data["tables_affectees"]

    def test_reset_module_invalide(self, client, admin_headers):
        with patch("src.core.config.obtenir_parametres") as mock_params:
            mock_params.return_value = type("Params", (), {"ENV": "test"})()
            response = client.post(
                "/api/v1/admin/reset-module",
                json={"module": "module_inexistant", "confirmer": True},
                headers=admin_headers,
            )
        assert response.status_code == 400
