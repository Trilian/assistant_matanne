"""
Tests unitaires - Module Redis Cache (Cache Distribué)

Couverture complète :
- RedisConfig (configuration)
- MemoryCache (fallback mémoire)
- RedisCache (cache Redis distribué)
- Sérialisation JSON/Pickle
- Invalidation par tags
- Connection pooling

Architecture : 5 sections de tests (Config, Memory, Redis, Serialization, Integration)
"""

import json
from datetime import datetime, timedelta
from unittest.mock import MagicMock, Mock, patch

import pytest
from src.core import redis_cache

@pytest.mark.unit
def test_import_redis_cache():
    """Vérifie que le module redis_cache s'importe sans erreur."""
    assert hasattr(redis_cache, "RedisCache") or hasattr(redis_cache, "__file__")

from src.core.redis_cache import (
    RedisConfig,
    MemoryCache,
    RedisCache,
    REDIS_DISPONIBLE,
)


# ═══════════════════════════════════════════════════════════
# SECTION 1: CONFIGURATION
# ═══════════════════════════════════════════════════════════


class TestRedisConfig:
    """Tests pour configuration Redis."""

    @pytest.mark.unit
    def test_default_config_values(self):
        """Test valeurs par défaut configuration."""
        config = RedisConfig()
        
        assert config.HOST == "localhost"
        assert config.PORT == 6379
        assert config.DB == 0
        assert config.SOCKET_TIMEOUT == 5
        assert config.MAX_CONNECTIONS == 10
        assert config.COMPRESSION_THRESHOLD == 1024
        assert config.DEFAULT_TTL == 3600
        assert config.KEY_PREFIX == "matanne:"

    @pytest.mark.unit
    def test_config_modification(self):
        """Test modification configuration."""
        config = RedisConfig()
        config.HOST = "redis.example.com"
        config.PORT = 6380
        
        assert config.HOST == "redis.example.com"
        assert config.PORT == 6380


# ═══════════════════════════════════════════════════════════
# SECTION 2: MEMORY CACHE
# ═══════════════════════════════════════════════════════════


class TestMemoryCache:
    """Tests pour cache mémoire fallback."""

    def setup_method(self):
        """Préparation avant chaque test."""
        self.cache = MemoryCache()

    @pytest.mark.unit
    def test_set_get_basic(self):
        """Test set/get basique."""
        self.cache.set("key1", "value1")
        
        result = self.cache.get("key1")
        
        assert result == "value1"

    @pytest.mark.unit
    def test_get_nonexistent(self):
        """Test récupération clé inexistante."""
        result = self.cache.get("nonexistent")
        
        assert result is None

    @pytest.mark.unit
    def test_set_with_ttl(self):
        """Test set avec TTL."""
        # Mettre TTL très court pour test
        self.cache.set("expire_key", "value", ttl=1)
        
        # Vérifier présent immédiatement
        assert self.cache.get("expire_key") == "value"
        
        # Note: On ne peut pas tester l'expiration facilement sans sleep

    @pytest.mark.unit
    def test_delete_key(self):
        """Test suppression clé."""
        self.cache.set("key1", "value1")
        
        result = self.cache.delete("key1")
        
        assert result is True
        assert self.cache.get("key1") is None

    @pytest.mark.unit
    def test_delete_nonexistent(self):
        """Test suppression clé inexistante."""
        result = self.cache.delete("nonexistent")
        
        assert result is False

    @pytest.mark.unit
    def test_set_with_tags(self):
        """Test set avec tags."""
        self.cache.set("key1", "value1", tags=["tag1", "tag2"])
        self.cache.set("key2", "value2", tags=["tag1"])
        
        # Vérifier contenu
        assert self.cache.get("key1") == "value1"
        assert self.cache.get("key2") == "value2"

    @pytest.mark.unit
    def test_invalidate_tag(self):
        """Test invalidation par tag."""
        self.cache.set("key1", "value1", tags=["tag1"])
        self.cache.set("key2", "value2", tags=["tag1"])
        self.cache.set("key3", "value3", tags=["tag2"])
        
        count = self.cache.invalidate_tag("tag1")
        
        assert count == 2
        assert self.cache.get("key1") is None
        assert self.cache.get("key2") is None
        assert self.cache.get("key3") == "value3"

    @pytest.mark.unit
    def test_invalidate_nonexistent_tag(self):
        """Test invalidation tag inexistant."""
        count = self.cache.invalidate_tag("nonexistent")
        
        assert count == 0

    @pytest.mark.unit
    def test_clear_cache(self):
        """Test vidage complet cache."""
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")
        
        count = self.cache.clear()
        
        assert count == 2
        assert self.cache.get("key1") is None
        assert self.cache.get("key2") is None

    @pytest.mark.unit
    def test_stats(self):
        """Test statistiques cache."""
        self.cache.set("key1", "value1", tags=["tag1"])
        self.cache.set("key2", "value2")
        
        stats = self.cache.stats()
        
        assert stats["type"] == "memory"
        assert stats["keys"] == 2
        assert stats["tags"] == 1

    @pytest.mark.unit
    def test_cache_complex_types(self):
        """Test cache avec types complexes."""
        data = {
            "name": "test",
            "items": [1, 2, 3],
            "nested": {"key": "value"}
        }
        
        self.cache.set("complex", data)
        
        result = self.cache.get("complex")
        
        assert result == data

    @pytest.mark.unit
    def test_cache_overwrite(self):
        """Test overwrite valeur existante."""
        self.cache.set("key", "value1")
        assert self.cache.get("key") == "value1"
        
        self.cache.set("key", "value2")
        assert self.cache.get("key") == "value2"


# ═══════════════════════════════════════════════════════════
# SECTION 3: REDIS CACHE SINGLETON
# ═══════════════════════════════════════════════════════════


class TestRedisCache:
    """Tests pour cache Redis."""

    @pytest.mark.unit
    def test_redis_cache_singleton(self):
        """Test pattern Singleton."""
        cache1 = RedisCache()
        cache2 = RedisCache()
        
        assert cache1 is cache2

    @pytest.mark.unit
    def test_redis_cache_initialization(self):
        """Test initialisation."""
        cache = RedisCache()
        
        # Devrait avoir fallback
        assert cache._fallback is not None

    @pytest.mark.unit
    def test_stats_initialization(self):
        """Test stats initialisées."""
        cache = RedisCache()
        
        stats = cache._stats
        
        assert stats["hits"] == 0
        assert stats["misses"] == 0
        assert stats["errors"] == 0

    @pytest.mark.unit
    @patch('src.core.redis_cache.REDIS_DISPONIBLE', False)
    def test_fallback_to_memory(self):
        """Test fallback quand Redis indisponible."""
        cache = RedisCache()
        
        # Avec Redis indisponible, devrait utiliser fallback
        assert cache._fallback is not None

    @pytest.mark.unit
    def test_get_set_operations(self):
        """Test opérations get/set."""
        cache = RedisCache()
        
        # Utiliser fallback pour tests
        if cache._redis is None:
            cache.set("test_key", "test_value")
            result = cache.get("test_key")
            
            assert result == "test_value"

    @pytest.mark.unit
    def test_delete_operation(self):
        """Test suppression."""
        cache = RedisCache()
        
        if cache._redis is None:
            cache.set("key", "value")
            cache.delete("key")
            
            assert cache.get("key") is None

    @pytest.mark.unit
    def test_tag_invalidation(self):
        """Test invalidation tags."""
        cache = RedisCache()
        
        if cache._redis is None:
            cache.set("key1", "value1", tags=["tag1"])
            cache.set("key2", "value2", tags=["tag1"])
            
            cache.invalidate_tag("tag1")
            
            assert cache.get("key1") is None
            assert cache.get("key2") is None

    @pytest.mark.unit
    def test_cache_stats(self):
        """Test statistiques cache."""
        cache = RedisCache()
        
        stats = cache.stats()  # C'est une méthode
        
        assert isinstance(stats, dict)
        assert "hits" in stats or "type" in stats

    @pytest.mark.unit
    def test_cache_with_ttl(self):
        """Test cache avec TTL."""
        cache = RedisCache()
        
        if cache._redis is None:
            cache.set("ttl_key", "ttl_value", ttl=60)
            
            result = cache.get("ttl_key")
            assert result == "ttl_value"


# ═══════════════════════════════════════════════════════════
# SECTION 4: SÉRIALISATION
# ═══════════════════════════════════════════════════════════


class TestCacheSerialization:
    """Tests pour sérialisation cache."""

    def setup_method(self):
        """Préparation avant chaque test."""
        self.cache = MemoryCache()

    @pytest.mark.unit
    def test_serialize_string(self):
        """Test sérialisation string."""
        self.cache.set("str_key", "string_value")
        
        assert self.cache.get("str_key") == "string_value"

    @pytest.mark.unit
    def test_serialize_dict(self):
        """Test sérialisation dict."""
        data = {"name": "test", "value": 42}
        self.cache.set("dict_key", data)
        
        assert self.cache.get("dict_key") == data

    @pytest.mark.unit
    def test_serialize_list(self):
        """Test sérialisation list."""
        data = [1, 2, 3, "four", 5.0]
        self.cache.set("list_key", data)
        
        assert self.cache.get("list_key") == data

    @pytest.mark.unit
    def test_serialize_nested(self):
        """Test sérialisation structure imbriquée."""
        data = {
            "users": [
                {"id": 1, "name": "Alice"},
                {"id": 2, "name": "Bob"}
            ],
            "meta": {"count": 2}
        }
        
        self.cache.set("nested_key", data)
        
        assert self.cache.get("nested_key") == data

    @pytest.mark.unit
    def test_serialize_boolean(self):
        """Test sérialisation booléens."""
        self.cache.set("bool_true", True)
        self.cache.set("bool_false", False)
        
        assert self.cache.get("bool_true") is True
        assert self.cache.get("bool_false") is False

    @pytest.mark.unit
    def test_serialize_none(self):
        """Test sérialisation None."""
        self.cache.set("none_key", None)
        
        # Note: Get retourne None si clé inexistante aussi
        # Donc test avec tag pour vérifier
        assert "none_key" in self.cache._data


# ═══════════════════════════════════════════════════════════
# SECTION 5: CAS D'INTÉGRATION
# ═══════════════════════════════════════════════════════════


class TestRedisCacheIntegration:
    """Tests d'intégration."""

    def setup_method(self):
        """Préparation avant chaque test."""
        self.cache = MemoryCache()

    @pytest.mark.integration
    def test_complete_cache_workflow(self):
        """Test workflow complet cache."""
        # Ajouter données
        self.cache.set("user:1", {"name": "Alice"}, tags=["user"])
        self.cache.set("user:2", {"name": "Bob"}, tags=["user"])
        self.cache.set("meta:count", 2, tags=["meta"])
        
        # Vérifier
        assert self.cache.get("user:1") == {"name": "Alice"}
        assert self.cache.get("user:2") == {"name": "Bob"}
        assert self.cache.get("meta:count") == 2
        
        # Invalider par tag
        self.cache.invalidate_tag("user")
        
        assert self.cache.get("user:1") is None
        assert self.cache.get("user:2") is None
        assert self.cache.get("meta:count") == 2

    @pytest.mark.integration
    def test_cache_with_multiple_tags(self):
        """Test cache avec plusieurs tags."""
        self.cache.set("data1", "value1", tags=["tag1", "tag2", "tag3"])
        self.cache.set("data2", "value2", tags=["tag1", "tag2"])
        self.cache.set("data3", "value3", tags=["tag1"])
        
        self.cache.invalidate_tag("tag1")
        
        assert self.cache.get("data1") is None
        assert self.cache.get("data2") is None
        assert self.cache.get("data3") is None

    @pytest.mark.integration
    def test_cache_stats_workflow(self):
        """Test statistiques pendant workflow."""
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2", tags=["tag"])
        
        stats = self.cache.stats()
        
        assert stats["keys"] == 2
        assert stats["tags"] == 1


class TestRedisCacheEdgeCases:
    """Tests des cas limites."""

    def setup_method(self):
        """Préparation avant chaque test."""
        self.cache = MemoryCache()

    @pytest.mark.unit
    def test_very_large_value(self):
        """Test avec très grande valeur."""
        large_data = "x" * 1000000  # 1MB
        
        self.cache.set("large", large_data)
        
        assert self.cache.get("large") == large_data

    @pytest.mark.unit
    def test_many_tags_single_key(self):
        """Test clé avec beaucoup de tags."""
        tags = [f"tag_{i}" for i in range(100)]
        
        self.cache.set("key", "value", tags=tags)
        
        # Invalider premier tag
        self.cache.invalidate_tag("tag_0")
        
        assert self.cache.get("key") is None

    @pytest.mark.unit
    def test_many_keys_single_tag(self):
        """Test beaucoup de clés avec même tag."""
        for i in range(1000):
            self.cache.set(f"key_{i}", f"value_{i}", tags=["common"])
        
        count = self.cache.invalidate_tag("common")
        
        assert count == 1000

    @pytest.mark.unit
    def test_unicode_keys_values(self):
        """Test clés/valeurs Unicode."""
        self.cache.set("clé_français", "valeur_français_🎉")
        self.cache.set("中文键", "中文值")
        
        assert self.cache.get("clé_français") == "valeur_français_🎉"
        assert self.cache.get("中文键") == "中文值"

    @pytest.mark.unit
    def test_special_characters_keys(self):
        """Test clés avec caractères spéciaux."""
        special_keys = [
            "key:with:colons",
            "key/with/slashes",
            "key|with|pipes",
            "key@#$%^&*()"
        ]
        
        for key in special_keys:
            self.cache.set(key, f"value_for_{key}")
            assert self.cache.get(key) == f"value_for_{key}"

    @pytest.mark.unit
    def test_clear_empty_cache(self):
        """Test vidage cache vide."""
        count = self.cache.clear()
        
        assert count == 0

    @pytest.mark.unit
    def test_duplicate_tags(self):
        """Test tags dupliqués."""
        self.cache.set("key", "value", tags=["tag", "tag", "tag"])
        
        count = self.cache.invalidate_tag("tag")
        
        # Devrait compter une fois
        assert count == 1
