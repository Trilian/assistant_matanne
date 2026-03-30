"""Tests de fumée pour les routes Habitat."""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    from src.api.main import app

    return TestClient(app, raise_server_exceptions=False)


@pytest.mark.parametrize(
    ("method", "path", "payload"),
    [
        ("GET", "/api/v1/habitat/hub", None),
        ("GET", "/api/v1/habitat/scenarios", None),
        ("POST", "/api/v1/habitat/scenarios", {"nom": "Test scenario"}),
        ("GET", "/api/v1/habitat/scenarios/comparaison", None),
        ("GET", "/api/v1/habitat/criteres-immo", None),
        ("POST", "/api/v1/habitat/criteres-immo", {"nom": "ARA"}),
        ("GET", "/api/v1/habitat/annonces", None),
        (
            "POST",
            "/api/v1/habitat/annonces",
            {"source": "manuel", "url_source": "https://example.com/annonce"},
        ),
        ("GET", "/api/v1/habitat/plans", None),
        ("POST", "/api/v1/habitat/plans", {"nom": "Plan RDC", "type_plan": "interieur"}),
        ("GET", "/api/v1/habitat/deco/projets", None),
        ("POST", "/api/v1/habitat/deco/projets", {"nom_piece": "Salon"}),
        ("GET", "/api/v1/habitat/jardin/zones", None),
    ],
)
def test_routes_habitat_existent(client: TestClient, method: str, path: str, payload: dict | None):
    func = getattr(client, method.lower())
    response = func(path, json=payload) if payload is not None else func(path)
    assert response.status_code not in (404, 405), f"{method} {path} retourne {response.status_code}"
