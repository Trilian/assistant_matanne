"""Tests de contrat OpenAPI (contrat OpenAPI).

Valide le endpoint public `/health` directement contre la spec OpenAPI
servie par l'application ASGI, sans dépendre d'une lib externe optionnelle.
"""

from __future__ import annotations

import httpx
import pytest

from src.api.main import app


@pytest.mark.contract
@pytest.mark.asyncio(loop_scope="function")
async def test_contrat_endpoint_health() -> None:
    """Le endpoint `/health` est présent dans la spec et conforme à la réponse réelle."""
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        spec_response = await client.get("/openapi.json")
        assert spec_response.status_code == 200

        spec = spec_response.json()
        assert "/health" in spec["paths"]
        assert "get" in spec["paths"]["/health"]

        response = await client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] in {"healthy", "degraded", "unhealthy"}
        assert "version" in data
        assert "services" in data
        assert "database" in data["services"]
        assert "timestamp" in data
        assert "uptime_seconds" in data
