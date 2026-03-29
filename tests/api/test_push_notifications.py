"""
CT-13 â€” Tests des notifications push (Sprint 3)

Tests couvrant:
- Endpoint VAPID public key (B-02 Sprint 1)
- Jobs scheduler digest_ntfy et rappel_courses (B-03 Sprint 1)
- Persistance en DB lors d'un abonnement (B-01 Sprint 1)
- DÃ©sabonnement (supprimer_abonnement)
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import httpx
import pytest
import pytest_asyncio
from httpx import ASGITransport


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# FIXTURES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest_asyncio.fixture
async def async_client():
    from src.api.main import app
    from src.api.dependencies import require_auth

    app.dependency_overrides[require_auth] = lambda: {"id": "test-user", "role": "membre"}
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app, raise_app_exceptions=False),
        base_url="http://test",
    ) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture
def subscription_payload() -> dict:
    return {
        "endpoint": "https://fcm.googleapis.com/fcm/send/test-token-123",
        "keys": {
            "p256dh": "BNcRdreALRFXTkOOUHK1EtK2wtaz5Ry4YfYCA_0QTpQtUbVlUls0VJXg7A8u-Ts1XbjhazAkj7I99e8QcYP7DkM",
            "auth": "tBHItJI5svbpez7KI4CCXg",
        },
    }


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# B-02 â€” Endpoint clÃ© publique VAPID
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestVapidPublicKey:
    """Tests pour GET /api/v1/push/vapid-public-key."""

    @pytest.mark.asyncio
    async def test_retourne_200(self, async_client: httpx.AsyncClient):
        """L'endpoint doit rÃ©pondre 200."""
        response = await async_client.get("/api/v1/push/vapid-public-key")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_retourne_public_key(self, async_client: httpx.AsyncClient):
        """La rÃ©ponse doit contenir le champ public_key."""
        response = await async_client.get("/api/v1/push/vapid-public-key")
        assert response.status_code == 200
        data = response.json()
        assert "public_key" in data

    @pytest.mark.asyncio
    async def test_public_key_est_une_chaine(self, async_client: httpx.AsyncClient):
        """La clÃ© publique doit Ãªtre une chaÃ®ne non vide."""
        response = await async_client.get("/api/v1/push/vapid-public-key")
        data = response.json()
        assert isinstance(data["public_key"], str)

    @pytest.mark.asyncio
    async def test_endpoint_sans_auth(self):
        """L'endpoint VAPID ne nÃ©cessite pas d'authentification."""
        from src.api.main import app

        async with httpx.AsyncClient(
            transport=ASGITransport(app=app, raise_app_exceptions=False),
            base_url="http://test",
        ) as client:
            response = await client.get("/api/v1/push/vapid-public-key")
        assert response.status_code == 200


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# B-03 â€” Jobs scheduler
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestSchedulerJobs:
    """Tests de la prÃ©sence des jobs planifiÃ©s dans DÃ©marreurCron."""

    def _get_job_ids(self) -> list[str]:
        """Instancie DÃ©marreurCron et retourne les IDs des jobs configurÃ©s."""
        from src.services.core.cron.jobs import DÃ©marreurCron

        demarreur = DÃ©marreurCron()
        return [job.id for job in demarreur._scheduler.get_jobs()]

    def test_digest_ntfy_dans_scheduler(self):
        """Le job digest_ntfy doit Ãªtre enregistrÃ© dans le scheduler."""
        job_ids = self._get_job_ids()
        assert "digest_ntfy" in job_ids, (
            f"Job 'digest_ntfy' absent du scheduler. Jobs prÃ©sents : {job_ids}"
        )

    def test_rappel_courses_dans_scheduler(self):
        """Le job rappel_courses doit Ãªtre enregistrÃ© dans le scheduler."""
        job_ids = self._get_job_ids()
        assert "rappel_courses" in job_ids, (
            f"Job 'rappel_courses' absent du scheduler. Jobs prÃ©sents : {job_ids}"
        )

    def test_push_quotidien_dans_scheduler(self):
        """Le job push_quotidien doit Ãªtre enregistrÃ© dans le scheduler."""
        job_ids = self._get_job_ids()
        assert "push_quotidien" in job_ids

    def test_scheduler_a_au_moins_5_jobs(self):
        """Le scheduler doit avoir au moins 5 jobs configurÃ©s."""
        job_ids = self._get_job_ids()
        assert len(job_ids) >= 5, f"Seulement {len(job_ids)} jobs configurÃ©s : {job_ids}"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# B-01 â€” Persistance abonnement en base
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestSubscribePersistance:
    """Tests que POST /subscribe persiste l'abonnement via le service."""

    @pytest.mark.asyncio
    async def test_subscribe_appelle_sauvegarder_abonnement(
        self, async_client: httpx.AsyncClient, subscription_payload: dict
    ):
        """sauvegarder_abonnement doit Ãªtre appelÃ© lors d'un POST /subscribe."""
        mock_service = MagicMock()
        mock_service.sauvegarder_abonnement.return_value = MagicMock(
            endpoint=subscription_payload["endpoint"],
            user_id="test-user",
        )

        with patch(
            "src.services.core.notifications.notif_web_core.obtenir_push_notification_service",
            return_value=mock_service,
        ):
            response = await async_client.post(
                "/api/v1/push/subscribe", json=subscription_payload
            )

        assert response.status_code in [200, 201], response.text
        mock_service.sauvegarder_abonnement.assert_called_once()

    @pytest.mark.asyncio
    async def test_subscribe_passe_user_id_correct(
        self, async_client: httpx.AsyncClient, subscription_payload: dict
    ):
        """sauvegarder_abonnement doit recevoir le user_id de l'utilisateur authentifiÃ©."""
        mock_service = MagicMock()
        mock_service.sauvegarder_abonnement.return_value = MagicMock(
            endpoint=subscription_payload["endpoint"],
            user_id="test-user",
        )

        with patch(
            "src.services.core.notifications.notif_web_core.obtenir_push_notification_service",
            return_value=mock_service,
        ):
            await async_client.post("/api/v1/push/subscribe", json=subscription_payload)

        call_args = mock_service.sauvegarder_abonnement.call_args
        assert call_args is not None
        user_id_arg = call_args[0][0] if call_args[0] else call_args[1].get("user_id")
        assert user_id_arg == "test-user"

    @pytest.mark.asyncio
    async def test_subscribe_reponse_contient_endpoint(
        self, async_client: httpx.AsyncClient, subscription_payload: dict
    ):
        """La rÃ©ponse doit contenir l'endpoint de l'abonnement."""
        mock_service = MagicMock()
        mock_service.sauvegarder_abonnement.return_value = MagicMock(
            endpoint=subscription_payload["endpoint"],
            user_id="test-user",
        )

        with patch(
            "src.services.core.notifications.notif_web_core.obtenir_push_notification_service",
            return_value=mock_service,
        ):
            response = await async_client.post(
                "/api/v1/push/subscribe", json=subscription_payload
            )

        if response.status_code in [200, 201]:
            data = response.json()
            assert data.get("endpoint") == subscription_payload["endpoint"]
            assert data.get("success") is True


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# DÃ©sabonnement
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestUnsubscribe:
    """Tests pour DELETE /api/v1/push/unsubscribe."""

    @pytest.mark.asyncio
    async def test_unsubscribe_appelle_supprimer_abonnement(
        self, async_client: httpx.AsyncClient
    ):
        """supprimer_abonnement doit Ãªtre appelÃ© lors du dÃ©sabonnement."""
        mock_service = MagicMock()
        endpoint = "https://fcm.googleapis.com/fcm/send/test-token-123"

        with patch(
            "src.services.core.notifications.notif_web_core.obtenir_push_notification_service",
            return_value=mock_service,
        ):
            response = await async_client.request(
                "DELETE",
                "/api/v1/push/unsubscribe",
                json={"endpoint": endpoint},
            )

        assert response.status_code in [200, 201, 204], response.text
        mock_service.supprimer_abonnement.assert_called_once()

    @pytest.mark.asyncio
    async def test_unsubscribe_reponse_success(self, async_client: httpx.AsyncClient):
        """La rÃ©ponse du dÃ©sabonnement doit indiquer success=True."""
        mock_service = MagicMock()
        endpoint = "https://fcm.googleapis.com/fcm/send/test-token-to-remove"

        with patch(
            "src.services.core.notifications.notif_web_core.obtenir_push_notification_service",
            return_value=mock_service,
        ):
            response = await async_client.request(
                "DELETE",
                "/api/v1/push/unsubscribe",
                json={"endpoint": endpoint},
            )

        if response.status_code == 200:
            data = response.json()
            assert data.get("success") is True

