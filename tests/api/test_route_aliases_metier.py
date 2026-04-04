"""Tests de régression pour la redistribution des routes métier."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client() -> TestClient:
    """Client FastAPI avec auth et limite IA neutralisées pour les alias de routes."""
    from src.api.dependencies import require_auth
    from src.api.main import app
    from src.api.rate_limiting import verifier_limite_debit_ia

    app.dependency_overrides[require_auth] = lambda: {
        "id": "1",
        "email": "test@matanne.fr",
        "role": "membre",
    }

    async def mock_rate_check():
        return {"allowed": True, "remaining": 99}

    app.dependency_overrides[verifier_limite_debit_ia] = mock_rate_check

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def mock_innovations_service():
    """Mock central pour les endpoints redistribués."""
    service = MagicMock()
    service.suggerer_repas_ce_soir.return_value = None
    service.generer_planification_hebdo_complete.return_value = None
    service.calculer_score_famille_hebdo.return_value = None
    service.detecter_anomalies_energie.return_value = None
    service.generer_bilan_annuel.return_value = None

    with patch("src.services.ia_avancee.get_innovations_service", return_value=service, create=True):
        yield service


def test_alias_recettes_mange_ce_soir_est_expose(client: TestClient, mock_innovations_service) -> None:
    response = client.post(
        "/api/v1/recettes/mange-ce-soir",
        json={"temps_disponible_min": 20, "humeur": "rapide"},
    )

    assert response.status_code == 200


def test_alias_planning_planification_auto_est_expose(client: TestClient, mock_innovations_service) -> None:
    response = client.get("/api/v1/planning/planification-auto")

    assert response.status_code == 200


def test_alias_famille_score_hebdo_est_expose(client: TestClient, mock_innovations_service) -> None:
    response = client.get("/api/v1/famille/score-famille-hebdo")

    assert response.status_code == 200


def test_alias_habitat_anomalies_energie_est_expose(client: TestClient, mock_innovations_service) -> None:
    response = client.get("/api/v1/habitat/anomalies-energie")

    assert response.status_code == 200


def test_alias_rapports_retrospective_annuelle_est_expose(client: TestClient, mock_innovations_service) -> None:
    response = client.get("/api/v1/rapports/retrospective-annuelle")

    assert response.status_code == 200
