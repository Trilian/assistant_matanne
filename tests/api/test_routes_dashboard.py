"""Tests dédiés pour src/api/routes/dashboard.py."""

import httpx
import pytest
import pytest_asyncio
from fastapi import FastAPI

from src.api.dependencies import require_auth
from src.api.routes.dashboard import router

pytestmark = pytest.mark.asyncio(loop_scope="function")


@pytest_asyncio.fixture
async def client():
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[require_auth] = lambda: {"id": "test-user", "role": "admin"}

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
