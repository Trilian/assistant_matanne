"""Tests des routes bridges inter-modules."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client() -> TestClient:
    from src.api.dependencies import require_auth
    from src.api.main import app

    async def _mock_auth() -> dict:
        return {"sub": "test-user", "role": "admin"}

    app.dependency_overrides[require_auth] = _mock_auth

    yield TestClient(app, raise_server_exceptions=False)

    app.dependency_overrides.pop(require_auth, None)


def test_catalogue_bridges_expose_la_consolidation(client: TestClient) -> None:
    response = client.get("/api/v1/bridges/catalogue")

    assert response.status_code == 200
    payload = response.json()
    assert payload["resume"]["total_legacy"] == 11
    assert payload["resume"]["consolides"] == 11
    assert payload["resume"]["statut"] == "termine"
    assert any(item["flux"] == "Chat IA → Event Bus" for item in payload["items"])


def test_energie_heures_creuses_endpoint(client: TestClient) -> None:
    service = MagicMock()
    service.energie_hc_hp_vers_planning_machines.return_value = {
        "interaction": "IM-5",
        "en_heures_creuses": False,
        "plage": {"debut": "22:00", "fin": "06:00"},
        "appareils_recommandes": [{"nom": "Lave-linge"}],
    }

    with patch("src.services.ia.bridges.obtenir_service_bridges", return_value=service):
        response = client.get("/api/v1/bridges/energie-heures-creuses")

    assert response.status_code == 200
    payload = response.json()
    assert payload["interaction"] == "IM-5"
    assert "plage" in payload
    assert payload["appareils_recommandes"][0]["nom"] == "Lave-linge"
