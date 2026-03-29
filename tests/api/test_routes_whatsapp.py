"""
T2 — Tests routes WhatsApp webhook.

Couvre src/api/routes/webhooks_whatsapp.py :
- GET  /api/v1/whatsapp/webhook : vérification Meta challenge
- POST /api/v1/whatsapp/webhook : réception message texte et bouton
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import httpx
import pytest
import pytest_asyncio
from httpx import ASGITransport


# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest_asyncio.fixture
async def async_client():
    """Client async standard (webhooks WhatsApp ne nécessitent pas d'auth utilisateur)."""
    from src.api.main import app

    async with httpx.AsyncClient(
        transport=ASGITransport(app=app, raise_app_exceptions=False),
        base_url="http://test",
    ) as client:
        yield client


def _payload_message_texte(sender: str, texte: str) -> dict:
    """Construit un payload WhatsApp Cloud API typique (message texte)."""
    return {
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "messages": [
                                {
                                    "from": sender,
                                    "type": "text",
                                    "text": {"body": texte},
                                    "id": "wamid.test123",
                                }
                            ]
                        }
                    }
                ]
            }
        ]
    }


def _payload_button_reply(sender: str, action_id: str) -> dict:
    """Construit un payload WhatsApp interactive button_reply."""
    return {
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "messages": [
                                {
                                    "from": sender,
                                    "type": "interactive",
                                    "interactive": {
                                        "type": "button_reply",
                                        "button_reply": {"id": action_id, "title": "OK"},
                                    },
                                    "id": "wamid.btn123",
                                }
                            ]
                        }
                    }
                ]
            }
        ]
    }


# ═══════════════════════════════════════════════════════════
# TESTS — VÉRIFICATION CHALLENGE META
# ═══════════════════════════════════════════════════════════


class TestVerificationChallenge:
    """GET /api/v1/whatsapp/webhook — handshake Meta."""

    @pytest.mark.asyncio
    async def test_challenge_valide_retourne_challenge(self, async_client: httpx.AsyncClient):
        """Bon token + hub.challenge → retourne la valeur du challenge."""
        with patch("src.api.routes.webhooks_whatsapp.obtenir_parametres") as mock_params:
            mock_params.return_value.WHATSAPP_VERIFY_TOKEN = "mon-token-secret"
            response = await async_client.get(
                "/api/v1/whatsapp/webhook",
                params={
                    "hub.mode": "subscribe",
                    "hub.verify_token": "mon-token-secret",
                    "hub.challenge": "42",
                },
            )

        assert response.status_code == 200
        assert response.json() == 42

    @pytest.mark.asyncio
    async def test_challenge_mauvais_token_403(self, async_client: httpx.AsyncClient):
        """Mauvais token → 403."""
        with patch("src.api.routes.webhooks_whatsapp.obtenir_parametres") as mock_params:
            mock_params.return_value.WHATSAPP_VERIFY_TOKEN = "mon-token-secret"
            response = await async_client.get(
                "/api/v1/whatsapp/webhook",
                params={
                    "hub.mode": "subscribe",
                    "hub.verify_token": "mauvais-token",
                    "hub.challenge": "99",
                },
            )

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_challenge_sans_params_403(self, async_client: httpx.AsyncClient):
        """Aucun paramètre → 403."""
        response = await async_client.get("/api/v1/whatsapp/webhook")
        assert response.status_code == 403


# ═══════════════════════════════════════════════════════════
# TESTS — RÉCEPTION MESSAGE TEXTE
# ═══════════════════════════════════════════════════════════


class TestReceptionMessageTexte:
    """POST /api/v1/whatsapp/webhook — messages texte."""

    @pytest.mark.asyncio
    async def test_message_planning_repond_ok(self, async_client: httpx.AsyncClient):
        """Message 'planning' → réponse planning envoyée, HTTP 200."""
        with patch(
            "src.api.routes.webhooks_whatsapp._traiter_message_texte",
            new_callable=lambda: lambda *a, **kw: AsyncMock(return_value=None).__call__(*a, **kw),
        ) as mock_traiter:
            mock_traiter = AsyncMock()
            with patch("src.api.routes.webhooks_whatsapp._traiter_message_texte", mock_traiter):
                response = await async_client.post(
                    "/api/v1/whatsapp/webhook",
                    json=_payload_message_texte("33612345678", "planning"),
                )

        assert response.status_code == 200
        mock_traiter.assert_called_once_with("33612345678", "planning")

    @pytest.mark.asyncio
    async def test_message_courses_repond_ok(self, async_client: httpx.AsyncClient):
        """Message 'courses' → handler appelé."""
        mock_traiter = AsyncMock()
        with patch("src.api.routes.webhooks_whatsapp._traiter_message_texte", mock_traiter):
            response = await async_client.post(
                "/api/v1/whatsapp/webhook",
                json=_payload_message_texte("33612345678", "courses"),
            )

        assert response.status_code == 200
        mock_traiter.assert_called_once_with("33612345678", "courses")

    @pytest.mark.asyncio
    async def test_payload_vide_ok(self, async_client: httpx.AsyncClient):
        """Payload sans entry → 200 ok (Meta health check)."""
        response = await async_client.post("/api/v1/whatsapp/webhook", json={})
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_payload_changes_vide_ok(self, async_client: httpx.AsyncClient):
        """Payload entry sans changes → 200."""
        response = await async_client.post(
            "/api/v1/whatsapp/webhook",
            json={"entry": [{"changes": []}]},
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_payload_messages_vide_ok(self, async_client: httpx.AsyncClient):
        """Payload changes sans messages → 200."""
        response = await async_client.post(
            "/api/v1/whatsapp/webhook",
            json={"entry": [{"changes": [{"value": {"messages": []}}]}]},
        )
        assert response.status_code == 200


# ═══════════════════════════════════════════════════════════
# TESTS — RÉPONSE BOUTON
# ═══════════════════════════════════════════════════════════


class TestReponsesBouton:
    """POST /api/v1/whatsapp/webhook — button_reply machine d'état."""

    @pytest.mark.asyncio
    async def test_button_reply_planning_valider(self, async_client: httpx.AsyncClient):
        """Button planning_valider → _traiter_action_bouton appelé."""
        mock_action = AsyncMock()
        with patch("src.api.routes.webhooks_whatsapp._traiter_action_bouton", mock_action):
            response = await async_client.post(
                "/api/v1/whatsapp/webhook",
                json=_payload_button_reply("33612345678", "planning_valider"),
            )

        assert response.status_code == 200
        mock_action.assert_called_once_with("33612345678", "planning_valider")

    @pytest.mark.asyncio
    async def test_button_reply_planning_modifier(self, async_client: httpx.AsyncClient):
        """Button planning_modifier → handler appelé."""
        mock_action = AsyncMock()
        with patch("src.api.routes.webhooks_whatsapp._traiter_action_bouton", mock_action):
            response = await async_client.post(
                "/api/v1/whatsapp/webhook",
                json=_payload_button_reply("33600000000", "planning_modifier"),
            )

        assert response.status_code == 200
        mock_action.assert_called_once_with("33600000000", "planning_modifier")

    @pytest.mark.asyncio
    async def test_traiter_action_bouton_valider_envoie_confirmation(self):
        """_traiter_action_bouton(planning_valider) → appel envoyer_message_whatsapp."""
        from src.api.routes.webhooks_whatsapp import _traiter_action_bouton

        mock_envoyer = AsyncMock(return_value=True)
        mock_valider = AsyncMock()
        with (
            patch("src.api.routes.webhooks_whatsapp.envoyer_message_whatsapp", mock_envoyer),
            patch("src.api.routes.webhooks_whatsapp._valider_planning_courant", mock_valider),
        ):
            await _traiter_action_bouton("33611111111", "planning_valider")

        mock_valider.assert_called_once()
        mock_envoyer.assert_called_once()
        assert "validé" in mock_envoyer.call_args[0][1].lower()

    @pytest.mark.asyncio
    async def test_traiter_message_texte_courses_envoie_liste(self):
        """_traiter_message_texte('courses') → appel _envoyer_liste_courses."""
        from src.api.routes.webhooks_whatsapp import _traiter_message_texte

        mock_envoyer_liste = AsyncMock()
        with patch("src.api.routes.webhooks_whatsapp._envoyer_liste_courses", mock_envoyer_liste):
            await _traiter_message_texte("33611111111", "courses")

        mock_envoyer_liste.assert_called_once_with("33611111111")
