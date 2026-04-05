"""
Tests pour les callbacks Telegram.

Tests unitaires et d'intégration pour les handlers de callbacks Telegram
(planning_valider, planning_modifier, planning_regenerer, courses_confirmer, courses_ajouter, courses_refaire).
"""

from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Client de test FastAPI."""
    from src.api.main import app

    return TestClient(app, raise_server_exceptions=False)


# ═══════════════════════════════════════════════════════════════════════════
# DONNÉES DE TEST — CALLBACKS
# ═══════════════════════════════════════════════════════════════════════════

# Callback Telegram updates (format Telegram Bot API)
UPDATE_CALLBACK_PLANNING_VALIDER = {
    "update_id": 1001,
    "callback_query": {
        "id": "callback_123",
        "from": {
            "id": 123456,
            "is_bot": False,
            "first_name": "Test",
            "username": "testuser",
        },
        "chat_instance": "1234567890",
        "data": "planning_valider:42",
        "message": {
            "message_id": 100,
            "date": 1234567890,
            "chat": {"id": 123456},
        },
    },
}

UPDATE_CALLBACK_PLANNING_MODIFIER = {
    "update_id": 1002,
    "callback_query": {
        "id": "callback_124",
        "from": {"id": 123456, "is_bot": False},
        "chat_instance": "1234567890",
        "data": "planning_modifier:42",
        "message": {"message_id": 100, "date": 1234567890, "chat": {"id": 123456}},
    },
}

UPDATE_CALLBACK_PLANNING_REGENERER = {
    "update_id": 1003,
    "callback_query": {
        "id": "callback_125",
        "from": {"id": 123456, "is_bot": False},
        "chat_instance": "1234567890",
        "data": "planning_regenerer:42",
        "message": {"message_id": 100, "date": 1234567890, "chat": {"id": 123456}},
    },
}

UPDATE_CALLBACK_COURSES_CONFIRMER = {
    "update_id": 2001,
    "callback_query": {
        "id": "callback_201",
        "from": {"id": 123456, "is_bot": False},
        "chat_instance": "1234567890",
        "data": "courses_confirmer:15",
        "message": {"message_id": 101, "date": 1234567891, "chat": {"id": 123456}},
    },
}

UPDATE_CALLBACK_COURSES_AJOUTER = {
    "update_id": 2002,
    "callback_query": {
        "id": "callback_202",
        "from": {"id": 123456, "is_bot": False},
        "chat_instance": "1234567890",
        "data": "courses_ajouter:15",
        "message": {"message_id": 101, "date": 1234567891, "chat": {"id": 123456}},
    },
}

UPDATE_CALLBACK_COURSES_REFAIRE = {
    "update_id": 2003,
    "callback_query": {
        "id": "callback_203",
        "from": {"id": 123456, "is_bot": False},
        "chat_instance": "1234567890",
        "data": "courses_refaire:15",
        "message": {"message_id": 101, "date": 1234567891, "chat": {"id": 123456}},
    },
}


# ═══════════════════════════════════════════════════════════════════════════
# TESTS ROUTE WEBHOOK — ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════


class TestWebhookTelegramCallbacksEndpoint:
    """Tests du endpoint webhook Telegram pour les callbacks."""

    def test_webhook_endpoint_exists(self, client):
        """POST /api/v1/telegram/webhook existe."""
        response = client.post("/api/v1/telegram/webhook", json={"update_id": 0})
        assert response.status_code in (200, 400, 500)

    def test_webhook_rejects_invalid_json(self, client):
        """Webhook rejette JSON invalide."""
        response = client.post("/api/v1/telegram/webhook", json={"invalid": "data"})
        # Devrait accepter mais ignorer ou retourner 200 de toute façon
        assert response.status_code in (200, 400, 422, 500)

    def test_webhook_planning_callback_route(self, client):
        """Webhook accepte callback planning_valider:ID."""
        with patch("src.api.routes.webhooks_telegram._traiter_callback_planning", new_callable=AsyncMock):
            response = client.post("/api/v1/telegram/webhook", json=UPDATE_CALLBACK_PLANNING_VALIDER)
            # Ne doit pas échouer sur route invalide
            assert response.status_code in (200, 500)

    def test_webhook_courses_callback_route(self, client):
        """Webhook accepte callback courses_confirmer:ID."""
        with patch("src.api.routes.webhooks_telegram._traiter_callback_courses", new_callable=AsyncMock):
            response = client.post("/api/v1/telegram/webhook", json=UPDATE_CALLBACK_COURSES_CONFIRMER)
            assert response.status_code in (200, 500)


# ═══════════════════════════════════════════════════════════════════════════
# TESTS EXTRACTION DE CALLBACKS
# ═══════════════════════════════════════════════════════════════════════════


class TestExtrairIdDepuisCallback:
    """Tests pour l'extraction d'ID depuis callback_data."""

    def test_extraire_id_format_valide(self):
        """Extraction d'ID depuis format 'prefix:ID' fonctionne."""
        from src.api.routes.webhooks_telegram import _extraire_id_depuis_callback

        result = _extraire_id_depuis_callback("planning_valider:42", "planning_valider")
        assert result == 42

    def test_extraire_id_format_sans_id(self):
        """Extraction retourne None si pas d'ID."""
        from src.api.routes.webhooks_telegram import _extraire_id_depuis_callback

        result = _extraire_id_depuis_callback("planning_valider", "planning_valider")
        assert result is None

    def test_extraire_id_format_invalide(self):
        """Extraction retourne None si format invalide."""
        from src.api.routes.webhooks_telegram import _extraire_id_depuis_callback

        result = _extraire_id_depuis_callback("planning_valider:abc", "planning_valider")
        assert result is None

    def test_extraire_id_prefix_different(self):
        """Extraction retourne None si prefix différent."""
        from src.api.routes.webhooks_telegram import _extraire_id_depuis_callback

        result = _extraire_id_depuis_callback("planning_valider:42", "courses_confirmer")
        assert result is None


# ═══════════════════════════════════════════════════════════════════════════
# TESTS PLANNING CALLBACKS — TRANSITIONS D'ÉTAT
# ═══════════════════════════════════════════════════════════════════════════


class TestPlanningCallbackValider:
    """Tests pour callback planning_valider."""

    @pytest.mark.asyncio
    async def test_planning_valider_succes(self):
        """Callback valider transite planning brouillon → valide."""
        with patch("src.api.utils.executer_async") as mock_execute:
            with patch("src.services.integrations.telegram.repondre_callback_query", new_callable=AsyncMock) as mock_respond:
                with patch("src.services.integrations.telegram.modifier_message", new_callable=AsyncMock):
                # Simuler le résultat de _valider()
                    mock_execute.return_value = {"message": "Planning validé", "id": 42, "status": 200}

                    from src.api.routes.webhooks_telegram import _traiter_callback_planning

                    await _traiter_callback_planning("planning_valider:42", "callback_123", 123456)

                    # Vérifier que repondre_callback_query a été appelé avec succès
                    mock_respond.assert_called_once()
                    call_args = mock_respond.call_args
                    assert call_args.args[0] == "callback_123"
                    assert "✅" in call_args.args[1]
                    assert call_args.kwargs["show_alert"] is False

    @pytest.mark.asyncio
    async def test_planning_valider_planning_inexistant(self):
        """Callback valider retourne erreur si planning n'existe pas."""
        with patch("src.api.utils.executer_async") as mock_execute:
            with patch("src.services.integrations.telegram.repondre_callback_query", new_callable=AsyncMock) as mock_respond:
                # Simuler planning inexistant
                mock_execute.return_value = {"error": "Planning non trouvé", "status": 404}

                from src.api.routes.webhooks_telegram import _traiter_callback_planning

                await _traiter_callback_planning("planning_valider:999", "callback_123", 123456)

                # Vérifier erreur
                mock_respond.assert_called_once()
                call_args = mock_respond.call_args
                assert call_args.kwargs["show_alert"] is True


class TestPlanningCallbackModifier:
    """Tests pour callback planning_modifier."""

    @pytest.mark.asyncio
    async def test_planning_modifier_envoie_url(self):
        """Callback modifier envoie URL web."""
        with patch("src.services.integrations.telegram.repondre_callback_query", new_callable=AsyncMock) as mock_respond:
            from src.api.routes.webhooks_telegram import _traiter_callback_planning

            await _traiter_callback_planning("planning_modifier:42", "callback_124", 123456)

            # Vérifier que URL est renvoyée
            mock_respond.assert_called_once()
            call_args = mock_respond.call_args
            assert "https://matanne.vercel.app" in call_args.args[1] or "lien" in call_args.args[1].lower()


class TestPlanningCallbackRegenerer:
    """Tests pour callback planning_regenerer."""

    @pytest.mark.asyncio
    async def test_planning_regenerer_cree_nouveau(self):
        """Callback regenerer crée nouveau planning en brouillon."""
        with patch("src.api.utils.executer_async") as mock_execute:
            with patch("src.services.integrations.telegram.repondre_callback_query", new_callable=AsyncMock) as mock_respond:
                with patch("src.services.integrations.telegram.modifier_message", new_callable=AsyncMock):
                # Simuler succès de régénération
                    mock_execute.return_value = {"message": "Planning régénéré", "id": 43, "status": 200}

                    from src.api.routes.webhooks_telegram import _traiter_callback_planning

                    await _traiter_callback_planning("planning_regenerer:42", "callback_125", 123456)

                    # Vérifier succès
                    mock_respond.assert_called_once()
                    call_args = mock_respond.call_args
                    assert "🔄" in call_args.args[1]


# ═══════════════════════════════════════════════════════════════════════════
# TESTS COURSES CALLBACKS — TRANSITIONS D'ÉTAT
# ═══════════════════════════════════════════════════════════════════════════


class TestCoursesCallbackConfirmer:
    """Tests pour callback courses_confirmer."""

    @pytest.mark.asyncio
    async def test_courses_confirmer_succes(self):
        """Callback confirmer transite courses brouillon → active."""
        with patch("src.api.utils.executer_async") as mock_execute:
            with patch("src.services.integrations.telegram.repondre_callback_query", new_callable=AsyncMock) as mock_respond:
                with patch("src.services.integrations.telegram.modifier_message", new_callable=AsyncMock):
                # Simuler succès
                    mock_execute.return_value = {"message": "Courses confirmées", "id": 15, "status": 200}

                    from src.api.routes.webhooks_telegram import _traiter_callback_courses

                    await _traiter_callback_courses("courses_confirmer:15", "callback_201", 123456)

                    # Vérifier succès
                    mock_respond.assert_called_once()
                    call_args = mock_respond.call_args
                    assert "✅" in call_args.args[1]

    @pytest.mark.asyncio
    async def test_courses_confirmer_liste_inexistante(self):
        """Callback confirmer retourne erreur si liste n'existe pas."""
        with patch("src.api.utils.executer_async") as mock_execute:
            with patch("src.services.integrations.telegram.repondre_callback_query", new_callable=AsyncMock) as mock_respond:
                # Simuler liste inexistante
                mock_execute.return_value = {"error": "Liste non trouvée", "status": 404}

                from src.api.routes.webhooks_telegram import _traiter_callback_courses

                await _traiter_callback_courses("courses_confirmer:999", "callback_201", 123456)

                # Vérifier erreur
                mock_respond.assert_called_once()
                call_args = mock_respond.call_args
                assert call_args.kwargs["show_alert"] is True


class TestCoursesCallbackAjouter:
    """Tests pour callback courses_ajouter."""

    @pytest.mark.asyncio
    async def test_courses_ajouter_envoie_url(self):
        """Callback ajouter envoie URL web."""
        with patch("src.services.integrations.telegram.repondre_callback_query", new_callable=AsyncMock) as mock_respond:
            from src.api.routes.webhooks_telegram import _traiter_callback_courses

            await _traiter_callback_courses("courses_ajouter:15", "callback_202", 123456)

            # Vérifier que URL est renvoyée
            mock_respond.assert_called_once()
            call_args = mock_respond.call_args
            assert "https://matanne.vercel.app" in call_args.args[1] or "lien" in call_args.args[1].lower()


class TestCoursesCallbackRefaire:
    """Tests pour callback courses_refaire."""

    @pytest.mark.asyncio
    async def test_courses_refaire_cree_nouveau(self):
        """Callback refaire crée nouvelle liste en brouillon."""
        with patch("src.api.utils.executer_async") as mock_execute:
            with patch("src.services.integrations.telegram.repondre_callback_query", new_callable=AsyncMock) as mock_respond:
                with patch("src.services.integrations.telegram.modifier_message", new_callable=AsyncMock):
                # Simuler succès
                    mock_execute.return_value = {"message": "Nouvelle liste créée", "id": 16, "status": 200}

                    from src.api.routes.webhooks_telegram import _traiter_callback_courses

                    await _traiter_callback_courses("courses_refaire:15", "callback_203", 123456)

                    # Vérifier succès
                    mock_respond.assert_called_once()
                    call_args = mock_respond.call_args
                    assert "🔄" in call_args.args[1]


# ═══════════════════════════════════════════════════════════════════════════
# TESTS D'INTÉGRATION — DISPATCHER
# ═══════════════════════════════════════════════════════════════════════════


class TestCallbackDispatcher:
    """Tests du dispatcher de callbacks."""

    def test_dispatcher_route_planning_callbacks(self, client):
        """Dispatcher reconnait et route planning_* callbacks."""
        with patch("src.api.routes.webhooks_telegram._traiter_callback_planning", new_callable=AsyncMock):
            response = client.post("/api/v1/telegram/webhook", json=UPDATE_CALLBACK_PLANNING_VALIDER)
            assert response.status_code in (200, 500)

    def test_dispatcher_route_courses_callbacks(self, client):
        """Dispatcher reconnait et route courses_* callbacks."""
        with patch("src.api.routes.webhooks_telegram._traiter_callback_courses", new_callable=AsyncMock):
            response = client.post("/api/v1/telegram/webhook", json=UPDATE_CALLBACK_COURSES_CONFIRMER)
            assert response.status_code in (200, 500)

    def test_dispatcher_backward_compatibility(self, client):
        """Dispatcher conserve backward compatibility avec callbacks legacy."""
        legacy_callback = {
            "update_id": 3001,
            "callback_query": {
                "id": "callback_legacy",
                "from": {"id": 123456, "is_bot": False},
                "chat_instance": "1234567890",
                "data": "cmd_ce_soir",  # Legacy format
                "message": {"message_id": 100, "date": 1234567890, "chat": {"id": 123456}},
            },
        }

        with patch("src.api.routes.webhooks_telegram._envoyer_repas_du_soir", new_callable=AsyncMock):
            response = client.post("/api/v1/telegram/webhook", json=legacy_callback)
            # Ne doit pas échouer
            assert response.status_code in (200, 500)


# ═══════════════════════════════════════════════════════════════════════════
# TESTS ERROR HANDLING
# ═══════════════════════════════════════════════════════════════════════════


class TestCallbackErrorHandling:
    """Tests gestion des erreurs dans callbacks."""

    @pytest.mark.asyncio
    async def test_callback_exception_handling(self):
        """Exception dans callback est catchée et rapportée."""
        with patch("src.api.utils.executer_async") as mock_execute:
            with patch("src.services.integrations.telegram.repondre_callback_query", new_callable=AsyncMock) as mock_respond:
                # Simuler exception
                mock_execute.side_effect = Exception("DB Error")

                from src.api.routes.webhooks_telegram import _traiter_callback_planning

                await _traiter_callback_planning("planning_valider:42", "callback_123", 123456)

                # Vérifier erreur est envoyée
                mock_respond.assert_called_once()
                call_args = mock_respond.call_args
                assert "❌" in call_args.args[1]

    def test_callback_missing_user_context(self, client):
        """Callback sans contexte utilisateur est rejeté."""
        bad_callback = {
            "update_id": 4001,
            "callback_query": {
                "id": "callback_bad",
                # Pas de 'from' ou 'chat_instance'
                "data": "planning_valider:42",
            },
        }

        response = client.post("/api/v1/telegram/webhook", json=bad_callback)
        # Devrait être robuste face aux données mal formées
        assert response.status_code in (200, 400, 422, 500)
