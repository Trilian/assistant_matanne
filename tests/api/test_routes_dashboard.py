"""Tests dédiés pour src/api/routes/dashboard.py."""

import httpx
import pytest
import pytest_asyncio
from unittest.mock import Mock, patch
from fastapi import FastAPI

from src.api.dependencies import require_auth
from src.api.routes.dashboard import router

pytestmark = pytest.mark.asyncio(loop_scope="function")


@pytest_asyncio.fixture
async def client():
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[require_auth] = lambda: {"id": "test-user", "role": "admin"}

    # Désactiver le rate limiting IA pour les tests
    try:
        from src.api.routes.dashboard import verifier_limite_debit_ia as vld_dash
        app.dependency_overrides[vld_dash] = lambda: {}
    except ImportError:
        pass

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


class TestRoutesDashboard:
    @pytest.mark.parametrize(
        "path",
        [
            "/api/v1/dashboard",
            "/api/v1/dashboard/cuisine",
            "/api/v1/dashboard/budget-unifie",
            "/api/v1/dashboard/score-ecologique",
        ],
    )
    async def test_endpoints_existent(self, client, path):
        response = await client.get(path)
        assert response.status_code not in (404, 405)


class TestInsightsAnalyticsRoute:
    """Tests GET /api/v1/dashboard/insights-analytics"""

    async def test_insights_success(self, client):
        """Insights analytics → 200."""
        from src.services.dashboard.insights_analytics import InsightsFamille

        mock_svc = Mock()
        mock_svc.generer_insights_famille.return_value = InsightsFamille(
            periode_jours=30,
            repas_planifies=14,
            repas_cuisines=12,
            taux_realisation_repas=85.7,
            resume_ia="Bonne semaine !",
        )

        with patch(
            "src.services.dashboard.insights_analytics.get_insights_analytics_service",
            return_value=mock_svc,
        ):
            response = await client.get("/api/v1/dashboard/insights-analytics?periode_mois=1")

        assert response.status_code == 200

    async def test_insights_periode_invalide(self, client):
        """Période > 12 → 422."""
        response = await client.get("/api/v1/dashboard/insights-analytics?periode_mois=24")
        assert response.status_code == 422
