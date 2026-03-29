"""
T6a — Tests service WhatsApp.

Couvre src/services/integrations/whatsapp.py :
- envoyer_message_whatsapp : envoi message texte
- envoyer_message_interactif_whatsapp : envoi message avec boutons
- Masquage du numéro de destinataire (hash SHA-256)
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ═══════════════════════════════════════════════════════════
# TESTS — ENVOI MESSAGE TEXTE
# ═══════════════════════════════════════════════════════════


class TestEnvoyerMessageWhatsapp:
    """Tests envoyer_message_whatsapp()."""

    @pytest.mark.asyncio
    async def test_envoi_non_configure_retourne_false(self):
        """Sans token/phone_id configuré, retourne False sans lever d'exception."""
        from src.services.integrations.whatsapp import envoyer_message_whatsapp

        with patch("src.services.integrations.whatsapp.obtenir_parametres") as mock_params:
            mock_params.return_value.META_WHATSAPP_TOKEN = ""
            mock_params.return_value.META_PHONE_NUMBER_ID = ""
            result = await envoyer_message_whatsapp("33612345678", "Test")

        assert result is False

    @pytest.mark.asyncio
    async def test_envoi_reussi_retourne_true(self):
        """Avec configuration + réponse HTTP 200 → True."""
        from src.services.integrations.whatsapp import envoyer_message_whatsapp

        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json.return_value = {"messages": [{"id": "wamid.test"}]}

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = False
        mock_client.post.return_value = mock_resp

        with (
            patch("src.services.integrations.whatsapp.obtenir_parametres") as mock_params,
            patch("src.services.integrations.whatsapp.httpx.AsyncClient", return_value=mock_client),
        ):
            mock_params.return_value.META_WHATSAPP_TOKEN = "test-token"
            mock_params.return_value.META_PHONE_NUMBER_ID = "12345"
            result = await envoyer_message_whatsapp("33612345678", "Bonjour !")

        assert result is True
        mock_client.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_envoi_echec_http_retourne_false(self):
        """Erreur HTTP → False sans lever d'exception au niveau appelant."""
        from src.services.integrations.whatsapp import envoyer_message_whatsapp

        import httpx as httpx_lib

        mock_resp = MagicMock()
        mock_resp.raise_for_status.side_effect = httpx_lib.HTTPStatusError(
            "400 Bad Request", request=MagicMock(), response=mock_resp
        )

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = False
        mock_client.post.return_value = mock_resp

        with (
            patch("src.services.integrations.whatsapp.obtenir_parametres") as mock_params,
            patch("src.services.integrations.whatsapp.httpx.AsyncClient", return_value=mock_client),
        ):
            mock_params.return_value.META_WHATSAPP_TOKEN = "test-token"
            mock_params.return_value.META_PHONE_NUMBER_ID = "12345"
            result = await envoyer_message_whatsapp("33612345678", "Test")

        assert result is False


# ═══════════════════════════════════════════════════════════
# TESTS — MASQUAGE DU NUMÉRO (C10)
# ═══════════════════════════════════════════════════════════


class TestMasquageNumero:
    """Vérifie que le numéro de destinataire est masqué dans les logs (C10)."""

    def test_log_ne_contient_pas_numero_brut(self, caplog):
        """Le logger ne doit pas écrire le numéro en clair."""
        import asyncio
        import logging

        from src.services.integrations.whatsapp import envoyer_message_whatsapp

        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json.return_value = {}

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = False
        mock_client.post.return_value = mock_resp

        numero = "33699887766"

        with (
            caplog.at_level(logging.INFO, logger="src.services.integrations.whatsapp"),
            patch("src.services.integrations.whatsapp.obtenir_parametres") as mock_params,
            patch("src.services.integrations.whatsapp.httpx.AsyncClient", return_value=mock_client),
        ):
            mock_params.return_value.META_WHATSAPP_TOKEN = "test-token"
            mock_params.return_value.META_PHONE_NUMBER_ID = "12345"
            asyncio.get_event_loop().run_until_complete(
                envoyer_message_whatsapp(numero, "Test message")
            )

        # Le numéro brut ne doit pas apparaître dans les logs
        for record in caplog.records:
            assert numero not in record.getMessage(), (
                f"Le numéro {numero} est écrit en clair dans les logs!"
            )

    def test_log_contient_hash_sha256(self, caplog):
        """Le logger doit écrire un hash SHA-256 partiel à la place du numéro."""
        import asyncio
        import hashlib
        import logging

        from src.services.integrations.whatsapp import envoyer_message_whatsapp

        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json.return_value = {}

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = False
        mock_client.post.return_value = mock_resp

        numero = "33699887766"
        hash_attendu = hashlib.sha256(numero.encode()).hexdigest()[:8]

        with (
            caplog.at_level(logging.INFO, logger="src.services.integrations.whatsapp"),
            patch("src.services.integrations.whatsapp.obtenir_parametres") as mock_params,
            patch("src.services.integrations.whatsapp.httpx.AsyncClient", return_value=mock_client),
        ):
            mock_params.return_value.META_WHATSAPP_TOKEN = "test-token"
            mock_params.return_value.META_PHONE_NUMBER_ID = "12345"
            asyncio.get_event_loop().run_until_complete(
                envoyer_message_whatsapp(numero, "Test message")
            )

        # Au moins un log avec le hash SHA-256
        found = any(hash_attendu in r.getMessage() for r in caplog.records)
        assert found, f"Hash SHA-256 '{hash_attendu}' non trouvé dans les logs."
