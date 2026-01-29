"""
Tests pour les optimisations de performance
- Redis Cache
- Query Optimizer (N+1 prevention)
- Lazy Image Loader
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import json


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS REDIS CACHE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class TestRedisCache:
    """Tests pour le cache Redis"""
    
    def test_redis_cache_singleton(self):
        """Le cache Redis est un singleton"""
        from src.core.performance_optimizations import RedisCache
        
        # Reset singleton pour test
        RedisCache._instance = None
        RedisCache._client = None
        RedisCache._fallback_cache = {}
        
        cache1 = RedisCache()
        cache2 = RedisCache()
        
        assert cache1 is cache2
    
    def test_fallback_cache_set_get(self):
        """Set/Get fonctionne avec le fallback mémoire"""
        from src.core.performance_optimizations import RedisCache
        
        # Reset et désactiver Redis
        RedisCache._instance = None
        RedisCache._client = None
        RedisCache._fallback_cache = {}
        
        cache = RedisCache()
        cache._client = None  # Force fallback
        
        cache.set("test_key", {"value": 42}, ttl=3600)
        result = cache.get("test_key")
        
        assert result == {"value": 42}
    
    def test_fallback_cache_expiry(self):
        """Le cache mémoire expire correctement"""
        from src.core.performance_optimizations import RedisCache
        import time
        
        RedisCache._instance = None
        RedisCache._client = None
        RedisCache._fallback_cache = {}
        
        cache = RedisCache()
        cache._client = None
        
        # Set avec TTL très court
        cache.set("expire_key", "value", ttl=1)
        
        # Devrait être accessible immédiatement
        assert cache.get("expire_key") == "value"
        
        # Simuler expiration en manipulant le timestamp
        import time as time_module
        key, (val, expiry) = list(cache._fallback_cache.items())[0]
        cache._fallback_cache[key] = (val, time_module.time() - 1)
        
        # Devrait être expiré
        assert cache.get("expire_key") is None
    
    def test_delete_key(self):
        """Suppression d'une clé fonctionne"""
        from src.core.performance_optimizations import RedisCache
        
        RedisCache._instance = None
        RedisCache._client = None
        RedisCache._fallback_cache = {}
        
        cache = RedisCache()
        cache._client = None
        
        cache.set("to_delete", "value")
        assert cache.get("to_delete") == "value"
        
        cache.delete("to_delete")
        assert cache.get("to_delete") is None
    
    def test_clear_pattern(self):
        """Clear pattern supprime les clés matching"""
        from src.core.performance_optimizations import RedisCache
        
        RedisCache._instance = None
        RedisCache._client = None
        RedisCache._fallback_cache = {}
        
        cache = RedisCache()
        cache._client = None
        
        cache.set("recettes:1", "r1")
        cache.set("recettes:2", "r2")
        cache.set("users:1", "u1")
        
        count = cache.clear_pattern("recettes:*")
        
        assert count == 2
        assert cache.get("recettes:1") is None
        assert cache.get("users:1") == "u1"
    
    def test_stats(self):
        """Les stats retournent les bonnes infos"""
        from src.core.performance_optimizations import RedisCache
        
        RedisCache._instance = None
        RedisCache._client = None
        RedisCache._fallback_cache = {}
        
        cache = RedisCache()
        cache._client = None
        
        cache.set("key1", "v1")
        cache.set("key2", "v2")
        
        stats = cache.stats()
        
        assert stats["backend"] == "memory"
        assert stats["memory_keys"] == 2
    
    def test_is_available_false_without_redis(self):
        """is_available retourne False sans Redis"""
        from src.core.performance_optimizations import RedisCache
        
        RedisCache._instance = None
        RedisCache._client = None
        RedisCache._fallback_cache = {}
        
        cache = RedisCache()
        cache._client = None
        
        assert cache.is_available is False


class TestRedisCachedDecorator:
    """Tests pour le décorateur redis_cached"""
    
    def test_decorator_caches_result(self):
        """Le décorateur met en cache le résultat"""
        from src.core.performance_optimizations import redis_cached, RedisCache
        
        RedisCache._instance = None
        RedisCache._client = None
        RedisCache._fallback_cache = {}
        
        call_count = 0
        
        @redis_cached("test", ttl=3600)
        def expensive_function():
            nonlocal call_count
            call_count += 1
            return {"result": call_count}
        
        result1 = expensive_function()
        result2 = expensive_function()
        
        assert result1 == {"result": 1}
        assert result2 == {"result": 1}  # Même résultat (caché)
        assert call_count == 1  # Appelé une seule fois
    
    def test_decorator_different_args(self):
        """Le décorateur cache séparément pour différents args"""
        from src.core.performance_optimizations import redis_cached, RedisCache
        
        RedisCache._instance = None
        RedisCache._client = None
        RedisCache._fallback_cache = {}
        
        @redis_cached("test", ttl=3600)
        def func_with_args(x, y):
            return x + y
        
        result1 = func_with_args(1, 2)
        result2 = func_with_args(3, 4)
        
        assert result1 == 3
        assert result2 == 7


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS QUERY OPTIMIZER
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class TestQueryOptimizer:
    """Tests pour le QueryOptimizer (prévention N+1)"""
    
    def test_optimizer_init(self):
        """L'optimizer s'initialise correctement"""
        from src.core.performance_optimizations import QueryOptimizer
        
        mock_session = Mock()
        optimizer = QueryOptimizer(mock_session)
        
        assert optimizer.session is mock_session
        assert optimizer._query is None
    
    def test_query_creates_query(self):
        """La méthode query crée une requête"""
        from src.core.performance_optimizations import QueryOptimizer
        
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        
        class FakeModel:
            pass
        
        optimizer = QueryOptimizer(mock_session)
        result = optimizer.query(FakeModel)
        
        mock_session.query.assert_called_once_with(FakeModel)
        assert result is optimizer
    
    def test_filter_adds_filters(self):
        """La méthode filter ajoute des filtres"""
        from src.core.performance_optimizations import QueryOptimizer
        
        mock_session = Mock()
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_session.query.return_value = mock_query
        
        class FakeModel:
            id = Mock()
        
        optimizer = QueryOptimizer(mock_session)
        optimizer.query(FakeModel).filter(FakeModel.id == 1)
        
        mock_query.filter.assert_called_once()
    
    def test_all_returns_results(self):
        """La méthode all retourne les résultats"""
        from src.core.performance_optimizations import QueryOptimizer
        
        mock_session = Mock()
        mock_query = Mock()
        mock_query.all.return_value = [1, 2, 3]
        mock_session.query.return_value = mock_query
        
        class FakeModel:
            pass
        
        optimizer = QueryOptimizer(mock_session)
        results = optimizer.query(FakeModel).all()
        
        assert results == [1, 2, 3]
    
    def test_first_returns_first(self):
        """La méthode first retourne le premier résultat"""
        from src.core.performance_optimizations import QueryOptimizer
        
        mock_session = Mock()
        mock_query = Mock()
        mock_query.first.return_value = "first_item"
        mock_session.query.return_value = mock_query
        
        class FakeModel:
            pass
        
        optimizer = QueryOptimizer(mock_session)
        result = optimizer.query(FakeModel).first()
        
        assert result == "first_item"
    
    def test_count_returns_count(self):
        """La méthode count retourne le nombre"""
        from src.core.performance_optimizations import QueryOptimizer
        
        mock_session = Mock()
        mock_query = Mock()
        mock_query.count.return_value = 42
        mock_session.query.return_value = mock_query
        
        class FakeModel:
            pass
        
        optimizer = QueryOptimizer(mock_session)
        count = optimizer.query(FakeModel).count()
        
        assert count == 42
    
    def test_limit_and_offset(self):
        """Les méthodes limit et offset fonctionnent"""
        from src.core.performance_optimizations import QueryOptimizer
        
        mock_session = Mock()
        mock_query = Mock()
        mock_query.limit.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_session.query.return_value = mock_query
        
        class FakeModel:
            pass
        
        optimizer = QueryOptimizer(mock_session)
        optimizer.query(FakeModel).limit(10).offset(5)
        
        mock_query.limit.assert_called_once_with(10)
        mock_query.offset.assert_called_once_with(5)
    
    def test_exists_true(self):
        """exists retourne True si count > 0"""
        from src.core.performance_optimizations import QueryOptimizer
        
        mock_session = Mock()
        mock_query = Mock()
        mock_query.count.return_value = 5
        mock_session.query.return_value = mock_query
        
        class FakeModel:
            pass
        
        optimizer = QueryOptimizer(mock_session)
        assert optimizer.query(FakeModel).exists() is True
    
    def test_exists_false(self):
        """exists retourne False si count == 0"""
        from src.core.performance_optimizations import QueryOptimizer
        
        mock_session = Mock()
        mock_query = Mock()
        mock_query.count.return_value = 0
        mock_session.query.return_value = mock_query
        
        class FakeModel:
            pass
        
        optimizer = QueryOptimizer(mock_session)
        assert optimizer.query(FakeModel).exists() is False
    
    def test_query_none_returns_empty(self):
        """Sans query, les méthodes retournent des valeurs par défaut"""
        from src.core.performance_optimizations import QueryOptimizer
        
        mock_session = Mock()
        optimizer = QueryOptimizer(mock_session)
        
        assert optimizer.all() == []
        assert optimizer.first() is None
        assert optimizer.count() == 0
    
    def test_with_related_raises_without_query(self):
        """with_related raise si pas de query"""
        from src.core.performance_optimizations import QueryOptimizer
        
        mock_session = Mock()
        optimizer = QueryOptimizer(mock_session)
        
        with pytest.raises(ValueError, match="Appelez query"):
            optimizer.with_related("ingredients")


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS LAZY IMAGE LOADER
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class TestLazyImageLoader:
    """Tests pour le LazyImageLoader"""
    
    def test_init(self):
        """Le loader s'initialise correctement"""
        from src.core.performance_optimizations import LazyImageLoader
        
        loader = LazyImageLoader(cache_ttl=7200)
        
        assert loader.cache_ttl == 7200
        assert len(loader._loading) == 0
        assert len(loader._loaded_urls) == 0
    
    def test_placeholder_property(self):
        """La propriété placeholder retourne l'URL"""
        from src.core.performance_optimizations import LazyImageLoader
        
        loader = LazyImageLoader()
        
        assert loader.placeholder.startswith("data:image/svg+xml")
    
    def test_get_image_url_with_url(self):
        """get_image_url retourne l'URL si fournie"""
        from src.core.performance_optimizations import LazyImageLoader
        
        loader = LazyImageLoader()
        
        result = loader.get_image_url(1, "https://example.com/image.jpg")
        
        assert result == "https://example.com/image.jpg"
    
    def test_get_image_url_without_url(self):
        """get_image_url retourne le placeholder si pas d'URL"""
        from src.core.performance_optimizations import LazyImageLoader
        
        loader = LazyImageLoader()
        
        result = loader.get_image_url(1, None)
        
        assert result == loader.placeholder
    
    def test_get_image_url_loaded(self):
        """get_image_url retourne l'URL chargée"""
        from src.core.performance_optimizations import LazyImageLoader
        
        loader = LazyImageLoader()
        loader._loaded_urls[1] = "https://loaded.com/image.jpg"
        
        result = loader.get_image_url(1, None)
        
        assert result == "https://loaded.com/image.jpg"
    
    def test_should_load_true(self):
        """should_load retourne True si pas en cours"""
        from src.core.performance_optimizations import LazyImageLoader
        
        loader = LazyImageLoader()
        
        assert loader.should_load(1) is True
    
    def test_should_load_false_loading(self):
        """should_load retourne False si en cours"""
        from src.core.performance_optimizations import LazyImageLoader
        
        loader = LazyImageLoader()
        loader._loading.add(1)
        
        assert loader.should_load(1) is False
    
    def test_should_load_false_loaded(self):
        """should_load retourne False si déjà chargé"""
        from src.core.performance_optimizations import LazyImageLoader
        
        loader = LazyImageLoader()
        loader._loaded_urls[1] = "url"
        
        assert loader.should_load(1) is False
    
    def test_mark_loading(self):
        """mark_loading ajoute l'ID aux en cours"""
        from src.core.performance_optimizations import LazyImageLoader
        
        loader = LazyImageLoader()
        loader.mark_loading(42)
        
        assert 42 in loader._loading
    
    def test_mark_loaded(self):
        """mark_loaded retire des en cours et ajoute aux chargés"""
        from src.core.performance_optimizations import LazyImageLoader
        
        loader = LazyImageLoader()
        loader._loading.add(42)
        
        loader.mark_loaded(42, "https://final.com/image.jpg")
        
        assert 42 not in loader._loading
        assert loader._loaded_urls[42] == "https://final.com/image.jpg"
    
    def test_generate_lazy_html(self):
        """generate_lazy_html génère le HTML correct"""
        from src.core.performance_optimizations import LazyImageLoader
        
        loader = LazyImageLoader()
        
        html = loader.generate_lazy_html(1, "https://example.com/img.jpg", "Alt text")
        
        assert 'data-src="https://example.com/img.jpg"' in html
        assert 'data-recette-id="1"' in html
        assert 'alt="Alt text"' in html
        assert 'class="lazy-image"' in html
        assert 'loading="lazy"' in html
    
    def test_get_css(self):
        """get_css retourne du CSS valide"""
        from src.core.performance_optimizations import LazyImageLoader
        
        loader = LazyImageLoader()
        css = loader.get_css()
        
        assert "<style>" in css
        assert ".lazy-image" in css
        assert "@keyframes shimmer" in css
    
    def test_get_javascript(self):
        """get_javascript retourne du JS valide"""
        from src.core.performance_optimizations import LazyImageLoader
        
        loader = LazyImageLoader()
        js = loader.get_javascript()
        
        assert "<script>" in js
        assert "IntersectionObserver" in js
        assert "data.src" in js or "dataset.src" in js
    
    def test_clear_cache(self):
        """clear_cache vide les caches"""
        from src.core.performance_optimizations import LazyImageLoader
        
        loader = LazyImageLoader()
        loader._loading.add(1)
        loader._loaded_urls[2] = "url"
        
        loader.clear_cache()
        
        assert len(loader._loading) == 0
        assert len(loader._loaded_urls) == 0


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS HELPER FUNCTIONS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class TestHelperFunctions:
    """Tests pour les fonctions helpers"""
    
    def test_get_redis_cache_singleton(self):
        """get_redis_cache retourne un singleton"""
        from src.core.performance_optimizations import get_redis_cache, RedisCache
        
        # Reset
        RedisCache._instance = None
        
        import src.core.performance_optimizations as module
        module._redis_cache_instance = None
        
        cache1 = get_redis_cache()
        cache2 = get_redis_cache()
        
        assert cache1 is cache2
    
    def test_get_lazy_image_loader_singleton(self):
        """get_lazy_image_loader retourne un singleton"""
        import src.core.performance_optimizations as module
        module._lazy_loader_instance = None
        
        from src.core.performance_optimizations import get_lazy_image_loader
        
        loader1 = get_lazy_image_loader()
        loader2 = get_lazy_image_loader()
        
        assert loader1 is loader2
    
    def test_invalidate_cache(self):
        """invalidate_cache appelle clear_pattern"""
        from src.core.performance_optimizations import invalidate_cache, RedisCache
        
        RedisCache._instance = None
        RedisCache._client = None
        RedisCache._fallback_cache = {}
        
        import src.core.performance_optimizations as module
        module._redis_cache_instance = None
        
        cache = RedisCache()
        cache.set("recettes:1", "r1")
        cache.set("recettes:2", "r2")
        
        count = invalidate_cache("recettes:*")
        
        assert count == 2
    
    def test_get_query_optimizer(self):
        """get_query_optimizer retourne un optimizer"""
        from src.core.performance_optimizations import get_query_optimizer, QueryOptimizer
        
        mock_session = Mock()
        optimizer = get_query_optimizer(mock_session)
        
        assert isinstance(optimizer, QueryOptimizer)
        assert optimizer.session is mock_session


class TestBatchOperations:
    """Tests pour les opérations batch"""
    
    def test_batch_load_images(self):
        """batch_load_images charge les images"""
        import src.core.performance_optimizations as module
        module._lazy_loader_instance = None
        
        from src.core.performance_optimizations import batch_load_images, LazyImageLoader
        
        def get_url(rid):
            return f"https://example.com/{rid}.jpg"
        
        results = batch_load_images([1, 2, 3], get_url)
        
        assert results[1] == "https://example.com/1.jpg"
        assert results[2] == "https://example.com/2.jpg"
        assert results[3] == "https://example.com/3.jpg"
    
    def test_batch_load_images_skips_loaded(self):
        """batch_load_images ne recharge pas les images chargées"""
        import src.core.performance_optimizations as module
        module._lazy_loader_instance = None
        
        from src.core.performance_optimizations import batch_load_images, get_lazy_image_loader
        
        loader = get_lazy_image_loader()
        loader._loaded_urls[1] = "already_loaded.jpg"
        
        call_count = 0
        def get_url(rid):
            nonlocal call_count
            call_count += 1
            return f"https://example.com/{rid}.jpg"
        
        results = batch_load_images([1, 2], get_url)
        
        assert call_count == 1  # Seulement pour ID 2
        assert 1 not in results  # ID 1 pas rechargé


class TestEagerLoadingDecorator:
    """Tests pour le décorateur with_eager_loading"""
    
    def test_decorator_adds_hint(self):
        """Le décorateur ajoute un hint pour les relations"""
        from src.core.performance_optimizations import with_eager_loading
        
        @with_eager_loading("ingredients", "etapes")
        def my_function(**kwargs):
            return kwargs
        
        result = my_function(other_arg="value")
        
        assert result["_eager_load"] == ("ingredients", "etapes")
        assert result["other_arg"] == "value"

