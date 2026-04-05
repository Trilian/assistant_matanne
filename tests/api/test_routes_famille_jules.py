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

    async def test_creation_jalon_retourne_evenement_journal(self, client, monkeypatch):
        from datetime import date

        class _Enfant:
            id = 1

        class _Jalon:
            id = 15
            titre = "Premier pas"
            categorie = "motricite"
            date_atteint = date(2026, 4, 3)

        class _Query:
            def __init__(self, resultat):
                self._resultat = resultat

            def filter(self, *_args, **_kwargs):
                return self

            def first(self):
                return self._resultat

        class _Session:
            def __init__(self):
                self._calls = 0
                self._jalon = _Jalon()

            def query(self, *_args, **_kwargs):
                self._calls += 1
                return _Query(_Enfant() if self._calls == 1 else self._jalon)

            def add(self, _obj):
                return None

            def commit(self):
                return None

            def refresh(self, _obj):
                # La DB convertit normalement en date; on simule ce comportement.
                if hasattr(_obj, "date_atteint") and isinstance(_obj.date_atteint, str):
                    _obj.date_atteint = date.fromisoformat(_obj.date_atteint)
                return None

        @contextmanager
        def _session_fausse():
            yield _Session()

        class _Bus:
            def emettre(self, *_args, **_kwargs):
                return 1

        class _Bridge:
            def jalon_vers_evenement_familial(self, **_kwargs):
                return {"evenement_id": 99, "titre": "Jalon Jules: Premier pas"}

        monkeypatch.setattr("src.api.routes.famille_jules.executer_avec_session", _session_fausse)
        monkeypatch.setattr("src.services.core.events.obtenir_bus", lambda: _Bus())
        monkeypatch.setattr("src.services.ia.inter_modules.obtenir_service_bridges", lambda: _Bridge())

        response = await client.post(
            "/api/v1/famille/enfants/1/jalons",
            json={"titre": "Premier pas", "categorie": "motricite"},
        )

        assert response.status_code == 201
        assert response.json()["journal_evenement"]["evenement_id"] == 99

    async def test_jules_nutrition_retourne_recommandations_et_portions(self, client):
        """GET /jules/nutrition renvoie les recommandations, portions et aliments exclus."""

        class _ServiceNutrition:
            def adapter_planning_nutrition_jules(self, jours_horizon: int = 7):
                assert jours_horizon == 5
                return {
                    "age_mois": 19,
                    "recommandations": ["Limiter le sel", "Textures adaptées"],
                    "message": "Planning adapté pour Jules.",
                }

            def adapter_portions_recettes_planifiees(self, jours_horizon: int = 7):
                assert jours_horizon == 5
                return {
                    "portion_jules": 0.7,
                    "repas_mis_a_jour": 3,
                }

        pref = MagicMock()
        pref.aliments_exclus_jules = ["miel", "sel"]

        session = MagicMock()
        session.execute.return_value.scalar_one_or_none.return_value = pref

        @contextmanager
        def _session_fausse():
            yield session

        with patch(
            "src.api.routes.famille_jules.executer_avec_session",
            _session_fausse,
        ), patch(
            "src.services.cuisine.inter_module_jules_nutrition.obtenir_service_jules_nutrition_interaction",
            lambda: _ServiceNutrition(),
        ):
            response = await client.get("/api/v1/famille/jules/nutrition?jours_horizon=5")

        assert response.status_code == 200
        data = response.json()
        assert data["age_mois"] == 19
        assert data["recommandations"] == ["Limiter le sel", "Textures adaptées"]
        assert data["portions"]["portion_jules"] == 0.7
        assert data["portions"]["repas_mis_a_jour"] == 3
        assert data["aliments_exclus"] == ["miel", "sel"]
        assert "adapté" in data["message"].lower()


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
