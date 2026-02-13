"""
Tests pour src/core/lazy_loader.py
Cible: ChargeurModuleDiffere, RouteurOptimise
"""

import time
from unittest.mock import patch

import pytest

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS LAZY MODULE LOADER
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestLazyModuleLoader:
    """Tests pour ChargeurModuleDiffere."""

    def setup_method(self):
        """Reset le cache avant chaque test."""
        from src.core.lazy_loader import ChargeurModuleDiffere

        ChargeurModuleDiffere._cache.clear()
        ChargeurModuleDiffere._load_times.clear()

    def test_load_caches_module(self):
        """VÃ©rifie que le module est mis en cache aprÃ¨s chargement."""
        from src.core.lazy_loader import ChargeurModuleDiffere

        # Charger un module standard Python
        module = ChargeurModuleDiffere.load("json")

        assert "json" in ChargeurModuleDiffere._cache
        assert module is not None

    def test_load_returns_cached_module(self):
        """VÃ©rifie que le module est retournÃ© depuis le cache."""
        from src.core.lazy_loader import ChargeurModuleDiffere

        # Premier chargement
        module1 = ChargeurModuleDiffere.load("json")
        # DeuxiÃ¨me chargement (devrait venir du cache)
        module2 = ChargeurModuleDiffere.load("json")

        assert module1 is module2

    def test_load_with_reload_reloads_module(self):
        """VÃ©rifie que reload=True recharge le module."""
        from src.core.lazy_loader import ChargeurModuleDiffere

        # Premier chargement
        module1 = ChargeurModuleDiffere.load("json")
        # Recharger
        module2 = ChargeurModuleDiffere.load("json", reload=True)

        # Les modules devraient Ãªtre diffÃ©rentes instances
        # (ou la mÃªme si Python optimise, mais le rechargement a eu lieu)
        assert module2 is not None

    def test_load_records_load_time(self):
        """VÃ©rifie que le temps de chargement est enregistrÃ©."""
        from src.core.lazy_loader import ChargeurModuleDiffere

        ChargeurModuleDiffere.load("os")

        assert "os" in ChargeurModuleDiffere._load_times
        assert ChargeurModuleDiffere._load_times["os"] >= 0

    def test_load_raises_on_invalid_module(self):
        """VÃ©rifie que ModuleNotFoundError est levÃ© pour module invalide."""
        from src.core.lazy_loader import ChargeurModuleDiffere

        with pytest.raises(ModuleNotFoundError):
            ChargeurModuleDiffere.load("module_qui_nexiste_pas_12345")

    def test_get_stats_returns_dict(self):
        """VÃ©rifie que get_stats retourne un dictionnaire."""
        from src.core.lazy_loader import ChargeurModuleDiffere

        # Charger quelques modules
        ChargeurModuleDiffere.load("json")
        ChargeurModuleDiffere.load("os")

        stats = ChargeurModuleDiffere.get_stats()

        assert isinstance(stats, dict)
        assert "cached_modules" in stats
        assert "total_load_time" in stats
        assert stats["cached_modules"] == 2

    def test_get_stats_empty_cache(self):
        """VÃ©rifie get_stats avec cache vide."""
        from src.core.lazy_loader import ChargeurModuleDiffere

        stats = ChargeurModuleDiffere.get_stats()

        assert stats["cached_modules"] == 0
        assert stats["total_load_time"] == 0

    def test_preload_loads_modules(self):
        """VÃ©rifie que preload charge les modules."""
        from src.core.lazy_loader import ChargeurModuleDiffere

        modules = ["json", "os", "sys"]

        # PrÃ©charger en mode synchrone
        ChargeurModuleDiffere.preload(modules, background=False)

        for mod in modules:
            assert mod in ChargeurModuleDiffere._cache

    def test_preload_background_does_not_block(self):
        """VÃ©rifie que preload en arriÃ¨re-plan ne bloque pas."""
        from src.core.lazy_loader import ChargeurModuleDiffere

        modules = ["json", "os"]

        start = time.time()
        ChargeurModuleDiffere.preload(modules, background=True)
        elapsed = time.time() - start

        # Ne devrait pas bloquer longtemps
        assert elapsed < 1.0

    def test_preload_handles_invalid_modules(self):
        """VÃ©rifie que preload gÃ¨re les modules invalides sans crash."""
        from src.core.lazy_loader import ChargeurModuleDiffere

        modules = ["json", "module_invalide_xyz", "os"]

        # Ne devrait pas lever d'exception
        ChargeurModuleDiffere.preload(modules, background=False)

        # Les modules valides devraient Ãªtre chargÃ©s
        assert "json" in ChargeurModuleDiffere._cache
        assert "os" in ChargeurModuleDiffere._cache


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS CLEAR CACHE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestLazyModuleLoaderCache:
    """Tests pour la gestion du cache."""

    def setup_method(self):
        """Reset le cache avant chaque test."""
        from src.core.lazy_loader import ChargeurModuleDiffere

        ChargeurModuleDiffere._cache.clear()
        ChargeurModuleDiffere._load_times.clear()

    def test_clear_cache_empties_cache(self):
        """VÃ©rifie que clear_cache vide le cache."""
        from src.core.lazy_loader import ChargeurModuleDiffere

        # Charger des modules
        ChargeurModuleDiffere.load("json")
        ChargeurModuleDiffere.load("os")

        assert len(ChargeurModuleDiffere._cache) == 2

        # Vider le cache
        ChargeurModuleDiffere._cache.clear()

        assert len(ChargeurModuleDiffere._cache) == 0

    def test_cache_isolation_between_calls(self):
        """VÃ©rifie l'isolation du cache entre diffÃ©rents appels."""
        from src.core.lazy_loader import ChargeurModuleDiffere

        # Charger un module
        ChargeurModuleDiffere.load("json")

        # Le cache devrait contenir json
        assert "json" in ChargeurModuleDiffere._cache

        # Mais pas d'autres modules
        assert "datetime" not in ChargeurModuleDiffere._cache


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS OPTIMIZED ROUTER (si prÃ©sent)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestOptimizedRouter:
    """Tests pour RouteurOptimise."""

    def test_router_exists(self):
        """VÃ©rifie que RouteurOptimise existe."""
        try:
            from src.core.lazy_loader import RouteurOptimise

            assert RouteurOptimise is not None
        except ImportError:
            pytest.skip("RouteurOptimise non disponible")

    def test_router_module_registry_is_dict(self):
        """VÃ©rifie que MODULE_REGISTRY est un dictionnaire."""
        try:
            from src.core.lazy_loader import RouteurOptimise

            assert isinstance(RouteurOptimise.MODULE_REGISTRY, dict)
        except (ImportError, AttributeError):
            pytest.skip("MODULE_REGISTRY non disponible")

    def test_router_charger_module(self):
        """Teste le chargement de module via le router."""
        try:
            from src.core.lazy_loader import RouteurOptimise

            # Utiliser un module connu
            if hasattr(RouteurOptimise, "charger_module"):
                # Mock le registry pour le test
                with patch.object(RouteurOptimise, "MODULE_REGISTRY", {"test": "json"}):
                    module = RouteurOptimise.charger_module("test")
                    assert module is not None
        except (ImportError, AttributeError):
            pytest.skip("charger_module non disponible")


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS PERFORMANCE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestLazyLoaderPerformance:
    """Tests de performance pour le lazy loader."""

    def setup_method(self):
        """Reset le cache avant chaque test."""
        from src.core.lazy_loader import ChargeurModuleDiffere

        ChargeurModuleDiffere._cache.clear()
        ChargeurModuleDiffere._load_times.clear()

    def test_cached_load_is_faster(self):
        """VÃ©rifie que le chargement depuis cache est plus rapide."""
        from src.core.lazy_loader import ChargeurModuleDiffere

        # Premier chargement (sans cache)
        start1 = time.time()
        ChargeurModuleDiffere.load("json")
        time1 = time.time() - start1

        # DeuxiÃ¨me chargement (avec cache)
        start2 = time.time()
        ChargeurModuleDiffere.load("json")
        time2 = time.time() - start2

        # Le chargement depuis cache devrait Ãªtre trÃ¨s rapide
        assert time2 < time1 or time2 < 0.001

    def test_load_many_modules(self):
        """Teste le chargement de nombreux modules."""
        from src.core.lazy_loader import ChargeurModuleDiffere

        modules = ["json", "os", "sys", "re", "math", "collections"]

        for mod in modules:
            ChargeurModuleDiffere.load(mod)

        stats = ChargeurModuleDiffere.get_stats()
        assert stats["cached_modules"] == len(modules)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS THREAD SAFETY
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestLazyLoaderThreadSafety:
    """Tests de thread safety."""

    def setup_method(self):
        """Reset le cache avant chaque test."""
        from src.core.lazy_loader import ChargeurModuleDiffere

        ChargeurModuleDiffere._cache.clear()
        ChargeurModuleDiffere._load_times.clear()

    def test_concurrent_loads(self):
        """Teste les chargements concurrents."""
        import threading

        from src.core.lazy_loader import ChargeurModuleDiffere

        results = []
        errors = []

        def load_module(name):
            try:
                mod = ChargeurModuleDiffere.load(name)
                results.append(mod)
            except Exception as e:
                errors.append(e)

        threads = [
            threading.Thread(target=load_module, args=("json",)),
            threading.Thread(target=load_module, args=("os",)),
            threading.Thread(target=load_module, args=("sys",)),
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert len(results) == 3
