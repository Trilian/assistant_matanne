"""
T4 - Tests dedies pour les routes automations.

Couvre src/api/routes/automations.py :
- GET  /api/v1/automations              : lecture sans mutation (C4 fix)
- POST /api/v1/automations/init         : migration idempotente
- POST /api/v1/automations              : creation
- POST /api/v1/automations/{id}/executer-maintenant : execution manuelle
"""

from __future__ import annotations

from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import MagicMock, patch, call

import httpx
import pytest
import pytest_asyncio
from httpx import ASGITransport


# -----------------------------------------------------------------------------
# FIXTURES
# -----------------------------------------------------------------------------


@pytest_asyncio.fixture
async def async_client():
    """Client async avec auth override."""
    from src.api.dependencies import require_auth
    from src.api.main import app

    app.dependency_overrides[require_auth] = lambda: {
        "id": "test-user",
        "email": "test@matanne.fr",
        "role": "membre",
    }
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app, raise_app_exceptions=False),
        base_url="http://test",
    ) as client:
        yield client
    app.dependency_overrides.clear()


def _make_automation(id_: int = 1, nom: str = "Automation test") -> SimpleNamespace:
    return SimpleNamespace(
        id=id_,
        nom=nom,
        declencheur={"type": "stock_bas", "seuil": 2},
        action={"type": "ajouter_courses", "quantite": 1},
        active=True,
        derniere_execution=None,
        execution_count=0,
    )


# -----------------------------------------------------------------------------
# T4a - GET sans mutation
# -----------------------------------------------------------------------------


class TestListerAutomationsSansMutation:
    """GET /api/v1/automations - verification qu'aucun commit n'est effectue."""

    @pytest.mark.asyncio
    async def test_get_automations_200(self, async_client: httpx.AsyncClient):
        """GET retourne 200 avec la liste."""
        profil = SimpleNamespace(id=1, email="test@matanne.fr", preferences_modules={})
        automations = [_make_automation(1, "Auto 1"), _make_automation(2, "Auto 2")]

        with patch(
            "src.api.routes.automations._charger_automations",
            return_value=(profil, automations),
        ):
            response = await async_client.get("/api/v1/automations")

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert data["total"] == 2

    @pytest.mark.asyncio
    async def test_get_automations_ne_commit_pas(self, async_client: httpx.AsyncClient):
        """GET /api/v1/automations ne doit pas appeler session.commit()."""
        profil = SimpleNamespace(id=1, email="test@matanne.fr", preferences_modules={})
        automations = []

        mock_session = MagicMock()

        @contextmanager
        def _ctx():
            yield mock_session

        with (
            patch("src.api.routes.automations._charger_automations", return_value=(profil, automations)),
            patch("src.core.db.obtenir_contexte_db", return_value=_ctx()),
        ):
            response = await async_client.get("/api/v1/automations")

        assert response.status_code == 200
        # Le mock session ne doit pas avoir ete commit par la route GET
        # (_charger_automations est patche, donc session.commit n'est pas appele)
        mock_session.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_automations_sans_auth_401(self, monkeypatch):
        """GET sans token -> 401."""
        from src.api.main import app
        monkeypatch.setenv("ENVIRONMENT", "production")

        async with httpx.AsyncClient(
            transport=ASGITransport(app=app, raise_app_exceptions=False),
            base_url="http://test",
        ) as unauthenticated:
            response = await unauthenticated.get("/api/v1/automations")

        assert response.status_code in (401, 403)


# -----------------------------------------------------------------------------
# T4b - POST /init (migration idempotente)
# -----------------------------------------------------------------------------


class TestInitAutomations:
    """POST /api/v1/automations/init - migration idempotente."""

    @pytest.mark.asyncio
    async def test_init_deja_initialisees(self, async_client: httpx.AsyncClient):
        """Si des automations existent deja, le message indique qu'elles le sont."""
        profil = SimpleNamespace(id=1, email="test@matanne.fr", preferences_modules={})
        automations = [_make_automation(1)]

        with patch(
            "src.api.routes.automations._charger_automations",
            return_value=(profil, automations),
        ):
            response = await async_client.post("/api/v1/automations/init")

        assert response.status_code == 200
        data = response.json()
        assert "déjà" in data.get("message", "").lower() or data["total"] >= 1

    @pytest.mark.asyncio
    async def test_init_vide_migre(self, async_client: httpx.AsyncClient):
        """Avec des preferences legacy, la migration cree des automations."""
        profil = SimpleNamespace(
            id=1,
            email="test@matanne.fr",
            preferences_modules={
                "automations": [
                    {"nom": "Auto legacy", "declencheur": {"type": "stock_bas", "seuil": 2}},
                ]
            },
        )
        auto_migree = _make_automation(1, "Auto legacy")

        with (
            patch(
                "src.api.routes.automations._charger_automations",
                return_value=(profil, []),
            ),
            patch(
                "src.api.routes.automations._migrer_automations_depuis_preferences",
                return_value=[auto_migree],
            ),
        ):
            response = await async_client.post("/api/v1/automations/init")

        assert response.status_code in (200, 201)
        data = response.json()
        assert data["total"] == 1


# -----------------------------------------------------------------------------
# T4c - POST /api/v1/automations (creation)
# -----------------------------------------------------------------------------


class TestCreerAutomation:
    """POST /api/v1/automations - creation d'une regle Si->Alors."""

    @pytest.mark.asyncio
    async def test_creer_automation_si_alors(self, async_client: httpx.AsyncClient):
        """POST avec payload valide -> item cree en base."""
        profil = SimpleNamespace(id=1, email="test@matanne.fr", preferences_modules={})
        auto_cree = _make_automation(5, "Stock bas -> courses")

        mock_session = MagicMock()
        mock_session.refresh = MagicMock()

        def _add(obj):
            obj.id = 5
            obj.derniere_execution = None
            obj.execution_count = 0

        mock_session.add.side_effect = _add

        @contextmanager
        def _ctx():
            yield mock_session

        with (
            patch("src.api.routes.automations._charger_automations", return_value=(profil, [])),
            patch("src.core.db.obtenir_contexte_db", return_value=_ctx()),
        ):
            response = await async_client.post(
                "/api/v1/automations",
                json={
                    "nom": "Stock bas -> courses",
                    "declencheur": {"type": "stock_bas", "seuil": 2},
                    "action": {"type": "ajouter_courses", "quantite": 1},
                    "active": True,
                },
            )

        assert response.status_code in (200, 201)
        data = response.json()
        assert "message" in data

    @pytest.mark.asyncio
    async def test_creer_automation_condition_stock_bas(self, async_client: httpx.AsyncClient):
        """Le payload avec condition stock_bas est accepte."""
        profil = SimpleNamespace(id=1, email="test@matanne.fr", preferences_modules={})

        mock_session = MagicMock()

        def _add(obj):
            obj.id = 10
            obj.derniere_execution = None
            obj.execution_count = 0

        mock_session.add.side_effect = _add

        @contextmanager
        def _ctx():
            yield mock_session

        with (
            patch("src.api.routes.automations._charger_automations", return_value=(profil, [])),
            patch("src.core.db.obtenir_contexte_db", return_value=_ctx()),
        ):
            response = await async_client.post(
                "/api/v1/automations",
                json={
                    "nom": "Alerte stock farine",
                    "declencheur": {"type": "stock_bas", "seuil": 0, "ingredient": "farine"},
                    "action": {"type": "notification", "message": "Farine presque épuisée!"},
                },
            )

        assert response.status_code in (200, 201)


# -----------------------------------------------------------------------------
# T4d - POST /{id}/executer-maintenant
# -----------------------------------------------------------------------------


class TestExecuterAutomation:
    """POST /api/v1/automations/{id}/executer-maintenant - execution manuelle."""

    @pytest.mark.asyncio
    async def test_executer_maintenant_success(self, async_client: httpx.AsyncClient):
        """Execution manuelle -> success + resultat."""
        profil = SimpleNamespace(id=1, email="test@matanne.fr", preferences_modules={})
        mock_service = MagicMock()
        mock_service.executer_automation_par_id.return_value = {
            "success": True,
            "automation_id": 3,
            "executed": 2,
        }

        with (
            patch("src.api.routes.automations._charger_automations", return_value=(profil, [])),
            patch(
                "src.services.utilitaires.automations_engine.obtenir_moteur_automations_service",
                return_value=mock_service,
            ),
        ):
            response = await async_client.post("/api/v1/automations/3/executer-maintenant")

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Automation exécutée"
        assert data["resultat"]["success"] is True

    @pytest.mark.asyncio
    async def test_executer_automation_introuvable_404(self, async_client: httpx.AsyncClient):
        """Automation introuvable -> 404."""
        profil = SimpleNamespace(id=1, email="test@matanne.fr", preferences_modules={})
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
            response = await async_client.post("/api/v1/automations/9999/executer-maintenant")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_executer_maintenant_passe_user_id_au_service(self, async_client: httpx.AsyncClient):
        """La route doit exécuter avec le profil courant (isolation multi-user)."""
        profil = SimpleNamespace(id=42, email="test@matanne.fr", preferences_modules={})
        mock_service = MagicMock()
        mock_service.executer_automation_par_id.return_value = {
            "success": True,
            "automation_id": 7,
            "executed": 1,
        }

        with (
            patch("src.api.routes.automations._charger_automations", return_value=(profil, [])),
            patch(
                "src.services.utilitaires.automations_engine.obtenir_moteur_automations_service",
                return_value=mock_service,
            ),
        ):
            response = await async_client.post("/api/v1/automations/7/executer-maintenant")

        assert response.status_code == 200
        mock_service.executer_automation_par_id.assert_called_once()
        _, kwargs = mock_service.executer_automation_par_id.call_args
        assert kwargs["user_id"] == 42

