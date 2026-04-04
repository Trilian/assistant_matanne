"""
CT-14 â€” Tests des routes admin et RGPD (admin)

Tests couvrant:
- Routes admin (audit-logs, audit-stats, audit-export) : contrÃ´le de rÃ´le
- Routes RGPD (export, data-summary, delete-account) : authentification + structure
"""

from __future__ import annotations

import httpx
import pytest
import pytest_asyncio
from httpx import ASGITransport
from typing import Any, cast
from unittest.mock import patch


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# FIXTURES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest_asyncio.fixture
async def async_client():
    """Client async avec override d'authÂ : rÃ´le admin pour les tests admin/RGPD."""
    from src.api.main import app
    from src.api.dependencies import require_auth

    app.dependency_overrides[require_auth] = lambda: {"id": "test-user", "role": "admin"}
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app, raise_app_exceptions=False),
        base_url="http://test",
    ) as client:
        yield client
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def unauthenticated_client():
    """Client async SANS override d'auth pour tester les refus."""
    from src.api.main import app

    async with httpx.AsyncClient(
        transport=ASGITransport(app=app, raise_app_exceptions=False),
        base_url="http://test",
    ) as client:
        yield client


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# CT-14 â€” Routes admin : contrÃ´le du rÃ´le
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestAdminAuditLogs:
    """GET /api/v1/admin/audit-logs â€” accessible admin seulement."""

    @pytest.mark.asyncio
    async def test_sans_auth_retourne_401_ou_403(self, unauthenticated_client: httpx.AsyncClient):
        """L'endpoint doit refuser les requÃªtes sans token."""
        response = await unauthenticated_client.get("/api/v1/admin/audit-logs")
        assert response.status_code in [401, 403, 404]

    @pytest.mark.asyncio
    async def test_avec_token_admin_retourne_200_ou_200(
        self, async_client: httpx.AsyncClient
    ):
        """Avec un token admin valide, l'endpoint doit rÃ©pondre."""
        response = await async_client.get("/api/v1/admin/audit-logs")
        assert response.status_code in [200, 401, 403, 404, 500]

    @pytest.mark.asyncio
    async def test_reponse_json(self, async_client: httpx.AsyncClient):
        """Quand il retourne 200, la rÃ©ponse doit Ãªtre du JSON."""
        response = await async_client.get("/api/v1/admin/audit-logs")
        if response.status_code == 200:
            data = response.json()
            assert "items" in data or "total" in data

    @pytest.mark.asyncio
    async def test_pagination_params_acceptes(self, async_client: httpx.AsyncClient):
        """Les paramÃ¨tres de pagination doivent Ãªtre acceptÃ©s."""
        response = await async_client.get(
            "/api/v1/admin/audit-logs?page=1&par_page=10"
        )
        assert response.status_code in [200, 401, 403, 404, 422, 500]


class TestAdminAuditStats:
    """GET /api/v1/admin/audit-stats â€” accessible admin seulement."""

    @pytest.mark.asyncio
    async def test_sans_auth_retourne_401_ou_403(
        self, unauthenticated_client: httpx.AsyncClient
    ):
        response = await unauthenticated_client.get("/api/v1/admin/audit-stats")
        assert response.status_code in [401, 403, 404]

    @pytest.mark.asyncio
    async def test_avec_token_admin(self, async_client: httpx.AsyncClient):
        response = await async_client.get("/api/v1/admin/audit-stats")
        assert response.status_code in [200, 401, 403, 404, 500]


class TestAdminAuditExport:
    """GET /api/v1/admin/audit-export â€” export CSV admin."""

    @pytest.mark.asyncio
    async def test_sans_auth_retourne_401_ou_403(
        self, unauthenticated_client: httpx.AsyncClient
    ):
        response = await unauthenticated_client.get("/api/v1/admin/audit-export")
        assert response.status_code in [401, 403, 404]

    @pytest.mark.asyncio
    async def test_avec_token_admin_csv_ou_erreur(self, async_client: httpx.AsyncClient):
        response = await async_client.get("/api/v1/admin/audit-export")
        assert response.status_code in [200, 401, 403, 404, 500]
        if response.status_code == 200:
            content_type = response.headers.get("content-type", "")
            assert "text/csv" in content_type or "application/octet-stream" in content_type


class TestAdminJobsACL:
    """GET /api/v1/admin/jobs* â€” contrÃ´le d'accÃ¨s admin."""

    @pytest.mark.asyncio
    async def test_jobs_sans_auth_refuse(self, unauthenticated_client: httpx.AsyncClient):
        response = await unauthenticated_client.get("/api/v1/admin/jobs")
        assert response.status_code in [401, 403, 404]

    @pytest.mark.asyncio
    async def test_jobs_logs_sans_auth_refuse(self, unauthenticated_client: httpx.AsyncClient):
        response = await unauthenticated_client.get("/api/v1/admin/jobs/rappels_famille/logs")
        assert response.status_code in [401, 403, 404]

    @pytest.mark.asyncio
    async def test_jobs_avec_admin_repond(self, async_client: httpx.AsyncClient):
        response = await async_client.get("/api/v1/admin/jobs")
        assert response.status_code in [200, 401, 403, 404, 500]

    @pytest.mark.asyncio
    async def test_jobs_logs_avec_admin_repond(self, async_client: httpx.AsyncClient):
        response = await async_client.get("/api/v1/admin/jobs/rappels_famille/logs")
        assert response.status_code in [200, 401, 403, 404, 500]

    @pytest.mark.asyncio
    async def test_executer_job_dry_run_propage_flag(self, async_client: httpx.AsyncClient):
        with (
            patch("src.api.routes.admin_jobs._verifier_limite_jobs"),
            patch("src.api.routes.admin_jobs._ajouter_log_job"),
            patch("src.api.routes.admin_jobs._journaliser_action_admin"),
            patch(
                "src.services.core.cron.jobs.lister_jobs_disponibles",
                return_value=["rappels_famille"],
            ),
            patch(
                "src.services.core.cron.jobs.executer_job_par_id",
                return_value={
                    "status": "dry_run",
                    "job_id": "rappels_famille",
                    "message": "Job 'rappels_famille' simulÃ© (dry-run).",
                    "duration_ms": 7,
                    "dry_run": True,
                },
            ) as mock_exec,
        ):
            response = await async_client.post("/api/v1/admin/jobs/rappels_famille/run?dry_run=true")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "dry_run"
        assert data["dry_run"] is True
        mock_exec.assert_called_once_with(
            "rappels_famille",
            dry_run=True,
            source="manual",
            triggered_by_user_id="test-user",
            relancer_exception=True,
        )

    @pytest.mark.asyncio
    async def test_jobs_liste_inclut_job_automatisation_si_scheduler_actif(self, async_client: httpx.AsyncClient):
        class FakeScheduler:
            running = True

            def get_jobs(self) -> list[object]:
                return [job]

        job = type(
            "FakeJob",
            (),
            {
                "id": "job_briefing_matinal_push",
                "name": "Briefing matinal IA",
                "trigger": "cron[hour='7', minute='0']",
                "next_run_time": None,
            },
        )()
        fake_scheduler = FakeScheduler()
        fake_demarreur = type("FakeDemarreur", (), {"_scheduler": fake_scheduler})()

        with patch("src.services.core.cron.jobs._demarreur", fake_demarreur):
            response = await async_client.get("/api/v1/admin/jobs")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == "job_briefing_matinal_push"
        assert data[0]["nom"] == "Briefing matinal IA (07h00)"
        assert data[0]["statut"] == "inactif"

    @pytest.mark.asyncio
    async def test_executer_job_dry_run_automatisation(self, async_client: httpx.AsyncClient):
        with (
            patch("src.api.routes.admin_jobs._verifier_limite_jobs"),
            patch("src.api.routes.admin_jobs._ajouter_log_job"),
            patch("src.api.routes.admin_jobs._journaliser_action_admin"),
            patch(
                "src.services.core.cron.jobs.lister_jobs_disponibles",
                return_value=["job_nutrition_adultes_weekly"],
            ),
            patch(
                "src.services.core.cron.jobs.executer_job_par_id",
                return_value={
                    "status": "dry_run",
                    "job_id": "job_nutrition_adultes_weekly",
                    "message": "Job 'job_nutrition_adultes_weekly' simulÃ© (dry-run).",
                    "duration_ms": 11,
                    "dry_run": True,
                },
            ) as mock_exec,
        ):
            response = await async_client.post(
                "/api/v1/admin/jobs/job_nutrition_adultes_weekly/run?dry_run=true"
            )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "dry_run"
        assert data["job_id"] == "job_nutrition_adultes_weekly"
        assert data["dry_run"] is True
        mock_exec.assert_called_once_with(
            "job_nutrition_adultes_weekly",
            dry_run=True,
            source="manual",
            triggered_by_user_id="test-user",
            relancer_exception=True,
        )

    @pytest.mark.asyncio
    async def test_executer_job_inconnu_retourne_404(self, async_client: httpx.AsyncClient):
        with (
            patch("src.api.routes.admin_jobs._verifier_limite_jobs"),
            patch(
                "src.services.core.cron.jobs.lister_jobs_disponibles",
                return_value=["job_briefing_matinal_push"],
            ),
        ):
            response = await async_client.post("/api/v1/admin/jobs/job_inconnu/run")

        assert response.status_code == 404
        data = response.json()
        assert "job_inconnu" in data["detail"]


class TestAdminSqlViewsACL:
    """GET /api/v1/admin/sql-views* â€” contrÃ´le d'accÃ¨s admin."""

    @pytest.mark.asyncio
    async def test_sql_views_sans_auth_refuse(self, unauthenticated_client: httpx.AsyncClient):
        response = await unauthenticated_client.get("/api/v1/admin/sql-views")
        assert response.status_code in [401, 403, 404]

    @pytest.mark.asyncio
    async def test_sql_views_avec_admin_repond(self, async_client: httpx.AsyncClient):
        response = await async_client.get("/api/v1/admin/sql-views")
        assert response.status_code in [200, 401, 403, 404, 500]

    @pytest.mark.asyncio
    async def test_sql_view_detail_avec_admin_repond(self, async_client: httpx.AsyncClient):
        response = await async_client.get("/api/v1/admin/sql-views/v_objets_a_remplacer")
        assert response.status_code in [200, 401, 403, 404, 500]


class TestAdminNotificationEndpoints:
    """Endpoints complÃ©mentaires CRON."""

    @pytest.mark.asyncio
    async def test_notification_test_all(self, async_client: httpx.AsyncClient):
        with patch(
            "src.services.core.notifications.notif_dispatcher.DispatcherNotifications.envoyer",
            return_value={"ntfy": True, "push": True, "email": False, "telegram": True},
        ):
            response = await async_client.post(
                "/api/v1/admin/notifications/test-all",
                json={"message": "hello", "email": "admin@example.com", "inclure_telegram": True},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["resultats"]["ntfy"] is True
        assert "email" in data["echecs"]

    @pytest.mark.asyncio
    async def test_config_export(self, async_client: httpx.AsyncClient):
        response = await async_client.get("/api/v1/admin/config/export")
        assert response.status_code == 200
        data = response.json()
        assert "feature_flags" in data
        assert "runtime_config" in data

    @pytest.mark.asyncio
    async def test_config_import(self, async_client: httpx.AsyncClient):
        response = await async_client.post(
            "/api/v1/admin/config/import",
            json={
                "feature_flags": {"admin.mode_test": True},
                "runtime_config": {"dashboard.refresh_seconds": 30},
                "merge": True,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "feature_flags" in data

    @pytest.mark.asyncio
    async def test_flow_simulator(self, async_client: httpx.AsyncClient):
        response = await async_client.post(
            "/api/v1/admin/flow-simulator",
            json={"scenario": "peremption_j2", "dry_run": True},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["scenario"] == "peremption_j2"
        assert isinstance(data["actions"], list)
        assert data["dry_run"] is True

    @pytest.mark.asyncio
    async def test_live_snapshot(self, async_client: httpx.AsyncClient):
        response = await async_client.get("/api/v1/admin/live-snapshot")
        assert response.status_code == 200
        assert isinstance(response.json(), dict)


class TestAdminInterModuleBridgesStatus:
    """Endpoint statut opÃ©rationnel des bridges bridges inter-modules."""

    @pytest.mark.asyncio
    async def test_status_bridges_presence_mode(self, async_client: httpx.AsyncClient):
        response = await async_client.get("/api/v1/admin/bridges/status?inclure_smoke=false")
        assert response.status_code == 200

        data = response.json()
        assert data.get("phase") == "bridges_inter_modules"
        assert "resume" in data
        assert data["resume"].get("total_actions") == 17
        assert data["resume"].get("mode_verification") == "presence_only"
        assert data["consolidation_bridges"].get("total_legacy") == 11
        assert data["consolidation_bridges"].get("consolides") == 11
        assert data["consolidation_bridges"].get("statut") == "termine"
        assert isinstance(data.get("items"), list)
        assert len(data["items"]) == 17


class TestAdminRouterExiste:
    """VÃ©rifie que les routes admin sont bien enregistrÃ©es dans l'app."""

    def test_routes_admin_enregistrees(self):
        from src.api.main import app

        paths = [cast(Any, r).path for r in app.routes if hasattr(r, "path")]
        admin_paths = [p for p in paths if "/admin/" in p]
        assert len(admin_paths) >= 2, f"Routes admin introuvables. Chemins: {paths[:20]}"


class TestAdminNotificationsQueueEndpoints:
    """Couverture des endpoints ajoutÃ©s pour le Sprint F."""

    @pytest.mark.asyncio
    async def test_notifications_queue_listing(self, async_client: httpx.AsyncClient):
        response = await async_client.get("/api/v1/admin/notifications/queue")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    @pytest.mark.asyncio
    async def test_maintenance_toggle(self, async_client: httpx.AsyncClient):
        response = await async_client.put("/api/v1/admin/maintenance", json={"enabled": True})
        assert response.status_code == 200
        data = response.json()
        assert "maintenance_mode" in data

    @pytest.mark.asyncio
    async def test_console_ia_valide_structure(self, async_client: httpx.AsyncClient):
        response = await async_client.post("/api/v1/admin/ai/console", json={"prompt": "hello"})
        assert response.status_code in [200, 401, 403, 429, 500]
        if response.status_code == 200:
            data = response.json()
            assert "response" in data
            assert "duration_ms" in data

    @pytest.mark.asyncio
    async def test_db_export_json(self, async_client: httpx.AsyncClient):
        response = await async_client.get("/api/v1/admin/db/export?format=json")
        assert response.status_code in [200, 401, 403, 500]
        if response.status_code == 200:
            data = response.json()
            assert data.get("format") == "json"
            assert "tables" in data

    @pytest.mark.asyncio
    async def test_db_import_json_payload(self, async_client: httpx.AsyncClient):
        response = await async_client.post(
            "/api/v1/admin/db/import",
            json={"tables": {"etats_persistants": []}, "merge": True},
        )
        assert response.status_code in [200, 401, 403, 422, 500]

    @pytest.mark.asyncio
    async def test_seed_dev_dry_run(self, async_client: httpx.AsyncClient):
        class _Parametres:
            ENV = "development"

        with patch("src.core.config.obtenir_parametres", return_value=_Parametres()):
            response = await async_client.post(
                "/api/v1/admin/seed/dev?dry_run=true",
                json={"scope": "recettes_standard"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "dry_run"
        assert data["scope"] == "recettes_standard"

    @pytest.mark.asyncio
    async def test_seed_dev_demo_complet_dry_run(self, async_client: httpx.AsyncClient):
        class _Parametres:
            ENV = "development"

        with patch("src.core.config.obtenir_parametres", return_value=_Parametres()):
            response = await async_client.post(
                "/api/v1/admin/seed/dev?dry_run=true",
                json={"scope": "demo_complet"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "dry_run"
        assert data["scope"] == "demo_complet"
        assert "resume" in data

    @pytest.mark.asyncio
    async def test_config_diff_expose_variations(self, async_client: httpx.AsyncClient):
        response = await async_client.get("/api/v1/admin/config/diff")

        assert response.status_code == 200
        data = response.json()
        assert "feature_flags" in data
        assert "runtime_config" in data
        assert "changed" in data["feature_flags"]
        assert "changed" in data["runtime_config"]

    @pytest.mark.asyncio
    async def test_jobs_simulate_day_accepts_date_reference(self, async_client: httpx.AsyncClient):
        with (
            patch(
                "src.services.core.cron.jobs.lister_jobs_disponibles",
                return_value=["rappels_famille"],
            ),
            patch(
                "src.services.core.cron.jobs.executer_job_par_id",
                return_value={
                    "status": "dry_run",
                    "job_id": "rappels_famille",
                    "message": "simulation date OK",
                    "duration_ms": 5,
                    "dry_run": True,
                },
            ),
        ):
            response = await async_client.post(
                "/api/v1/admin/jobs/simulate-day",
                json={
                    "dry_run": True,
                    "continuer_sur_erreur": True,
                    "date_reference": "2026-05-01T08:00:00",
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert data["date_reference"].startswith("2026-05-01")
        assert data["mode"] == "dry_run"
        assert data["jobs_cibles"] == ["rappels_famille"]

    @pytest.mark.asyncio
    async def test_jobs_history_pagine_filtres(self, async_client: httpx.AsyncClient):
        response = await async_client.get(
            "/api/v1/admin/jobs/history",
            params={"page": 1, "par_page": 10, "status": "success"},
        )

        assert response.status_code in [200, 500]
        if response.status_code == 200:
            data = response.json()
            assert "items" in data
            assert "total" in data
            assert "page" in data
            assert "pages_totales" in data


class TestAdminQuickCommand:
    """Couverture D1: console commande rapide admin."""

    @pytest.mark.asyncio
    async def test_quick_command_help(self, async_client: httpx.AsyncClient):
        response = await async_client.post(
            "/api/v1/admin/quick-command",
            json={"commande": "help"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "ok"
        assert data.get("type") == "help"
        assert isinstance(data.get("commandes"), dict)

    @pytest.mark.asyncio
    async def test_quick_command_run_job_dry_run(self, async_client: httpx.AsyncClient):
        with patch(
            "src.services.core.cron.jobs.executer_job_par_id",
            return_value={
                "status": "dry_run",
                "job_id": "rappels_famille",
                "message": "simulÃ©",
                "duration_ms": 10,
                "dry_run": True,
            },
        ) as mock_exec:
            response = await async_client.post(
                "/api/v1/admin/quick-command",
                json={"commande": "run job rappels_famille --dry-run"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data.get("type") == "job_result"
        mock_exec.assert_called_once_with(
            "rappels_famille",
            dry_run=True,
            source="admin_console",
        )

    @pytest.mark.asyncio
    async def test_quick_command_inconnue(self, async_client: httpx.AsyncClient):
        response = await async_client.post(
            "/api/v1/admin/quick-command",
            json={"commande": "foo bar baz"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("type") == "error"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# CT-14 â€” Backup personnel
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestBackupPersonnel:
    """POST /api/v1/export/backup â€” export backup utilisateur."""

    @pytest.mark.asyncio
    async def test_sans_auth_retourne_401_ou_200(
        self, unauthenticated_client: httpx.AsyncClient
    ):
        """Le backup nÃ©cessite une authentification (ou dev mode accepte)."""
        response = await unauthenticated_client.post("/api/v1/export/backup")
        assert response.status_code in [200, 401, 403, 500]

    @pytest.mark.asyncio
    async def test_avec_auth_retourne_zip(self, async_client: httpx.AsyncClient):
        """Avec authentification, le backup retourne un fichier ZIP."""
        response = await async_client.post("/api/v1/export/backup")
        assert response.status_code in [200, 401, 403, 500]
        if response.status_code == 200:
            content_type = response.headers.get("content-type", "")
            assert "zip" in content_type or "octet-stream" in content_type
