"""
Tests de contrat pour les endpoints Telegram.

Valide la conformité des endpoints Telegram avec la spec OpenAPI,
et vérifie la shape des réponses.
"""

from __future__ import annotations

import httpx
import pytest

from src.api.main import app


TELEGRAM_BASE = "/api/v1/telegram"

TELEGRAM_ENDPOINTS = {
    f"{TELEGRAM_BASE}/envoyer-planning": "post",
    f"{TELEGRAM_BASE}/envoyer-courses": "post",
    f"{TELEGRAM_BASE}/envoyer-courses-magasin": "post",
    f"{TELEGRAM_BASE}/webhook": "post",
}


@pytest.mark.contract
@pytest.mark.asyncio(loop_scope="function")
async def test_contrat_endpoints_telegram_presents_dans_openapi() -> None:
    """Tous les endpoints Telegram sont déclarés dans la spec OpenAPI."""
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        spec_response = await client.get("/openapi.json")
        assert spec_response.status_code == 200

        spec = spec_response.json()
        paths = spec["paths"]

        for endpoint_path, method in TELEGRAM_ENDPOINTS.items():
            assert endpoint_path in paths, (
                f"Endpoint {endpoint_path} absent de la spec OpenAPI"
            )
            assert method in paths[endpoint_path], (
                f"Méthode {method.upper()} absente pour {endpoint_path}"
            )


@pytest.mark.contract
@pytest.mark.asyncio(loop_scope="function")
async def test_contrat_envoyer_planning_schema() -> None:
    """L'endpoint envoyer-planning a un schema de requête valide dans OpenAPI."""
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        spec_response = await client.get("/openapi.json")
        spec = spec_response.json()

        path = f"{TELEGRAM_BASE}/envoyer-planning"
        endpoint_spec = spec["paths"][path]["post"]

        # L'endpoint doit avoir un tag Telegram
        assert any("telegram" in t.lower() for t in endpoint_spec.get("tags", []))

        # Vérifier qu'il y a des réponses définies
        assert "responses" in endpoint_spec
        assert "200" in endpoint_spec["responses"] or "201" in endpoint_spec["responses"]


@pytest.mark.contract
@pytest.mark.asyncio(loop_scope="function")
async def test_contrat_envoyer_courses_schema() -> None:
    """L'endpoint envoyer-courses a un schema valide."""
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        spec_response = await client.get("/openapi.json")
        spec = spec_response.json()

        path = f"{TELEGRAM_BASE}/envoyer-courses"
        endpoint_spec = spec["paths"][path]["post"]

        assert "responses" in endpoint_spec


@pytest.mark.contract
@pytest.mark.asyncio(loop_scope="function")
async def test_contrat_webhook_schema() -> None:
    """L'endpoint webhook accepte les updates Telegram."""
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        spec_response = await client.get("/openapi.json")
        spec = spec_response.json()

        path = f"{TELEGRAM_BASE}/webhook"
        endpoint_spec = spec["paths"][path]["post"]

        assert "responses" in endpoint_spec


@pytest.mark.contract
@pytest.mark.asyncio(loop_scope="function")
async def test_contrat_envoyer_planning_reponse_401_sans_auth(monkeypatch) -> None:
    """L'envoi sans authentification retourne 401/403 (ou 422 de validation), jamais 500."""
    monkeypatch.setenv("ENVIRONMENT", "production")
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            f"{TELEGRAM_BASE}/envoyer-planning",
            json={"planning_id": 1},
        )
        assert response.status_code in {401, 403, 422}, (
            f"Attendu 401/403/422, reçu {response.status_code}"
        )


@pytest.mark.contract
@pytest.mark.asyncio(loop_scope="function")
async def test_contrat_envoyer_courses_reponse_401_sans_auth(monkeypatch) -> None:
    """L'envoi courses sans auth retourne 401 ou 403."""
    monkeypatch.setenv("ENVIRONMENT", "production")
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            f"{TELEGRAM_BASE}/envoyer-courses",
            json={},
        )
        assert response.status_code in {401, 403, 422}


@pytest.mark.contract
@pytest.mark.asyncio(loop_scope="function")
async def test_contrat_webhook_content_type_json() -> None:
    """Le webhook accepte du JSON et ne crash pas sur un body vide."""
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            f"{TELEGRAM_BASE}/webhook",
            json={"update_id": 0},
            headers={"Content-Type": "application/json"},
        )
        # Le webhook doit toujours répondre (même si l'update est invalide)
        assert response.status_code in {200, 400, 422}
        assert response.headers.get("content-type", "").startswith("application/json")
