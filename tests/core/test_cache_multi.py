"""
Tests pour le module cache multi-niveaux (cache_multi.py).

Tests couverts:
- CacheMemoireN1 (LRU, TTL, éviction)
- CacheFichierN3 (pickle, persistence)
- CacheMultiNiveau (cascade, invalidation, stats)
- Décorateur @cached
"""

import tempfile
from datetime import datetime
from unittest.mock import patch

import pytest

# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def mock_session_state():
    """Mock streamlit session_state."""
    state = {}
    with patch("streamlit.session_state", state):
        yield state


@pytest.fixture
def temp_cache_dir():
    """Crée un dossier temporaire pour le cache fichier."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def l1_cache():
    """Instance CacheMemoireN1 isolée."""
    from src.core.caching import CacheMemoireN1

    cache = CacheMemoireN1(max_entries=10)
    yield cache
    cache.clear()


@pytest.fixture
def l3_cache(temp_cache_dir):
    """Instance CacheFichierN3 avec dossier temporaire."""
    from src.core.caching import CacheFichierN3

    cache = CacheFichierN3(cache_dir=temp_cache_dir)
    yield cache
    cache.clear()


# ═══════════════════════════════════════════════════════════
# TESTS L1 MEMORY CACHE
# ═══════════════════════════════════════════════════════════


class TestL1MemoryCache:
    """Tests pour le cache mémoire L1."""

    def test_set_get_basic(self, l1_cache):
        """Test set/get basique avec EntreeCache."""
        from src.core.caching import EntreeCache

        entry = EntreeCache(value={"data": "value1"}, ttl=300)
        l1_cache.set("key1", entry)
        result = l1_cache.get("key1")

        assert result is not None
        assert result.value["data"] == "value1"

    def test_get_missing_key(self, l1_cache):
        """Test get clé inexistante."""
        result = l1_cache.get("nonexistent")
        assert result is None

    def test_ttl_expiration(self, l1_cache):
        """Test expiration TTL avec mock time."""
        import time as time_module

        from src.core.caching import EntreeCache

        # Utiliser un TTL de 10 secondes pour le test
        base_time = 1000.0

        # Créer l'entrée avec created_at explicite
        entry = EntreeCache(value="expiring_value", ttl=10, created_at=base_time)
        l1_cache.set("expiring", entry)

        # Immédiatement disponible (time < expiration)
        with patch.object(time_module, "time", return_value=base_time + 5):
            result = l1_cache.get("expiring")
            assert result is not None
            assert result.value == "expiring_value"

        # Après expiration (time > creation + ttl)
        with patch.object(time_module, "time", return_value=base_time + 15):
            assert l1_cache.get("expiring") is None

    def test_lru_eviction(self):
        """Test éviction LRU quand max_entries atteint."""
        import time as time_module

        from src.core.caching import CacheMemoireN1, EntreeCache

        cache = CacheMemoireN1(max_entries=3)

        # Créer entrées avec created_at explicite
        base_time = 1000.0
        cache.set("a", EntreeCache(value=1, ttl=3600, created_at=base_time))
        cache.set("b", EntreeCache(value=2, ttl=3600, created_at=base_time + 1))
        cache.set("c", EntreeCache(value=3, ttl=3600, created_at=base_time + 2))

        # Accéder à "a" pour le rendre récent (mise à jour de l'ordre LRU)
        with patch.object(time_module, "time", return_value=base_time + 100):
            cache.get("a")

        # Ajouter "d" devrait évincer "b" (le moins récent)
        cache.set("d", EntreeCache(value=4, ttl=3600, created_at=base_time + 4))

        # Vérifier le résultat
        with patch.object(time_module, "time", return_value=base_time + 100):
            assert cache.get("a") is not None  # Toujours là
            assert cache.get("b") is None  # Évincé
            assert cache.get("c") is not None
            assert cache.get("d") is not None

    def test_invalidate_by_pattern(self, l1_cache):
        """Test invalidation par pattern."""
        from src.core.caching import EntreeCache

        l1_cache.set("recipe:1", EntreeCache(value="tarte"))
        l1_cache.set("recipe:2", EntreeCache(value="salade"))
        l1_cache.set("user:1", EntreeCache(value="alice"))

        # Invalider par pattern
        count = l1_cache.invalidate(pattern="recipe")

        assert count == 2
        assert l1_cache.get("recipe:1") is None
        assert l1_cache.get("recipe:2") is None
        assert l1_cache.get("user:1") is not None

    def test_invalidate_by_tags(self, l1_cache):
        """Test invalidation par tags."""
        from src.core.caching import EntreeCache

        l1_cache.set("recipe:1", EntreeCache(value="tarte", tags=["recipes", "desserts"]))
        l1_cache.set("recipe:2", EntreeCache(value="salade", tags=["recipes", "salads"]))
        l1_cache.set("user:1", EntreeCache(value="alice", tags=["users"]))

        # Invalider par tag
        count = l1_cache.invalidate(tags=["desserts"])

        assert count == 1
        assert l1_cache.get("recipe:1") is None  # Invalidé
        assert l1_cache.get("recipe:2") is not None  # Pas touché
        assert l1_cache.get("user:1") is not None  # Pas touché

    def test_clear(self, l1_cache):
        """Test vidage complet."""
        from src.core.caching import EntreeCache

        l1_cache.set("key1", EntreeCache(value="value1"))
        l1_cache.set("key2", EntreeCache(value="value2"))

        l1_cache.clear()

        assert l1_cache.get("key1") is None
        assert l1_cache.get("key2") is None
        assert l1_cache.size == 0

    def test_stats(self, l1_cache):
        """Test statistiques."""
        from src.core.caching import EntreeCache

        l1_cache.set("key1", EntreeCache(value="value1"))

        # Hits
        l1_cache.get("key1")
        l1_cache.get("key1")

        stats = l1_cache.obtenir_statistiques()

        assert stats["entries"] == 1
        assert stats["max_entries"] == 10


# ═══════════════════════════════════════════════════════════
# TESTS L3 FILE CACHE
# ═══════════════════════════════════════════════════════════


class TestL3FileCache:
    """Tests pour le cache fichier L3."""

    def test_set_get_basic(self, l3_cache):
        """Test set/get basique."""
        from src.core.caching import EntreeCache

        entry = EntreeCache(value={"data": "persisted"}, ttl=300)
        l3_cache.set("file_key", entry)
        result = l3_cache.get("file_key")

        assert result is not None
        assert result.value["data"] == "persisted"

    def test_persistence(self, temp_cache_dir):
        """Test persistance entre instances."""
        from src.core.caching import CacheFichierN3, EntreeCache

        # Première instance
        cache1 = CacheFichierN3(cache_dir=temp_cache_dir)
        cache1.set("persistent", EntreeCache(value={"value": 42}, ttl=3600))

        # Nouvelle instance avec même dossier
        cache2 = CacheFichierN3(cache_dir=temp_cache_dir)
        result = cache2.get("persistent")

        assert result is not None
        assert result.value["value"] == 42

    def test_ttl_expiration(self, l3_cache):
        """Test expiration TTL fichier avec mock time."""
        import time as time_module

        from src.core.caching import EntreeCache

        base_time = 1000.0

        # Créer l'entrée avec created_at explicite
        entry = EntreeCache(value="data", ttl=10, created_at=base_time)
        l3_cache.set("expiring_file", entry)

        # Avant expiration
        with patch.object(time_module, "time", return_value=base_time + 5):
            result = l3_cache.get("expiring_file")
            assert result is not None

        # Après expiration
        with patch.object(time_module, "time", return_value=base_time + 15):
            assert l3_cache.get("expiring_file") is None

    def test_invalidate(self, l3_cache):
        """Test invalidation par tags (L3 ne supporte pas pattern car clés hashées)."""
        import time as real_time

        from src.core.caching import EntreeCache

        l3_cache.set("to_delete", EntreeCache(value="value", ttl=3600, tags=["test_tag"]))

        # Attendre un peu que le fichier soit écrit
        real_time.sleep(0.05)

        # Invalider par tag (seule méthode supportée pour L3)
        count = l3_cache.invalidate(tags=["test_tag"])

        # Doit avoir invalidé au moins une entrée
        assert count >= 1

        # L'entrée ne doit plus être accessible
        assert l3_cache.get("to_delete") is None

    def test_clear(self, l3_cache):
        """Test vidage complet."""
        from src.core.caching import EntreeCache

        l3_cache.set("key1", EntreeCache(value="value1"))
        l3_cache.set("key2", EntreeCache(value="value2"))

        l3_cache.clear()

        assert l3_cache.get("key1") is None

    def test_complex_data(self, l3_cache):
        """Test données complexes (sérialisables)."""
        from src.core.caching import EntreeCache

        complex_data = {
            "list": [1, 2, 3],
            "nested": {"a": {"b": "c"}},
            "date": datetime.now().isoformat(),
        }

        l3_cache.set("complex", EntreeCache(value=complex_data, ttl=300))
        result = l3_cache.get("complex")

        assert result.value["list"] == [1, 2, 3]
        assert result.value["nested"]["a"]["b"] == "c"


# ═══════════════════════════════════════════════════════════
# TESTS MULTI-LEVEL CACHE
# ═══════════════════════════════════════════════════════════


class TestMultiLevelCache:
    """Tests pour le cache multi-niveaux."""

    @pytest.fixture(autouse=True)
    def reset_singleton(self):
        """Reset singleton avant et après chaque test."""
        from src.core.caching import CacheMultiNiveau

        CacheMultiNiveau._instance = None
        yield
        CacheMultiNiveau._instance = None

    @pytest.fixture
    def multi_cache(self, temp_cache_dir, mock_session_state):
        """Instance CacheMultiNiveau isolée."""
        from src.core.caching import CacheMultiNiveau

        cache = CacheMultiNiveau(
            l1_max_entries=10,
            l2_enabled=False,  # Désactiver L2 pour tests isolés
            l3_enabled=True,
            l3_cache_dir=temp_cache_dir,
        )
        yield cache
        cache.clear()

    def test_cascade_write(self, multi_cache):
        """Test écriture en cascade."""
        # Avec persistent=True, doit écrire en L1 et L3
        multi_cache.set("cascade_key", {"data": "test"}, persistent=True)

        # Doit être dans L1
        assert multi_cache.l1.get("cascade_key") is not None

        # Doit être dans L3 (car persistent=True)
        if multi_cache.l3:
            assert multi_cache.l3.get("cascade_key") is not None

    def test_cascade_read_promotion(self, multi_cache):
        """Test promotion de L3 vers L1."""
        from src.core.caching import EntreeCache

        # Écrire directement dans L3
        if multi_cache.l3:
            multi_cache.l3.set("l3_only", EntreeCache(value="value", ttl=300))

        # Vider L1
        multi_cache.l1.clear()

        # Lire via multi-cache â†’ doit promouvoir vers L1
        result = multi_cache.get("l3_only")

        assert result == "value"
        # Vérifie promotion
        l1_entry = multi_cache.l1.get("l3_only")
        assert l1_entry is not None

    def test_delete_cascade(self, multi_cache):
        """Test suppression en cascade via invalidate."""
        multi_cache.set("to_delete", "value", persistent=True)

        # Utiliser invalidate avec pattern
        multi_cache.invalidate(pattern="to_delete")

        assert multi_cache.l1.get("to_delete") is None
        # Note: CacheFichierN3 ne supporte pas l'invalidation par pattern
        # car les clés sont hashées

    def test_invalidate_tag(self, multi_cache):
        """Test invalidation par tag."""
        multi_cache.set("tagged:1", "v1", tags=["group_a"])
        multi_cache.set("tagged:2", "v2", tags=["group_a"])
        multi_cache.set("other:1", "v3", tags=["group_b"])

        # Utiliser invalidate avec tags=
        multi_cache.invalidate(tags=["group_a"])

        assert multi_cache.get("tagged:1") is None
        assert multi_cache.get("tagged:2") is None
        assert multi_cache.get("other:1") == "v3"

    def test_obtenir_ou_calculer(self, multi_cache):
        """Test obtenir_ou_calculer (lazy loading)."""
        call_count = 0

        def loader():
            nonlocal call_count
            call_count += 1
            return {"loaded": True}

        # Premier appel → exécute loader
        result1 = multi_cache.obtenir_ou_calculer("lazy_key", loader, ttl=60)
        assert result1["loaded"] is True
        assert call_count == 1

        # Deuxième appel → utilise cache
        result2 = multi_cache.obtenir_ou_calculer("lazy_key", loader, ttl=60)
        assert result2["loaded"] is True
        assert call_count == 1  # Pas de nouvel appel

    def test_stats_aggregation(self, multi_cache):
        """Test agrégation des statistiques."""
        multi_cache.set("key1", "v1")
        multi_cache.get("key1")  # Hit L1
        multi_cache.get("nonexistent")  # Miss

        stats = multi_cache.obtenir_statistiques()

        assert "l1" in stats or "hits" in str(stats)


# ═══════════════════════════════════════════════════════════
# TESTS DECORATOR @cached
# ═══════════════════════════════════════════════════════════
# Note: Le décorateur @cached a été supprimé en faveur de @avec_cache.
# Les tests pour @avec_cache sont dans test_decorators.py et test_cache.py.
# ═══════════════════════════════════════════════════════════


# ═══════════════════════════════════════════════════════════
# TESTS EDGE CASES
# ═══════════════════════════════════════════════════════════


class TestCacheEdgeCases:
    """Tests cas limites."""

    def test_none_value(self, l1_cache):
        """Test stockage de None."""
        from src.core.caching import EntreeCache

        l1_cache.set("none_key", EntreeCache(value=None))

        result = l1_cache.get("none_key")
        # L'entrée existe mais value est None
        assert result is not None
        assert result.value is None

    def test_empty_string_key(self, l1_cache):
        """Test clé vide."""
        from src.core.caching import EntreeCache

        l1_cache.set("", EntreeCache(value="value"))
        result = l1_cache.get("")
        assert result is not None
        assert result.value == "value"

    def test_special_characters_key(self, l1_cache):
        """Test caractères spéciaux dans clé."""
        from src.core.caching import EntreeCache

        special_key = "clé:avec/spéciaux#chars"
        l1_cache.set(special_key, EntreeCache(value="value"))

        result = l1_cache.get(special_key)
        assert result is not None
        assert result.value == "value"

    def test_large_value(self, l1_cache):
        """Test valeur volumineuse."""
        from src.core.caching import EntreeCache

        large_data = {"items": list(range(10000))}

        l1_cache.set("large", EntreeCache(value=large_data))
        result = l1_cache.get("large")

        assert len(result.value["items"]) == 10000

    def test_concurrent_access(self, l1_cache):
        """Test accès concurrent basique."""
        import threading

        from src.core.caching import EntreeCache

        results = []

        def writer():
            for i in range(100):
                l1_cache.set(f"key_{i}", EntreeCache(value=i))

        def reader():
            for i in range(100):
                entry = l1_cache.get(f"key_{i}")
                if entry:
                    results.append(entry.value)

        t1 = threading.Thread(target=writer)
        t2 = threading.Thread(target=reader)

        t1.start()
        t2.start()
        t1.join()
        t2.join()

        # Pas d'exception = succès basique


# ═══════════════════════════════════════════════════════════
# TESTS ADDITIONNELS POUR COUVERTURE 85%+
# ═══════════════════════════════════════════════════════════


class TestCacheSessionN2:
    """Tests pour le cache L2 basé sur session Streamlit."""

    @pytest.fixture
    def l2_cache(self, mock_session_state):
        """Fixture pour cache L2."""
        from src.core.caching import CacheSessionN2

        return CacheSessionN2()

    def test_l2_get_nonexistent_key(self, l2_cache):
        """Test get sur clé inexistante."""
        result = l2_cache.get("nonexistent_key")
        assert result is None

    def test_l2_set_and_get(self, l2_cache):
        """Test set puis get."""
        from src.core.caching import EntreeCache

        entry = EntreeCache(value="test_value", ttl=3600)
        l2_cache.set("test_key", entry)

        result = l2_cache.get("test_key")
        assert result is not None
        assert result.value == "test_value"

    def test_l2_remove(self, l2_cache):
        """Test suppression d'entrée."""
        from src.core.caching import EntreeCache

        l2_cache.set("to_remove", EntreeCache(value="temp"))
        l2_cache.remove("to_remove")

        result = l2_cache.get("to_remove")
        assert result is None

    def test_l2_invalidate_by_pattern(self, l2_cache):
        """Test invalidation par pattern."""
        from src.core.caching import EntreeCache

        l2_cache.set("prefix_key1", EntreeCache(value="v1"))
        l2_cache.set("prefix_key2", EntreeCache(value="v2"))
        l2_cache.set("other_key", EntreeCache(value="v3"))

        count = l2_cache.invalidate(pattern="prefix")
        assert count == 2

    def test_l2_invalidate_by_tags(self, l2_cache):
        """Test invalidation par tags."""
        from src.core.caching import EntreeCache

        l2_cache.set("tagged1", EntreeCache(value="v1", tags=["group_a"]))
        l2_cache.set("tagged2", EntreeCache(value="v2", tags=["group_a"]))
        l2_cache.set("tagged3", EntreeCache(value="v3", tags=["group_b"]))

        count = l2_cache.invalidate(tags=["group_a"])
        assert count == 2

    def test_l2_clear(self, l2_cache):
        """Test vidage complet."""
        from src.core.caching import EntreeCache

        l2_cache.set("key1", EntreeCache(value="v1"))
        l2_cache.set("key2", EntreeCache(value="v2"))

        l2_cache.clear()
        assert l2_cache.size == 0

    def test_l2_size_property(self, l2_cache):
        """Test propriété size."""
        from src.core.caching import EntreeCache

        assert l2_cache.size == 0
        l2_cache.set("key1", EntreeCache(value="v1"))
        assert l2_cache.size == 1


class TestCacheFichierN3Advanced:
    """Tests avancés pour le cache L3 fichier."""

    @pytest.fixture
    def l3_cache(self, temp_cache_dir):
        """Fixture pour cache L3."""
        from src.core.caching import CacheFichierN3

        return CacheFichierN3(cache_dir=temp_cache_dir)

    def test_l3_key_to_filename_consistency(self, l3_cache):
        """Test que les clés donnent des noms de fichiers cohérents."""
        path1 = l3_cache._key_to_filename("test_key")
        path2 = l3_cache._key_to_filename("test_key")

        assert path1 == path2

    def test_l3_key_to_filename_different_keys(self, l3_cache):
        """Test que différentes clés donnent différents fichiers."""
        path1 = l3_cache._key_to_filename("key1")
        path2 = l3_cache._key_to_filename("key2")

        assert path1 != path2

    def test_l3_get_expired_entry(self, l3_cache):
        """Test get sur entrée expirée."""
        import time

        from src.core.caching import EntreeCache

        # Créer entrée déjà expirée
        entry = EntreeCache(
            value="expired",
            ttl=0,  # Expire immédiatement
            created_at=time.time() - 100,
        )
        l3_cache.set("expired_key", entry)

        result = l3_cache.get("expired_key")
        assert result is None

    def test_l3_remove_nonexistent(self, l3_cache):
        """Test suppression clé inexistante (ne lève pas d'erreur)."""
        l3_cache.remove("nonexistent_key_xyz")
        # Should not raise


class TestEntreeCacheAdvanced:
    """Tests avancés pour le dataclass EntreeCache."""

    def test_entree_cache_est_expire(self):
        """Test propriété est_expire."""
        import time

        from src.core.caching import EntreeCache

        # Entrée fraîche
        fresh = EntreeCache(value="fresh", ttl=3600)
        assert fresh.est_expire is False

        # Entrée expirée
        expired = EntreeCache(value="old", ttl=1, created_at=time.time() - 100)
        assert expired.est_expire is True

    def test_entree_cache_age_seconds(self):
        """Test propriété age_seconds."""
        import time

        from src.core.caching import EntreeCache

        entry = EntreeCache(value="test", created_at=time.time() - 10)

        age = entry.age_seconds
        assert age >= 10


class TestStatistiquesCacheAdvanced:
    """Tests avancés pour StatistiquesCache."""

    def test_stats_total_hits(self):
        """Test calcul total_hits."""
        from src.core.caching import StatistiquesCache

        stats = StatistiquesCache(l1_hits=10, l2_hits=5, l3_hits=2)
        assert stats.total_hits == 17

    def test_stats_hit_rate_zero_total(self):
        """Test hit_rate avec 0 accès."""
        from src.core.caching import StatistiquesCache

        stats = StatistiquesCache()
        assert stats.hit_rate == 0.0

    def test_stats_hit_rate_all_hits(self):
        """Test hit_rate avec 100% hits."""
        from src.core.caching import StatistiquesCache

        stats = StatistiquesCache(l1_hits=10, misses=0)
        assert stats.hit_rate == 100.0

    def test_stats_hit_rate_mixed(self):
        """Test hit_rate avec hits et misses."""
        from src.core.caching import StatistiquesCache

        stats = StatistiquesCache(l1_hits=3, l2_hits=2, misses=5)
        # 5 hits / 10 total = 50%
        assert stats.hit_rate == 50.0

    def test_stats_to_dict(self):
        """Test conversion to_dict."""
        from src.core.caching import StatistiquesCache

        stats = StatistiquesCache(
            l1_hits=10, l2_hits=5, l3_hits=2, misses=3, writes=20, evictions=1
        )

        d = stats.to_dict()
        assert d["l1_hits"] == 10
        assert d["l2_hits"] == 5
        assert d["l3_hits"] == 2
        assert d["total_hits"] == 17
        assert d["misses"] == 3
        assert d["writes"] == 20
        assert d["evictions"] == 1
        assert "%" in d["hit_rate"]


class TestCacheMultiNiveauAdvanced:
    """Tests avancés pour CacheMultiNiveau."""

    @pytest.fixture(autouse=True)
    def reset_singleton(self):
        """Reset singleton avant et après chaque test."""
        from src.core.caching import CacheMultiNiveau

        CacheMultiNiveau._instance = None
        yield
        CacheMultiNiveau._instance = None

    @pytest.fixture
    def multi_cache(self, mock_session_state, temp_cache_dir):
        """Fixture pour cache multi-niveaux."""
        from src.core.caching import CacheMultiNiveau

        return CacheMultiNiveau(l1_max_entries=100, l3_cache_dir=temp_cache_dir)

    def test_singleton_pattern(self, mock_session_state, temp_cache_dir):
        """Test que obtenir_cache() retourne un singleton."""
        from src.core.caching.orchestrator import obtenir_cache, reinitialiser_cache

        reinitialiser_cache()
        cache1 = obtenir_cache()
        cache2 = obtenir_cache()

        assert cache1 is cache2
        reinitialiser_cache()

    def test_clear_all_levels(self, multi_cache):
        """Test vidage de tous les niveaux."""
        multi_cache.set("key1", "value1")
        multi_cache.set("key2", "value2", persistent=True)

        multi_cache.clear()

        assert multi_cache.l1.size == 0

    def test_obtenir_ou_calculer_with_tags(self, multi_cache):
        """Test obtenir_ou_calculer avec tags."""

        def loader():
            return {"computed": True}

        result = multi_cache.obtenir_ou_calculer(
            "computed_key", loader, ttl=60, tags=["test_group"]
        )

        assert result["computed"] is True
