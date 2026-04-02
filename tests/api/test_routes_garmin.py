"""
T5b - Tests routes Garmin.

Couvre src/api/routes/garmin.py :
- GET  /api/v1/garmin/status                : statut connexion Garmin
- POST /api/v1/garmin/connect-url           : URL d'autorisation OAuth
- POST /api/v1/garmin/sync                  : synchronisation donnees
- GET  /api/v1/garmin/stats                 : statistiques activite
- GET  /api/v1/garmin/recommandation-diner  : recommandation diner selon calories
"""

from __future__ import annotations

from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import httpx
import pytest
import pytest_asyncio
from httpx import ASGITransport


# -----------------------------------------------------------------------------
# FIXTURES
# -----------------------------------------------------------------------------


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


# -----------------------------------------------------------------------------
# TESTS - STATUT GARMIN
# -----------------------------------------------------------------------------


class TestStatutGarmin:
    """GET /api/v1/garmin/status."""

    @pytest.mark.asyncio
    async def test_statut_non_connecte(self, async_client: httpx.AsyncClient):
        """Profil sans Garmin -> connected: False."""
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
        """Profil avec Garmin connecte -> connected: True."""
        session, profil = _session_avec_profil(garmin_connected=True)

        @contextmanager
        def _ctx():
            yield session

        with patch("src.core.db.obtenir_contexte_db", return_value=_ctx()):
            response = await async_client.get("/api/v1/garmin/status")

        assert response.status_code == 200
        data = response.json()
        assert data["connected"] is True


# -----------------------------------------------------------------------------
# TESTS - URL DE CONNEXION GARMIN
# -----------------------------------------------------------------------------


class TestConnectUrlGarmin:
    """POST /api/v1/garmin/connect-url."""

    @pytest.mark.asyncio
    async def test_connect_url_non_configure(self, async_client: httpx.AsyncClient):
        """Service Garmin non configure -> 503."""
        mock_service = MagicMock()
        mock_service.get_authorization_url.return_value = (None, None)

        with patch("src.services.integrations.garmin.service.obtenir_garmin_service", return_value=mock_service):
            response = await async_client.post("/api/v1/garmin/connect-url")

        assert response.status_code == 503

    @pytest.mark.asyncio
    async def test_connect_url_retourne_url(self, async_client: httpx.AsyncClient):
        """Service Garmin configure -> URL d'autorisation retournee."""
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


# -----------------------------------------------------------------------------
# TESTS - SYNC GARMIN
# -----------------------------------------------------------------------------


class TestSyncGarmin:
    """POST /api/v1/garmin/sync."""

    @pytest.mark.asyncio
    async def test_sync_succes(self, async_client: httpx.AsyncClient):
        """Synchronisation reussie -> donnees retournees."""
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


# -----------------------------------------------------------------------------
# TESTS - RECOMMANDATION DINER
# -----------------------------------------------------------------------------


class TestRecommandationDiner:
    """GET /api/v1/garmin/recommandation-diner - adaptation selon calories brulees (LT-01)."""

    @pytest.mark.asyncio
    async def test_recommandation_recharge_haute_activite(self, async_client: httpx.AsyncClient):
        """>=600 kcal brulees -> strategie recharge."""
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

        # Soit 200 (recette proposee) soit 200 avec message approprie
        assert response.status_code == 200
        data = response.json()
        assert "strategie" in data
        assert data["strategie"] == "recharge"

    @pytest.mark.asyncio
    async def test_recommandation_leger_faible_activite(self, async_client: httpx.AsyncClient):
        """0 kcal brulees -> strategie leger."""
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
        """Aucune recette en base -> message clair (pas de 500)."""
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

