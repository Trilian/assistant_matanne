"""
Tests pour src/core/ai/client.py (ClientIA)

Tests couvrant:
- Initialisation lazy loading
- Appels API avec retry et cache
- Gestion d'erreurs (rate limit, API, réseau)
- Méthodes métier (discuter, etc.)
- Helpers et singleton
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from httpx import HTTPError as HttpXError

from src.core.ai.client import ClientIA, obtenir_client_ia
from src.core.errors import ErreurServiceIA, ErreurLimiteDebit


# ═══════════════════════════════════════════════════════════
# SECTION 1: TESTS INITIALISATION & CONFIG LAZY LOADING
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestClientIAInit:
    """Tests d'initialisation et lazy loading."""

    def test_client_creation(self):
        """Test création du client."""
        client = ClientIA()
        assert client is not None
        assert client._config_loaded is False
        assert client.cle_api is None

    def test_client_lazy_loading(self):
        """Test que la config n'est pas chargée au démarrage."""
        client = ClientIA()
        # Config ne doit pas être chargée immédiatement
        assert client.cle_api is None
        assert client.modele is None

    @patch('src.core.ai.client.obtenir_parametres')
    def test_ensure_config_loaded_success(self, mock_params):
        """Test chargement réussi de la config."""
        mock_params.return_value = MagicMock(
            MISTRAL_API_KEY="test_key_123",
            MISTRAL_MODEL="mistral-small",
            MISTRAL_BASE_URL="https://api.mistral.ai/v1",
            MISTRAL_TIMEOUT=30,
        )
        
        client = ClientIA()
        client._ensure_config_loaded()
        
        assert client._config_loaded is True
        assert client.cle_api == "test_key_123"
        assert client.modele == "mistral-small"

    @patch('src.core.ai.client.obtenir_parametres')
    def test_ensure_config_loaded_missing_api_key(self, mock_params):
        """Test gestion de clé API manquante."""
        mock_params.side_effect = ValueError("MISTRAL_API_KEY non trouvée")
        
        client = ClientIA()
        
        with pytest.raises(ValueError):
            client._ensure_config_loaded()
        
        assert client.cle_api is None
        assert client._config_loaded is False

    def test_singleton_obtenir_client_ia(self):
        """Test que obtenir_client_ia retourne un singleton."""
        client1 = obtenir_client_ia()
        client2 = obtenir_client_ia()
        
        assert client1 is client2


# ═══════════════════════════════════════════════════════════
# SECTION 2: TESTS APPELS API AVEC MOCKS HTTPX
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestClientIAAppels:
    """Tests des appels API."""

    @pytest.mark.asyncio
    @patch('src.core.ai.client.obtenir_parametres')
    @patch('src.core.ai.client.httpx.AsyncClient')
    async def test_appel_simple(self, mock_async_client, mock_params):
        """Test un appel API simple."""
        # Configurer les mocks
        mock_params.return_value = MagicMock(
            MISTRAL_API_KEY="test_key",
            MISTRAL_MODEL="mistral-small",
            MISTRAL_BASE_URL="https://api.mistral.ai/v1",
            MISTRAL_TIMEOUT=30,
        )
        
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Réponse test"}}]
        }
        mock_response.raise_for_status = MagicMock()
        
        mock_client_instance = AsyncMock()
        mock_client_instance.post = AsyncMock(return_value=mock_response)
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        
        mock_async_client.return_value = mock_client_instance
        
        # Créer le client et appeler
        client = ClientIA()
        
        with patch('src.core.cache.LimiteDebit.peut_appeler', return_value=(True, "")):
            with patch('src.core.cache.LimiteDebit.enregistrer_appel'):
                with patch('src.core.ai.client.CacheIA.obtenir', return_value=None):
                    with patch('src.core.ai.client.CacheIA.definir'):
                        reponse = await client.appeler(
                            prompt="Test prompt",
                            prompt_systeme="Test system",
                        )
        
        assert reponse == "Réponse test"

    @pytest.mark.asyncio
    @patch('src.core.ai.client.obtenir_parametres')
    async def test_appel_avec_rate_limit(self, mock_params):
        """Test que rate limit est vérifiée."""
        mock_params.return_value = MagicMock(
            MISTRAL_API_KEY="test_key",
            MISTRAL_MODEL="mistral-small",
            MISTRAL_BASE_URL="https://api.mistral.ai/v1",
            MISTRAL_TIMEOUT=30,
        )
        
        client = ClientIA()
        
        with patch('src.core.cache.LimiteDebit.peut_appeler', 
                   return_value=(False, "Rate limit dépassé")):
            with pytest.raises(ErreurLimiteDebit):
                await client.appeler(prompt="Test")

    @pytest.mark.asyncio
    @patch('src.core.ai.client.obtenir_parametres')
    @patch('src.core.ai.client.httpx.AsyncClient')
    async def test_appel_avec_retry(self, mock_async_client, mock_params):
        """Test retry automatique sur erreur réseau."""
        mock_params.return_value = MagicMock(
            MISTRAL_API_KEY="test_key",
            MISTRAL_MODEL="mistral-small",
            MISTRAL_BASE_URL="https://api.mistral.ai/v1",
            MISTRAL_TIMEOUT=30,
        )
        
        # Première tentative: erreur, deuxième: succès
        mock_response_error = MagicMock()
        mock_response_error.raise_for_status.side_effect = HttpXError("Connection refused")
        
        mock_response_ok = MagicMock()
        mock_response_ok.json.return_value = {
            "choices": [{"message": {"content": "Succès après retry"}}]
        }
        mock_response_ok.raise_for_status = MagicMock()
        
        mock_client_instance = AsyncMock()
        # Premier appel: erreur, deuxième: succès
        mock_client_instance.post = AsyncMock(
            side_effect=[mock_response_error, mock_response_ok]
        )
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        
        mock_async_client.return_value = mock_client_instance
        
        client = ClientIA()
        
        with patch('src.core.ai.client.asyncio.sleep', new_callable=AsyncMock):
            with patch('src.core.cache.LimiteDebit.peut_appeler', return_value=(True, "")):
                with patch('src.core.cache.LimiteDebit.enregistrer_appel'):
                    with patch('src.core.ai.client.CacheIA.obtenir', return_value=None):
                        with patch('src.core.ai.client.CacheIA.definir'):
                            reponse = await client.appeler(
                                prompt="Test",
                                max_tentatives=2,
                            )
        
        assert reponse == "Succès après retry"


# ═══════════════════════════════════════════════════════════
# SECTION 3: TESTS CACHE
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestClientIACache:
    """Tests du cache IA."""

    @pytest.mark.asyncio
    @patch('src.core.ai.client.obtenir_parametres')
    async def test_appel_avec_cache_hit(self, mock_params):
        """Test que le cache est utilisé."""
        mock_params.return_value = MagicMock(
            MISTRAL_API_KEY="test_key",
            MISTRAL_MODEL="mistral-small",
            MISTRAL_BASE_URL="https://api.mistral.ai/v1",
            MISTRAL_TIMEOUT=30,
        )
        
        client = ClientIA()
        
        with patch('src.core.cache.LimiteDebit.peut_appeler', return_value=(True, "")):
            with patch('src.core.ai.client.CacheIA.obtenir', return_value="Réponse en cache"):
                reponse = await client.appeler(
                    prompt="Test",
                    utiliser_cache=True,
                )
        
        assert reponse == "Réponse en cache"

    @pytest.mark.asyncio
    @patch('src.core.ai.client.obtenir_parametres')
    async def test_appel_sans_cache(self, mock_params):
        """Test appel sans cache."""
        mock_params.return_value = MagicMock(
            MISTRAL_API_KEY="test_key",
            MISTRAL_MODEL="mistral-small",
            MISTRAL_BASE_URL="https://api.mistral.ai/v1",
            MISTRAL_TIMEOUT=30,
        )
        
        client = ClientIA()
        
        with patch('src.core.cache.LimiteDebit.peut_appeler', return_value=(True, "")):
            with patch('src.core.ai.client.CacheIA.obtenir', return_value=None) as mock_cache:
                with patch.object(client, '_effectuer_appel', 
                                 new_callable=AsyncMock, 
                                 return_value="Réponse fraîche"):
                    with patch('src.core.cache.LimiteDebit.enregistrer_appel'):
                        reponse = await client.appeler(
                            prompt="Test",
                            utiliser_cache=False,
                        )
        
        assert reponse == "Réponse fraîche"


# ═══════════════════════════════════════════════════════════
# SECTION 4: TESTS MÉTHODES MÉTIER
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestClientIAMetier:
    """Tests des méthodes métier."""

    @pytest.mark.asyncio
    @patch('src.core.ai.client.obtenir_parametres')
    async def test_discuter(self, mock_params):
        """Test la méthode discuter."""
        mock_params.return_value = MagicMock(
            MISTRAL_API_KEY="test_key",
            MISTRAL_MODEL="mistral-small",
            MISTRAL_BASE_URL="https://api.mistral.ai/v1",
            MISTRAL_TIMEOUT=30,
        )
        
        client = ClientIA()
        
        with patch.object(client, 'appeler', 
                         new_callable=AsyncMock,
                         return_value="Réponse conversation") as mock_appel:
            reponse = await client.discuter("Quel repas suggères-tu?")
        
        assert reponse == "Réponse conversation"
        mock_appel.assert_called_once()

    @pytest.mark.asyncio
    @patch('src.core.ai.client.obtenir_parametres')
    async def test_discuter_avec_historique(self, mock_params):
        """Test discuter avec historique."""
        mock_params.return_value = MagicMock(
            MISTRAL_API_KEY="test_key",
            MISTRAL_MODEL="mistral-small",
            MISTRAL_BASE_URL="https://api.mistral.ai/v1",
            MISTRAL_TIMEOUT=30,
        )
        
        client = ClientIA()
        historique = [
            {"role": "user", "content": "Bonjour"},
            {"role": "assistant", "content": "Bonjour!"},
        ]
        
        with patch.object(client, 'appeler', 
                         new_callable=AsyncMock,
                         return_value="Réponse") as mock_appel:
            await client.discuter("Quoi de neuf?", historique=historique)
        
        # Vérifier que le prompt contient l'historique
        call_args = mock_appel.call_args
        assert "Historique" in call_args.kwargs['prompt'] or "Historique" in call_args.args[0]


# ═══════════════════════════════════════════════════════════
# SECTION 5: TESTS HELPERS
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestClientIAHelpers:
    """Tests des méthodes helpers."""

    @patch('src.core.ai.client.obtenir_parametres')
    def test_obtenir_infos_modele(self, mock_params):
        """Test obtention des infos modèle."""
        mock_params.return_value = MagicMock(
            MISTRAL_API_KEY="test_key",
            MISTRAL_MODEL="mistral-small",
            MISTRAL_BASE_URL="https://api.mistral.ai/v1",
            MISTRAL_TIMEOUT=30,
        )
        
        client = ClientIA()
        infos = client.obtenir_infos_modele()
        
        assert infos["modele"] == "mistral-small"
        assert infos["url_base"] == "https://api.mistral.ai/v1"
        assert infos["timeout"] == 30


# ═══════════════════════════════════════════════════════════
# SECTION 6: TESTS D'INTÉGRATION
# ═══════════════════════════════════════════════════════════


@pytest.mark.integration
class TestClientIAIntegration:
    """Tests d'intégration."""

    @pytest.mark.asyncio
    @patch('src.core.ai.client.obtenir_parametres')
    async def test_workflow_complet_appel(self, mock_params):
        """Test workflow complet d'un appel."""
        mock_params.return_value = MagicMock(
            MISTRAL_API_KEY="test_key",
            MISTRAL_MODEL="mistral-small",
            MISTRAL_BASE_URL="https://api.mistral.ai/v1",
            MISTRAL_TIMEOUT=30,
        )
        
        client = ClientIA()
        
        # Workflow: cache miss → appel API → cache store
        with patch('src.core.cache.LimiteDebit.peut_appeler', return_value=(True, "")):
            with patch('src.core.ai.client.CacheIA.obtenir', return_value=None):
                with patch('src.core.ai.client.CacheIA.definir') as mock_cache_store:
                    with patch.object(client, '_effectuer_appel',
                                     new_callable=AsyncMock,
                                     return_value="Réponse API"):
                        with patch('src.core.cache.LimiteDebit.enregistrer_appel'):
                            reponse = await client.appeler(
                                prompt="Question?",
                                utiliser_cache=True,
                            )
        
        assert reponse == "Réponse API"
        mock_cache_store.assert_called_once()


# ═══════════════════════════════════════════════════════════
# SECTION 7: TESTS GENERER JSON
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestClientIAGenererJson:
    """Tests pour generer_json() - wrapper synchrone."""

    @patch('src.core.ai.client.obtenir_parametres')
    def test_generer_json_success(self, mock_params):
        """Test génération JSON réussie."""
        mock_params.return_value = MagicMock(
            MISTRAL_API_KEY="test_key",
            MISTRAL_MODEL="mistral-small",
            MISTRAL_BASE_URL="https://api.mistral.ai/v1",
            MISTRAL_TIMEOUT=30,
        )
        
        client = ClientIA()
        
        # Mock l'appel async
        with patch.object(client, 'appeler', new_callable=AsyncMock) as mock_appeler:
            mock_appeler.return_value = '{"recette": "Tarte aux pommes", "portions": 6}'
            
            result = client.generer_json("Génère une recette")
            
            assert result is not None
            assert isinstance(result, dict)
            assert result["recette"] == "Tarte aux pommes"
            assert result["portions"] == 6

    @patch('src.core.ai.client.obtenir_parametres')
    def test_generer_json_with_code_blocks(self, mock_params):
        """Test parsing JSON avec blocs de code markdown."""
        mock_params.return_value = MagicMock(
            MISTRAL_API_KEY="test_key",
            MISTRAL_MODEL="mistral-small",
            MISTRAL_BASE_URL="https://api.mistral.ai/v1",
            MISTRAL_TIMEOUT=30,
        )
        
        client = ClientIA()
        
        with patch.object(client, 'appeler', new_callable=AsyncMock) as mock_appeler:
            mock_appeler.return_value = '```json\n{"nom": "Test"}\n```'
            
            result = client.generer_json("Test")
            
            assert result is not None
            assert result["nom"] == "Test"

    @patch('src.core.ai.client.obtenir_parametres')
    def test_generer_json_invalid_json(self, mock_params):
        """Test retour None si JSON invalide."""
        mock_params.return_value = MagicMock(
            MISTRAL_API_KEY="test_key",
            MISTRAL_MODEL="mistral-small",
            MISTRAL_BASE_URL="https://api.mistral.ai/v1",
            MISTRAL_TIMEOUT=30,
        )
        
        client = ClientIA()
        
        with patch.object(client, 'appeler', new_callable=AsyncMock) as mock_appeler:
            mock_appeler.return_value = 'Ceci nest pas du JSON valide {'
            
            result = client.generer_json("Test")
            
            # JSON invalide retourne la réponse brute ou None
            assert result is None or isinstance(result, str)

    @patch('src.core.ai.client.obtenir_parametres')
    def test_generer_json_error_returns_none(self, mock_params):
        """Test retour None en cas d'erreur."""
        mock_params.return_value = MagicMock(
            MISTRAL_API_KEY="test_key",
            MISTRAL_MODEL="mistral-small",
            MISTRAL_BASE_URL="https://api.mistral.ai/v1",
            MISTRAL_TIMEOUT=30,
        )
        
        client = ClientIA()
        
        with patch.object(client, 'appeler', new_callable=AsyncMock) as mock_appeler:
            mock_appeler.side_effect = Exception("Erreur réseau")
            
            result = client.generer_json("Test")
            
            assert result is None


# ═══════════════════════════════════════════════════════════
# SECTION 8: TESTS CHAT WITH VISION (OCR)
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestClientIAChatWithVision:
    """Tests pour chat_with_vision() - OCR."""

    @pytest.mark.asyncio
    @patch('src.core.ai.client.obtenir_parametres')
    @patch('src.core.ai.client.httpx.AsyncClient')
    async def test_chat_with_vision_success(self, mock_async_client, mock_params):
        """Test appel vision réussi."""
        mock_params.return_value = MagicMock(
            MISTRAL_API_KEY="test_key",
            MISTRAL_MODEL="mistral-small",
            MISTRAL_BASE_URL="https://api.mistral.ai/v1",
            MISTRAL_TIMEOUT=30,
        )
        
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Texte extrait de l'image"}}]
        }
        mock_response.raise_for_status = MagicMock()
        
        mock_client_instance = AsyncMock()
        mock_client_instance.post = AsyncMock(return_value=mock_response)
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        
        mock_async_client.return_value = mock_client_instance
        
        client = ClientIA()
        result = await client.chat_with_vision(
            prompt="Extrais le texte",
            image_base64="dGVzdA==",  # "test" en base64
        )
        
        assert result == "Texte extrait de l'image"

    @pytest.mark.asyncio
    @patch('src.core.ai.client.obtenir_parametres')
    async def test_chat_with_vision_no_api_key(self, mock_params):
        """Test erreur si pas de clé API."""
        mock_params.side_effect = ValueError("Pas de clé")
        
        client = ClientIA()
        
        with pytest.raises(ValueError):
            await client.chat_with_vision(
                prompt="Test",
                image_base64="dGVzdA==",
            )

    @pytest.mark.asyncio
    @patch('src.core.ai.client.obtenir_parametres')
    @patch('src.core.ai.client.httpx.AsyncClient')
    async def test_chat_with_vision_empty_response(self, mock_async_client, mock_params):
        """Test erreur si réponse vide."""
        mock_params.return_value = MagicMock(
            MISTRAL_API_KEY="test_key",
            MISTRAL_MODEL="mistral-small",
            MISTRAL_BASE_URL="https://api.mistral.ai/v1",
            MISTRAL_TIMEOUT=30,
        )
        
        mock_response = MagicMock()
        mock_response.json.return_value = {"choices": []}  # Réponse vide
        mock_response.raise_for_status = MagicMock()
        
        mock_client_instance = AsyncMock()
        mock_client_instance.post = AsyncMock(return_value=mock_response)
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        
        mock_async_client.return_value = mock_client_instance
        
        client = ClientIA()
        
        with pytest.raises(ErreurServiceIA):
            await client.chat_with_vision(
                prompt="Test",
                image_base64="dGVzdA==",
            )


# ═══════════════════════════════════════════════════════════
# SECTION 9: TESTS RETRY & ERROR HANDLING
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestClientIARetryLogic:
    """Tests pour la logique de retry et gestion d'erreurs."""

    @pytest.mark.asyncio
    @patch('src.core.ai.client.obtenir_parametres')
    @patch('src.core.ai.client.httpx.AsyncClient')
    async def test_appel_all_retries_fail(self, mock_async_client, mock_params):
        """Test échec après toutes les tentatives."""
        mock_params.return_value = MagicMock(
            MISTRAL_API_KEY="test_key",
            MISTRAL_MODEL="mistral-small",
            MISTRAL_BASE_URL="https://api.mistral.ai/v1",
            MISTRAL_TIMEOUT=30,
        )
        
        # Toutes les tentatives échouent
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = HttpXError("Server error")
        
        mock_client_instance = AsyncMock()
        mock_client_instance.post = AsyncMock(return_value=mock_response)
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        
        mock_async_client.return_value = mock_client_instance
        
        client = ClientIA()
        
        with patch('src.core.ai.client.asyncio.sleep', new_callable=AsyncMock):
            with patch('src.core.cache.LimiteDebit.peut_appeler', return_value=(True, "")):
                with patch('src.core.ai.client.CacheIA.obtenir', return_value=None):
                    with pytest.raises(ErreurServiceIA) as exc_info:
                        await client.appeler(
                            prompt="Test",
                            max_tentatives=3,
                        )
        
        assert "Erreur API Mistral" in str(exc_info.value)

    @pytest.mark.asyncio
    @patch('src.core.ai.client.obtenir_parametres')
    async def test_appel_unexpected_error(self, mock_params):
        """Test erreur inattendue (non HTTP)."""
        mock_params.return_value = MagicMock(
            MISTRAL_API_KEY="test_key",
            MISTRAL_MODEL="mistral-small",
            MISTRAL_BASE_URL="https://api.mistral.ai/v1",
            MISTRAL_TIMEOUT=30,
        )
        
        client = ClientIA()
        
        with patch('src.core.cache.LimiteDebit.peut_appeler', return_value=(True, "")):
            with patch('src.core.ai.client.CacheIA.obtenir', return_value=None):
                with patch.object(client, '_effectuer_appel', 
                                new_callable=AsyncMock,
                                side_effect=RuntimeError("Erreur système")):
                    with pytest.raises(ErreurServiceIA) as exc_info:
                        await client.appeler(prompt="Test")
        
        assert "Erreur inattendue" in str(exc_info.value)

    @pytest.mark.asyncio
    @patch('src.core.ai.client.obtenir_parametres')
    @patch('src.core.ai.client.httpx.AsyncClient')
    async def test_effectuer_appel_empty_response(self, mock_async_client, mock_params):
        """Test _effectuer_appel avec réponse vide."""
        mock_params.return_value = MagicMock(
            MISTRAL_API_KEY="test_key",
            MISTRAL_MODEL="mistral-small",
            MISTRAL_BASE_URL="https://api.mistral.ai/v1",
            MISTRAL_TIMEOUT=30,
        )
        
        mock_response = MagicMock()
        mock_response.json.return_value = {"choices": []}  # Pas de contenu
        mock_response.raise_for_status = MagicMock()
        
        mock_client_instance = AsyncMock()
        mock_client_instance.post = AsyncMock(return_value=mock_response)
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        
        mock_async_client.return_value = mock_client_instance
        
        client = ClientIA()
        
        with pytest.raises(ErreurServiceIA) as exc_info:
            await client._effectuer_appel(
                prompt="Test",
                prompt_systeme="",
                temperature=0.7,
                max_tokens=100,
            )
        
        assert "pas de contenu" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    @patch('src.core.ai.client.obtenir_parametres')
    async def test_effectuer_appel_no_api_key(self, mock_params):
        """Test _effectuer_appel sans clé API."""
        mock_params.return_value = MagicMock(
            MISTRAL_API_KEY=None,  # Pas de clé
            MISTRAL_MODEL="mistral-small",
            MISTRAL_BASE_URL="https://api.mistral.ai/v1",
            MISTRAL_TIMEOUT=30,
        )
        
        client = ClientIA()
        client._config_loaded = True  # Forcer le rechargement
        client.cle_api = None
        
        with pytest.raises(ErreurServiceIA) as exc_info:
            await client._effectuer_appel(
                prompt="Test",
                prompt_systeme="",
                temperature=0.7,
                max_tokens=100,
            )
        
        assert "Clé API" in str(exc_info.value)

    @pytest.mark.asyncio
    @patch('src.core.ai.client.obtenir_parametres')
    async def test_effectuer_appel_no_base_url(self, mock_params):
        """Test _effectuer_appel sans URL de base."""
        mock_params.return_value = MagicMock(
            MISTRAL_API_KEY="test_key",
            MISTRAL_MODEL="mistral-small",
            MISTRAL_BASE_URL=None,  # Pas d'URL
            MISTRAL_TIMEOUT=30,
        )
        
        client = ClientIA()
        client._config_loaded = True
        client.cle_api = "test_key"
        client.url_base = None
        
        with pytest.raises(ErreurServiceIA) as exc_info:
            await client._effectuer_appel(
                prompt="Test",
                prompt_systeme="",
                temperature=0.7,
                max_tokens=100,
            )
        
        assert "URL" in str(exc_info.value) or "configuration" in str(exc_info.value).lower()
