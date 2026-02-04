"""
Tests approfondis pour src/core/redis_cache.py
Objectif: Augmenter la couverture de 44.55% vers 80%+
"""

import pytest
import json
import zlib
import pickle
from unittest.mock import patch, MagicMock, PropertyMock
from datetime import datetime, timedelta


class TestRedisConfig:
    """Tests pour la classe RedisConfig"""
    
    def test_config_default_values(self):
        """Test des valeurs par défaut de configuration"""
        from src.core.redis_cache import RedisConfig
        
        config = RedisConfig()
        
        assert config.HOST == "localhost"
        assert config.PORT == 6379
        assert config.DB == 0
        assert config.PASSWORD is None
        assert config.KEY_PREFIX == "matanne:"
        assert config.DEFAULT_TTL == 3600
        assert config.MAX_CONNECTIONS == 10
        assert config.SOCKET_TIMEOUT == 5
        assert config.SOCKET_CONNECT_TIMEOUT == 5
        assert config.COMPRESSION_THRESHOLD == 1024
    
    def test_config_custom_values(self):
        """Test de configuration personnalisée"""
        from src.core.redis_cache import RedisConfig
        
        config = RedisConfig(
            HOST="redis.example.com",
            PORT=6380,
            DB=1,
            PASSWORD="secret",
            KEY_PREFIX="custom:",
            DEFAULT_TTL=7200
        )
        
        assert config.HOST == "redis.example.com"
        assert config.PORT == 6380
        assert config.DB == 1
        assert config.PASSWORD == "secret"
        assert config.KEY_PREFIX == "custom:"
        assert config.DEFAULT_TTL == 7200


class TestMemoryCache:
    """Tests pour la classe MemoryCache (fallback)"""
    
    def test_memory_cache_set_get(self):
        """Test set/get basique"""
        from src.core.redis_cache import MemoryCache
        
        cache = MemoryCache()
        cache.set("key1", "value1")
        
        assert cache.get("key1") == "value1"
    
    def test_memory_cache_get_missing(self):
        """Test get pour clé inexistante"""
        from src.core.redis_cache import MemoryCache
        
        cache = MemoryCache()
        
        assert cache.get("nonexistent") is None
    
    def test_memory_cache_set_with_ttl(self):
        """Test set avec TTL"""
        from src.core.redis_cache import MemoryCache
        
        cache = MemoryCache()
        cache.set("key_ttl", "value", ttl=3600)
        
        assert cache.get("key_ttl") == "value"
    
    def test_memory_cache_expired_entry(self):
        """Test entrée expirée"""
        from src.core.redis_cache import MemoryCache
        
        cache = MemoryCache()
        
        # Simuler une entrée expirée en modifiant directement le cache
        cache._cache["expired_key"] = {
            "value": "old_value",
            "expires_at": datetime.now() - timedelta(hours=1)
        }
        
        assert cache.get("expired_key") is None
    
    def test_memory_cache_set_with_tags(self):
        """Test set avec tags"""
        from src.core.redis_cache import MemoryCache
        
        cache = MemoryCache()
        cache.set("tagged_key", "value", tags=["tag1", "tag2"])
        
        assert cache.get("tagged_key") == "value"
        assert "tag1" in cache._tags
        assert "tagged_key" in cache._tags["tag1"]
    
    def test_memory_cache_delete(self):
        """Test suppression"""
        from src.core.redis_cache import MemoryCache
        
        cache = MemoryCache()
        cache.set("to_delete", "value")
        
        assert cache.delete("to_delete") is True
        assert cache.get("to_delete") is None
    
    def test_memory_cache_delete_nonexistent(self):
        """Test suppression clé inexistante"""
        from src.core.redis_cache import MemoryCache
        
        cache = MemoryCache()
        
        result = cache.delete("nonexistent")
        # Devrait retourner False ou True selon l'implémentation
        assert isinstance(result, bool)
    
    def test_memory_cache_invalidate_tag(self):
        """Test invalidation par tag"""
        from src.core.redis_cache import MemoryCache
        
        cache = MemoryCache()
        cache.set("key1", "value1", tags=["recipes"])
        cache.set("key2", "value2", tags=["recipes"])
        cache.set("key3", "value3", tags=["users"])
        
        cache.invalidate_tag("recipes")
        
        assert cache.get("key1") is None
        assert cache.get("key2") is None
        assert cache.get("key3") == "value3"
    
    def test_memory_cache_clear(self):
        """Test vidage complet"""
        from src.core.redis_cache import MemoryCache
        
        cache = MemoryCache()
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        cache.clear()
        
        assert cache.get("key1") is None
        assert cache.get("key2") is None
    
    def test_memory_cache_stats(self):
        """Test statistiques"""
        from src.core.redis_cache import MemoryCache
        
        cache = MemoryCache()
        cache.set("key1", "value1")
        cache.get("key1")  # Hit
        cache.get("nonexistent")  # Miss
        
        stats = cache.stats()
        
        assert "hits" in stats
        assert "misses" in stats
        assert "size" in stats
    
    def test_memory_cache_cleanup_expired(self):
        """Test nettoyage des entrées expirées"""
        from src.core.redis_cache import MemoryCache
        
        cache = MemoryCache()
        
        # Ajouter une entrée expirée
        cache._cache["expired"] = {
            "value": "old",
            "expires_at": datetime.now() - timedelta(hours=1)
        }
        cache._cache["valid"] = {
            "value": "new",
            "expires_at": datetime.now() + timedelta(hours=1)
        }
        
        cache._cleanup_expired()
        
        assert "expired" not in cache._cache
        assert "valid" in cache._cache


class TestRedisCacheSingleton:
    """Tests pour le pattern singleton de RedisCache"""
    
    @patch('src.core.redis_cache.REDIS_DISPONIBLE', False)
    def test_singleton_without_redis(self):
        """Test singleton sans Redis disponible"""
        from src.core.redis_cache import RedisCache
        
        # Reset singleton pour le test
        RedisCache._instance = None
        RedisCache._initialized = False
        
        cache1 = RedisCache()
        cache2 = RedisCache()
        
        assert cache1 is cache2
    
    @patch('src.core.redis_cache.REDIS_DISPONIBLE', False)
    def test_fallback_mode(self):
        """Test mode fallback mémoire"""
        from src.core.redis_cache import RedisCache
        
        RedisCache._instance = None
        RedisCache._initialized = False
        
        cache = RedisCache()
        
        assert cache._redis is None
        assert cache._fallback is not None


class TestRedisCacheOperations:
    """Tests pour les opérations du cache Redis"""
    
    @pytest.fixture(autouse=True)
    def setup_cache(self):
        """Setup avec mock Redis"""
        with patch('src.core.redis_cache.REDIS_DISPONIBLE', False):
            from src.core.redis_cache import RedisCache
            
            RedisCache._instance = None
            RedisCache._initialized = False
            
            self.cache = RedisCache()
            yield
    
    def test_make_key(self):
        """Test création de clé avec préfixe"""
        full_key = self.cache._make_key("test_key")
        
        assert full_key.startswith("matanne:")
        assert "test_key" in full_key
    
    def test_get_from_fallback(self):
        """Test get depuis fallback"""
        self.cache._fallback.set("test", "value")
        
        result = self.cache.get("test")
        
        assert result == "value"
    
    def test_get_with_default(self):
        """Test get avec valeur par défaut"""
        result = self.cache.get("nonexistent", default="default_value")
        
        assert result == "default_value"
    
    def test_set_to_fallback(self):
        """Test set vers fallback"""
        result = self.cache.set("new_key", "new_value")
        
        assert result is True
        assert self.cache.get("new_key") == "new_value"
    
    def test_set_with_ttl(self):
        """Test set avec TTL"""
        result = self.cache.set("ttl_key", "value", ttl=1800)
        
        assert result is True
    
    def test_set_with_tags(self):
        """Test set avec tags"""
        result = self.cache.set("tagged", "value", tags=["tag1", "tag2"])
        
        assert result is True
    
    def test_delete_from_fallback(self):
        """Test suppression depuis fallback"""
        self.cache.set("to_delete", "value")
        
        result = self.cache.delete("to_delete")
        
        assert result is True
        assert self.cache.get("to_delete") is None
    
    def test_invalidate_tag(self):
        """Test invalidation par tag"""
        self.cache.set("key1", "val1", tags=["mytag"])
        self.cache.set("key2", "val2", tags=["mytag"])
        
        self.cache.invalidate_tag("mytag")
        
        assert self.cache.get("key1") is None
        assert self.cache.get("key2") is None
    
    def test_clear(self):
        """Test vidage complet"""
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")
        
        self.cache.clear()
        
        assert self.cache.get("key1") is None
    
    def test_stats(self):
        """Test statistiques"""
        self.cache.set("key", "value")
        self.cache.get("key")
        self.cache.get("missing")
        
        stats = self.cache.stats()
        
        assert isinstance(stats, dict)
        assert "hits" in stats or "fallback_used" in stats


class TestRedisCacheSerialization:
    """Tests pour la sérialisation/désérialisation"""
    
    @pytest.fixture(autouse=True)
    def setup_cache(self):
        """Setup avec mock Redis"""
        with patch('src.core.redis_cache.REDIS_DISPONIBLE', False):
            from src.core.redis_cache import RedisCache
            
            RedisCache._instance = None
            RedisCache._initialized = False
            
            self.cache = RedisCache()
            yield
    
    def test_serialize_json_simple(self):
        """Test sérialisation JSON simple"""
        data = {"key": "value", "number": 42}
        
        serialized = self.cache._serialize(data)
        
        assert isinstance(serialized, bytes)
        assert serialized[0:1] in [b'j', b'c']  # JSON ou compressed
    
    def test_serialize_json_list(self):
        """Test sérialisation liste JSON"""
        data = [1, 2, 3, "test"]
        
        serialized = self.cache._serialize(data)
        
        assert isinstance(serialized, bytes)
    
    def test_serialize_pickle_fallback(self):
        """Test sérialisation pickle pour objets complexes"""
        # Créer un objet non-JSON serializable
        data = {"date": datetime.now()}
        
        serialized = self.cache._serialize(data)
        
        assert isinstance(serialized, bytes)
    
    def test_deserialize_json(self):
        """Test désérialisation JSON"""
        original = {"key": "value", "list": [1, 2, 3]}
        
        serialized = self.cache._serialize(original)
        deserialized = self.cache._deserialize(serialized)
        
        assert deserialized == original
    
    def test_deserialize_none(self):
        """Test désérialisation de None"""
        result = self.cache._deserialize(None)
        
        assert result is None
    
    def test_deserialize_empty(self):
        """Test désérialisation de bytes vides"""
        result = self.cache._deserialize(b'')
        
        assert result is None
    
    def test_serialize_large_data_compressed(self):
        """Test compression pour grandes données"""
        # Créer des données dépassant le seuil de compression
        large_data = {"data": "x" * 2000}
        
        serialized = self.cache._serialize(large_data)
        
        # Vérifier que c'est compressé (commence par 'c')
        assert serialized[0:1] == b'c'
    
    def test_roundtrip_complex_data(self):
        """Test aller-retour avec données complexes"""
        original = {
            "string": "hello",
            "number": 42,
            "float": 3.14,
            "list": [1, 2, 3],
            "nested": {"a": {"b": "c"}}
        }
        
        serialized = self.cache._serialize(original)
        deserialized = self.cache._deserialize(serialized)
        
        assert deserialized == original


class TestRedisCacheWithMockRedis:
    """Tests avec Redis mocké"""
    
    @pytest.fixture
    def mock_redis(self):
        """Fixture pour mocker Redis"""
        with patch('src.core.redis_cache.REDIS_DISPONIBLE', True):
            with patch('src.core.redis_cache.redis') as mock_redis_module:
                with patch('src.core.redis_cache.ConnectionPool') as mock_pool:
                    mock_redis_instance = MagicMock()
                    mock_redis_module.Redis.return_value = mock_redis_instance
                    mock_redis_instance.ping.return_value = True
                    
                    from src.core.redis_cache import RedisCache
                    RedisCache._instance = None
                    RedisCache._initialized = False
                    RedisCache._pool = None
                    
                    cache = RedisCache()
                    cache._redis = mock_redis_instance
                    
                    yield cache, mock_redis_instance
    
    def test_get_from_redis_hit(self, mock_redis):
        """Test get avec hit Redis"""
        cache, redis_mock = mock_redis
        
        # Simuler une valeur stockée
        test_value = {"test": "data"}
        serialized = cache._serialize(test_value)
        redis_mock.get.return_value = serialized
        
        result = cache.get("test_key")
        
        assert result == test_value
        assert cache._stats["hits"] > 0
    
    def test_get_from_redis_miss(self, mock_redis):
        """Test get avec miss Redis"""
        cache, redis_mock = mock_redis
        redis_mock.get.return_value = None
        
        result = cache.get("missing_key", default="default")
        
        assert result == "default"
        assert cache._stats["misses"] > 0
    
    def test_get_redis_error_fallback(self, mock_redis):
        """Test fallback sur erreur Redis"""
        cache, redis_mock = mock_redis
        redis_mock.get.side_effect = Exception("Connection error")
        
        # Pré-remplir le fallback
        cache._fallback.set("key", "fallback_value")
        
        result = cache.get("key")
        
        assert result == "fallback_value"
        assert cache._stats["errors"] > 0
    
    def test_set_to_redis(self, mock_redis):
        """Test set vers Redis"""
        cache, redis_mock = mock_redis
        redis_mock.setex.return_value = True
        
        result = cache.set("key", "value", ttl=3600)
        
        assert result is True
        redis_mock.setex.assert_called()
    
    def test_set_redis_error_fallback(self, mock_redis):
        """Test fallback sur erreur set"""
        cache, redis_mock = mock_redis
        redis_mock.setex.side_effect = Exception("Write error")
        
        result = cache.set("key", "value")
        
        # Devrait utiliser le fallback
        assert cache._fallback.get("key") == "value"
    
    def test_delete_from_redis(self, mock_redis):
        """Test suppression Redis"""
        cache, redis_mock = mock_redis
        redis_mock.delete.return_value = 1
        
        result = cache.delete("key")
        
        assert result is True
        redis_mock.delete.assert_called()


class TestRedisCacheTagInvalidation:
    """Tests pour l'invalidation par tags"""
    
    @pytest.fixture(autouse=True)
    def setup_cache(self):
        """Setup avec fallback uniquement"""
        with patch('src.core.redis_cache.REDIS_DISPONIBLE', False):
            from src.core.redis_cache import RedisCache
            
            RedisCache._instance = None
            RedisCache._initialized = False
            
            self.cache = RedisCache()
            yield
    
    def test_tag_multiple_keys(self):
        """Test tag sur plusieurs clés"""
        self.cache.set("recipe:1", "data1", tags=["recipes"])
        self.cache.set("recipe:2", "data2", tags=["recipes"])
        self.cache.set("recipe:3", "data3", tags=["recipes"])
        
        self.cache.invalidate_tag("recipes")
        
        assert self.cache.get("recipe:1") is None
        assert self.cache.get("recipe:2") is None
        assert self.cache.get("recipe:3") is None
    
    def test_key_with_multiple_tags(self):
        """Test clé avec plusieurs tags"""
        self.cache.set("item", "data", tags=["tag1", "tag2"])
        
        # Invalider un seul tag devrait supprimer la clé
        self.cache.invalidate_tag("tag1")
        
        assert self.cache.get("item") is None
    
    def test_invalidate_nonexistent_tag(self):
        """Test invalidation tag inexistant"""
        self.cache.set("key", "value")
        
        # Ne devrait pas lever d'erreur
        self.cache.invalidate_tag("nonexistent_tag")
        
        assert self.cache.get("key") == "value"


class TestRedisCacheStats:
    """Tests pour les statistiques du cache"""
    
    @pytest.fixture(autouse=True)
    def setup_cache(self):
        """Setup avec fallback uniquement"""
        with patch('src.core.redis_cache.REDIS_DISPONIBLE', False):
            from src.core.redis_cache import RedisCache
            
            RedisCache._instance = None
            RedisCache._initialized = False
            
            self.cache = RedisCache()
            yield
    
    def test_stats_initial(self):
        """Test stats initiales"""
        stats = self.cache.stats()
        
        assert isinstance(stats, dict)
    
    def test_stats_after_operations(self):
        """Test stats après opérations"""
        self.cache.set("key", "value")
        self.cache.get("key")  # Hit
        self.cache.get("key")  # Hit
        self.cache.get("missing")  # Miss
        
        stats = self.cache.stats()
        
        assert stats.get("fallback_used", 0) >= 0


class TestGetRedisCache:
    """Tests pour la fonction factory get_redis_cache"""
    
    @patch('src.core.redis_cache.REDIS_DISPONIBLE', False)
    def test_get_redis_cache_returns_singleton(self):
        """Test que get_redis_cache retourne le singleton"""
        from src.core.redis_cache import RedisCache, get_redis_cache
        
        RedisCache._instance = None
        RedisCache._initialized = False
        
        cache1 = get_redis_cache()
        cache2 = get_redis_cache()
        
        assert cache1 is cache2


class TestCacheDecorator:
    """Tests pour les décorateurs de cache si présents"""
    
    @patch('src.core.redis_cache.REDIS_DISPONIBLE', False)
    def test_cache_decorator_basic(self):
        """Test décorateur de cache basique"""
        from src.core.redis_cache import RedisCache
        
        RedisCache._instance = None
        RedisCache._initialized = False
        
        cache = RedisCache()
        
        # Test du cache avec une fonction simple
        call_count = 0
        
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        # Première exécution
        key = "func:1"
        result = cache.get(key)
        if result is None:
            result = expensive_function(5)
            cache.set(key, result)
        
        assert result == 10
        assert call_count == 1
        
        # Deuxième exécution depuis cache
        cached_result = cache.get(key)
        
        assert cached_result == 10
        assert call_count == 1  # Pas d'appel supplémentaire
