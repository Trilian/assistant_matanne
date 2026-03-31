"""Tests dédiés pour src/api/routes/famille_jules.py."""

import httpx
import pytest
import pytest_asyncio
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
