# -*- coding: utf-8 -*-
"""
Tests pour cache_multi.py - amÃ©lioration de la couverture

Cible:
- EntreeCache dataclass
- StatistiquesCache dataclass
- CacheMemoireN1 class
- CacheSessionN2 class
- CacheFichierN3 class (partiellement, car fichiers)
"""
import pytest
import time
from unittest.mock import MagicMock, patch


class TestCacheEntry:
    """Tests pour EntreeCache dataclass."""
    
    def test_default_values(self):
        """Valeurs par dÃ©faut correctes."""
        from src.core.cache_multi import EntreeCache
        
        entry = EntreeCache(value="test")
        
        assert entry.value == "test"
        assert entry.ttl == 300
        assert entry.tags == []
        assert entry.hits == 0
        assert entry.created_at > 0
    
    def test_is_expired_false_for_new_entry(self):
        """is_expired retourne False pour entrÃ©e fraÃ®che."""
        from src.core.cache_multi import EntreeCache
        
        entry = EntreeCache(value="test", ttl=300)
        assert entry.is_expired is False
    
    def test_is_expired_true_after_ttl(self):
        """is_expired retourne True aprÃ¨s expiration TTL."""
        from src.core.cache_multi import EntreeCache
        
        entry = EntreeCache(
            value="test", 
            ttl=0,  # Expire immÃ©diatement
            created_at=time.time() - 1
        )
        assert entry.is_expired is True
    
    def test_age_seconds(self):
        """age_seconds retourne l'Ã¢ge correct."""
        from src.core.cache_multi import EntreeCache
        
        entry = EntreeCache(
            value="test",
            created_at=time.time() - 60
        )
        
        assert 59 <= entry.age_seconds <= 61


class TestCacheStats:
    """Tests pour StatistiquesCache dataclass."""
    
    def test_default_values(self):
        """Valeurs par dÃ©faut Ã  zÃ©ro."""
        from src.core.cache_multi import StatistiquesCache
        
        stats = StatistiquesCache()
        
        assert stats.l1_hits == 0
        assert stats.l2_hits == 0
        assert stats.l3_hits == 0
        assert stats.misses == 0
        assert stats.writes == 0
        assert stats.evictions == 0
    
    def test_total_hits(self):
        """total_hits additionne les 3 niveaux."""
        from src.core.cache_multi import StatistiquesCache
        
        stats = StatistiquesCache(l1_hits=10, l2_hits=5, l3_hits=2)
        assert stats.total_hits == 17
    
    def test_hit_rate_zero_when_no_access(self):
        """hit_rate retourne 0 si pas d'accÃ¨s."""
        from src.core.cache_multi import StatistiquesCache
        
        stats = StatistiquesCache()
        assert stats.hit_rate == 0.0
    
    def test_hit_rate_calculation(self):
        """hit_rate calcule le pourcentage correct."""
        from src.core.cache_multi import StatistiquesCache
        
        stats = StatistiquesCache(l1_hits=80, misses=20)
        assert stats.hit_rate == 80.0
    
    def test_to_dict(self):
        """to_dict retourne un dictionnaire complet."""
        from src.core.cache_multi import StatistiquesCache
        
        stats = StatistiquesCache(l1_hits=10, misses=10, writes=5)
        d = stats.to_dict()
        
        assert d["l1_hits"] == 10
        assert d["misses"] == 10
        assert d["writes"] == 5
        assert "hit_rate" in d
        assert "%" in d["hit_rate"]


class TestL1MemoryCache:
    """Tests pour CacheMemoireN1."""
    
    def test_get_missing_key_returns_none(self):
        """get retourne None si clÃ© absente."""
        from src.core.cache_multi import CacheMemoireN1
        
        cache = CacheMemoireN1()
        assert cache.get("nonexistent") is None
    
    def test_set_and_get(self):
        """set puis get fonctionne."""
        from src.core.cache_multi import CacheMemoireN1, EntreeCache
        
        cache = CacheMemoireN1()
        entry = EntreeCache(value="hello", ttl=300)
        
        cache.set("key1", entry)
        result = cache.get("key1")
        
        assert result is not None
        assert result.value == "hello"
    
    def test_get_updates_hits(self):
        """get incrÃ©mente le compteur hits."""
        from src.core.cache_multi import CacheMemoireN1, EntreeCache
        
        cache = CacheMemoireN1()
        entry = EntreeCache(value="test", ttl=300)
        cache.set("key1", entry)
        
        result1 = cache.get("key1")
        result2 = cache.get("key1")
        
        assert result2.hits >= 2
    
    def test_get_expired_returns_none(self):
        """get retourne None pour entrÃ©e expirÃ©e."""
        from src.core.cache_multi import CacheMemoireN1, EntreeCache
        
        cache = CacheMemoireN1()
        entry = EntreeCache(value="test", ttl=0, created_at=time.time() - 10)
        cache._cache["expired_key"] = entry
        
        result = cache.get("expired_key")
        assert result is None
    
    def test_lru_eviction(self):
        """Ã‰viction LRU quand max atteint."""
        from src.core.cache_multi import CacheMemoireN1, EntreeCache
        
        cache = CacheMemoireN1(max_entries=3)
        
        cache.set("key1", EntreeCache(value="1"))
        cache.set("key2", EntreeCache(value="2"))
        cache.set("key3", EntreeCache(value="3"))
        cache.set("key4", EntreeCache(value="4"))  # Devrait Ã©vincer key1
        
        assert cache.get("key1") is None
        assert cache.get("key4") is not None
    
    def test_invalidate_by_pattern(self):
        """invalidate par pattern fonctionne."""
        from src.core.cache_multi import CacheMemoireN1, EntreeCache
        
        cache = CacheMemoireN1()
        cache.set("user:1", EntreeCache(value="u1"))
        cache.set("user:2", EntreeCache(value="u2"))
        cache.set("other:1", EntreeCache(value="o1"))
        
        removed = cache.invalidate(pattern="user:")
        
        assert removed == 2
        assert cache.get("user:1") is None
        assert cache.get("other:1") is not None
    
    def test_invalidate_by_tags(self):
        """invalidate par tags fonctionne."""
        from src.core.cache_multi import CacheMemoireN1, EntreeCache
        
        cache = CacheMemoireN1()
        cache.set("key1", EntreeCache(value="1", tags=["user", "admin"]))
        cache.set("key2", EntreeCache(value="2", tags=["user"]))
        cache.set("key3", EntreeCache(value="3", tags=["other"]))
        
        removed = cache.invalidate(tags=["user"])
        
        assert removed == 2
        assert cache.get("key3") is not None
    
    def test_clear(self):
        """clear vide le cache."""
        from src.core.cache_multi import CacheMemoireN1, EntreeCache
        
        cache = CacheMemoireN1()
        cache.set("key1", EntreeCache(value="1"))
        cache.set("key2", EntreeCache(value="2"))
        
        cache.clear()
        
        assert cache.size == 0
    
    def test_size_property(self):
        """size retourne le nombre d'entrÃ©es."""
        from src.core.cache_multi import CacheMemoireN1, EntreeCache
        
        cache = CacheMemoireN1()
        assert cache.size == 0
        
        cache.set("key1", EntreeCache(value="1"))
        assert cache.size == 1
    
    def test_get_stats(self):
        """get_stats retourne les statistiques."""
        from src.core.cache_multi import CacheMemoireN1, EntreeCache
        
        cache = CacheMemoireN1(max_entries=100)
        cache.set("key1", EntreeCache(value="1"))
        cache.set("key2", EntreeCache(value="2"))
        
        stats = cache.get_stats()
        
        assert stats["entries"] == 2
        assert stats["max_entries"] == 100
        assert "usage_percent" in stats


class TestL2SessionCache:
    """Tests pour CacheSessionN2."""
    
    @pytest.fixture(autouse=True)
    def mock_streamlit(self):
        """Mock streamlit session_state directement."""
        import streamlit as st
        
        # Sauvegarder l'Ã©tat original si existe
        had_key = hasattr(st, 'session_state') and isinstance(st.session_state, dict)
        
        # CrÃ©er un dict mock pour session_state
        mock_state = {}
        
        with patch.object(st, 'session_state', mock_state):
            yield mock_state
    
    def test_get_missing_returns_none(self, mock_streamlit):
        """get retourne None si clÃ© absente."""
        from src.core.cache_multi import CacheSessionN2
        
        cache = CacheSessionN2()
        assert cache.get("nonexistent") is None
    
    def test_set_and_get(self, mock_streamlit):
        """set puis get fonctionne."""
        from src.core.cache_multi import CacheSessionN2, EntreeCache
        
        cache = CacheSessionN2()
        entry = EntreeCache(value={"data": "test"}, ttl=300)
        
        cache.set("key1", entry)
        result = cache.get("key1")
        
        assert result is not None
        assert result.value == {"data": "test"}
    
    def test_get_expired_returns_none(self, mock_streamlit):
        """get retourne None pour entrÃ©e expirÃ©e."""
        from src.core.cache_multi import CacheSessionN2
        
        cache = CacheSessionN2()
        
        # Ajouter directement une entrÃ©e expirÃ©e
        mock_streamlit["_cache_l2_data"] = {
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
        """remove supprime une entrÃ©e."""
        from src.core.cache_multi import CacheSessionN2, EntreeCache
        
        cache = CacheSessionN2()
        cache.set("key1", EntreeCache(value="test"))
        
        cache.remove("key1")
        
        assert cache.get("key1") is None
    
    def test_invalidate_by_pattern(self, mock_streamlit):
        """invalidate par pattern fonctionne."""
        from src.core.cache_multi import CacheSessionN2, EntreeCache
        
        cache = CacheSessionN2()
        cache.set("prefix:1", EntreeCache(value="1"))
        cache.set("prefix:2", EntreeCache(value="2"))
        cache.set("other:1", EntreeCache(value="3"))
        
        removed = cache.invalidate(pattern="prefix:")
        
        assert removed == 2
    
    def test_clear(self, mock_streamlit):
        """clear vide le cache."""
        from src.core.cache_multi import CacheSessionN2, EntreeCache
        
        cache = CacheSessionN2()
        cache.set("key1", EntreeCache(value="1"))
        
        cache.clear()
        
        assert cache.size == 0
    
    def test_size_property(self, mock_streamlit):
        """size retourne le nombre d'entrÃ©es."""
        from src.core.cache_multi import CacheSessionN2, EntreeCache
        
        cache = CacheSessionN2()
        cache.set("key1", EntreeCache(value="1"))
        cache.set("key2", EntreeCache(value="2"))
        
        assert cache.size == 2


class TestL2SessionCacheNoStreamlit:
    """Tests L2 sans contexte Streamlit."""
    
    def test_handles_no_streamlit_context(self):
        """GÃ¨re l'absence de Streamlit gracieusement."""
        from src.core.cache_multi import CacheSessionN2, EntreeCache
        import streamlit as st
        
        # Simuler une erreur lors de l'accÃ¨s Ã  session_state
        class RaisingState:
            def __getitem__(self, key):
                raise Exception("No ScriptRunContext")
            def __setitem__(self, key, value):
                raise Exception("No ScriptRunContext")
            def __contains__(self, key):
                raise Exception("No ScriptRunContext")
            def get(self, key, default=None):
                raise Exception("No ScriptRunContext")
        
        with patch.object(st, 'session_state', RaisingState()):
            cache = CacheSessionN2()
            # Ne doit pas lever d'exception
            result = cache.get("key")
            assert result is None
            
            # set ne doit pas lever d'exception non plus  
            cache.set("key", EntreeCache(value="test"))
            # Pas d'exception = succÃ¨s
