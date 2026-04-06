"""Tests ciblés — adaptation recette et automations par défaut."""

from fastapi.testclient import TestClient
import pytest


@pytest.fixture
def client():
    """Client FastAPI avec auth et rate limiting IA neutralisés pour les tests."""
    from src.api.main import app
    from src.api.dependencies import require_auth
    from src.api.rate_limiting import verifier_limite_debit_ia

    app.dependency_overrides[require_auth] = lambda: {
        "id": "test-user",
        "email": "test@matanne.fr",
        "role": "membre",
    }

    async def mock_rate_check():
        return {"allowed": True, "remaining": 99}

    app.dependency_overrides[verifier_limite_debit_ia] = mock_rate_check

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_adaptation_recette_propose_une_substitution_connue(client: TestClient):
    """Le scénario 'j'ai pas de crème fraîche' doit retourner une alternative exploitable."""
    response = client.post(
        "/api/v1/suggestions/adaptation-recette",
        json={
            "ingredient_manquant": "crème fraîche",
            "quantite": 20,
            "unite": "cl",
            "stock_disponible": ["yaourt nature", "lait", "moutarde"],
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["ingredient_manquant"] == "crème fraîche"
    assert data["substitutions"]
    assert any(item["ingredient_substitut"] == "yaourt nature" for item in data["substitutions"])
    assert data["meilleure_en_stock"]["ingredient_substitut"] == "yaourt nature"


def test_automations_par_defaut_contiennent_cinq_regles():
    """Les automations par défaut initialisent bien les règles A1 à A9."""
    from src.api.routes.automations import _automations_par_defaut

    regles = _automations_par_defaut()

    assert len(regles) == 9
    noms = {regle["nom"] for regle in regles}
    assert any(nom.startswith("A1") for nom in noms)
    assert any(nom.startswith("A2") for nom in noms)
    assert any(nom.startswith("A3") for nom in noms)
    assert any(nom.startswith("A4") for nom in noms)
    assert any(nom.startswith("A5") for nom in noms)
    assert any(nom.startswith("A6") for nom in noms)
    assert any(nom.startswith("A7") for nom in noms)
    assert any(nom.startswith("A8") for nom in noms)
    assert any(nom.startswith("A9") for nom in noms)
