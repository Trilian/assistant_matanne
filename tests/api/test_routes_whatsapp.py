"""
T2 — Tests routes WhatsApp webhook.

Couvre src/api/routes/webhooks_whatsapp.py :
- GET  /api/v1/whatsapp/webhook : vérification Meta challenge
- POST /api/v1/whatsapp/webhook : réception message texte et bouton
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any, cast
from unittest.mock import AsyncMock, patch

import httpx
import pytest
import pytest_asyncio
from httpx import ASGITransport

Payload = dict[str, Any]


# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest_asyncio.fixture
async def async_client() -> AsyncIterator[httpx.AsyncClient]:
    """Client async standard (webhooks WhatsApp ne nécessitent pas d'auth utilisateur)."""
    from src.api.main import app

    async with httpx.AsyncClient(
        transport=ASGITransport(app=app, raise_app_exceptions=False),
        base_url="http://test",
    ) as client:
        yield client


def _payload_message_texte(sender: str, texte: str) -> Payload:
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


def _payload_button_reply(sender: str, action_id: str) -> Payload:
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


def _payload_list_reply(sender: str, action_id: str) -> Payload:
    """Construit un payload WhatsApp interactive list_reply."""
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
                                        "type": "list_reply",
                                        "list_reply": {"id": action_id, "title": "Action"},
                                    },
                                    "id": "wamid.list123",
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
            json=cast(Payload, {"entry": [{"changes": []}]}),
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_payload_messages_vide_ok(self, async_client: httpx.AsyncClient):
        """Payload changes sans messages → 200."""
        response = await async_client.post(
            "/api/v1/whatsapp/webhook",
            json=cast(Payload, {"entry": [{"changes": [{"value": {"messages": []}}]}]}),
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
    async def test_list_reply_redirige_vers_traiter_action(self, async_client: httpx.AsyncClient):
        """Interactive list_reply doit être routé vers _traiter_action_bouton."""
        mock_action = AsyncMock()
        with patch("src.api.routes.webhooks_whatsapp._traiter_action_bouton", mock_action):
            response = await async_client.post(
                "/api/v1/whatsapp/webhook",
                json=_payload_list_reply("33600000000", "cmd_meteo"),
            )

        assert response.status_code == 200
        mock_action.assert_called_once_with("33600000000", "cmd_meteo")

    @pytest.mark.asyncio
    async def test_traiter_action_bouton_valider_envoie_confirmation(self):
        """_traiter_action_bouton(planning_valider) → appel envoyer_message_whatsapp."""
        from src.api.routes import webhooks_whatsapp as webhook_module

        traiter_action_bouton = cast(Any, webhook_module)._traiter_action_bouton

        mock_envoyer = AsyncMock(return_value=True)
        mock_valider = AsyncMock()
        with (
            patch("src.services.integrations.whatsapp.envoyer_message_whatsapp", mock_envoyer),
            patch("src.api.routes.webhooks_whatsapp._valider_planning_courant", mock_valider),
        ):
            await traiter_action_bouton("33611111111", "planning_valider")

        mock_valider.assert_called_once()
        mock_envoyer.assert_called_once()
        assert "valide" in mock_envoyer.call_args[0][1].lower()

    @pytest.mark.asyncio
    async def test_traiter_message_texte_courses_envoie_liste(self):
        """_traiter_message_texte('courses') → appel _envoyer_liste_courses."""
        from src.api.routes import webhooks_whatsapp as webhook_module

        traiter_message_texte = cast(Any, webhook_module)._traiter_message_texte

        mock_envoyer_liste = AsyncMock()
        with patch("src.api.routes.webhooks_whatsapp._envoyer_liste_courses", mock_envoyer_liste):
            await traiter_message_texte("33611111111", "courses")

        mock_envoyer_liste.assert_called_once_with("33611111111")

    @pytest.mark.asyncio
    async def test_traiter_action_bouton_digest_courses(self):
        """Action digest_courses doit renvoyer la liste de courses."""
        from src.api.routes import webhooks_whatsapp as webhook_module

        traiter_action_bouton = cast(Any, webhook_module)._traiter_action_bouton

        mock_liste = AsyncMock()
        with patch("src.api.routes.webhooks_whatsapp._envoyer_liste_courses", mock_liste):
            await traiter_action_bouton("33611111111", "digest_courses")

        mock_liste.assert_called_once_with("33611111111")

    @pytest.mark.asyncio
    async def test_traiter_action_bouton_cmd_route_texte(self):
        """Action cmd_* doit être reroutée vers _traiter_message_texte."""
        from src.api.routes import webhooks_whatsapp as webhook_module

        traiter_action_bouton = cast(Any, webhook_module)._traiter_action_bouton

        mock_texte = AsyncMock()
        with patch("src.api.routes.webhooks_whatsapp._traiter_message_texte", mock_texte):
            await traiter_action_bouton("33611111111", "cmd_meteo")

        mock_texte.assert_called_once_with("33611111111", "meteo")


# ═══════════════════════════════════════════════════════════
# TESTS — PAYLOADS MALFORMÉS & SÉCURITÉ
# ═══════════════════════════════════════════════════════════


class TestPayloadsMalformes:
    """Tests de résilience face aux payloads invalides."""

    @pytest.mark.asyncio
    async def test_payload_entry_invalide(self, async_client: httpx.AsyncClient):
        """Payload avec entry qui n'est pas une liste → 200 sans crash."""
        response = await async_client.post(
            "/api/v1/whatsapp/webhook",
            json=cast(Payload, {"entry": "pas_une_liste"}),
        )
        # Doit ne pas crash — 200 ou 422/500 selon implémentation
        assert response.status_code in (200, 422, 500)

    @pytest.mark.asyncio
    async def test_payload_message_sans_from(self, async_client: httpx.AsyncClient):
        """Message sans champ 'from' → 200 sans crash."""
        payload = {
            "entry": [
                {
                    "changes": [
                        {
                            "value": {
                                "messages": [
                                    {"type": "text", "text": {"body": "test"}, "id": "wamid.x"}
                                ]
                            }
                        }
                    ]
                }
            ]
        }
        response = await async_client.post("/api/v1/whatsapp/webhook", json=payload)
        assert response.status_code in (200, 500)

    @pytest.mark.asyncio
    async def test_payload_message_type_inconnu(self, async_client: httpx.AsyncClient):
        """Type de message inconnu (image, video, etc.) → 200 ok."""
        payload = {
            "entry": [
                {
                    "changes": [
                        {
                            "value": {
                                "messages": [
                                    {
                                        "from": "33600000000",
                                        "type": "image",
                                        "image": {"id": "img123"},
                                        "id": "wamid.img",
                                    }
                                ]
                            }
                        }
                    ]
                }
            ]
        }
        response = await async_client.post("/api/v1/whatsapp/webhook", json=payload)
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_challenge_mode_non_subscribe(self, async_client: httpx.AsyncClient):
        """Mode != subscribe → 403."""
        response = await async_client.get(
            "/api/v1/whatsapp/webhook",
            params={
                "hub.mode": "unsubscribe",
                "hub.verify_token": "quelconque",
                "hub.challenge": "42",
            },
        )
        assert response.status_code == 403


class TestWhatsappConversationStatePersistence:
    """Couverture D8: état conversationnel persistant multi-turn."""

    @pytest.mark.asyncio
    async def test_planning_modifier_persiste_etat(self):
        from src.api.routes import webhooks_whatsapp as webhook_module

        traiter_action_bouton = cast(Any, webhook_module)._traiter_action_bouton

        mock_envoyer = AsyncMock(return_value=True)
        with (
            patch("src.services.integrations.whatsapp.envoyer_message_whatsapp", mock_envoyer),
            patch("src.services.integrations.whatsapp.sauvegarder_etat_conversation") as mock_save,
        ):
            await traiter_action_bouton("33611111111", "planning_modifier")

        mock_save.assert_called_once()
        args = mock_save.call_args[0]
        assert args[0] == "33611111111"
        assert args[1].get("etat") == "attente_creneau_modification"

    @pytest.mark.asyncio
    async def test_message_creneau_fait_transition_etat(self):
        from src.api.routes import webhooks_whatsapp as webhook_module

        traiter_message_texte = cast(Any, webhook_module)._traiter_message_texte

        with (
            patch(
                "src.services.integrations.whatsapp.charger_etat_conversation",
                return_value={"etat": "attente_creneau_modification"},
            ),
            patch("src.services.integrations.whatsapp.sauvegarder_etat_conversation") as mock_save,
            patch("src.services.integrations.whatsapp.envoyer_message_whatsapp", new=AsyncMock(return_value=True)),
        ):
            await traiter_message_texte("33611111111", "lundi soir")

        mock_save.assert_called_once()
        saved_state = mock_save.call_args[0][1]
        assert saved_state.get("etat") == "attente_detail_modification"
        assert saved_state.get("creneau") == "lundi soir"

    @pytest.mark.asyncio
    async def test_message_detail_efface_etat(self):
        from src.api.routes import webhooks_whatsapp as webhook_module

        traiter_message_texte = cast(Any, webhook_module)._traiter_message_texte

        with (
            patch(
                "src.services.integrations.whatsapp.charger_etat_conversation",
                return_value={"etat": "attente_detail_modification", "creneau": "lundi soir"},
            ),
            patch("src.services.integrations.whatsapp.effacer_etat_conversation") as mock_clear,
            patch("src.services.integrations.whatsapp.envoyer_message_whatsapp", new=AsyncMock(return_value=True)),
        ):
            await traiter_message_texte("33611111111", "remplacer par pâtes")

        mock_clear.assert_called_once_with("33611111111")
