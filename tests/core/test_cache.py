"""
Tests pour src/core/cache.py - Système de cache (façade sur CacheMultiNiveau).
"""

import time

import pytest


@pytest.fixture(autouse=True)
def _reset_cache_singleton():
    """Réinitialise le singleton CacheMultiNiveau entre chaque test.

    L2 (session Streamlit) et L3 (fichier) sont désactivés pour isoler
    les tests sur la logique pure du cache (L1 mémoire uniquement).
    """
    from src.core.caching.orchestrator import CacheMultiNiveau

    # Forcer un nouveau singleton L1-only pour chaque test
    CacheMultiNiveau._instance = None
    CacheMultiNiveau(l2_enabled=False, l3_enabled=False)
    yield
    # Nettoyage final
    CacheMultiNiveau._instance = None


# ═══════════════════════════════════════════════════════════
# TESTS CACHE CLASS (façade statique → CacheMultiNiveau)
# ═══════════════════════════════════════════════════════════


class TestCacheBase:
    """Tests de base pour la classe Cache."""

    def test_initialise_creates_structures(self):
        """Test initialisation — le singleton CacheMultiNiveau se crée."""
        from src.core.caching.cache import Cache, _cache

        # L'accès au cache crée le singleton
        c = _cache()
        assert c is not None
        assert c.l1 is not None

        # L'API statique fonctionne sans exception
        stats = Cache.obtenir_statistiques()
        assert isinstance(stats, dict)

    def test_initialise_only_once(self):
        """Test le singleton ne se recrée pas — les données persistent."""
        from src.core.caching.cache import Cache

        Cache.definir("test", "valeur")

        # Deuxième accès au cache — la valeur doit être toujours là
        result = Cache.obtenir("test")
        assert result == "valeur"


class TestCacheObtenir:
    """Tests pour Cache.obtenir()."""

    def test_obtenir_returns_sentinelle_if_missing(self):
        """Test obtenir retourne sentinelle si clé absente."""
        from src.core.caching.cache import Cache

        result = Cache.obtenir("inexistant", sentinelle="default")
        assert result == "default"

    def test_obtenir_returns_value_if_present_and_fresh(self):
        """Test obtenir retourne valeur si présente et fraîche."""
        from src.core.caching.cache import Cache

        Cache.definir("ma_cle", "ma_valeur", ttl=300)
        result = Cache.obtenir("ma_cle", ttl=300)
        assert result == "ma_valeur"

    def test_obtenir_returns_sentinelle_if_expired(self):
        """Test obtenir retourne sentinelle si expiré."""
        from src.core.caching.cache import Cache, _cache

        Cache.definir("ma_cle", "ma_valeur", ttl=300)

        # Simuler expiration en modifiant created_at dans L1
        entry = _cache().l1._cache["ma_cle"]
        entry.created_at = time.time() - 400

        result = Cache.obtenir("ma_cle", sentinelle="expiré")
        assert result == "expiré"

    def test_obtenir_increments_miss_counter(self):
        """Test obtenir incrémente compteur miss."""
        from src.core.caching.cache import Cache

        stats_before = Cache.obtenir_statistiques()
        initial_misses = stats_before["misses"]

        Cache.obtenir("inexistant")

        stats_after = Cache.obtenir_statistiques()
        assert stats_after["misses"] == initial_misses + 1

    def test_obtenir_increments_hit_counter(self):
        """Test obtenir incrémente compteur hit."""
        from src.core.caching.cache import Cache

        Cache.definir("ma_cle", "ma_valeur")

        stats_before = Cache.obtenir_statistiques()
        initial_hits = stats_before["hits"]

        Cache.obtenir("ma_cle")

        stats_after = Cache.obtenir_statistiques()
        assert stats_after["hits"] == initial_hits + 1


class TestCacheDefinir:
    """Tests pour Cache.definir()."""

    def test_definir_stores_value(self):
        """Test definir stocke la valeur."""
        from src.core.caching.cache import Cache

        Cache.definir("test_cle", {"data": "valeur"})

        result = Cache.obtenir("test_cle")
        assert result == {"data": "valeur"}

    def test_definir_stores_timestamp(self):
        """Test definir stocke le timestamp (created_at dans EntreeCache)."""
        from src.core.caching.cache import Cache, _cache

        avant = time.time()
        Cache.definir("test_cle", "valeur")
        apres = time.time()

        entry = _cache().l1._cache["test_cle"]
        assert avant <= entry.created_at <= apres

    def test_definir_with_dependencies(self):
        """Test definir avec dépendances (tags)."""
        from src.core.caching.cache import Cache, _cache

        Cache.definir("recette_1", "data", dependencies=["recettes", "recette_1"])

        entry = _cache().l1._cache["recette_1"]
        assert "recettes" in entry.tags
        assert "recette_1" in entry.tags


class TestCacheInvalider:
    """Tests pour Cache.invalider()."""

    def test_invalider_by_pattern(self):
        """Test invalidation par pattern."""
        from src.core.caching.cache import Cache

        Cache.definir("recettes_liste", "data1")
        Cache.definir("recettes_detail_1", "data2")
        Cache.definir("courses_liste", "data3")

        Cache.invalider(pattern="recettes")

        assert Cache.obtenir("recettes_liste") is None
        assert Cache.obtenir("recettes_detail_1") is None
        assert Cache.obtenir("courses_liste") == "data3"

    def test_invalider_by_dependencies(self):
        """Test invalidation par dépendances (tags)."""
        from src.core.caching.cache import Cache

        Cache.definir("recette_1", "data1", dependencies=["tag_recette"])
        Cache.definir("recette_2", "data2", dependencies=["tag_recette"])
        Cache.definir("autre", "data3")

        Cache.invalider(dependencies=["tag_recette"])

        assert Cache.obtenir("recette_1") is None
        assert Cache.obtenir("recette_2") is None
        assert Cache.obtenir("autre") == "data3"

    def test_invalider_increments_counter(self):
        """Test invalidation met à jour les statistiques (evictions)."""
        from src.core.caching.cache import Cache

        Cache.definir("test", "valeur")

        stats_before = Cache.obtenir_statistiques()
        initial_invalidations = stats_before["invalidations"]

        Cache.invalider(pattern="test")

        stats_after = Cache.obtenir_statistiques()
        assert stats_after["invalidations"] > initial_invalidations


class TestCacheVider:
    """Tests pour Cache.vider() et clear()."""

    def test_vider_removes_all_data(self):
        """Test vider supprime toutes les données."""
        from src.core.caching.cache import Cache

        Cache.definir("cle1", "val1")
        Cache.definir("cle2", "val2")

        Cache.vider()

        assert Cache.obtenir("cle1") is None
        assert Cache.obtenir("cle2") is None

    def test_clear_alias_works(self):
        """Test alias clear fonctionne."""
        from src.core.caching.cache import Cache

        Cache.definir("cle", "val")

        Cache.clear()

        assert Cache.obtenir("cle") is None


class TestCacheStatistiques:
    """Tests pour Cache.obtenir_statistiques()."""

    def test_obtenir_statistiques_returns_dict(self):
        """Test statistiques retourne dict."""
        from src.core.caching.cache import Cache

        stats = Cache.obtenir_statistiques()

        assert isinstance(stats, dict)
        assert "hits" in stats
        assert "misses" in stats
        assert "entrees" in stats
        assert "taux_hit" in stats

    def test_taux_hit_calculation(self):
        """Test calcul taux de hit."""
        from src.core.caching.cache import Cache

        Cache.definir("cle", "val")

        # 2 hits
        Cache.obtenir("cle")
        Cache.obtenir("cle")

        # 1 miss
        Cache.obtenir("inexistant")

        stats = Cache.obtenir_statistiques()

        # 2 hits sur 3 requêtes = 66.67%
        assert stats["taux_hit"] == pytest.approx(66.67, rel=0.01)


class TestCacheNettoyerExpires:
    """Tests pour Cache.nettoyer_expires()."""

    def test_nettoyer_removes_old_entries(self):
        """Test nettoyer supprime entrées anciennes."""
        from src.core.caching.cache import Cache, _cache

        Cache.definir("recente", "val1", ttl=7200)
        Cache.definir("ancienne", "val2", ttl=300)

        # Simuler entrée ancienne en modifiant created_at dans L1
        entry = _cache().l1._cache["ancienne"]
        entry.created_at = time.time() - 7200  # 2h dans le passé

        Cache.nettoyer_expires(age_max_secondes=3600)

        assert Cache.obtenir("recente") == "val1"
        assert Cache.obtenir("ancienne") is None


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
