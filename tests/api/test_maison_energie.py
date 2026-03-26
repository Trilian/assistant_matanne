import pytest
from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)

@pytest.mark.integration
def test_historique_energie_ok():
    resp = client.get("/api/v1/maison/depenses/energie/electricite?nb_mois=3")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "items" in data or isinstance(data.get("items", []), list)

@pytest.mark.integration
def test_tendances_energie_ok():
    resp = client.get("/api/v1/maison/energie/tendances?type_compteur=electricite&nb_mois=3")
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("type") == "electricite"
    assert "points" in data

@pytest.mark.integration
def test_previsions_energie_ia_ok():
    resp = client.get("/api/v1/maison/energie/previsions-ia?type_compteur=electricite&nb_mois=6")
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("type") == "electricite"
    # either a valid forecast or an explanatory message
    assert any(k in data for k in ("consommation_prevue", "message"))
