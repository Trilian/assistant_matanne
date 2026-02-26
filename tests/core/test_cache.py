"""
Tests pour le système de cache multi-niveaux (CacheMultiNiveau).
"""

import time

import pytest


@pytest.fixture(autouse=True)
def _reset_cache_singleton():
    """Réinitialise le singleton CacheMultiNiveau entre chaque test.

    L2 (session Streamlit) et L3 (fichier) sont désactivés pour isoler
    les tests sur la logique pure du cache (L1 mémoire uniquement).
    """
    from src.core.caching.orchestrator import obtenir_cache, reinitialiser_cache

    # Forcer un nouveau singleton L1-only pour chaque test
    reinitialiser_cache()
    obtenir_cache(l2_enabled=False, l3_enabled=False)
    yield
    # Nettoyage final
    reinitialiser_cache()


# ═══════════════════════════════════════════════════════════
# TESTS CACHE MULTINIVEAU (via obtenir_cache())
# ═══════════════════════════════════════════════════════════


class TestCacheMultiNiveau:
    """Tests pour CacheMultiNiveau (remplace l'ancienne façade Cache)."""

    def test_initialise_creates_structures(self):
        """Test initialisation — le singleton CacheMultiNiveau se crée."""
        from src.core.caching.orchestrator import obtenir_cache

        c = obtenir_cache()
        assert c is not None
        assert c.l1 is not None

        stats = c.obtenir_statistiques()
        assert isinstance(stats, dict)

    def test_initialise_only_once(self):
        """Test le singleton ne se recrée pas — les données persistent."""
        from src.core.caching.orchestrator import obtenir_cache

        cache = obtenir_cache()
        cache.set("test", "valeur")

        # Deuxième accès au cache — la valeur doit être toujours là
        result = obtenir_cache().get("test")
        assert result == "valeur"


class TestCacheObtenir:
    """Tests pour CacheMultiNiveau.get()."""

    def test_obtenir_returns_default_if_missing(self):
        """Test get retourne default si clé absente."""
        from src.core.caching.orchestrator import obtenir_cache

        result = obtenir_cache().get("inexistant", default="default")
        assert result == "default"

    def test_obtenir_returns_value_if_present_and_fresh(self):
        """Test get retourne valeur si présente et fraîche."""
        from src.core.caching.orchestrator import obtenir_cache

        cache = obtenir_cache()
        cache.set("ma_cle", "ma_valeur", ttl=300)
        result = cache.get("ma_cle")
        assert result == "ma_valeur"

    def test_obtenir_returns_default_if_expired(self):
        """Test get retourne default si expiré."""
        from src.core.caching.orchestrator import obtenir_cache

        cache = obtenir_cache()
        cache.set("ma_cle", "ma_valeur", ttl=300)

        # Simuler expiration en modifiant created_at dans L1
        entry = cache.l1._cache["ma_cle"]
        entry.created_at = time.time() - 400

        result = cache.get("ma_cle")
        assert result is None

    def test_obtenir_increments_miss_counter(self):
        """Test get incrémente compteur miss."""
        from src.core.caching.orchestrator import obtenir_cache

        cache = obtenir_cache()
        stats_before = cache.obtenir_statistiques()
        initial_misses = stats_before["misses"]

        cache.get("inexistant")

        stats_after = cache.obtenir_statistiques()
        assert stats_after["misses"] == initial_misses + 1

    def test_obtenir_increments_hit_counter(self):
        """Test get incrémente compteur hit."""
        from src.core.caching.orchestrator import obtenir_cache

        cache = obtenir_cache()
        cache.set("ma_cle", "ma_valeur")

        stats_before = cache.obtenir_statistiques()
        initial_hits = stats_before["total_hits"]

        cache.get("ma_cle")

        stats_after = cache.obtenir_statistiques()
        assert stats_after["total_hits"] == initial_hits + 1


class TestCacheDefinir:
    """Tests pour CacheMultiNiveau.set()."""

    def test_definir_stores_value(self):
        """Test set stocke la valeur."""
        from src.core.caching.orchestrator import obtenir_cache

        cache = obtenir_cache()
        cache.set("test_cle", {"data": "valeur"})

        result = cache.get("test_cle")
        assert result == {"data": "valeur"}

    def test_definir_stores_timestamp(self):
        """Test set stocke le timestamp (created_at dans EntreeCache)."""
        from src.core.caching.orchestrator import obtenir_cache

        cache = obtenir_cache()
        avant = time.time()
        cache.set("test_cle", "valeur")
        apres = time.time()

        entry = cache.l1._cache["test_cle"]
        assert avant <= entry.created_at <= apres

    def test_definir_with_tags(self):
        """Test set avec tags."""
        from src.core.caching.orchestrator import obtenir_cache

        cache = obtenir_cache()
        cache.set("recette_1", "data", tags=["recettes", "recette_1"])

        entry = cache.l1._cache["recette_1"]
        assert "recettes" in entry.tags
        assert "recette_1" in entry.tags


class TestCacheInvalider:
    """Tests pour CacheMultiNiveau.invalidate()."""

    def test_invalider_by_pattern(self):
        """Test invalidation par pattern."""
        from src.core.caching.orchestrator import obtenir_cache

        cache = obtenir_cache()
        cache.set("recettes_liste", "data1")
        cache.set("recettes_detail_1", "data2")
        cache.set("courses_liste", "data3")

        cache.invalidate(pattern="recettes")

        assert cache.get("recettes_liste") is None
        assert cache.get("recettes_detail_1") is None
        assert cache.get("courses_liste") == "data3"

    def test_invalider_by_tags(self):
        """Test invalidation par tags."""
        from src.core.caching.orchestrator import obtenir_cache

        cache = obtenir_cache()
        cache.set("recette_1", "data1", tags=["tag_recette"])
        cache.set("recette_2", "data2", tags=["tag_recette"])
        cache.set("autre", "data3")

        cache.invalidate(tags=["tag_recette"])

        assert cache.get("recette_1") is None
        assert cache.get("recette_2") is None
        assert cache.get("autre") == "data3"

    def test_invalider_increments_counter(self):
        """Test invalidation met à jour les statistiques (evictions)."""
        from src.core.caching.orchestrator import obtenir_cache

        cache = obtenir_cache()
        cache.set("test", "valeur")

        stats_before = cache.obtenir_statistiques()
        initial_evictions = stats_before["evictions"]

        cache.invalidate(pattern="test")

        stats_after = cache.obtenir_statistiques()
        assert stats_after["evictions"] > initial_evictions


class TestCacheVider:
    """Tests pour CacheMultiNiveau.clear()."""

    def test_vider_removes_all_data(self):
        """Test clear supprime toutes les données."""
        from src.core.caching.orchestrator import obtenir_cache

        cache = obtenir_cache()
        cache.set("cle1", "val1")
        cache.set("cle2", "val2")

        cache.clear()

        assert cache.get("cle1") is None
        assert cache.get("cle2") is None


class TestCacheStatistiques:
    """Tests pour CacheMultiNiveau.obtenir_statistiques()."""

    def test_obtenir_statistiques_returns_dict(self):
        """Test statistiques retourne dict."""
        from src.core.caching.orchestrator import obtenir_cache

        stats = obtenir_cache().obtenir_statistiques()

        assert isinstance(stats, dict)
        assert "total_hits" in stats
        assert "misses" in stats
        assert "l1" in stats
        assert "hit_rate" in stats

    def test_taux_hit_calculation(self):
        """Test calcul taux de hit."""
        from src.core.caching.orchestrator import obtenir_cache

        cache = obtenir_cache()
        cache.set("cle", "val")

        # 2 hits
        cache.get("cle")
        cache.get("cle")

        # 1 miss
        cache.get("inexistant")

        stats = cache.obtenir_statistiques()

        # hit_rate is formatted as string like "66.7%"
        assert "hit_rate" in stats
        rate = float(stats["hit_rate"].rstrip("%"))
        assert rate == pytest.approx(66.7, abs=1.0)


class TestCacheNettoyerExpires:
    """Tests pour nettoyage des entrées expirées."""

    def test_nettoyer_removes_old_entries(self):
        """Test nettoyer supprime entrées anciennes."""
        from src.core.caching.orchestrator import obtenir_cache

        cache = obtenir_cache()
        cache.set("recente", "val1", ttl=7200)
        cache.set("ancienne", "val2", ttl=300)

        # Simuler entrée ancienne en modifiant created_at dans L1
        entry = cache.l1._cache["ancienne"]
        entry.created_at = time.time() - 7200  # 2h dans le passé

        cache.l1.cleanup_expired()

        assert cache.get("recente") == "val1"
        assert cache.get("ancienne") is None


# ═══════════════════════════════════════════════════════════
# TESTS LIMITE DEBIT (RATE LIMIT)
# via MemorySessionStorage (plus de mock st.session_state)
# ═══════════════════════════════════════════════════════════


class TestLimiteDebitBase:
    """Tests de base pour RateLimitIA."""

    @pytest.fixture(autouse=True)
    def setup_memory_storage(self):
        from src.core.storage import MemorySessionStorage, configurer_storage

        self._storage = MemorySessionStorage()
        configurer_storage(self._storage)
        yield
        configurer_storage(MemorySessionStorage())

    def test_initialise_creates_structures(self):
        """Test initialisation crée les structures."""
        from src.core.ai import RateLimitIA

        RateLimitIA._initialiser()

        data = self._storage.get("rate_limit_ia")
        assert data is not None
        assert "appels_jour" in data
        assert "appels_heure" in data


class TestLimiteDebitPeutAppeler:
    """Tests pour RateLimitIA.peut_appeler()."""

    @pytest.fixture(autouse=True)
    def setup_memory_storage(self):
        from src.core.storage import MemorySessionStorage, configurer_storage

        self._storage = MemorySessionStorage()
        configurer_storage(self._storage)
        yield
        configurer_storage(MemorySessionStorage())

    def test_peut_appeler_returns_true_initially(self):
        """Test peut_appeler retourne True au départ."""
        from src.core.ai import RateLimitIA

        autorise, erreur = RateLimitIA.peut_appeler()

        assert autorise is True
        assert erreur == ""

    def test_peut_appeler_false_when_daily_limit_reached(self):
        """Test peut_appeler retourne False si limite jour atteinte."""
        from src.core.ai import RateLimitIA
        from src.core.constants import AI_RATE_LIMIT_DAILY

        RateLimitIA._initialiser()
        data = self._storage.get("rate_limit_ia")
        data["appels_jour"] = AI_RATE_LIMIT_DAILY
        self._storage.set("rate_limit_ia", data)

        autorise, erreur = RateLimitIA.peut_appeler()

        assert autorise is False
        assert "quotidienne" in erreur.lower()

    def test_peut_appeler_false_when_hourly_limit_reached(self):
        """Test peut_appeler retourne False si limite heure atteinte."""
        from src.core.ai import RateLimitIA
        from src.core.constants import AI_RATE_LIMIT_HOURLY

        RateLimitIA._initialiser()
        data = self._storage.get("rate_limit_ia")
        data["appels_heure"] = AI_RATE_LIMIT_HOURLY
        self._storage.set("rate_limit_ia", data)

        autorise, erreur = RateLimitIA.peut_appeler()

        assert autorise is False
        assert "horaire" in erreur.lower()


class TestLimiteDebitEnregistrer:
    """Tests pour RateLimitIA.enregistrer_appel()."""

    @pytest.fixture(autouse=True)
    def setup_memory_storage(self):
        from src.core.storage import MemorySessionStorage, configurer_storage

        self._storage = MemorySessionStorage()
        configurer_storage(self._storage)
        yield
        configurer_storage(MemorySessionStorage())

    def test_enregistrer_appel_increments_counters(self):
        """Test enregistrer_appel incrémente les compteurs."""
        from src.core.ai import RateLimitIA

        RateLimitIA._initialiser()
        data = self._storage.get("rate_limit_ia")
        initial_jour = data["appels_jour"]
        initial_heure = data["appels_heure"]

        RateLimitIA.enregistrer_appel()

        data = self._storage.get("rate_limit_ia")
        assert data["appels_jour"] == initial_jour + 1
        assert data["appels_heure"] == initial_heure + 1


class TestLimiteDebitStatistiques:
    """Tests pour RateLimitIA.obtenir_statistiques()."""

    @pytest.fixture(autouse=True)
    def setup_memory_storage(self):
        from src.core.storage import MemorySessionStorage, configurer_storage

        self._storage = MemorySessionStorage()
        configurer_storage(self._storage)
        yield
        configurer_storage(MemorySessionStorage())

    def test_obtenir_statistiques_returns_dict(self):
        """Test statistiques retourne dict complet."""
        from src.core.ai import RateLimitIA

        stats = RateLimitIA.obtenir_statistiques()

        assert isinstance(stats, dict)
        assert "appels_jour" in stats
        assert "limite_jour" in stats
        assert "appels_heure" in stats
        assert "limite_heure" in stats
        assert "restant_jour" in stats
        assert "restant_heure" in stats


class TestLimiteDebitReset:
    """Tests pour le reset automatique des compteurs."""

    @pytest.fixture(autouse=True)
    def setup_memory_storage(self):
        from src.core.storage import MemorySessionStorage, configurer_storage

        self._storage = MemorySessionStorage()
        configurer_storage(self._storage)
        yield
        configurer_storage(MemorySessionStorage())

    def test_reset_daily_on_new_day(self):
        """Test reset journalier au changement de jour."""
        from datetime import date

        from src.core.ai import RateLimitIA

        RateLimitIA._initialiser()
        data = self._storage.get("rate_limit_ia")
        data["appels_jour"] = 50
        data["dernier_reset_jour"] = date(2024, 1, 1)
        self._storage.set("rate_limit_ia", data)

        # peut_appeler() devrait reset le compteur
        RateLimitIA.peut_appeler()

        data = self._storage.get("rate_limit_ia")
        assert data["appels_jour"] == 0


# ═══════════════════════════════════════════════════════════
# TESTS DECORATEUR @avec_cache (unifié)
# ═══════════════════════════════════════════════════════════


class TestAvecCacheDecorator:
    """Tests pour le décorateur @avec_cache (unifié, multi-niveaux)."""

    def test_avec_cache_returns_cached_value(self):
        """Test avec_cache retourne valeur en cache."""
        from src.core.decorators import avec_cache

        call_count = 0

        @avec_cache(ttl=300)
        def ma_fonction():
            nonlocal call_count
            call_count += 1
            return "résultat"

        # Premier appel - exécute la fonction
        result1 = ma_fonction()
        assert result1 == "résultat"
        assert call_count == 1

        # Deuxième appel - retourne du cache
        result2 = ma_fonction()
        assert result2 == "résultat"
        assert call_count == 1  # Pas réexécuté
