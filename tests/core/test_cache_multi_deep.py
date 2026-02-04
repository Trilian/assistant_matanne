# -*- coding: utf-8 -*-
"""
Tests pour cache_multi.py - amélioration de la couverture

Cible:
- CacheEntry dataclass
- CacheStats dataclass
- L1MemoryCache class
- L2SessionCache class
- L3FileCache class (partiellement, car fichiers)
"""
import pytest
import time
from unittest.mock import MagicMock, patch


class TestCacheEntry:
    """Tests pour CacheEntry dataclass."""
    
    def test_default_values(self):
        """Valeurs par défaut correctes."""
        from src.core.cache_multi import CacheEntry
        
        entry = CacheEntry(value="test")
        
        assert entry.value == "test"
        assert entry.ttl == 300
        assert entry.tags == []
        assert entry.hits == 0
        assert entry.created_at > 0
    
    def test_is_expired_false_for_new_entry(self):
        """is_expired retourne False pour entrée fraîche."""
        from src.core.cache_multi import CacheEntry
        
        entry = CacheEntry(value="test", ttl=300)
        assert entry.is_expired is False
    
    def test_is_expired_true_after_ttl(self):
        """is_expired retourne True après expiration TTL."""
        from src.core.cache_multi import CacheEntry
        
        entry = CacheEntry(
            value="test", 
            ttl=0,  # Expire immédiatement
            created_at=time.time() - 1
        )
        assert entry.is_expired is True
    
    def test_age_seconds(self):
        """age_seconds retourne l'âge correct."""
        from src.core.cache_multi import CacheEntry
        
        entry = CacheEntry(
            value="test",
            created_at=time.time() - 60
        )
        
        assert 59 <= entry.age_seconds <= 61


class TestCacheStats:
    """Tests pour CacheStats dataclass."""
    
    def test_default_values(self):
        """Valeurs par défaut à zéro."""
        from src.core.cache_multi import CacheStats
        
        stats = CacheStats()
        
        assert stats.l1_hits == 0
        assert stats.l2_hits == 0
        assert stats.l3_hits == 0
        assert stats.misses == 0
        assert stats.writes == 0
        assert stats.evictions == 0
    
    def test_total_hits(self):
        """total_hits additionne les 3 niveaux."""
        from src.core.cache_multi import CacheStats
        
        stats = CacheStats(l1_hits=10, l2_hits=5, l3_hits=2)
        assert stats.total_hits == 17
    
    def test_hit_rate_zero_when_no_access(self):
        """hit_rate retourne 0 si pas d'accès."""
        from src.core.cache_multi import CacheStats
        
        stats = CacheStats()
        assert stats.hit_rate == 0.0
    
    def test_hit_rate_calculation(self):
        """hit_rate calcule le pourcentage correct."""
        from src.core.cache_multi import CacheStats
        
        stats = CacheStats(l1_hits=80, misses=20)
        assert stats.hit_rate == 80.0
    
    def test_to_dict(self):
        """to_dict retourne un dictionnaire complet."""
        from src.core.cache_multi import CacheStats
        
        stats = CacheStats(l1_hits=10, misses=10, writes=5)
        d = stats.to_dict()
        
        assert d["l1_hits"] == 10
        assert d["misses"] == 10
        assert d["writes"] == 5
        assert "hit_rate" in d
        assert "%" in d["hit_rate"]


class TestL1MemoryCache:
    """Tests pour L1MemoryCache."""
    
    def test_get_missing_key_returns_none(self):
        """get retourne None si clé absente."""
        from src.core.cache_multi import L1MemoryCache
        
        cache = L1MemoryCache()
        assert cache.get("nonexistent") is None
    
    def test_set_and_get(self):
        """set puis get fonctionne."""
        from src.core.cache_multi import L1MemoryCache, CacheEntry
        
        cache = L1MemoryCache()
        entry = CacheEntry(value="hello", ttl=300)
        
        cache.set("key1", entry)
        result = cache.get("key1")
        
        assert result is not None
        assert result.value == "hello"
    
    def test_get_updates_hits(self):
        """get incrémente le compteur hits."""
        from src.core.cache_multi import L1MemoryCache, CacheEntry
        
        cache = L1MemoryCache()
        entry = CacheEntry(value="test", ttl=300)
        cache.set("key1", entry)
        
        result1 = cache.get("key1")
        result2 = cache.get("key1")
        
        assert result2.hits >= 2
    
    def test_get_expired_returns_none(self):
        """get retourne None pour entrée expirée."""
        from src.core.cache_multi import L1MemoryCache, CacheEntry
        
        cache = L1MemoryCache()
        entry = CacheEntry(value="test", ttl=0, created_at=time.time() - 10)
        cache._cache["expired_key"] = entry
        
        result = cache.get("expired_key")
        assert result is None
    
    def test_lru_eviction(self):
        """Éviction LRU quand max atteint."""
        from src.core.cache_multi import L1MemoryCache, CacheEntry
        
        cache = L1MemoryCache(max_entries=3)
        
        cache.set("key1", CacheEntry(value="1"))
        cache.set("key2", CacheEntry(value="2"))
        cache.set("key3", CacheEntry(value="3"))
        cache.set("key4", CacheEntry(value="4"))  # Devrait évincer key1
        
        assert cache.get("key1") is None
        assert cache.get("key4") is not None
    
    def test_invalidate_by_pattern(self):
        """invalidate par pattern fonctionne."""
        from src.core.cache_multi import L1MemoryCache, CacheEntry
        
        cache = L1MemoryCache()
        cache.set("user:1", CacheEntry(value="u1"))
        cache.set("user:2", CacheEntry(value="u2"))
        cache.set("other:1", CacheEntry(value="o1"))
        
        removed = cache.invalidate(pattern="user:")
        
        assert removed == 2
        assert cache.get("user:1") is None
        assert cache.get("other:1") is not None
    
    def test_invalidate_by_tags(self):
        """invalidate par tags fonctionne."""
        from src.core.cache_multi import L1MemoryCache, CacheEntry
        
        cache = L1MemoryCache()
        cache.set("key1", CacheEntry(value="1", tags=["user", "admin"]))
        cache.set("key2", CacheEntry(value="2", tags=["user"]))
        cache.set("key3", CacheEntry(value="3", tags=["other"]))
        
        removed = cache.invalidate(tags=["user"])
        
        assert removed == 2
        assert cache.get("key3") is not None
    
    def test_clear(self):
        """clear vide le cache."""
        from src.core.cache_multi import L1MemoryCache, CacheEntry
        
        cache = L1MemoryCache()
        cache.set("key1", CacheEntry(value="1"))
        cache.set("key2", CacheEntry(value="2"))
        
        cache.clear()
        
        assert cache.size == 0
    
    def test_size_property(self):
        """size retourne le nombre d'entrées."""
        from src.core.cache_multi import L1MemoryCache, CacheEntry
        
        cache = L1MemoryCache()
        assert cache.size == 0
        
        cache.set("key1", CacheEntry(value="1"))
        assert cache.size == 1
    
    def test_get_stats(self):
        """get_stats retourne les statistiques."""
        from src.core.cache_multi import L1MemoryCache, CacheEntry
        
        cache = L1MemoryCache(max_entries=100)
        cache.set("key1", CacheEntry(value="1"))
        cache.set("key2", CacheEntry(value="2"))
        
        stats = cache.get_stats()
        
        assert stats["entries"] == 2
        assert stats["max_entries"] == 100
        assert "usage_percent" in stats


class TestL2SessionCache:
    """Tests pour L2SessionCache."""
    
    @pytest.fixture(autouse=True)
    def mock_streamlit(self):
        """Mock streamlit session_state."""
        with patch('src.core.cache_multi.st') as mock_st:
            mock_st.session_state = {}
            yield mock_st
    
    def test_get_missing_returns_none(self, mock_streamlit):
        """get retourne None si clé absente."""
        from src.core.cache_multi import L2SessionCache
        
        cache = L2SessionCache()
        assert cache.get("nonexistent") is None
    
    def test_set_and_get(self, mock_streamlit):
        """set puis get fonctionne."""
        from src.core.cache_multi import L2SessionCache, CacheEntry
        
        cache = L2SessionCache()
        entry = CacheEntry(value={"data": "test"}, ttl=300)
        
        cache.set("key1", entry)
        result = cache.get("key1")
        
        assert result is not None
        assert result.value == {"data": "test"}
    
    def test_get_expired_returns_none(self, mock_streamlit):
        """get retourne None pour entrée expirée."""
        from src.core.cache_multi import L2SessionCache
        
        cache = L2SessionCache()
        
        # Ajouter directement une entrée expirée
        mock_streamlit.session_state["_cache_l2_data"] = {
            "expired": {
                "value": "old",
                "created_at": time.time() - 1000,
                "ttl": 1,
                "tags": [],
                "hits": 0,
            }
        }
        
        result = cache.get("expired")
        assert result is None
    
    def test_remove(self, mock_streamlit):
        """remove supprime une entrée."""
        from src.core.cache_multi import L2SessionCache, CacheEntry
        
        cache = L2SessionCache()
        cache.set("key1", CacheEntry(value="test"))
        
        cache.remove("key1")
        
        assert cache.get("key1") is None
    
    def test_invalidate_by_pattern(self, mock_streamlit):
        """invalidate par pattern fonctionne."""
        from src.core.cache_multi import L2SessionCache, CacheEntry
        
        cache = L2SessionCache()
        cache.set("prefix:1", CacheEntry(value="1"))
        cache.set("prefix:2", CacheEntry(value="2"))
        cache.set("other:1", CacheEntry(value="3"))
        
        removed = cache.invalidate(pattern="prefix:")
        
        assert removed == 2
    
    def test_clear(self, mock_streamlit):
        """clear vide le cache."""
        from src.core.cache_multi import L2SessionCache, CacheEntry
        
        cache = L2SessionCache()
        cache.set("key1", CacheEntry(value="1"))
        
        cache.clear()
        
        assert cache.size == 0
    
    def test_size_property(self, mock_streamlit):
        """size retourne le nombre d'entrées."""
        from src.core.cache_multi import L2SessionCache, CacheEntry
        
        cache = L2SessionCache()
        cache.set("key1", CacheEntry(value="1"))
        cache.set("key2", CacheEntry(value="2"))
        
        assert cache.size == 2


class TestL2SessionCacheNoStreamlit:
    """Tests L2 sans contexte Streamlit."""
    
    def test_handles_no_streamlit_context(self):
        """Gère l'absence de Streamlit gracieusement."""
        from src.core.cache_multi import L2SessionCache
        
        with patch('src.core.cache_multi.st') as mock_st:
            # Simuler erreur d'import
            mock_st.session_state = None
            type(mock_st).session_state = property(
                lambda self: (_ for _ in ()).throw(Exception("No context"))
            )
            
            cache = L2SessionCache()
            # Ne doit pas lever d'exception
            result = cache.get("key")
            assert result is None
