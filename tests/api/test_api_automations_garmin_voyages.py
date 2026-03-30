"""
Tests API cibles Sprint 10.

Couvre:
- POST /api/v1/automations/{id}/executer-maintenant
- GET  /api/v1/garmin/recommandation-diner
- POST /api/v1/famille/voyages/{id}/generer-courses
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock, patch

import httpx
import pytest
import pytest_asyncio
from httpx import ASGITransport


@pytest_asyncio.fixture
async def async_client():
    """Client async avec auth override membre."""
    from src.api.dependencies import require_auth
    from src.api.main import app

    app.dependency_overrides[require_auth] = lambda: {"id": "test-user", "role": "membre"}
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app, raise_app_exceptions=False),
        base_url="http://test",
    ) as client:
        yield client
    app.dependency_overrides.clear()


class TestAutomationsExecuterMaintenant:
    """Tests endpoint execution manuelle d'automation (LT-04)."""

    @pytest.mark.asyncio
    async def test_executer_automation_success(self, async_client: httpx.AsyncClient):
        profil = SimpleNamespace(id=42)
        mock_service = MagicMock()
        mock_service.executer_automation_par_id.return_value = {
            "success": True,
            "automation_id": 7,
            "executed": 2,
        }

        with (
            patch("src.api.routes.automations._charger_automations", return_value=(profil, [])),
            patch(
                "src.services.utilitaires.automations_engine.obtenir_moteur_automations_service",
                return_value=mock_service,
            ),
        ):
            response = await async_client.post("/api/v1/automations/7/executer-maintenant")

        assert response.status_code == 200, response.text
        data = response.json()
        assert data["message"] == "Automation exécutée"
        assert data["user_id"] == 42
        assert data["resultat"]["success"] is True

    @pytest.mark.asyncio
    async def test_executer_automation_introuvable(self, async_client: httpx.AsyncClient):
        profil = SimpleNamespace(id=42)
        mock_service = MagicMock()
        mock_service.executer_automation_par_id.return_value = {
            "success": False,
            "message": "Automation introuvable",
        }

        with (
            patch("src.api.routes.automations._charger_automations", return_value=(profil, [])),
            patch(
                "src.services.utilitaires.automations_engine.obtenir_moteur_automations_service",
                return_value=mock_service,
            ),
        ):
            response = await async_client.post("/api/v1/automations/999/executer-maintenant")

        assert response.status_code == 404


class TestGarminRecommandationDiner:
    """Tests endpoint recommandation diner selon calories brulees (LT-01)."""

    @pytest.mark.asyncio
    async def test_recommandation_diner_success(self, async_client: httpx.AsyncClient):
        recette1 = SimpleNamespace(
            id=1,
            nom="Poulet riz",
            calories=640,
            categorie="Plat",
            temps_preparation=25,
        )
        recette2 = SimpleNamespace(
            id=2,
            nom="Bowl saumon",
            calories=590,
            categorie="Plat",
            temps_preparation=20,
        )

        class FakeQuery:
            def filter(self, *args: Any, **kwargs: Any) -> FakeQuery:
                return self

            def order_by(self, *args: Any, **kwargs: Any) -> FakeQuery:
                return self

            def limit(self, *args: Any, **kwargs: Any) -> FakeQuery:
                return self

            def all(self) -> list[SimpleNamespace]:
                return [recette1, recette2]

        mock_session = MagicMock()
        mock_session.query.return_value = FakeQuery()

        @contextmanager
        def fake_session_ctx() -> Iterator[MagicMock]:
            yield mock_session

        with patch("src.api.routes.garmin.executer_avec_session", side_effect=fake_session_ctx):
            response = await async_client.get("/api/v1/garmin/recommandation-diner?calories_brulees=420")

        assert response.status_code == 200, response.text
        data = response.json()
        assert data["strategie"] == "equilibre"
        assert len(data["items"]) == 2
        assert data["items"][0]["nom"] == "Poulet riz"

    @pytest.mark.asyncio
    async def test_recommandation_diner_validation_query(self, async_client: httpx.AsyncClient):
        response = await async_client.get("/api/v1/garmin/recommandation-diner?calories_brulees=4001")
        assert response.status_code == 422


class TestVoyagesGenererCourses:
    """Tests endpoint generation courses depuis voyage (LT-03)."""

    @pytest.mark.asyncio
    async def test_generer_courses_success(self, async_client: httpx.AsyncClient):
        mock_service = MagicMock()
        mock_service.obtenir_voyage.return_value = SimpleNamespace(id=12)
        mock_service.generer_courses_depuis_checklists.return_value = 3

        with patch(
            "src.services.famille.voyage.obtenir_service_voyage",
            return_value=mock_service,
        ):
            response = await async_client.post("/api/v1/famille/voyages/12/generer-courses")

        assert response.status_code == 200, response.text
        data = response.json()
        assert data["voyage_id"] == 12
        assert data["articles_ajoutes"] == 3

    @pytest.mark.asyncio
    async def test_generer_courses_voyage_introuvable(self, async_client: httpx.AsyncClient):
        mock_service = MagicMock()
        mock_service.obtenir_voyage.return_value = None

        with patch(
            "src.services.famille.voyage.obtenir_service_voyage",
            return_value=mock_service,
        ):
            response = await async_client.post("/api/v1/famille/voyages/404/generer-courses")

        assert response.status_code == 404

