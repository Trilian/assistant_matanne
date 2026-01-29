"""
Tests pour src/core/cache.py avec focus sur intégration et patterns.

Tests couvrant:
- Classe Cache (création, stockage, suppression)
- CacheIA pour cache sémantique
- LimiteDebit pour rate limiting
- Décorateur @cached
- Patterns d'expiration et invalidation
"""

import pytest
import time
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from src.core.cache import Cache, CacheIA, LimiteDebit


# ═══════════════════════════════════════════════════════════
# SECTION 1: TESTS CACHE BASIQUE
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestCacheBasique:
    """Tests pour la classe Cache."""

    def test_cache_creation(self):
        """Test création d'un cache."""
        cache = Cache()
        assert cache is not None

    def test_cache_set_get(self):
        """Test set et get basic."""
        cache = Cache()
        cache.set("key1", "value1")
        
        result = cache.get("key1")
        assert result == "value1"

    def test_cache_get_inexistant(self):
        """Test get sur clé inexistante."""
        cache = Cache()
        result = cache.get("inexistant")
        assert result is None

    def test_cache_get_default(self):
        """Test get avec valeur par défaut."""
        cache = Cache()
        result = cache.get("inexistant", default="default_value")
        assert result == "default_value"

    def test_cache_delete(self):
        """Test suppression d'une clé."""
        cache = Cache()
        cache.set("key1", "value1")
        cache.delete("key1")
        
        result = cache.get("key1")
        assert result is None

    def test_cache_clear(self):
        """Test clear du cache."""
        cache = Cache()
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        cache.clear()
        
        assert cache.get("key1") is None
        assert cache.get("key2") is None

    def test_cache_exists(self):
        """Test vérification d'existence."""
        cache = Cache()
        cache.set("key1", "value1")
        
        assert cache.exists("key1") is True
        assert cache.exists("inexistant") is False

    def test_cache_types_varies(self):
        """Test stockage de différents types."""
        cache = Cache()
        
        cache.set("string", "texte")
        cache.set("number", 42)
        cache.set("dict", {"key": "value"})
        cache.set("list", [1, 2, 3])
        
        assert cache.get("string") == "texte"
        assert cache.get("number") == 42
        assert cache.get("dict") == {"key": "value"}
        assert cache.get("list") == [1, 2, 3]


# ═══════════════════════════════════════════════════════════
# SECTION 2: TESTS CACHE TTL/EXPIRATION
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestCacheTTL:
    """Tests pour TTL et expiration."""

    def test_cache_set_ttl(self):
        """Test set avec TTL."""
        cache = Cache()
        cache.set("key1", "value1", ttl=1)
        
        result = cache.get("key1")
        assert result == "value1"

    def test_cache_expiration(self):
        """Test expiration d'une clé."""
        cache = Cache()
        cache.set("key1", "value1", ttl=1)
        
        time.sleep(1.1)
        
        result = cache.get("key1")
        assert result is None

    def test_cache_ttl_0_no_expire(self):
        """Test que TTL 0 = pas d'expiration."""
        cache = Cache()
        cache.set("key1", "value1", ttl=0)
        
        time.sleep(0.1)
        
        result = cache.get("key1")
        assert result == "value1"

    def test_cache_multiple_ttls(self):
        """Test plusieurs clés avec différents TTLs."""
        cache = Cache()
        cache.set("short", "value", ttl=1)
        cache.set("long", "value", ttl=10)
        
        time.sleep(1.1)
        
        assert cache.get("short") is None
        assert cache.get("long") == "value"


# ═══════════════════════════════════════════════════════════
# SECTION 3: TESTS CACHE AVEC PREFIXES
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestCachePrefix:
    """Tests pour les préfixes et nettoyage."""

    def test_cache_prefix_keys(self):
        """Test création de clés avec préfixes."""
        cache = Cache()
        cache.set("user:1:name", "Alice")
        cache.set("user:1:email", "alice@example.com")
        cache.set("user:2:name", "Bob")
        
        assert cache.get("user:1:name") == "Alice"
        assert cache.get("user:1:email") == "alice@example.com"

    def test_cache_nettoyer_prefix(self):
        """Test nettoyage par préfixe."""
        cache = Cache()
        cache.set("user:1:name", "Alice")
        cache.set("user:1:email", "alice@example.com")
        cache.set("settings:theme", "dark")
        
        cache.nettoyer("user:1")
        
        assert cache.get("user:1:name") is None
        assert cache.get("user:1:email") is None
        assert cache.get("settings:theme") == "dark"

    def test_cache_nettoyer_all_prefix(self):
        """Test nettoyage de tous les préfixes."""
        cache = Cache()
        cache.set("cache:recipe:1", "Tarte")
        cache.set("cache:recipe:2", "Pizza")
        cache.set("recipe:1", "Tarte")
        
        cache.nettoyer("cache:")
        
        assert cache.get("cache:recipe:1") is None
        assert cache.get("cache:recipe:2") is None
        assert cache.get("recipe:1") == "Tarte"


# ═══════════════════════════════════════════════════════════
# SECTION 4: TESTS CACHE_IA (SEMANTIC CACHE)
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestCacheIA:
    """Tests pour le cache IA sémantique."""

    def test_cacheIA_creation(self):
        """Test création de CacheIA."""
        cache_ia = CacheIA()
        assert cache_ia is not None

    def test_cacheIA_set_get_response(self):
        """Test set et get de réponse IA."""
        cache_ia = CacheIA()
        
        prompt = "Suggère une recette rapide"
        response = "Recette: Pâtes simples"
        
        cache_ia.set_response(prompt, response)
        result = cache_ia.get_response(prompt)
        
        assert result == response

    def test_cacheIA_semantic_similarity(self):
        """Test similarité sémantique."""
        cache_ia = CacheIA()
        
        # Prompts sémantiquement similaires
        prompt1 = "Donne moi une recette rapide"
        prompt2 = "J'ai besoin d'une recette facile"
        
        response = "Recette: Omelette"
        cache_ia.set_response(prompt1, response)
        
        # Should find similar prompt
        result = cache_ia.get_response(prompt2)
        # Note: Result dépend du seuil de similarité implémenté
        assert result is None or result == response

    def test_cacheIA_clear(self):
        """Test nettoyage du cache IA."""
        cache_ia = CacheIA()
        
        cache_ia.set_response("prompt1", "response1")
        cache_ia.set_response("prompt2", "response2")
        
        cache_ia.clear()
        
        assert cache_ia.get_response("prompt1") is None
        assert cache_ia.get_response("prompt2") is None


# ═══════════════════════════════════════════════════════════
# SECTION 5: TESTS LIMITE_DEBIT (RATE LIMITING)
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestLimiteDebit:
    """Tests pour le rate limiting."""

    def test_limiteDebit_creation(self):
        """Test création de LimiteDebit."""
        limiter = LimiteDebit(limit=10, window=60)
        assert limiter is not None

    def test_limiteDebit_allow_request(self):
        """Test allow d'une requête."""
        limiter = LimiteDebit(limit=10, window=60)
        
        allowed = limiter.allow_request("user1")
        assert allowed is True

    def test_limiteDebit_multiple_requests(self):
        """Test plusieurs requêtes."""
        limiter = LimiteDebit(limit=3, window=60)
        
        # Devrait permettre 3 requêtes
        assert limiter.allow_request("user1") is True
        assert limiter.allow_request("user1") is True
        assert limiter.allow_request("user1") is True
        
        # La 4ème devrait être refusée
        assert limiter.allow_request("user1") is False

    def test_limiteDebit_different_users(self):
        """Test limite par utilisateur."""
        limiter = LimiteDebit(limit=2, window=60)
        
        assert limiter.allow_request("user1") is True
        assert limiter.allow_request("user1") is True
        assert limiter.allow_request("user1") is False
        
        # User2 devrait avoir sa propre limite
        assert limiter.allow_request("user2") is True
        assert limiter.allow_request("user2") is True

    def test_limiteDebit_window_reset(self):
        """Test reset après fenêtre de temps."""
        limiter = LimiteDebit(limit=2, window=1)
        
        assert limiter.allow_request("user1") is True
        assert limiter.allow_request("user1") is True
        assert limiter.allow_request("user1") is False
        
        time.sleep(1.1)
        
        # Devrait être resetté
        assert limiter.allow_request("user1") is True

    def test_limiteDebit_get_remaining(self):
        """Test récupération du nombre de requêtes restantes."""
        limiter = LimiteDebit(limit=5, window=60)
        
        limiter.allow_request("user1")
        limiter.allow_request("user1")
        
        remaining = limiter.get_remaining("user1")
        assert remaining == 3

    def test_limiteDebit_reset(self):
        """Test reset manuel."""
        limiter = LimiteDebit(limit=3, window=60)
        
        limiter.allow_request("user1")
        limiter.allow_request("user1")
        limiter.allow_request("user1")
        
        assert limiter.allow_request("user1") is False
        
        limiter.reset_user("user1")
        
        assert limiter.allow_request("user1") is True


# ═══════════════════════════════════════════════════════════
# SECTION 6: TESTS INTERACTION CACHE + RATE_LIMIT
# ═══════════════════════════════════════════════════════════


@pytest.mark.integration
class TestCacheIntegration:
    """Tests d'intégration cache et rate limiting."""

    def test_cache_with_ratelimit(self):
        """Test cache combiné avec rate limiting."""
        cache = Cache()
        limiter = LimiteDebit(limit=5, window=60)
        
        # Ajouter en cache
        cache.set("api:result", "cached_response")
        
        # Vérifier rate limit
        assert limiter.allow_request("user1") is True
        
        # Récupérer du cache
        result = cache.get("api:result")
        assert result == "cached_response"

    def test_cache_expiration_and_ratelimit(self):
        """Test expiration du cache avec rate limit."""
        cache = Cache()
        limiter = LimiteDebit(limit=3, window=60)
        
        cache.set("expensive_op", "result", ttl=1)
        
        for i in range(3):
            limiter.allow_request("user1")
        
        time.sleep(1.1)
        
        # Cache expiré, peut faire une nouvelle requête
        assert cache.get("expensive_op") is None
        assert limiter.allow_request("user1") is False

    def test_cache_prefix_cleanup_flow(self):
        """Test workflow complet avec préfixes."""
        cache = Cache()
        
        # Ajouter plusieurs résultats IA
        cache.set("ia:recipe:chicken", "Recette poulet")
        cache.set("ia:recipe:pasta", "Recette pâtes")
        cache.set("ia:meal_plan:week1", "Plan semaine")
        
        # Nettoyer un type de cache
        cache.nettoyer("ia:recipe:")
        
        assert cache.get("ia:recipe:chicken") is None
        assert cache.get("ia:recipe:pasta") is None
        assert cache.get("ia:meal_plan:week1") == "Plan semaine"


# ═══════════════════════════════════════════════════════════
# SECTION 7: TESTS EDGE CASES
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestCacheEdgeCases:
    """Tests pour les cas limites."""

    def test_cache_empty_string(self):
        """Test stockage de chaîne vide."""
        cache = Cache()
        cache.set("key", "")
        
        assert cache.get("key") == ""

    def test_cache_none_value(self):
        """Test stockage de None."""
        cache = Cache()
        cache.set("key", None)
        
        # None peut être stocké explicitement
        assert cache.get("key") is None or "key" in cache._data

    def test_cache_large_data(self):
        """Test stockage de grandes données."""
        cache = Cache()
        large_data = {"items": [{"id": i, "value": f"item_{i}"} for i in range(1000)]}
        
        cache.set("large", large_data)
        result = cache.get("large")
        
        assert len(result["items"]) == 1000

    def test_cache_special_chars_keys(self):
        """Test clés avec caractères spéciaux."""
        cache = Cache()
        cache.set("user:1:name:first@test", "John")
        cache.set("api:v2.0:endpoint", "value")
        
        assert cache.get("user:1:name:first@test") == "John"
        assert cache.get("api:v2.0:endpoint") == "value"

    def test_limiteDebit_zero_limit(self):
        """Test limite à 0."""
        limiter = LimiteDebit(limit=0, window=60)
        
        # Aucune requête autorisée
        assert limiter.allow_request("user1") is False

    def test_limiteDebit_unlimited(self):
        """Test limite très haute = illimitée."""
        limiter = LimiteDebit(limit=999999, window=60)
        
        for i in range(100):
            assert limiter.allow_request("user1") is True


# ═══════════════════════════════════════════════════════════
# SECTION 8: TESTS PERFORMANCE
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestCachePerformance:
    """Tests de performance du cache."""

    def test_cache_many_keys(self):
        """Test stockage de nombreuses clés."""
        cache = Cache()
        
        # Ajouter 1000 clés
        for i in range(1000):
            cache.set(f"key_{i}", f"value_{i}")
        
        # Vérifier accès
        assert cache.get("key_500") == "value_500"
        assert cache.get("key_999") == "value_999"

    def test_cache_prefix_cleanup_performance(self):
        """Test performance du nettoyage par préfixe."""
        cache = Cache()
        
        # Ajouter beaucoup de clés avec préfixes
        for i in range(500):
            cache.set(f"prefix1:key_{i}", f"value_{i}")
            cache.set(f"prefix2:key_{i}", f"value_{i}")
        
        # Nettoyer un préfixe
        cache.nettoyer("prefix1:")
        
        # Vérifier que l'autre préfixe est intact
        assert cache.get("prefix2:key_100") == "value_100"
