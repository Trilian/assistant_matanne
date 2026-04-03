"""Tests dédiés pour src/api/routes/famille_jules.py."""

import httpx
import pytest
import pytest_asyncio
from contextlib import contextmanager
from unittest.mock import MagicMock, patch
from fastapi import FastAPI

from src.api.dependencies import require_auth
from src.api.routes.famille_jules import router

pytestmark = pytest.mark.asyncio(loop_scope="function")


@pytest_asyncio.fixture
async def client():
    app = FastAPI()
    app.include_router(router, prefix="/api/v1/famille")
    app.dependency_overrides[require_auth] = lambda: {"id": "test-user", "role": "admin"}

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


class TestRoutesFamilleJules:
    @pytest.mark.parametrize(
        "method,path,payload",
        [
            ("GET", "/api/v1/famille/enfants", None),
            ("GET", "/api/v1/famille/enfants/1", None),
            ("GET", "/api/v1/famille/enfants/1/jalons", None),
            (
                "POST",
                "/api/v1/famille/enfants/1/jalons",
                {"titre": "Premier mot", "categorie": "langage"},
            ),
            ("DELETE", "/api/v1/famille/enfants/1/jalons/1", None),
            ("GET", "/api/v1/famille/jules/croissance", None),
            (
                "POST",
                "/api/v1/famille/activites/suggestions-ia-auto",
                {"age_mois": 36, "meteo": "soleil"},
            ),
        ],
    )
    async def test_endpoints_existent(self, client, method, path, payload):
        func = getattr(client, method.lower())
        response = await func(path, json=payload) if payload is not None else await func(path)
        assert response.status_code not in (404, 405)


class TestTimelineEnrichieJardin:
    """Timeline familiale — vérification de l'enrichissement avec le journal jardin."""

    @pytest_asyncio.fixture
    async def client(self):
        app = FastAPI()
        app.include_router(router, prefix="/api/v1/famille")
        app.dependency_overrides[require_auth] = lambda: {"id": "test-user", "role": "admin"}
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
            yield c

    @pytest.fixture(autouse=True)
    def mock_session_vide(self):
        """Remplace executer_avec_session par une session retournant des listes vides."""
        mock_session = MagicMock()
        mock_session.query.return_value.order_by.return_value.limit.return_value.all.return_value = []
        mock_session.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = []
        mock_session.query.return_value.filter.return_value.first.return_value = None

        @contextmanager
        def mock_executer_avec_session():
            yield mock_session

        with patch("src.api.routes.famille_jules.executer_avec_session", mock_executer_avec_session):
            yield

    async def test_timeline_retourne_structure_valide(self, client):
        """La timeline répond 200 et retourne items/total/filtres."""
        response = await client.get("/api/v1/famille/timeline")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert isinstance(data["items"], list)
        assert data["total"] == len(data["items"])

    async def test_timeline_filtre_categorie_maison(self, client):
        """Le filtre categorie=maison répond 200 avec liste cohérente."""
        response = await client.get("/api/v1/famille/timeline?categorie=maison")
        assert response.status_code == 200
        items = response.json()["items"]
        for item in items:
            assert item["categorie"] == "maison"

    async def test_timeline_items_jardin_ont_meta_jardinage(self, client):
        """Les items jardin dans la timeline ont meta.type='jardinage' (avec données mockées)."""
        from datetime import date
        from unittest.mock import MagicMock

        # Données factices représentant un JournalJardin
        log_mock = MagicMock()
        log_mock.id = 42
        log_mock.action = "Arrosage"
        log_mock.notes = "Arrosage du potager"
        log_mock.date = date(2026, 4, 1)
        log_mock.garden_item = None
        log_mock.garden_item_id = None

        mock_session = MagicMock()
        # retourne [log_mock] pour le query JournalJardin
        mock_session.query.return_value.order_by.return_value.limit.return_value.all.return_value = [log_mock]
        mock_session.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = []
        mock_session.query.return_value.filter.return_value.first.return_value = None

        @contextmanager
        def mock_session_jardin():
            yield mock_session

        # La fixture autouse mock_session_vide est déjà appliquée — on réapplique pour remplacer
        with patch("src.api.routes.famille_jules.executer_avec_session", mock_session_jardin):
            response = await client.get("/api/v1/famille/timeline?categorie=maison")

        assert response.status_code == 200
        items = response.json()["items"]
        jardin_items = [it for it in items if it.get("id", "").startswith("jardin-")]
        for item in jardin_items:
            assert item["meta"]["type"] == "jardinage"
            assert "action" in item["meta"]
            assert item["titre"].startswith("Jardin:")

    async def test_timeline_filtre_categorie_jules(self, client):
        """Le filtre categorie=jules répond 200."""
        response = await client.get("/api/v1/famille/timeline?categorie=jules")
        assert response.status_code == 200
        items = response.json()["items"]
        for item in items:
            assert item["categorie"] == "jules"

    async def test_timeline_limite_respectee(self, client):
        """Le paramètre limite est respecté."""
        response = await client.get("/api/v1/famille/timeline?limite=5")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) <= 5
