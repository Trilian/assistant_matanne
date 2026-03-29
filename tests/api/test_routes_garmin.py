"""
T5b â€” Tests routes Garmin.

Couvre src/api/routes/garmin.py :
- GET  /api/v1/garmin/status                : statut connexion Garmin
- POST /api/v1/garmin/connect-url           : URL d'autorisation OAuth
- POST /api/v1/garmin/sync                  : synchronisation donnÃ©es
- GET  /api/v1/garmin/stats                 : statistiques activitÃ©
- GET  /api/v1/garmin/recommandation-diner  : recommandation dÃ®ner selon calories
"""

from __future__ import annotations

from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import httpx
import pytest
import pytest_asyncio
from httpx import ASGITransport


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# FIXTURES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest_asyncio.fixture
async def async_client():
    from src.api.dependencies import require_auth
    from src.api.main import app

    app.dependency_overrides[require_auth] = lambda: {
        "id": "test-user",
        "email": "test@matanne.fr",
        "role": "membre",
    }
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app, raise_app_exceptions=False),
        base_url="http://test",
    ) as client:
        yield client
    app.dependency_overrides.clear()


def _session_avec_profil(garmin_connected: bool = False) -> tuple[MagicMock, SimpleNamespace]:
    profil = SimpleNamespace(
        id=1,
        email="test@matanne.fr",
        garmin_connected=garmin_connected,
        display_name="Mathieu",
        objectif_pas_quotidien=8000,
        objectif_calories_brulees=500,
    )
    session = MagicMock()
    session.query.return_value.filter.return_value.first.return_value = profil
    session.get.return_value = profil
    return session, profil


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS â€” STATUT GARMIN
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestStatutGarmin:
    """GET /api/v1/garmin/status."""

    @pytest.mark.asyncio
    async def test_statut_non_connecte(self, async_client: httpx.AsyncClient):
        """Profil sans Garmin â†’ connected: False."""
        session, profil = _session_avec_profil(garmin_connected=False)

        @contextmanager
        def _ctx():
            yield session

        with patch("src.core.db.obtenir_contexte_db", return_value=_ctx()):
            response = await async_client.get("/api/v1/garmin/status")

        assert response.status_code == 200
        data = response.json()
        assert data["connected"] is False

    @pytest.mark.asyncio
    async def test_statut_connecte(self, async_client: httpx.AsyncClient):
        """Profil avec Garmin connectÃ© â†’ connected: True."""
        session, profil = _session_avec_profil(garmin_connected=True)

        @contextmanager
        def _ctx():
            yield session

        with patch("src.core.db.obtenir_contexte_db", return_value=_ctx()):
            response = await async_client.get("/api/v1/garmin/status")

        assert response.status_code == 200
        data = response.json()
        assert data["connected"] is True


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS â€” URL DE CONNEXION GARMIN
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestConnectUrlGarmin:
    """POST /api/v1/garmin/connect-url."""

    @pytest.mark.asyncio
    async def test_connect_url_non_configure(self, async_client: httpx.AsyncClient):
        """Service Garmin non configurÃ© â†’ 503."""
        mock_service = MagicMock()
        mock_service.get_authorization_url.return_value = (None, None)

        with patch("src.services.integrations.garmin.service.obtenir_garmin_service", return_value=mock_service):
            response = await async_client.post("/api/v1/garmin/connect-url")

        assert response.status_code == 503

    @pytest.mark.asyncio
    async def test_connect_url_retourne_url(self, async_client: httpx.AsyncClient):
        """Service Garmin configurÃ© â†’ URL d'autorisation retournÃ©e."""
        mock_service = MagicMock()
        mock_service.get_authorization_url.return_value = (
            "https://garmin.com/oauth/auth?token=xxx",
            "request_token_123",
        )

        with patch("src.services.integrations.garmin.service.obtenir_garmin_service", return_value=mock_service):
            response = await async_client.post("/api/v1/garmin/connect-url")

        assert response.status_code in (200, 201)
        data = response.json()
        assert "authorization_url" in data
        assert "garmin" in data["authorization_url"].lower()


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS â€” SYNC GARMIN
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestSyncGarmin:
    """POST /api/v1/garmin/sync."""

    @pytest.mark.asyncio
    async def test_sync_succes(self, async_client: httpx.AsyncClient):
        """Synchronisation rÃ©ussie â†’ donnÃ©es retournÃ©es."""
        session, profil = _session_avec_profil(garmin_connected=True)
        mock_service = MagicMock()
        mock_service.sync_user_data.return_value = {
            "synced": True,
            "activites": 3,
            "pas_totaux": 12000,
        }

        @contextmanager
        def _ctx():
            yield session

        with (
            patch("src.core.db.obtenir_contexte_db", return_value=_ctx()),
            patch("src.services.integrations.garmin.service.obtenir_garmin_service", return_value=mock_service),
        ):
            response = await async_client.post("/api/v1/garmin/sync?days_back=7")

        assert response.status_code in (200, 201)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS â€” RECOMMANDATION DÃŽNER
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestRecommandationDiner:
    """GET /api/v1/garmin/recommandation-diner â€” adaptation selon calories brÃ»lÃ©es (LT-01)."""

    @pytest.mark.asyncio
    async def test_recommandation_recharge_haute_activite(self, async_client: httpx.AsyncClient):
        """â‰¥600 kcal brÃ»lÃ©es â†’ stratÃ©gie recharge."""
        session, profil = _session_avec_profil()
        recette = SimpleNamespace(
            id=1, nom="Poulet riz", calories=700,
            categorie="Plat", temps_preparation=25,
        )
        mock_query = MagicMock()
        mock_query.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [recette]
        session.query.return_value = mock_query

        @contextmanager
        def _ctx():
            yield session

        with patch("src.core.db.obtenir_contexte_db", return_value=_ctx()):
            response = await async_client.get(
                "/api/v1/garmin/recommandation-diner?calories_brulees=700"
            )

        # Soit 200 (recette proposÃ©e) soit 200 avec message appropriÃ©
        assert response.status_code == 200
        data = response.json()
        assert "strategie" in data
        assert data["strategie"] == "recharge"

    @pytest.mark.asyncio
    async def test_recommandation_leger_faible_activite(self, async_client: httpx.AsyncClient):
        """0 kcal brÃ»lÃ©es â†’ stratÃ©gie lÃ©ger."""
        session, profil = _session_avec_profil()
        recette = SimpleNamespace(
            id=2, nom="Salade", calories=300,
            categorie="Salade", temps_preparation=10,
        )
        mock_query = MagicMock()
        mock_query.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [recette]
        session.query.return_value = mock_query

        @contextmanager
        def _ctx():
            yield session

        with patch("src.core.db.obtenir_contexte_db", return_value=_ctx()):
            response = await async_client.get(
                "/api/v1/garmin/recommandation-diner?calories_brulees=0"
            )

        assert response.status_code == 200
        data = response.json()
        assert "strategie" in data
        assert data["strategie"] == "leger"

    @pytest.mark.asyncio
    async def test_recommandation_sans_recette_message(self, async_client: httpx.AsyncClient):
        """Aucune recette en base â†’ message clair (pas de 500)."""
        session, profil = _session_avec_profil()
        mock_query = MagicMock()
        mock_query.filter.return_value.order_by.return_value.limit.return_value.all.return_value = []
        session.query.return_value = mock_query

        @contextmanager
        def _ctx():
            yield session

        with patch("src.core.db.obtenir_contexte_db", return_value=_ctx()):
            response = await async_client.get(
                "/api/v1/garmin/recommandation-diner?calories_brulees=400"
            )

        # Passe sans lever d'exception 500
        assert response.status_code in (200, 404)

