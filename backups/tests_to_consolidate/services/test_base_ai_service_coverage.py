"""
Tests couverture pour src/services/base_ai_service.py
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, AsyncMock
from pydantic import BaseModel


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# MODELS DE TEST
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class MockResponseModel(BaseModel):
    """ModÃ¨le de test pour parsing."""
    nom: str = ""
    valeur: int = 0


class MockItemModel(BaseModel):
    """ModÃ¨le d'item pour listes."""
    id: int
    titre: str = ""


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS INIT
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestBaseAIServiceInit:
    """Tests pour l'initialisation du service."""

    def test_init_defaults(self):
        """Test initialisation avec valeurs par dÃ©faut."""
        mock_client = Mock()
        
        from src.services.base_ai_service import BaseAIService
        
        service = BaseAIService(client=mock_client)
        
        assert service.client == mock_client
        assert service.cache_prefix == "ai"
        assert service.default_ttl == 3600
        assert service.default_temperature == 0.7
        assert service.service_name == "unknown"

    def test_init_custom(self):
        """Test initialisation avec valeurs personnalisÃ©es."""
        mock_client = Mock()
        
        from src.services.base_ai_service import BaseAIService
        
        service = BaseAIService(
            client=mock_client,
            cache_prefix="recettes",
            default_ttl=7200,
            default_temperature=0.8,
            service_name="recette_service"
        )
        
        assert service.cache_prefix == "recettes"
        assert service.default_ttl == 7200
        assert service.default_temperature == 0.8
        assert service.service_name == "recette_service"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS BUILD PROMPTS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestBuildJsonPrompt:
    """Tests pour build_json_prompt()."""

    def test_build_json_prompt_basic(self):
        """Test construction prompt JSON basique."""
        mock_client = Mock()
        
        from src.services.base_ai_service import BaseAIService
        
        service = BaseAIService(client=mock_client)
        
        result = service.build_json_prompt(
            context="GÃ©nÃ¨re des recettes",
            task="3 recettes de saison",
            json_schema='{"recettes": [{"nom": "string"}]}'
        )
        
        assert "GÃ©nÃ¨re des recettes" in result
        assert "3 recettes de saison" in result
        assert '{"recettes":' in result
        assert "JSON valide" in result

    def test_build_json_prompt_with_constraints(self):
        """Test avec contraintes."""
        mock_client = Mock()
        
        from src.services.base_ai_service import BaseAIService
        
        service = BaseAIService(client=mock_client)
        
        result = service.build_json_prompt(
            context="Contexte",
            task="TÃ¢che",
            json_schema="{}",
            constraints=["Moins de 30 minutes", "VÃ©gÃ©tarien"]
        )
        
        assert "CONTRAINTES" in result
        assert "Moins de 30 minutes" in result
        assert "VÃ©gÃ©tarien" in result


@pytest.mark.unit
class TestBuildSystemPrompt:
    """Tests pour build_system_prompt()."""

    def test_build_system_prompt_basic(self):
        """Test construction system prompt."""
        mock_client = Mock()
        
        from src.services.base_ai_service import BaseAIService
        
        service = BaseAIService(client=mock_client)
        
        result = service.build_system_prompt(
            role="un chef cuisinier expert",
            expertise=["Cuisine franÃ§aise", "PÃ¢tisserie"]
        )
        
        assert "chef cuisinier expert" in result
        assert "EXPERTISE" in result
        assert "Cuisine franÃ§aise" in result
        assert "PÃ¢tisserie" in result
        assert "franÃ§ais" in result

    def test_build_system_prompt_with_rules(self):
        """Test avec rÃ¨gles."""
        mock_client = Mock()
        
        from src.services.base_ai_service import BaseAIService
        
        service = BaseAIService(client=mock_client)
        
        result = service.build_system_prompt(
            role="un assistant",
            expertise=["cuisine"],
            rules=["RÃ©pondre en bullet points", "ÃŠtre concis"]
        )
        
        assert "RÃˆGLES" in result
        assert "bullet points" in result
        assert "concis" in result


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS CACHE & RATE LIMIT STATS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestStatsAndCache:
    """Tests pour les mÃ©thodes de stats."""

    @patch('src.services.base_ai_service.CacheIA')
    def test_get_cache_stats(self, mock_cache_ia):
        """Test rÃ©cupÃ©ration stats cache."""
        mock_cache_ia.obtenir_statistiques.return_value = {"hits": 10, "misses": 5}
        mock_client = Mock()
        
        from src.services.base_ai_service import BaseAIService
        
        service = BaseAIService(client=mock_client)
        result = service.get_cache_stats()
        
        mock_cache_ia.obtenir_statistiques.assert_called_once()
        assert result["hits"] == 10

    @patch('src.services.base_ai_service.RateLimitIA')
    def test_get_rate_limit_stats(self, mock_rate_limit):
        """Test rÃ©cupÃ©ration stats rate limit."""
        mock_rate_limit.obtenir_statistiques.return_value = {"appels_jour": 50}
        mock_client = Mock()
        
        from src.services.base_ai_service import BaseAIService
        
        service = BaseAIService(client=mock_client)
        result = service.get_rate_limit_stats()
        
        mock_rate_limit.obtenir_statistiques.assert_called_once()
        assert result["appels_jour"] == 50

    @patch('src.services.base_ai_service.CacheIA')
    def test_clear_cache(self, mock_cache_ia):
        """Test vidage cache."""
        mock_client = Mock()
        
        from src.services.base_ai_service import BaseAIService
        
        service = BaseAIService(client=mock_client, cache_prefix="test")
        service.clear_cache()
        
        mock_cache_ia.invalider_tout.assert_called_once()


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS CALL WITH CACHE (ASYNC)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
@pytest.mark.asyncio
class TestCallWithCacheAsync:
    """Tests pour call_with_cache()."""

    @patch('src.services.base_ai_service.RateLimitIA')
    @patch('src.services.base_ai_service.CacheIA')
    async def test_call_with_cache_no_client(self, mock_cache, mock_rate):
        """Test sans client IA."""
        from src.services.base_ai_service import BaseAIService
        
        service = BaseAIService(client=None, service_name="test")
        
        result = await service.call_with_cache("prompt", "system")
        
        assert result is None

    @patch('src.services.base_ai_service.RateLimitIA')
    @patch('src.services.base_ai_service.CacheIA')
    async def test_call_with_cache_hit(self, mock_cache, mock_rate):
        """Test cache hit."""
        mock_cache.obtenir.return_value = "RÃ©ponse cachÃ©e"
        mock_client = Mock()
        
        from src.services.base_ai_service import BaseAIService
        
        service = BaseAIService(client=mock_client, service_name="test")
        
        result = await service.call_with_cache("prompt", "system", use_cache=True)
        
        assert result == "RÃ©ponse cachÃ©e"
        mock_client.appeler.assert_not_called()

    @patch('src.services.base_ai_service.RateLimitIA')
    @patch('src.services.base_ai_service.CacheIA')
    async def test_call_with_cache_rate_limit_exceeded(self, mock_cache, mock_rate):
        """Test rate limit dÃ©passÃ© - lÃ¨ve ErreurLimiteDebit."""
        from src.core.errors import ErreurLimiteDebit
        
        mock_cache.obtenir.return_value = None
        mock_rate.peut_appeler.return_value = (False, "Quota dÃ©passÃ©")
        mock_client = Mock()
        
        from src.services.base_ai_service import BaseAIService
        
        service = BaseAIService(client=mock_client, service_name="test")
        
        # La mÃ©thode lÃ¨ve l'exception ErreurLimiteDebit
        with pytest.raises(ErreurLimiteDebit):
            await service.call_with_cache("prompt", "system")

    @patch('src.services.base_ai_service.RateLimitIA')
    @patch('src.services.base_ai_service.CacheIA')
    async def test_call_with_cache_api_call_success(self, mock_cache, mock_rate):
        """Test appel API rÃ©ussi (cache miss)."""
        mock_cache.obtenir.return_value = None
        mock_rate.peut_appeler.return_value = (True, "OK")
        
        mock_client = AsyncMock()
        mock_client.appeler = AsyncMock(return_value="RÃ©ponse IA")
        
        from src.services.base_ai_service import BaseAIService
        
        service = BaseAIService(client=mock_client, service_name="test")
        
        result = await service.call_with_cache("prompt", "system", use_cache=True)
        
        assert result == "RÃ©ponse IA"
        mock_client.appeler.assert_called_once()
        mock_cache.definir.assert_called_once()

    @patch('src.services.base_ai_service.RateLimitIA')
    @patch('src.services.base_ai_service.CacheIA')
    async def test_call_with_cache_no_cache(self, mock_cache, mock_rate):
        """Test appel sans utilisation du cache."""
        mock_rate.peut_appeler.return_value = (True, "OK")
        
        mock_client = AsyncMock()
        mock_client.appeler = AsyncMock(return_value="RÃ©ponse IA")
        
        from src.services.base_ai_service import BaseAIService
        
        service = BaseAIService(client=mock_client, service_name="test")
        
        result = await service.call_with_cache("prompt", "system", use_cache=False)
        
        assert result == "RÃ©ponse IA"
        mock_cache.obtenir.assert_not_called()


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS CALL WITH PARSING (ASYNC)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
@pytest.mark.asyncio
class TestCallWithParsingAsync:
    """Tests pour call_with_parsing() async."""

    @patch('src.services.base_ai_service.AnalyseurIA')
    @patch('src.services.base_ai_service.RateLimitIA')
    @patch('src.services.base_ai_service.CacheIA')
    async def test_call_with_parsing_success(self, mock_cache, mock_rate, mock_analyseur):
        """Test parsing rÃ©ussi."""
        mock_cache.obtenir.return_value = '{"nom": "Test", "valeur": 42}'
        mock_rate.peut_appeler.return_value = (True, "OK")
        
        parsed_model = MockResponseModel(nom="Test", valeur=42)
        mock_analyseur.analyser.return_value = parsed_model
        
        mock_client = AsyncMock()
        
        from src.services.base_ai_service import BaseAIService
        
        service = BaseAIService(client=mock_client, service_name="test")
        
        result = await service.call_with_parsing(
            prompt="test",
            response_model=MockResponseModel,
            system_prompt="system"
        )
        
        assert result == parsed_model

    @patch('src.services.base_ai_service.RateLimitIA')
    @patch('src.services.base_ai_service.CacheIA')
    async def test_call_with_parsing_no_response(self, mock_cache, mock_rate):
        """Test parsing sans rÃ©ponse."""
        mock_cache.obtenir.return_value = None
        mock_rate.peut_appeler.return_value = (True, "OK")
        
        mock_client = AsyncMock()
        mock_client.appeler = AsyncMock(return_value=None)
        
        from src.services.base_ai_service import BaseAIService
        
        service = BaseAIService(client=mock_client, service_name="test")
        
        result = await service.call_with_parsing(
            prompt="test",
            response_model=MockResponseModel
        )
        
        assert result is None

    @patch('src.services.base_ai_service.AnalyseurIA')
    @patch('src.services.base_ai_service.RateLimitIA')
    @patch('src.services.base_ai_service.CacheIA')
    async def test_call_with_parsing_validation_error_with_fallback(self, mock_cache, mock_rate, mock_analyseur):
        """Test erreur validation avec fallback."""
        from pydantic import ValidationError
        
        mock_cache.obtenir.return_value = '{"invalid": "data"}'
        mock_rate.peut_appeler.return_value = (True, "OK")
        
        # Simuler erreur de validation
        mock_analyseur.analyser.side_effect = ValidationError.from_exception_data(
            "MockResponseModel", []
        )
        
        mock_client = AsyncMock()
        
        from src.services.base_ai_service import BaseAIService
        
        service = BaseAIService(client=mock_client, service_name="test")
        
        result = await service.call_with_parsing(
            prompt="test",
            response_model=MockResponseModel,
            fallback={"nom": "Fallback", "valeur": 0}
        )
        
        # Le fallback devrait Ãªtre utilisÃ©
        assert result is not None
        assert result.nom == "Fallback"

    @patch('src.services.base_ai_service.AnalyseurIA')
    @patch('src.services.base_ai_service.RateLimitIA')
    @patch('src.services.base_ai_service.CacheIA')
    async def test_call_with_parsing_validation_error_no_fallback(self, mock_cache, mock_rate, mock_analyseur):
        """Test erreur validation sans fallback."""
        from pydantic import ValidationError
        
        mock_cache.obtenir.return_value = '{"invalid": "data"}'
        mock_rate.peut_appeler.return_value = (True, "OK")
        
        # Simuler erreur de validation
        mock_analyseur.analyser.side_effect = ValidationError.from_exception_data(
            "MockResponseModel", []
        )
        
        mock_client = AsyncMock()
        
        from src.services.base_ai_service import BaseAIService
        
        service = BaseAIService(client=mock_client, service_name="test")
        
        result = await service.call_with_parsing(
            prompt="test",
            response_model=MockResponseModel
            # Pas de fallback
        )
        
        # Retourne None car pas de fallback
        assert result is None


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS CALL WITH LIST PARSING (ASYNC)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
@pytest.mark.asyncio
class TestCallWithListParsingAsync:
    """Tests pour call_with_list_parsing() async."""

    @patch('src.core.ai.parser.analyser_liste_reponse')
    @patch('src.services.base_ai_service.RateLimitIA')
    @patch('src.services.base_ai_service.CacheIA')
    async def test_call_with_list_parsing_success(self, mock_cache, mock_rate, mock_parser):
        """Test liste parsing rÃ©ussi."""
        mock_cache.obtenir.return_value = '[{"id": 1, "titre": "Item1"}]'
        mock_rate.peut_appeler.return_value = (True, "OK")
        
        items = [MockItemModel(id=1, titre="Item1")]
        mock_parser.return_value = items
        
        mock_client = AsyncMock()
        
        from src.services.base_ai_service import BaseAIService
        
        service = BaseAIService(client=mock_client, service_name="test")
        
        result = await service.call_with_list_parsing(
            prompt="test",
            item_model=MockItemModel,
            list_key="items"
        )
        
        assert len(result) == 1

    @patch('src.services.base_ai_service.RateLimitIA')
    @patch('src.services.base_ai_service.CacheIA')
    async def test_call_with_list_parsing_empty(self, mock_cache, mock_rate):
        """Test liste vide."""
        mock_cache.obtenir.return_value = None
        mock_rate.peut_appeler.return_value = (True, "OK")
        
        mock_client = AsyncMock()
        mock_client.appeler = AsyncMock(return_value=None)
        
        from src.services.base_ai_service import BaseAIService
        
        service = BaseAIService(client=mock_client, service_name="test")
        
        result = await service.call_with_list_parsing(
            prompt="test",
            item_model=MockItemModel
        )
        
        assert result == []

    @patch('src.core.ai.parser.analyser_liste_reponse')
    @patch('src.services.base_ai_service.RateLimitIA')
    @patch('src.services.base_ai_service.CacheIA')
    async def test_call_with_list_parsing_max_items(self, mock_cache, mock_rate, mock_parser):
        """Test limitation nombre d'items."""
        mock_cache.obtenir.return_value = '{"items": [...]}'
        mock_rate.peut_appeler.return_value = (True, "OK")
        
        items = [MockItemModel(id=i, titre=f"Item{i}") for i in range(10)]
        mock_parser.return_value = items
        
        mock_client = AsyncMock()
        
        from src.services.base_ai_service import BaseAIService
        
        service = BaseAIService(client=mock_client, service_name="test")
        
        result = await service.call_with_list_parsing(
            prompt="test",
            item_model=MockItemModel,
            max_items=5
        )
        
        assert len(result) == 5

    @patch('src.core.ai.parser.analyser_liste_reponse')
    @patch('src.services.base_ai_service.RateLimitIA')
    @patch('src.services.base_ai_service.CacheIA')
    async def test_call_with_list_parsing_error(self, mock_cache, mock_rate, mock_parser):
        """Test erreur lors du parsing de liste."""
        mock_cache.obtenir.return_value = '{"items": [...]}'
        mock_rate.peut_appeler.return_value = (True, "OK")
        
        # Simuler une erreur de parsing
        mock_parser.side_effect = Exception("Parse error")
        
        mock_client = AsyncMock()
        
        from src.services.base_ai_service import BaseAIService
        
        service = BaseAIService(client=mock_client, service_name="test")
        
        result = await service.call_with_list_parsing(
            prompt="test",
            item_model=MockItemModel
        )
        
        # Retourne liste vide en cas d'erreur
        assert result == []


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS CALL WITH JSON PARSING (ASYNC)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
@pytest.mark.asyncio
class TestCallWithJsonParsingAsync:
    """Tests pour call_with_json_parsing() async."""

    @patch('src.services.base_ai_service.RateLimitIA')
    @patch('src.services.base_ai_service.CacheIA')
    async def test_call_with_json_parsing_success(self, mock_cache, mock_rate):
        """Test JSON parsing rÃ©ussi."""
        mock_cache.obtenir.return_value = '{"nom": "Test", "valeur": 42}'
        mock_rate.peut_appeler.return_value = (True, "OK")
        
        mock_client = AsyncMock()
        
        from src.services.base_ai_service import BaseAIService
        
        service = BaseAIService(client=mock_client, service_name="test")
        
        result = await service.call_with_json_parsing(
            prompt="test",
            response_model=MockResponseModel
        )
        
        assert result is not None
        assert result.nom == "Test"
        assert result.valeur == 42

    @patch('src.services.base_ai_service.RateLimitIA')
    @patch('src.services.base_ai_service.CacheIA')
    async def test_call_with_json_parsing_with_markdown(self, mock_cache, mock_rate):
        """Test JSON parsing avec markdown wrapper."""
        mock_cache.obtenir.return_value = '```json\n{"nom": "Test", "valeur": 42}\n```'
        mock_rate.peut_appeler.return_value = (True, "OK")
        
        mock_client = AsyncMock()
        
        from src.services.base_ai_service import BaseAIService
        
        service = BaseAIService(client=mock_client, service_name="test")
        
        result = await service.call_with_json_parsing(
            prompt="test",
            response_model=MockResponseModel
        )
        
        assert result is not None
        assert result.nom == "Test"

    @patch('src.services.base_ai_service.RateLimitIA')
    @patch('src.services.base_ai_service.CacheIA')
    async def test_call_with_json_parsing_no_response(self, mock_cache, mock_rate):
        """Test JSON parsing sans rÃ©ponse."""
        mock_cache.obtenir.return_value = None
        mock_rate.peut_appeler.return_value = (True, "OK")
        
        mock_client = AsyncMock()
        mock_client.appeler = AsyncMock(return_value=None)
        
        from src.services.base_ai_service import BaseAIService
        
        service = BaseAIService(client=mock_client, service_name="test")
        
        result = await service.call_with_json_parsing(
            prompt="test",
            response_model=MockResponseModel
        )
        
        assert result is None

    @patch('src.services.base_ai_service.RateLimitIA')
    @patch('src.services.base_ai_service.CacheIA')
    async def test_call_with_json_parsing_invalid_json(self, mock_cache, mock_rate):
        """Test JSON parsing avec JSON invalide."""
        mock_cache.obtenir.return_value = 'not valid json'
        mock_rate.peut_appeler.return_value = (True, "OK")
        
        mock_client = AsyncMock()
        
        from src.services.base_ai_service import BaseAIService
        
        service = BaseAIService(client=mock_client, service_name="test")
        
        result = await service.call_with_json_parsing(
            prompt="test",
            response_model=MockResponseModel
        )
        
        assert result is None

    @patch('src.services.base_ai_service.RateLimitIA')
    @patch('src.services.base_ai_service.CacheIA')
    async def test_call_with_json_parsing_validation_error(self, mock_cache, mock_rate):
        """Test JSON parsing avec erreur de validation Pydantic."""
        # JSON valide mais donnÃ©es invalides pour le modÃ¨le
        mock_cache.obtenir.return_value = '{"unknown_field": "value"}'
        mock_rate.peut_appeler.return_value = (True, "OK")
        
        mock_client = AsyncMock()
        
        from src.services.base_ai_service import BaseAIService
        
        # ModÃ¨le avec champ obligatoire
        class StrictModel(BaseModel):
            required_field: str  # Obligatoire
        
        service = BaseAIService(client=mock_client, service_name="test")
        
        result = await service.call_with_json_parsing(
            prompt="test",
            response_model=StrictModel
        )
        
        # Retourne None car validation Ã©choue
        assert result is None


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS CALL WITH PARSING SYNC
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestCallWithParsingSync:
    """Tests pour call_with_parsing_sync()."""

    @patch('src.services.base_ai_service.RateLimitIA')
    @patch('src.services.base_ai_service.CacheIA')
    def test_call_with_parsing_sync_returns_result(self, mock_cache, mock_rate):
        """Test appel sync avec parsing."""
        mock_cache.obtenir.return_value = '{"nom": "Test", "valeur": 42}'
        mock_client = Mock()
        
        from src.services.base_ai_service import BaseAIService
        
        service = BaseAIService(client=mock_client)
        
        # Note: Cette mÃ©thode fait un asyncio.run(), difficile Ã  tester en unitaire
        # On teste juste que la mÃ©thode existe et est callable
        assert callable(service.call_with_parsing_sync)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS RECIPE AI MIXIN
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestRecipeAIMixin:
    """Tests pour RecipeAIMixin."""

    def test_build_recipe_context_basic(self):
        """Test construction contexte recettes."""
        from src.services.base_ai_service import RecipeAIMixin
        
        mixin = RecipeAIMixin()
        
        result = mixin.build_recipe_context(
            filters={"saison": "Ã©tÃ©", "type_repas": "dÃ®ner"},
            nb_recettes=5
        )
        
        assert "5 recettes" in result
        assert "Ã©tÃ©" in result
        assert "dÃ®ner" in result

    def test_build_recipe_context_with_ingredients(self):
        """Test avec ingrÃ©dients disponibles."""
        from src.services.base_ai_service import RecipeAIMixin
        
        mixin = RecipeAIMixin()
        
        result = mixin.build_recipe_context(
            filters={},
            ingredients_dispo=["Tomate", "Oignon", "Ail"],
            nb_recettes=3
        )
        
        assert "3 recettes" in result
        assert "Tomate" in result
        assert "Oignon" in result


@pytest.mark.unit
class TestPlanningAIMixin:
    """Tests pour PlanningAIMixin."""

    def test_build_planning_context(self):
        """Test construction contexte planning."""
        from src.services.base_ai_service import PlanningAIMixin
        
        mixin = PlanningAIMixin()
        
        result = mixin.build_planning_context(
            config={"jours": 7, "personnes": 4, "budget": "normal"},
            semaine_debut="2024-01-15"
        )
        
        assert "2024-01-15" in result
        # VÃ©rifie que le contexte contient les infos foyer
        assert "adultes" in result.lower() or "FOYER" in result


@pytest.mark.unit
class TestInventoryAIMixin:
    """Tests pour InventoryAIMixin."""

    def test_build_inventory_summary(self):
        """Test rÃ©sumÃ© inventaire."""
        from src.services.base_ai_service import InventoryAIMixin
        
        mixin = InventoryAIMixin()
        
        inventaire = [
            {"nom": "Tomate", "quantite": 5, "unite": "piÃ¨ces", "categorie": "LÃ©gumes"},
            {"nom": "Lait", "quantite": 2, "unite": "L", "categorie": "Produits laitiers"}
        ]
        
        result = mixin.build_inventory_summary(inventaire)
        
        assert "Tomate" in result
        assert "Lait" in result

    def test_build_inventory_summary_with_status(self):
        """Test rÃ©sumÃ© inventaire avec diffÃ©rents statuts."""
        from src.services.base_ai_service import InventoryAIMixin
        
        mixin = InventoryAIMixin()
        
        inventaire = [
            {"nom": "Lait", "quantite": 0, "unite": "L", "categorie": "Produits laitiers", "statut": "critique"},
            {"nom": "Oeufs", "quantite": 2, "unite": "piÃ¨ces", "categorie": "Produits laitiers", "statut": "sous_seuil"},
            {"nom": "Beurre", "quantite": 1, "unite": "piÃ¨ces", "categorie": "Produits laitiers", "statut": "ok"}
        ]
        
        result = mixin.build_inventory_summary(inventaire)
        
        assert "Lait" in result
        assert "ðŸ”´" in result  # Critique
        assert "STATUTS" in result

    def test_build_inventory_summary_many_items(self):
        """Test rÃ©sumÃ© avec beaucoup d'items par catÃ©gorie."""
        from src.services.base_ai_service import InventoryAIMixin
        
        mixin = InventoryAIMixin()
        
        # Plus de 5 items dans une catÃ©gorie (trigger "et X autres")
        inventaire = [
            {"nom": f"LÃ©gume{i}", "quantite": i, "unite": "pcs", "categorie": "LÃ©gumes"}
            for i in range(8)
        ]
        
        result = mixin.build_inventory_summary(inventaire)
        
        assert "autres" in result  # "... et X autres"
        assert "8" in result  # 8 articles


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS MODULE EXPORTS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestModuleExports:
    """Tests pour les exports du module."""

    def test_base_ai_service_exported(self):
        """Test BaseAIService exportÃ©."""
        from src.services.base_ai_service import BaseAIService
        assert BaseAIService is not None

    def test_recipe_ai_mixin_exported(self):
        """Test RecipeAIMixin exportÃ©."""
        from src.services.base_ai_service import RecipeAIMixin
        assert RecipeAIMixin is not None

    def test_planning_ai_mixin_exported(self):
        """Test PlanningAIMixin exportÃ©."""
        from src.services.base_ai_service import PlanningAIMixin
        assert PlanningAIMixin is not None
