"""
Tests pour src/utils/helpers/helpers.py et src/utils/media.py
Ces fichiers ont une couverture faible, ces tests visent Ã  l'amÃ©liorer
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import io


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS MEDIA UTILITIES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class TestImageConfig:
    """Tests pour ImageConfig"""
    
    def test_default_values(self):
        """Les valeurs par dÃ©faut sont correctes"""
        from src.utils.media import ImageConfig
        
        config = ImageConfig()
        
        assert config.max_width == 1920
        assert config.max_height == 1080
        assert config.quality == 85
        assert config.format == "WebP"
        assert config.cache_ttl_seconds == 3600
    
    def test_custom_values(self):
        """Les valeurs custom fonctionnent"""
        from src.utils.media import ImageConfig
        
        config = ImageConfig(
            max_width=800,
            max_height=600,
            quality=90,
            format="JPEG",
            cache_ttl_seconds=7200
        )
        
        assert config.max_width == 800
        assert config.max_height == 600
        assert config.quality == 90
        assert config.format == "JPEG"
        assert config.cache_ttl_seconds == 7200


class TestImageCache:
    """Tests pour ImageCache"""
    
    def test_init(self):
        """L'initialisation fonctionne"""
        from src.utils.media import ImageCache
        
        cache = ImageCache(ttl_seconds=1800)
        
        assert cache.ttl_seconds == 1800
        assert len(cache.cache) == 0
    
    def test_set_and_get(self):
        """Set et get fonctionnent"""
        from src.utils.media import ImageCache
        from PIL import Image
        
        cache = ImageCache()
        img = Image.new('RGB', (100, 100), color='red')
        
        cache.set("test_key", img)
        result = cache.get("test_key")
        
        assert result is not None
        assert result.size == (100, 100)
    
    def test_get_missing_key(self):
        """Get retourne None pour clÃ© inexistante"""
        from src.utils.media import ImageCache
        
        cache = ImageCache()
        result = cache.get("nonexistent")
        
        assert result is None
    
    def test_get_expired(self):
        """Get retourne None pour clÃ© expirÃ©e"""
        from src.utils.media import ImageCache
        from PIL import Image
        from datetime import datetime, timedelta
        
        cache = ImageCache(ttl_seconds=1)
        img = Image.new('RGB', (50, 50))
        
        # InsÃ©rer avec timestamp passÃ©
        cache.cache["expired_key"] = (img, datetime.utcnow() - timedelta(seconds=10))
        
        result = cache.get("expired_key")
        
        assert result is None
        assert "expired_key" not in cache.cache
    
    def test_clear(self):
        """Clear vide le cache"""
        from src.utils.media import ImageCache
        from PIL import Image
        
        cache = ImageCache()
        img = Image.new('RGB', (50, 50))
        cache.set("key1", img)
        cache.set("key2", img)
        
        cache.clear()
        
        assert len(cache.cache) == 0
    
    def test_stats(self):
        """Stats retourne les bonnes infos"""
        from src.utils.media import ImageCache
        from PIL import Image
        
        cache = ImageCache()
        img = Image.new('RGB', (50, 50))
        cache.set("key1", img)
        cache.set("key2", img)
        
        stats = cache.stats()
        
        assert stats["size"] == 2
        assert "key1" in stats["keys"]
        assert "key2" in stats["keys"]


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS HELPERS DATA (fonctions rÃ©elles)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class TestDataHelpers:
    """Tests pour les helpers data"""
    
    def test_import(self):
        """Le module s'importe"""
        from src.utils.helpers import data
        assert data is not None
    
    def test_safe_get_simple(self):
        """safe_get fonctionne avec une clÃ©"""
        from src.utils.helpers.data import safe_get
        
        d = {"a": 1, "b": 2}
        
        assert safe_get(d, "a") == 1
        assert safe_get(d, "c", default="default") == "default"
    
    def test_safe_get_nested(self):
        """safe_get fonctionne avec plusieurs clÃ©s"""
        from src.utils.helpers.data import safe_get
        
        d = {"a": {"b": {"c": 42}}}
        
        assert safe_get(d, "a", "b", "c") == 42
        assert safe_get(d, "a", "b", "d", default=0) == 0
    
    def test_group_by(self):
        """group_by groupe correctement"""
        from src.utils.helpers.data import group_by
        
        items = [
            {"type": "a", "value": 1},
            {"type": "b", "value": 2},
            {"type": "a", "value": 3}
        ]
        
        result = group_by(items, "type")
        
        assert len(result["a"]) == 2
        assert len(result["b"]) == 1
    
    def test_count_by(self):
        """count_by compte correctement"""
        from src.utils.helpers.data import count_by
        
        items = [
            {"type": "a"},
            {"type": "b"},
            {"type": "a"},
            {"type": "a"}
        ]
        
        result = count_by(items, "type")
        
        assert result["a"] == 3
        assert result["b"] == 1
    
    def test_deduplicate(self):
        """deduplicate enlÃ¨ve les doublons"""
        from src.utils.helpers.data import deduplicate
        
        items = [1, 2, 2, 3, 3, 3]
        result = deduplicate(items)
        
        assert len(result) == 3
        assert set(result) == {1, 2, 3}
    
    def test_deduplicate_with_key(self):
        """deduplicate avec key fonctionne"""
        from src.utils.helpers.data import deduplicate
        
        items = [{"id": 1}, {"id": 2}, {"id": 1}]
        result = deduplicate(items, key=lambda x: x["id"])
        
        assert len(result) == 2
    
    def test_flatten(self):
        """flatten aplatit les listes"""
        from src.utils.helpers.data import flatten
        
        nested = [[1, 2], [3, 4], [5]]
        result = flatten(nested)
        
        assert result == [1, 2, 3, 4, 5]
    
    def test_merge_dicts(self):
        """merge_dicts fusionne les dictionnaires"""
        from src.utils.helpers.data import merge_dicts
        
        d1 = {"a": 1}
        d2 = {"b": 2}
        d3 = {"c": 3}
        
        result = merge_dicts(d1, d2, d3)
        
        assert result == {"a": 1, "b": 2, "c": 3}
    
    def test_pick(self):
        """pick extrait les clÃ©s spÃ©cifiÃ©es"""
        from src.utils.helpers.data import pick
        
        d = {"a": 1, "b": 2, "c": 3}
        result = pick(d, ["a", "c"])
        
        assert result == {"a": 1, "c": 3}
    
    def test_omit(self):
        """omit enlÃ¨ve les clÃ©s spÃ©cifiÃ©es"""
        from src.utils.helpers.data import omit
        
        d = {"a": 1, "b": 2, "c": 3}
        result = omit(d, ["b"])
        
        assert result == {"a": 1, "c": 3}


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS HELPERS STRINGS (fonctions rÃ©elles)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class TestStringHelpers:
    """Tests pour les helpers strings"""
    
    def test_import(self):
        """Le module s'importe"""
        from src.utils.helpers import strings
        assert strings is not None
    
    def test_generate_id(self):
        """generate_id gÃ©nÃ¨re un ID"""
        from src.utils.helpers.strings import generate_id
        
        id1 = generate_id("test")
        id2 = generate_id("test")
        id3 = generate_id("other")
        
        assert id1 == id2  # MÃªme input = mÃªme ID
        assert id1 != id3  # Input diffÃ©rent = ID diffÃ©rent
    
    def test_normalize_whitespace(self):
        """normalize_whitespace normalise les espaces"""
        from src.utils.helpers.strings import normalize_whitespace
        
        result = normalize_whitespace("  Hello   World  ")
        assert result == "Hello World"
    
    def test_remove_accents(self):
        """remove_accents enlÃ¨ve les accents"""
        from src.utils.helpers.strings import remove_accents
        
        result = remove_accents("CafÃ© crÃ¨me")
        assert result == "Cafe creme"
    
    def test_camel_to_snake(self):
        """camel_to_snake convertit correctement"""
        from src.utils.helpers.strings import camel_to_snake
        
        assert camel_to_snake("helloWorld") == "hello_world"
        assert camel_to_snake("HelloWorld") == "hello_world"
    
    def test_snake_to_camel(self):
        """snake_to_camel convertit correctement"""
        from src.utils.helpers.strings import snake_to_camel
        
        assert snake_to_camel("hello_world") == "helloWorld"
    
    def test_pluralize(self):
        """pluralize pluralise correctement"""
        from src.utils.helpers.strings import pluralize
        
        # Retourne "count word" ou "count words"
        assert pluralize("item", 1) == "1 item"
        assert pluralize("item", 2) == "2 items"
        assert pluralize("cheval", 2, "chevaux") == "2 chevaux"
    
    def test_mask_sensitive(self):
        """mask_sensitive masque les donnÃ©es sensibles"""
        from src.utils.helpers.strings import mask_sensitive
        
        # Affiche les premiers chars puis masque le reste
        result = mask_sensitive("1234567890", visible_chars=4)
        assert result == "1234******"
        assert result.startswith("1234")
        assert result.endswith("******")


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS HELPERS STATS (fonctions rÃ©elles)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class TestStatsHelpers:
    """Tests pour les helpers stats"""
    
    def test_import(self):
        """Le module s'importe"""
        from src.utils.helpers import stats
        assert stats is not None
    
    def test_calculate_average(self):
        """calculate_average calcule la moyenne"""
        from src.utils.helpers.stats import calculate_average
        
        assert calculate_average([1, 2, 3, 4, 5]) == 3.0
        assert calculate_average([10]) == 10.0
        assert calculate_average([]) == 0.0


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS HELPERS FOOD (fonctions rÃ©elles)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class TestFoodHelpers:
    """Tests pour les helpers food"""
    
    def test_import(self):
        """Le module s'importe"""
        from src.utils.helpers import food
        assert food is not None
    
    def test_validate_stock_level(self):
        """validate_stock_level valide les niveaux de stock"""
        from src.utils.helpers.food import validate_stock_level
        
        assert validate_stock_level(10, 5) is True  # Stock suffisant
        assert validate_stock_level(3, 5) is False  # Stock insuffisant


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS AI PARSER (aprÃ¨s fix Pydantic)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class TestAIParserPydanticV2:
    """Tests pour vÃ©rifier la migration Pydantic v2"""
    
    def test_import_parser(self):
        """Le parser s'importe sans erreur"""
        from src.core.ai.parser import AnalyseurIA
        assert AnalyseurIA is not None
    
    def test_model_validate_json_used(self):
        """model_validate_json est utilisÃ© (pas parse_raw)"""
        import inspect
        from src.core.ai.parser import AnalyseurIA
        
        source = inspect.getsource(AnalyseurIA)
        
        assert "model_validate_json" in source
    
    def test_model_fields_used(self):
        """model_fields est utilisÃ© (pas __fields__)"""
        import inspect
        from src.core.ai.parser import AnalyseurIA
        
        source = inspect.getsource(AnalyseurIA)
        
        assert "model_fields" in source


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS ACTION HISTORY (aprÃ¨s fix Pydantic)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class TestActionHistoryPydanticV2:
    """Tests pour vÃ©rifier la migration Pydantic v2 dans action_history"""
    
    def test_action_entry_model_config(self):
        """ActionEntry utilise model_config (pas class Config)"""
        from src.services.action_history import ActionEntry
        
        # VÃ©rifier que model_config est dÃ©fini
        assert hasattr(ActionEntry, 'model_config')
        assert ActionEntry.model_config.get('from_attributes') is True


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS API MAIN (aprÃ¨s fix Pydantic)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class TestAPIPydanticV2:
    """Tests pour vÃ©rifier la migration Pydantic v2 dans api/main"""
    
    def test_recette_response_model_config(self):
        """RecetteResponse utilise model_config"""
        from src.api.main import RecetteResponse
        
        assert hasattr(RecetteResponse, 'model_config')
        assert RecetteResponse.model_config.get('from_attributes') is True
    
    def test_inventaire_response_model_config(self):
        """InventaireItemResponse utilise model_config"""
        from src.api.main import InventaireItemResponse
        
        assert hasattr(InventaireItemResponse, 'model_config')
        assert InventaireItemResponse.model_config.get('from_attributes') is True

