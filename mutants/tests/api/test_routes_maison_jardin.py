"""Tests dédiés pour src/api/routes/maison_jardin.py."""

from contextlib import contextmanager

import httpx
import pytest
import pytest_asyncio
from fastapi import FastAPI

from src.api.dependencies import require_auth
from src.api.routes.maison_jardin import router

pytestmark = pytest.mark.asyncio(loop_scope="function")


@pytest_asyncio.fixture
async def client():
    app = FastAPI()
    app.include_router(router, prefix="/api/v1/maison")
    app.dependency_overrides[require_auth] = lambda: {"id": "test-user", "role": "admin"}

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


class TestRoutesMaisonJardin:
    @pytest.mark.parametrize(
        "method,path,payload",
        [
            ("GET", "/api/v1/maison/jardin", None),
            ("GET", "/api/v1/maison/jardin/1/journal", None),
            ("POST", "/api/v1/maison/jardin", {"nom": "Tomates"}),
            ("PATCH", "/api/v1/maison/jardin/1", {"statut": "recolte"}),
            ("DELETE", "/api/v1/maison/jardin/1", None),
            ("GET", "/api/v1/maison/stocks", None),
            ("POST", "/api/v1/maison/stocks", {"nom": "Ampoules", "quantite": 4}),
            ("PATCH", "/api/v1/maison/stocks/1", {"quantite": 3}),
            ("DELETE", "/api/v1/maison/stocks/1", None),
        ],
    )
    async def test_endpoints_existent(self, client, method, path, payload):
        func = getattr(client, method.lower())
        response = await func(path, json=payload) if payload is not None else await func(path)
        assert response.status_code not in (404, 405)

    async def test_patch_recolte_declenche_bridge_inventaire(self, client, monkeypatch):
        @contextmanager
        def _session_fausse():
            class _Element:
                id = 7
                nom = "Tomates"
                type = "legume"
                statut = "actif"

            class _Query:
                def filter(self, *_args, **_kwargs):
                    return self

                def first(self):
                    return _Element()

            class _Session:
                def query(self, *_args, **_kwargs):
                    return _Query()

                def commit(self):
                    return None

                def refresh(self, _obj):
                    return None

            yield _Session()

        class _Bridge:
            def recolte_vers_stock_inventaire(self, **_kwargs):
                return {"article_inventaire_id": 12, "action": "creation"}

        monkeypatch.setattr("src.api.routes.maison_jardin.executer_avec_session", _session_fausse)
        monkeypatch.setattr("src.services.ia.bridges.obtenir_service_bridges", lambda: _Bridge())

        response = await client.patch(
            "/api/v1/maison/jardin/7",
            json={"statut": "recolte", "quantite_recoltee": 2},
        )

        assert response.status_code == 200
        assert response.json()["bridge_inventaire"]["article_inventaire_id"] == 12
