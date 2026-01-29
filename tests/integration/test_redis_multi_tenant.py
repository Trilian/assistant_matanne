"""Tests unitaires pour redis_cache et multi_tenant."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch
import json


# =============================================================================
# TESTS REDIS CACHE
# =============================================================================

class TestRedisConfig:
    """Tests pour RedisConfig."""

    def test_config_defaults(self):
        """Valeurs par défaut de configuration Redis."""
        from src.core.redis_cache import RedisConfig
        
        config = RedisConfig()
        
        # Valeurs par défaut attendues
        assert config.HOST == "localhost"
        assert config.PORT == 6379
        assert config.DB == 0


class TestMemoryCache:
    """Tests pour MemoryCache (cache fallback en mémoire)."""

    def test_memory_cache_get_set(self):
        """Get/Set basique."""
        from src.core.redis_cache import MemoryCache
        
        cache = MemoryCache()
        
        cache.set("test_key", "test_value")
        result = cache.get("test_key")
        
        assert result == "test_value"

    def test_memory_cache_get_inexistant(self):
        """Get clé inexistante."""
        from src.core.redis_cache import MemoryCache
        
        cache = MemoryCache()
        
        result = cache.get("cle_inexistante")
        
        assert result is None

    def test_memory_cache_ttl_expiration(self):
        """Expiration par TTL."""
        from src.core.redis_cache import MemoryCache
        import time
        
        cache = MemoryCache()
        
        # TTL très court (1 seconde)
        cache.set("ephemere", "valeur", ttl=1)
        
        # Immédiatement disponible
        assert cache.get("ephemere") == "valeur"
        
        # Après expiration
        time.sleep(1.5)
        assert cache.get("ephemere") is None

    def test_memory_cache_delete(self):
        """Suppression de clé."""
        from src.core.redis_cache import MemoryCache
        
        cache = MemoryCache()
        
        cache.set("a_supprimer", "valeur")
        assert cache.get("a_supprimer") == "valeur"
        
        cache.delete("a_supprimer")
        assert cache.get("a_supprimer") is None

    def test_memory_cache_invalidate_tag(self):
        """Invalidation par tag."""
        from src.core.redis_cache import MemoryCache
        
        cache = MemoryCache()
        
        # Ajouter avec tags
        cache.set("recette_1", "data1", tags=["recettes"])
        cache.set("recette_2", "data2", tags=["recettes"])
        cache.set("autre", "data3", tags=["autre"])
        
        # Invalider le tag "recettes"
        cache.invalidate_tag("recettes")
        
        # Les recettes sont invalidées
        assert cache.get("recette_1") is None
        assert cache.get("recette_2") is None
        # L'autre est préservé
        assert cache.get("autre") == "data3"

    def test_memory_cache_clear(self):
        """Vidage complet du cache."""
        from src.core.redis_cache import MemoryCache
        
        cache = MemoryCache()
        
        cache.set("key1", "val1")
        cache.set("key2", "val2")
        
        cache.clear()
        
        assert cache.get("key1") is None
        assert cache.get("key2") is None

    def test_memory_cache_stats(self):
        """Statistiques du cache."""
        from src.core.redis_cache import MemoryCache
        
        cache = MemoryCache()
        cache.clear()
        
        cache.set("k1", "v1")
        cache.set("k2", "v2")
        
        stats = cache.stats()
        
        assert isinstance(stats, dict)
        assert "keys" in stats  # Le vrai format
        assert stats["keys"] == 2


class TestRedisCacheInit:
    """Tests d'initialisation de RedisCache."""

    def test_redis_cache_singleton(self):
        """RedisCache est un singleton."""
        from src.core.redis_cache import RedisCache
        
        cache1 = RedisCache()
        cache2 = RedisCache()
        
        assert cache1 is cache2

    def test_get_redis_cache(self):
        """La factory get_redis_cache retourne une instance."""
        from src.core.redis_cache import get_redis_cache
        
        cache = get_redis_cache()
        assert cache is not None


# =============================================================================
# TESTS MULTI-TENANT
# =============================================================================

class TestUserContext:
    """Tests pour UserContext."""

    def test_set_get_user(self):
        """Set et get de l'utilisateur."""
        from src.core.multi_tenant import UserContext
        
        UserContext.clear()
        
        UserContext.set_user("user-123")
        assert UserContext.get_user() == "user-123"
        
        UserContext.clear()

    def test_clear_user(self):
        """Clear efface l'utilisateur."""
        from src.core.multi_tenant import UserContext
        
        UserContext.set_user("user-456")
        UserContext.clear()
        
        assert UserContext.get_user() is None

    def test_bypass_isolation(self):
        """Bypass d'isolation pour admin."""
        from src.core.multi_tenant import UserContext
        
        UserContext.clear()
        
        assert UserContext.is_bypassed() is False
        
        UserContext.set_bypass(True)
        assert UserContext.is_bypassed() is True
        
        UserContext.set_bypass(False)
        assert UserContext.is_bypassed() is False


class TestUserContextManager:
    """Tests pour le context manager user_context."""

    def test_user_context_manager(self):
        """Context manager définit l'utilisateur temporairement."""
        from src.core.multi_tenant import UserContext, user_context
        
        UserContext.clear()
        
        with user_context("temp-user"):
            assert UserContext.get_user() == "temp-user"
        
        # Après le context, retour à None
        assert UserContext.get_user() is None

    def test_user_context_manager_nested(self):
        """Context managers imbriqués."""
        from src.core.multi_tenant import UserContext, user_context
        
        UserContext.clear()
        
        with user_context("user-1"):
            assert UserContext.get_user() == "user-1"
            
            with user_context("user-2"):
                assert UserContext.get_user() == "user-2"
            
            # Retour à user-1
            assert UserContext.get_user() == "user-1"


class TestAdminContext:
    """Tests pour admin_context."""

    def test_admin_context_bypass(self):
        """Admin context active le bypass."""
        from src.core.multi_tenant import UserContext, admin_context
        
        UserContext.clear()
        assert UserContext.is_bypassed() is False
        
        with admin_context():
            assert UserContext.is_bypassed() is True
        
        # Après le context, retour à False
        assert UserContext.is_bypassed() is False


class TestWithUserIsolationDecorator:
    """Tests pour le décorateur with_user_isolation."""

    def test_decorator_exists(self):
        """Le décorateur existe."""
        from src.core.multi_tenant import with_user_isolation
        
        assert callable(with_user_isolation)


class TestMultiTenantService:
    """Tests pour MultiTenantService."""

    def test_service_class_exists(self):
        """La classe MultiTenantService existe."""
        from src.core.multi_tenant import MultiTenantService
        
        assert MultiTenantService is not None


# =============================================================================
# TESTS LOGIQUE PURE
# =============================================================================

class TestTTLCalculation:
    """Tests pour les calculs de TTL."""

    def test_ttl_calcul_expiration(self):
        """Calcul de date d'expiration depuis TTL."""
        ttl_seconds = 3600
        
        now = datetime.now()
        expiry = now + timedelta(seconds=ttl_seconds)
        
        assert (expiry - now).total_seconds() == ttl_seconds

    def test_ttl_est_expire(self):
        """Vérification si une entrée est expirée."""
        def est_expire(expiry_timestamp: float) -> bool:
            return datetime.now().timestamp() > expiry_timestamp
        
        # Passé = expiré
        passe = datetime.now().timestamp() - 100
        assert est_expire(passe) is True
        
        # Futur = non expiré
        futur = datetime.now().timestamp() + 100
        assert est_expire(futur) is False


class TestKeyGeneration:
    """Tests pour la génération de clés cache."""

    def test_generer_cle_simple(self):
        """Génération de clé simple."""
        def gen_key(prefix: str, *args) -> str:
            return f"{prefix}:{':'.join(str(a) for a in args)}"
        
        key = gen_key("recettes", "user-1", "page-1")
        assert key == "recettes:user-1:page-1"

    def test_generer_cle_avec_hash(self):
        """Génération de clé avec hash pour données complexes."""
        import hashlib
        import json
        
        def gen_key_hash(prefix: str, data: dict) -> str:
            data_str = json.dumps(data, sort_keys=True)
            hash_val = hashlib.md5(data_str.encode()).hexdigest()[:8]
            return f"{prefix}:{hash_val}"
        
        data = {"filter": "actif", "page": 1}
        key = gen_key_hash("items", data)
        
        assert key.startswith("items:")
        assert len(key) == len("items:") + 8

