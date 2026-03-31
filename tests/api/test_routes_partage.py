"""Tests dédiés pour src/api/routes/partage.py."""

import httpx
import pytest
import pytest_asyncio
from fastapi import FastAPI

from src.api.routes.partage import router

pytestmark = pytest.mark.asyncio(loop_scope="function")


@pytest_asyncio.fixture
async def client():
    app = FastAPI()
    app.include_router(router)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


class TestRoutesPartage:
    async def test_lien_partage_invalide(self, client):
        response = await client.get("/share/recette/token-invalide")
        assert response.status_code == 404

    async def test_endpoint_existe(self, client):
        # Le endpoint existe: il doit répondre mais pas 405.
        response = await client.get("/share/recette/token-test")
        assert response.status_code != 405
