"""Tests dédiés pour src/api/routes/maison_finances.py."""

import httpx
import pytest
import pytest_asyncio
from fastapi import FastAPI

from src.api.dependencies import require_auth
from src.api.routes.maison_finances import router

pytestmark = pytest.mark.asyncio(loop_scope="function")


@pytest_asyncio.fixture
async def client():
    app = FastAPI()
    app.include_router(router, prefix="/api/v1/maison")
    app.dependency_overrides[require_auth] = lambda: {"id": "test-user", "role": "admin"}

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


class TestRoutesMaisonFinances:
    @pytest.mark.parametrize(
        "method,path,payload",
        [
            ("GET", "/api/v1/maison/artisans", None),
            ("GET", "/api/v1/maison/artisans/stats", None),
            ("POST", "/api/v1/maison/artisans", {"nom": "Artisan Test", "metier": "plombier"}),
            ("GET", "/api/v1/maison/contrats", None),
            ("GET", "/api/v1/maison/contrats/alertes", None),
            ("POST", "/api/v1/maison/contrats", {"nom": "Assurance", "type_contrat": "assurance"}),
            ("GET", "/api/v1/maison/garanties", None),
            ("GET", "/api/v1/maison/garanties/stats", None),
        ],
    )
    async def test_endpoints_existent(self, client, method, path, payload):
        func = getattr(client, method.lower())
        response = await func(path, json=payload) if payload is not None else await func(path)
        assert response.status_code not in (404, 405)
