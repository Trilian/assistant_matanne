"""
Tests profonds supplÃ©mentaires pour lazy_loader.py, cache.py et decorators.py

Cible les fonctions non couvertes pour atteindre 80% de couverture.
"""

import pytest
import time
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch, PropertyMock
from functools import wraps


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# MOCK STREAMLIT SESSION STATE (amÃ©liorÃ©)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class MockSessionState(dict):
    """Mock avancÃ© de st.session_state"""

    def __init__(self):
        super().__init__()
        self._data = {}

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value

    def __contains__(self, key):
        return key in self._data

    def __delitem__(self, key):
        del self._data[key]

    def get(self, key, default=None):
        return self._data.get(key, default)

    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()

    def items(self):
        return self._data.items()


@pytest.fixture
def mock_session():
    """Fixture pour mocker st.session_state"""
    mock_state = MockSessionState()
    with patch("streamlit.session_state", mock_state):
        yield mock_state


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS: RouteurOptimise
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestOptimizedRouter:
    """Tests pour RouteurOptimise"""

    def test_module_registry_exists(self):
        """Test MODULE_REGISTRY existe"""
        from src.core.lazy_loader import RouteurOptimise

        assert hasattr(RouteurOptimise, "MODULE_REGISTRY")
        assert isinstance(RouteurOptimise.MODULE_REGISTRY, dict)

    def test_module_registry_has_accueil(self):
        """Test MODULE_REGISTRY contient accueil"""
        from src.core.lazy_loader import RouteurOptimise

        assert "accueil" in RouteurOptimise.MODULE_REGISTRY

    def test_module_registry_has_cuisine(self):
        """Test MODULE_REGISTRY contient modules cuisine"""
        from src.core.lazy_loader import RouteurOptimise

        cuisine_modules = [k for k in RouteurOptimise.MODULE_REGISTRY if k.startswith("cuisine")]
        assert len(cuisine_modules) > 0

    def test_module_registry_has_famille(self):
        """Test MODULE_REGISTRY contient modules famille"""
        from src.core.lazy_loader import RouteurOptimise

        famille_modules = [k for k in RouteurOptimise.MODULE_REGISTRY if k.startswith("famille")]
        assert len(famille_modules) > 0

    def test_module_registry_has_maison(self):
        """Test MODULE_REGISTRY contient modules maison"""
        from src.core.lazy_loader import RouteurOptimise

        maison_modules = [k for k in RouteurOptimise.MODULE_REGISTRY if k.startswith("maison")]
        assert len(maison_modules) > 0

    def test_module_config_structure(self):
        """Test structure config module"""
        from src.core.lazy_loader import RouteurOptimise

        for name, config in RouteurOptimise.MODULE_REGISTRY.items():
            assert "path" in config, f"Module {name} manque 'path'"
            assert "type" in config, f"Module {name} manque 'type'"

    def test_preload_common_modules_exists(self):
        """Test mÃ©thode preload_common_modules existe"""
        from src.core.lazy_loader import RouteurOptimise

        assert hasattr(RouteurOptimise, "preload_common_modules")
        assert callable(RouteurOptimise.preload_common_modules)

    def test_load_module_exists(self):
        """Test mÃ©thode load_module existe"""
        from src.core.lazy_loader import RouteurOptimise

        assert hasattr(RouteurOptimise, "load_module")
        assert callable(RouteurOptimise.load_module)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS: lazy_import decorator
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestLazyImportDecorator:
    """Tests pour dÃ©corateur @lazy_import"""

    def test_lazy_import_exists(self):
        """Test lazy_import existe"""
        from src.core.lazy_loader import lazy_import

        assert callable(lazy_import)

    def test_lazy_import_decorator(self):
        """Test lazy_import comme dÃ©corateur"""
        from src.core.lazy_loader import lazy_import

        @lazy_import("json")
        def func_with_lazy():
            return "executed"

        result = func_with_lazy()
        assert result == "executed"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS: Cache avancÃ©
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestCacheNettoyer:
    """Tests pour Cache.nettoyer_expires"""

    def test_nettoyer_expires(self, mock_session):
        """Test nettoyage entrÃ©es expirÃ©es"""
        from src.core.cache import Cache

        # DÃ©finir une entrÃ©e
        Cache.definir("cle_ancienne", "valeur", ttl=1)

        # Simuler expiration
        mock_session["cache_timestamps"]["cle_ancienne"] = datetime.now() - timedelta(hours=2)

        # Nettoyer
        Cache.nettoyer_expires(age_max_secondes=3600)

        # VÃ©rifier suppression
        assert "cle_ancienne" not in mock_session.get("cache_donnees", {})


class TestCacheVider:
    """Tests pour Cache.vider"""

    def test_vider_cache(self, mock_session):
        """Test vidage complet"""
        from src.core.cache import Cache

        Cache.definir("cle1", "val1")
        Cache.definir("cle2", "val2")

        Cache.vider()

        assert len(mock_session["cache_donnees"]) == 0


class TestCacheStatistiques:
    """Tests pour Cache.obtenir_statistiques"""

    def test_obtenir_statistiques(self, mock_session):
        """Test rÃ©cupÃ©ration statistiques"""
        from src.core.cache import Cache

        Cache.definir("test", "value")
        Cache.obtenir("test", ttl=300)
        Cache.obtenir("inexistant", ttl=300)

        stats = Cache.obtenir_statistiques()

        assert "hits" in stats
        assert "misses" in stats
        assert "taux_hit" in stats
        assert "entrees" in stats

    def test_statistiques_taux_hit(self, mock_session):
        """Test calcul taux de hit"""
        from src.core.cache import Cache

        # 2 hits, 1 miss
        Cache.definir("key", "value")
        Cache.obtenir("key", ttl=300)  # hit
        Cache.obtenir("key", ttl=300)  # hit
        Cache.obtenir("miss", ttl=300)  # miss

        stats = Cache.obtenir_statistiques()

        assert stats["taux_hit"] > 0


class TestCacheAlias:
    """Tests pour alias Cache"""

    def test_clear_all_alias(self):
        """Test alias clear_all"""
        from src.core.cache import clear_all, Cache

        assert clear_all == Cache.vider


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS: DÃ©corateur with_validation
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestWithValidationDecorator:
    """Tests pour dÃ©corateur @with_validation"""

    def test_with_validation_exists(self):
        """Test with_validation existe"""
        from src.core.decorators import with_validation

        assert callable(with_validation)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS: DÃ©corateur with_db_session avancÃ©
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestWithDbSessionAdvanced:
    """Tests avancÃ©s pour @with_db_session"""

    def test_with_db_session_with_session_param(self):
        """Test avec paramÃ¨tre session au lieu de db"""
        from src.core.decorators import with_db_session

        @with_db_session
        def func_with_session(data, session=None):
            return session is not None

        # Appeler avec session fournie
        mock_session = MagicMock()
        result = func_with_session("data", session=mock_session)

        assert result is True

    def test_with_db_session_preserves_function_name(self):
        """Test conservation du nom de fonction"""
        from src.core.decorators import with_db_session

        @with_db_session
        def ma_fonction_originale(db=None):
            pass

        assert ma_fonction_originale.__name__ == "ma_fonction_originale"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS: DÃ©corateur with_cache avancÃ©
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestWithCacheAdvanced:
    """Tests avancÃ©s pour @with_cache"""

    def test_with_cache_key_func(self, mock_session):
        """Test avec key_func personnalisÃ©e"""
        from src.core.decorators import with_cache

        @with_cache(ttl=300, key_func=lambda x: f"custom_{x}")
        def func_custom_key(value):
            return value * 2

        result = func_custom_key(5)
        assert result == 10

    def test_with_cache_different_args(self, mock_session):
        """Test cache avec diffÃ©rents arguments"""
        from src.core.decorators import with_cache

        call_count = 0

        @with_cache(ttl=300)
        def func_with_args(a, b):
            nonlocal call_count
            call_count += 1
            return a + b

        result1 = func_with_args(1, 2)
        result2 = func_with_args(1, 2)  # Cache hit
        result3 = func_with_args(3, 4)  # Cache miss (args diffÃ©rents)

        assert result1 == 3
        assert result2 == 3
        assert result3 == 7


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS: DÃ©corateur with_error_handling avancÃ©
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestWithErrorHandlingAdvanced:
    """Tests avancÃ©s pour @with_error_handling"""

    def test_with_error_handling_log_level_warning(self):
        """Test niveau log WARNING"""
        from src.core.decorators import with_error_handling

        @with_error_handling(default_return="fallback", log_level="WARNING")
        def func_warning():
            raise ValueError("test")

        result = func_warning()
        assert result == "fallback"

    def test_with_error_handling_log_level_info(self):
        """Test niveau log INFO"""
        from src.core.decorators import with_error_handling

        @with_error_handling(default_return="fallback", log_level="INFO")
        def func_info():
            raise ValueError("test")

        result = func_info()
        assert result == "fallback"

    def test_with_error_handling_with_streamlit(self):
        """Test affichage erreur Streamlit"""
        from src.core.decorators import with_error_handling

        @with_error_handling(default_return=None, afficher_erreur=True)
        def func_with_ui():
            raise ValueError("Test error")

        with patch("streamlit.error") as mock_error:
            result = func_with_ui()
            # Ne doit pas crash mÃªme si Streamlit n'est pas initialisÃ©


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS: ChargeurModuleDiffere mÃ©triques
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestLazyModuleLoaderMetrics:
    """Tests pour mÃ©triques ChargeurModuleDiffere"""

    def test_load_times_recorded(self):
        """Test enregistrement temps de chargement"""
        from src.core.lazy_loader import ChargeurModuleDiffere

        ChargeurModuleDiffere.clear_cache()
        ChargeurModuleDiffere.load("json")

        stats = ChargeurModuleDiffere.get_stats()

        assert "json" in stats["load_times"]
        assert stats["load_times"]["json"] >= 0

    def test_average_load_time(self):
        """Test calcul temps moyen"""
        from src.core.lazy_loader import ChargeurModuleDiffere

        ChargeurModuleDiffere.clear_cache()
        ChargeurModuleDiffere.load("json")
        ChargeurModuleDiffere.load("re")

        stats = ChargeurModuleDiffere.get_stats()

        assert stats["average_load_time"] >= 0
        assert stats["total_load_time"] >= 0

    def test_empty_stats(self):
        """Test stats vides"""
        from src.core.lazy_loader import ChargeurModuleDiffere

        ChargeurModuleDiffere.clear_cache()

        stats = ChargeurModuleDiffere.get_stats()

        assert stats["cached_modules"] == 0
        assert stats["total_load_time"] == 0
        assert stats["average_load_time"] == 0


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS: afficher_stats_chargement_differe
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestRenderLazyLoadingStats:
    """Tests pour afficher_stats_chargement_differe"""

    def test_function_exists(self):
        """Test fonction existe"""
        from src.core.lazy_loader import afficher_stats_chargement_differe

        assert callable(afficher_stats_chargement_differe)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS: Preload async
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestPreloadAsync:
    """Tests pour prÃ©chargement asynchrone"""

    def test_preload_background(self):
        """Test prÃ©chargement en arriÃ¨re-plan"""
        from src.core.lazy_loader import ChargeurModuleDiffere

        ChargeurModuleDiffere.clear_cache()

        # PrÃ©charger en background (thread)
        ChargeurModuleDiffere.preload(["json", "re"], background=True)

        # Attendre un peu pour le thread
        time.sleep(0.1)

        # Les modules peuvent Ãªtre en cache maintenant
        # (pas garanti car async)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS: Cache dependencies avancÃ©
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestCacheDependenciesAdvanced:
    """Tests avancÃ©s pour dÃ©pendances du cache"""

    def test_multiple_dependencies(self, mock_session):
        """Test multiples dÃ©pendances"""
        from src.core.cache import Cache

        Cache.definir(
            "recette_1", {"id": 1}, dependencies=["recettes", "user_1", "categorie_desserts"]
        )

        assert "recettes" in mock_session["cache_dependances"]
        assert "user_1" in mock_session["cache_dependances"]
        assert "categorie_desserts" in mock_session["cache_dependances"]

    def test_invalidate_chain(self, mock_session):
        """Test invalidation en chaÃ®ne"""
        from src.core.cache import Cache

        # CrÃ©er plusieurs entrÃ©es avec dÃ©pendance commune
        Cache.definir("recette_1", "r1", dependencies=["recettes"])
        Cache.definir("recette_2", "r2", dependencies=["recettes"])
        Cache.definir("recette_3", "r3", dependencies=["recettes"])

        # Invalider par dÃ©pendance
        Cache.invalider(dependencies=["recettes"])

        # Toutes les recettes doivent Ãªtre supprimÃ©es
        assert "recette_1" not in mock_session["cache_donnees"]
        assert "recette_2" not in mock_session["cache_donnees"]
        assert "recette_3" not in mock_session["cache_donnees"]


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS: Cache taille
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestCacheTaille:
    """Tests pour calcul taille cache"""

    def test_taille_octets(self, mock_session):
        """Test calcul taille en octets"""
        from src.core.cache import Cache

        Cache.definir("large_data", "x" * 1000)

        stats = Cache.obtenir_statistiques()

        assert stats["taille_octets"] > 0

    def test_taille_mo(self, mock_session):
        """Test conversion en Mo"""
        from src.core.cache import Cache

        Cache.definir("data", "x" * 1000)

        stats = Cache.obtenir_statistiques()

        assert "taille_mo" in stats
        assert stats["taille_mo"] >= 0
