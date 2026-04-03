"""Tests dédiés pour src/api/routes/maison_entretien.py."""

import httpx
import pytest
import pytest_asyncio
from fastapi import FastAPI

from src.api.dependencies import require_auth
from src.api.routes.maison_entretien import router

pytestmark = pytest.mark.asyncio(loop_scope="function")


@pytest_asyncio.fixture
async def client():
    app = FastAPI()
    app.include_router(router, prefix="/api/v1/maison")
    app.dependency_overrides[require_auth] = lambda: {"id": "test-user", "role": "admin"}

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


class TestRoutesMaisonEntretien:
    @pytest.mark.parametrize(
        "method,path,payload",
        [
            ("GET", "/api/v1/maison/routines", None),
            ("GET", "/api/v1/maison/routines/1", None),
            ("GET", "/api/v1/maison/entretien", None),
            ("POST", "/api/v1/maison/entretien", {"nom": "Nettoyer VMC"}),
            ("PATCH", "/api/v1/maison/entretien/1", {"fait": True}),
            ("DELETE", "/api/v1/maison/entretien/1", None),
            ("GET", "/api/v1/maison/entretien-saisonnier", None),
            ("POST", "/api/v1/maison/rappels/envoyer", None),
        ],
    )
    async def test_endpoints_existent(self, client, method, path, payload):
        func = getattr(client, method.lower())
        response = await func(path, json=payload) if payload is not None else await func(path)
        assert response.status_code not in (404, 405)
