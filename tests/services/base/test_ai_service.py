"""
Tests unitaires complets pour src/services/base/ai_service.py
Module: BaseAIService - Rate limiting, cache, parsing Pydantic.

Couverture cible: >80%
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from pydantic import BaseModel, ValidationError

# ═══════════════════════════════════════════════════════════
# MODÈLES DE TEST PYDANTIC
# ═══════════════════════════════════════════════════════════


class RecetteTest(BaseModel):
    """Modèle de test pour parsing."""

    nom: str
    temps_preparation: int = 30


class IngredientTest(BaseModel):
    """Modèle de test pour parsing liste."""

    nom: str
    quantite: str = "1"


class ConfigTest(BaseModel):
    """Modèle complexe pour tests."""

    parametre: str
    valeur: int
    actif: bool = True


# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def mock_client_ia():
    """Client IA mocké."""
    client = Mock()
    client.appeler = AsyncMock(return_value='{"nom": "Test", "temps_preparation": 45}')
    return client


@pytest.fixture
def mock_client_ia_list():
    """Client IA mocké pour listes."""
    client = Mock()
    client.appeler = AsyncMock(
        return_value='{"items": [{"nom": "A", "quantite": "1"}, {"nom": "B", "quantite": "2"}]}'
    )
    return client


@pytest.fixture
def mock_client_ia_none():
    """Client IA qui retourne None."""
    client = Mock()
    client.appeler = AsyncMock(return_value=None)
    return client


@pytest.fixture
def mock_rate_limit_ok():
    """Rate limit autorisé."""
    with patch("src.core.ai.RateLimitIA.peut_appeler", return_value=(True, "")):
        with patch("src.core.ai.RateLimitIA.enregistrer_appel"):
            yield


@pytest.fixture
def mock_cache_miss():
    """Cache sans hit."""
    with patch("src.core.ai.cache.CacheIA.obtenir", return_value=None):
        with patch("src.core.ai.cache.CacheIA.definir"):
            yield


@pytest.fixture
def base_ai_service(mock_client_ia):
    """Instance BaseAIService pour tests."""
    from src.services.core.base.ai_service import BaseAIService

    return BaseAIService(
        client=mock_client_ia,
        cache_prefix="test",
        default_ttl=300,
        default_temperature=0.5,
        service_name="test_service",
    )


@pytest.fixture
def base_ai_service_list(mock_client_ia_list):
    """Instance BaseAIService pour tests de liste."""
    from src.services.core.base.ai_service import BaseAIService

    return BaseAIService(
        client=mock_client_ia_list,
        cache_prefix="test",
        default_ttl=300,
        default_temperature=0.5,
        service_name="test_service",
    )


# ═══════════════════════════════════════════════════════════
# TESTS INITIALISATION
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestBaseAIServiceInit:
    """Tests pour l'initialisation de BaseAIService."""

    def test_init_sets_client(self, mock_client_ia):
        """Vérifie que le client est correctement défini."""
        from src.services.core.base.ai_service import BaseAIService

        service = BaseAIService(client=mock_client_ia)

        assert service.client == mock_client_ia

    def test_init_sets_cache_prefix(self, mock_client_ia):
        """Vérifie que le préfixe cache est correctement défini."""
        from src.services.core.base.ai_service import BaseAIService

        service = BaseAIService(client=mock_client_ia, cache_prefix="recipes")

        assert service.cache_prefix == "recipes"

    def test_init_sets_default_values(self, mock_client_ia):
        """Vérifie les valeurs par défaut."""
        from src.services.core.base.ai_service import BaseAIService

        service = BaseAIService(client=mock_client_ia)

        assert service.default_ttl == 3600
        assert service.default_temperature == 0.7
        assert service.service_name == "unknown"

    def test_init_custom_values(self, mock_client_ia):
        """Vérifie les valeurs personnalisées."""
        from src.services.core.base.ai_service import BaseAIService

        service = BaseAIService(
            client=mock_client_ia,
            default_ttl=600,
            default_temperature=0.3,
            service_name="recettes",
        )

        assert service.default_ttl == 600
        assert service.default_temperature == 0.3
        assert service.service_name == "recettes"

    def test_init_accepts_none_client(self):
        """Vérifie que le service accepte un client None."""
        from src.services.core.base.ai_service import BaseAIService

        service = BaseAIService(client=None)

        assert service.client is None


# ═══════════════════════════════════════════════════════════
# TESTS CALL_WITH_CACHE (ASYNC)
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
@pytest.mark.asyncio
class TestCallWithCache:
    """Tests pour call_with_cache."""

    async def test_call_with_cache_returns_response(
        self, mock_client_ia, mock_rate_limit_ok, mock_cache_miss
    ):
        """Test appel basique."""
        from src.services.core.base.ai_service import BaseAIService

        service = BaseAIService(client=mock_client_ia, service_name="test")

        result = await service.call_with_cache("test prompt")

        assert result is not None
        mock_client_ia.appeler.assert_called_once()

    async def test_call_with_cache_none_client(self):
        """Test avec client None."""
        from src.services.core.base.ai_service import BaseAIService

        service = BaseAIService(client=None, service_name="test")

        result = await service.call_with_cache("test prompt")

        assert result is None

    async def test_call_with_cache_uses_cache(self, mock_client_ia):
        """Test que le cache est utilisé."""
        from src.services.core.base.ai_service import BaseAIService

        service = BaseAIService(client=mock_client_ia, service_name="test")

        with patch("src.core.ai.cache.CacheIA.obtenir", return_value="cached response"):
            result = await service.call_with_cache("test prompt", use_cache=True)

            assert result == "cached response"
            mock_client_ia.appeler.assert_not_called()

    async def test_call_with_cache_skips_cache_when_disabled(
        self, mock_client_ia, mock_rate_limit_ok
    ):
        """Test que le cache est ignoré quand désactivé."""
        from src.services.core.base.ai_service import BaseAIService

        service = BaseAIService(client=mock_client_ia, service_name="test")

        with patch("src.core.ai.cache.CacheIA.obtenir") as mock_get:
            with patch("src.core.ai.cache.CacheIA.definir"):
                result = await service.call_with_cache("test prompt", use_cache=False)

                mock_get.assert_not_called()

    async def test_call_with_cache_rate_limit_exceeded(self, mock_client_ia, mock_cache_miss):
        """Test rate limit dépassé."""
        from src.core.errors import ErreurLimiteDebit
        from src.services.core.base.ai_service import BaseAIService

        service = BaseAIService(client=mock_client_ia, service_name="test")

        with patch("src.core.ai.RateLimitIA.peut_appeler", return_value=(False, "Limite atteinte")):
            # Le décorateur gerer_erreurs devrait capturer l'erreur
            # Mais dans certains cas l'erreur peut être propagée
            try:
                result = await service.call_with_cache("test prompt")
                # Si pas d'exception, le résultat est None (valeur_fallback)
                assert result is None
            except ErreurLimiteDebit:
                # L'erreur peut être levée si le décorateur ne la capture pas
                pass  # Test réussi - l'erreur rate limit est bien levée

    async def test_call_with_cache_custom_temperature(
        self, mock_client_ia, mock_rate_limit_ok, mock_cache_miss
    ):
        """Test avec température personnalisée."""
        from src.services.core.base.ai_service import BaseAIService

        service = BaseAIService(client=mock_client_ia, default_temperature=0.5)

        await service.call_with_cache("test prompt", temperature=0.9)

        # Vérifier que appeler a été appelé avec temp=0.9
        call_args = mock_client_ia.appeler.call_args
        assert call_args.kwargs.get("temperature") == 0.9

    async def test_call_with_cache_saves_to_cache(self, mock_client_ia, mock_rate_limit_ok):
        """Test que la réponse est sauvegardée en cache."""
        from src.services.core.base.ai_service import BaseAIService

        service = BaseAIService(client=mock_client_ia, service_name="test")

        with patch("src.core.ai.cache.CacheIA.obtenir", return_value=None):
            with patch("src.core.ai.cache.CacheIA.definir") as mock_set:
                await service.call_with_cache("test prompt", use_cache=True)

                mock_set.assert_called_once()


# ═══════════════════════════════════════════════════════════
# TESTS CALL_WITH_PARSING (ASYNC)
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
@pytest.mark.asyncio
class TestCallWithParsing:
    """Tests pour call_with_parsing."""

    async def test_call_with_parsing_returns_model(
        self, mock_client_ia, mock_rate_limit_ok, mock_cache_miss
    ):
        """Test parsing vers modèle Pydantic."""
        from src.services.core.base.ai_service import BaseAIService

        service = BaseAIService(client=mock_client_ia, service_name="test")

        with patch("src.core.ai.AnalyseurIA.analyser") as mock_parse:
            mock_parse.return_value = RecetteTest(nom="Test", temps_preparation=45)

            result = await service.call_with_parsing("test", response_model=RecetteTest)

            assert result is not None
            assert result.nom == "Test"

    async def test_call_with_parsing_no_response(
        self, mock_client_ia_none, mock_rate_limit_ok, mock_cache_miss
    ):
        """Test parsing sans réponse IA."""
        from src.services.core.base.ai_service import BaseAIService

        service = BaseAIService(client=mock_client_ia_none, service_name="test")

        result = await service.call_with_parsing("test", response_model=RecetteTest)

        assert result is None

    async def test_call_with_parsing_validation_error_with_fallback(
        self, mock_client_ia, mock_rate_limit_ok, mock_cache_miss
    ):
        """Test parsing avec erreur et fallback."""
        from src.services.core.base.ai_service import BaseAIService

        service = BaseAIService(client=mock_client_ia, service_name="test")

        with patch("src.core.ai.AnalyseurIA.analyser") as mock_parse:
            mock_parse.side_effect = ValidationError.from_exception_data("test", [])

            fallback = {"nom": "Fallback", "temps_preparation": 10}

            result = await service.call_with_parsing(
                "test", response_model=RecetteTest, fallback=fallback
            )

            assert result is not None
            assert result.nom == "Fallback"


# ═══════════════════════════════════════════════════════════
# TESTS CALL_WITH_PARSING_SYNC
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestCallWithParsingSync:
    """Tests pour call_with_parsing_sync."""

    def test_sync_method_exists(self, base_ai_service):
        """Vérifie que la méthode sync existe."""
        assert hasattr(base_ai_service, "call_with_parsing_sync")
        assert callable(base_ai_service.call_with_parsing_sync)

    def test_sync_calls_async_version(self, mock_client_ia, mock_rate_limit_ok, mock_cache_miss):
        """Test que sync appelle la version async."""
        from src.services.core.base.ai_service import BaseAIService

        service = BaseAIService(client=mock_client_ia, service_name="test")

        with patch("src.core.ai.AnalyseurIA.analyser") as mock_parse:
            mock_parse.return_value = RecetteTest(nom="Test", temps_preparation=45)

            result = service.call_with_parsing_sync("test", response_model=RecetteTest)

            # Devrait avoir appelé le client
            assert mock_client_ia.appeler.called or result is not None


# ═══════════════════════════════════════════════════════════
# TESTS CALL_WITH_LIST_PARSING (ASYNC)
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
@pytest.mark.asyncio
class TestCallWithListParsing:
    """Tests pour call_with_list_parsing."""

    async def test_call_with_list_parsing_returns_list(
        self, mock_client_ia_list, mock_rate_limit_ok, mock_cache_miss
    ):
        """Test parsing liste."""
        from src.services.core.base.ai_service import BaseAIService

        service = BaseAIService(client=mock_client_ia_list, service_name="test")

        with patch("src.core.ai.parser.analyser_liste_reponse") as mock_parse:
            mock_parse.return_value = [
                IngredientTest(nom="A", quantite="1"),
                IngredientTest(nom="B", quantite="2"),
            ]

            result = await service.call_with_list_parsing(
                "test", item_model=IngredientTest, list_key="items"
            )

            assert len(result) == 2
            assert result[0].nom == "A"

    async def test_call_with_list_parsing_limits_items(
        self, mock_client_ia_list, mock_rate_limit_ok, mock_cache_miss
    ):
        """Test limite du nombre d'items."""
        from src.services.core.base.ai_service import BaseAIService

        service = BaseAIService(client=mock_client_ia_list, service_name="test")

        with patch("src.core.ai.parser.analyser_liste_reponse") as mock_parse:
            mock_parse.return_value = [
                IngredientTest(nom="A"),
                IngredientTest(nom="B"),
                IngredientTest(nom="C"),
                IngredientTest(nom="D"),
            ]

            result = await service.call_with_list_parsing(
                "test", item_model=IngredientTest, max_items=2
            )

            assert len(result) == 2

    async def test_call_with_list_parsing_no_response(
        self, mock_client_ia_none, mock_rate_limit_ok, mock_cache_miss
    ):
        """Test parsing liste sans réponse."""
        from src.services.core.base.ai_service import BaseAIService

        service = BaseAIService(client=mock_client_ia_none, service_name="test")

        result = await service.call_with_list_parsing("test", item_model=IngredientTest)

        assert result == []

    async def test_call_with_list_parsing_error(
        self, mock_client_ia_list, mock_rate_limit_ok, mock_cache_miss
    ):
        """Test parsing liste avec erreur."""
        from src.services.core.base.ai_service import BaseAIService

        service = BaseAIService(client=mock_client_ia_list, service_name="test")

        with patch("src.core.ai.parser.analyser_liste_reponse") as mock_parse:
            mock_parse.side_effect = Exception("Parsing error")

            result = await service.call_with_list_parsing("test", item_model=IngredientTest)

            assert result == []


# ═══════════════════════════════════════════════════════════
# TESTS CALL_WITH_LIST_PARSING_SYNC
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestCallWithListParsingSync:
    """Tests pour call_with_list_parsing_sync."""

    def test_sync_method_exists(self, base_ai_service):
        """Vérifie que la méthode sync existe."""
        assert hasattr(base_ai_service, "call_with_list_parsing_sync")
        assert callable(base_ai_service.call_with_list_parsing_sync)


# ═══════════════════════════════════════════════════════════
# TESTS CALL_WITH_JSON_PARSING (ASYNC)
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
@pytest.mark.asyncio
class TestCallWithJsonParsing:
    """Tests pour call_with_json_parsing."""

    async def test_json_parsing_basic(self, mock_rate_limit_ok, mock_cache_miss):
        """Test parsing JSON basique."""
        from src.services.core.base.ai_service import BaseAIService

        client = Mock()
        client.appeler = AsyncMock(return_value='{"nom": "Test", "temps_preparation": 30}')

        service = BaseAIService(client=client, service_name="test")

        result = await service.call_with_json_parsing("test", response_model=RecetteTest)

        assert result is not None
        assert result.nom == "Test"

    async def test_json_parsing_with_markdown_blocks(self, mock_rate_limit_ok, mock_cache_miss):
        """Test parsing JSON avec blocs markdown."""
        from src.services.core.base.ai_service import BaseAIService

        client = Mock()
        client.appeler = AsyncMock(
            return_value='```json\n{"nom": "Test", "temps_preparation": 30}\n```'
        )

        service = BaseAIService(client=client, service_name="test")

        result = await service.call_with_json_parsing("test", response_model=RecetteTest)

        assert result is not None
        assert result.nom == "Test"

    async def test_json_parsing_invalid_json(self, mock_rate_limit_ok, mock_cache_miss):
        """Test parsing JSON invalide."""
        from src.services.core.base.ai_service import BaseAIService

        client = Mock()
        client.appeler = AsyncMock(return_value="not valid json")

        service = BaseAIService(client=client, service_name="test")

        result = await service.call_with_json_parsing("test", response_model=RecetteTest)

        assert result is None

    async def test_json_parsing_validation_error(self, mock_rate_limit_ok, mock_cache_miss):
        """Test parsing JSON avec erreur de validation."""
        from src.services.core.base.ai_service import BaseAIService

        client = Mock()
        # JSON valide mais ne correspond pas au modèle (manque 'nom')
        client.appeler = AsyncMock(return_value='{"foo": "bar"}')

        service = BaseAIService(client=client, service_name="test")

        result = await service.call_with_json_parsing("test", response_model=RecetteTest)

        assert result is None

    async def test_json_parsing_no_response(self, mock_rate_limit_ok, mock_cache_miss):
        """Test parsing JSON sans réponse."""
        from src.services.core.base.ai_service import BaseAIService

        client = Mock()
        client.appeler = AsyncMock(return_value=None)

        service = BaseAIService(client=client, service_name="test")

        result = await service.call_with_json_parsing("test", response_model=RecetteTest)

        assert result is None


# ═══════════════════════════════════════════════════════════
# TESTS CALL_WITH_JSON_PARSING_SYNC
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestCallWithJsonParsingSync:
    """Tests pour call_with_json_parsing_sync."""

    def test_sync_method_exists(self, base_ai_service):
        """Vérifie que la méthode sync existe."""
        assert hasattr(base_ai_service, "call_with_json_parsing_sync")
        assert callable(base_ai_service.call_with_json_parsing_sync)


# ═══════════════════════════════════════════════════════════
# TESTS HELPERS PROMPTS
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestPromptHelpers:
    """Tests pour les helpers de construction de prompts."""

    def test_build_json_prompt_basic(self, base_ai_service):
        """Test construction prompt JSON basique."""
        result = base_ai_service.build_json_prompt(
            context="Contexte test", task="Faire quelque chose", json_schema='{"field": "value"}'
        )

        assert "Contexte test" in result
        assert "Faire quelque chose" in result
        assert '{"field": "value"}' in result

    def test_build_json_prompt_with_constraints(self, base_ai_service):
        """Test construction prompt JSON avec contraintes."""
        result = base_ai_service.build_json_prompt(
            context="Contexte",
            task="Tâche",
            json_schema="{}",
            constraints=["Contrainte 1", "Contrainte 2"],
        )

        assert "CONTRAINTES" in result
        assert "Contrainte 1" in result
        assert "Contrainte 2" in result

    def test_build_json_prompt_includes_json_instruction(self, base_ai_service):
        """Test que l'instruction JSON est incluse."""
        result = base_ai_service.build_json_prompt(context="", task="", json_schema="{}")

        assert "JSON valide" in result

    def test_build_system_prompt_basic(self, base_ai_service):
        """Test construction system prompt basique."""
        result = base_ai_service.build_system_prompt(
            role="un expert culinaire", expertise=["Cuisine française", "Pâtisserie"]
        )

        assert "Tu es un expert culinaire" in result
        assert "Cuisine française" in result
        assert "Pâtisserie" in result

    def test_build_system_prompt_with_rules(self, base_ai_service):
        """Test construction system prompt avec règles."""
        result = base_ai_service.build_system_prompt(
            role="un assistant", expertise=["Aide"], rules=["Être poli", "Être concis"]
        )

        assert "RÈGLES" in result
        assert "Être poli" in result
        assert "Être concis" in result

    def test_build_system_prompt_french(self, base_ai_service):
        """Test que le prompt demande de répondre en français."""
        result = base_ai_service.build_system_prompt(role="", expertise=[])

        assert "français" in result.lower()


# ═══════════════════════════════════════════════════════════
# TESTS MÉTRIQUES & DEBUG
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestMetricsDebug:
    """Tests pour les méthodes de métriques et debug."""

    def test_get_cache_stats(self, base_ai_service):
        """Test récupération stats cache."""
        with patch("src.core.ai.cache.CacheIA.obtenir_statistiques") as mock_stats:
            mock_stats.return_value = {"hits": 10, "misses": 5}

            result = base_ai_service.get_cache_stats()

            assert "hits" in result
            mock_stats.assert_called_once()

    def test_get_rate_limit_stats(self, base_ai_service):
        """Test récupération stats rate limit."""
        with patch("src.core.ai.RateLimitIA.obtenir_statistiques") as mock_stats:
            mock_stats.return_value = {"daily": 50, "hourly": 10}

            result = base_ai_service.get_rate_limit_stats()

            assert "daily" in result
            mock_stats.assert_called_once()

    def test_clear_cache(self, base_ai_service):
        """Test vidage du cache."""
        with patch("src.core.ai.cache.CacheIA.invalider_tout") as mock_clear:
            base_ai_service.clear_cache()

            mock_clear.assert_called_once()


# ═══════════════════════════════════════════════════════════
# TESTS MIXINS
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestRecipeAIMixin:
    """Tests pour RecipeAIMixin."""

    def test_build_recipe_context_basic(self):
        """Test construction contexte recette basique."""
        from src.services.core.base.ai_service import RecipeAIMixin

        mixin = RecipeAIMixin()

        result = mixin.build_recipe_context(filters={"saison": "été"}, nb_recettes=5)

        assert "5 recettes" in result
        assert "été" in result

    def test_build_recipe_context_with_type_repas(self):
        """Test contexte avec type de repas."""
        from src.services.core.base.ai_service import RecipeAIMixin

        mixin = RecipeAIMixin()

        result = mixin.build_recipe_context(filters={"type_repas": "dîner"}, nb_recettes=3)

        assert "dîner" in result

    def test_build_recipe_context_with_difficulte(self):
        """Test contexte avec difficulté."""
        from src.services.core.base.ai_service import RecipeAIMixin

        mixin = RecipeAIMixin()

        result = mixin.build_recipe_context(filters={"difficulte": "facile"}, nb_recettes=3)

        assert "facile" in result

    def test_build_recipe_context_quick(self):
        """Test contexte recettes rapides."""
        from src.services.core.base.ai_service import RecipeAIMixin

        mixin = RecipeAIMixin()

        result = mixin.build_recipe_context(filters={"is_quick": True}, nb_recettes=3)

        assert "30 minutes" in result

    def test_build_recipe_context_with_ingredients(self):
        """Test contexte avec ingrédients."""
        from src.services.core.base.ai_service import RecipeAIMixin

        mixin = RecipeAIMixin()

        result = mixin.build_recipe_context(
            filters={}, ingredients_dispo=["tomates", "oignons", "poulet"], nb_recettes=3
        )

        assert "INGRÉDIENTS DISPONIBLES" in result
        assert "tomates" in result


@pytest.mark.unit
class TestPlanningAIMixin:
    """Tests pour PlanningAIMixin."""

    def test_build_planning_context_basic(self):
        """Test construction contexte planning basique."""
        from src.services.core.base.ai_service import PlanningAIMixin

        mixin = PlanningAIMixin()

        result = mixin.build_planning_context(
            config={"nb_adultes": 2, "nb_enfants": 1}, semaine_debut="2024-03-18"
        )

        assert "2024-03-18" in result
        assert "2 adultes" in result
        assert "1 enfants" in result

    def test_build_planning_context_with_bebe(self):
        """Test contexte avec bébé."""
        from src.services.core.base.ai_service import PlanningAIMixin

        mixin = PlanningAIMixin()

        result = mixin.build_planning_context(
            config={"nb_adultes": 2, "a_bebe": True}, semaine_debut="2024-03-18"
        )

        assert "jeune enfant" in result

    def test_build_planning_context_batch_cooking(self):
        """Test contexte avec batch cooking."""
        from src.services.core.base.ai_service import PlanningAIMixin

        mixin = PlanningAIMixin()

        result = mixin.build_planning_context(
            config={"nb_adultes": 2, "batch_cooking_actif": True}, semaine_debut="2024-03-18"
        )

        assert "Batch cooking" in result


@pytest.mark.unit
class TestInventoryAIMixin:
    """Tests pour InventoryAIMixin."""

    def test_build_inventory_summary_basic(self):
        """Test résumé inventaire basique."""
        from src.services.core.base.ai_service import InventoryAIMixin

        mixin = InventoryAIMixin()

        inventaire = [
            {
                "nom": "Tomates",
                "quantite": 5,
                "unite": "pièces",
                "categorie": "Légumes",
                "statut": "ok",
            },
            {
                "nom": "Oignons",
                "quantite": 2,
                "unite": "kg",
                "categorie": "Légumes",
                "statut": "critique",
            },
        ]

        result = mixin.build_inventory_summary(inventaire)

        assert "INVENTAIRE" in result
        assert "Tomates" in result
        assert "Légumes" in result

    def test_build_inventory_summary_status_icons(self):
        """Test icônes de statut."""
        from src.services.core.base.ai_service import InventoryAIMixin

        mixin = InventoryAIMixin()

        inventaire = [
            {"nom": "A", "quantite": 1, "unite": "u", "categorie": "C", "statut": "ok"},
            {"nom": "B", "quantite": 1, "unite": "u", "categorie": "C", "statut": "sous_seuil"},
            {"nom": "C", "quantite": 1, "unite": "u", "categorie": "C", "statut": "critique"},
        ]

        result = mixin.build_inventory_summary(inventaire)

        assert "✅" in result
        assert "⚠️" in result
        assert "🔴" in result

    def test_build_inventory_summary_limits_items(self):
        """Test limite d'items par catégorie."""
        from src.services.core.base.ai_service import InventoryAIMixin

        mixin = InventoryAIMixin()

        # 10 items dans la même catégorie
        inventaire = [
            {"nom": f"Item{i}", "quantite": 1, "unite": "u", "categorie": "Cat", "statut": "ok"}
            for i in range(10)
        ]

        result = mixin.build_inventory_summary(inventaire)

        # Doit mentionner "et X autres"
        assert "autres" in result

    def test_build_inventory_summary_counts(self):
        """Test comptage des statuts."""
        from src.services.core.base.ai_service import InventoryAIMixin

        mixin = InventoryAIMixin()

        inventaire = [
            {"nom": "A", "quantite": 1, "unite": "u", "categorie": "C", "statut": "critique"},
            {"nom": "B", "quantite": 1, "unite": "u", "categorie": "C", "statut": "critique"},
            {"nom": "C", "quantite": 1, "unite": "u", "categorie": "C", "statut": "sous_seuil"},
        ]

        result = mixin.build_inventory_summary(inventaire)

        assert "STATUTS" in result
        assert "2 articles critiques" in result
        assert "1 articles sous le seuil" in result


# ═══════════════════════════════════════════════════════════
# TESTS FACTORY
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestFactory:
    """Tests pour la factory create_base_ai_service."""

    def test_factory_creates_service(self):
        """Test création via factory."""
        from src.services.core.base.ai_service import create_base_ai_service

        with patch("src.core.ai.obtenir_client_ia") as mock_get_client:
            mock_get_client.return_value = Mock()

            service = create_base_ai_service(
                cache_prefix="test",
                default_ttl=600,
                default_temperature=0.5,
                service_name="test_factory",
            )

            assert service.cache_prefix == "test"
            assert service.default_ttl == 600
            assert service.default_temperature == 0.5
            assert service.service_name == "test_factory"

    def test_factory_default_values(self):
        """Test factory avec valeurs par défaut."""
        from src.services.core.base.ai_service import create_base_ai_service

        with patch("src.core.ai.obtenir_client_ia") as mock_get_client:
            mock_get_client.return_value = Mock()

            service = create_base_ai_service()

            assert service.cache_prefix == "ai"
            assert service.default_ttl == 3600
            assert service.default_temperature == 0.7
            assert service.service_name == "unknown"


# ═══════════════════════════════════════════════════════════
# TESTS EDGE CASES
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestEdgeCases:
    """Tests pour les cas limites."""

    def test_empty_prompt(self, base_ai_service, mock_rate_limit_ok, mock_cache_miss):
        """Test avec prompt vide."""
        # Ne devrait pas lever d'exception
        result = base_ai_service.call_with_parsing_sync(prompt="", response_model=RecetteTest)
        # Le résultat dépend de la réponse du mock

    def test_very_long_prompt(self, base_ai_service, mock_rate_limit_ok, mock_cache_miss):
        """Test avec prompt très long."""
        long_prompt = "x" * 10000

        # Ne devrait pas lever d'exception
        result = base_ai_service.call_with_parsing_sync(
            prompt=long_prompt, response_model=RecetteTest
        )

    def test_special_characters_in_prompt(
        self, base_ai_service, mock_rate_limit_ok, mock_cache_miss
    ):
        """Test avec caractères spéciaux."""
        prompt = "Recette avec émojis ðŸ•ðŸ et accents éèàù"

        # Ne devrait pas lever d'exception
        result = base_ai_service.build_json_prompt(context=prompt, task="Test", json_schema="{}")

        assert "ðŸ•" in result


# ═══════════════════════════════════════════════════════════
# TESTS ASYNC CONTEXT (EVENT LOOP)
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestAsyncContext:
    """Tests pour la gestion du contexte async."""

    def test_sync_without_running_loop(self, mock_client_ia, mock_rate_limit_ok, mock_cache_miss):
        """Test sync sans boucle d'événements en cours."""
        from src.services.core.base.ai_service import BaseAIService

        service = BaseAIService(client=mock_client_ia, service_name="test")

        with patch("src.core.ai.AnalyseurIA.analyser") as mock_parse:
            mock_parse.return_value = RecetteTest(nom="Test", temps_preparation=30)

            # Appel sync direct
            result = service.call_with_parsing_sync(prompt="test", response_model=RecetteTest)

            # Devrait fonctionner sans erreur

    def test_sync_method_parameters(self, base_ai_service):
        """Test que les méthodes sync ont les bons paramètres."""
        import inspect

        # call_with_parsing_sync
        sig = inspect.signature(base_ai_service.call_with_parsing_sync)
        params = list(sig.parameters.keys())

        assert "prompt" in params
        assert "response_model" in params
        assert "system_prompt" in params
        assert "temperature" in params
        assert "max_tokens" in params
        assert "use_cache" in params
        assert "fallback" in params
