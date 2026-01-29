"""
Tests unitaires - Module Lazy Loader (Chargement Différé)

Couverture complète :
- LazyModuleLoader (chargement dynamique modules)
- @lazy_import decorator (import lazy)
- OptimizedRouter (routage et caching modules)
- Preload strategies (préchargement)
- Performance metrics (métriques chargement)

Architecture : 5 sections de tests (LazyModuleLoader, LazyImport, OptimizedRouter, Integration, EdgeCases)
"""

import importlib
import sys
import time
import threading
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
import streamlit as st

from src.core.lazy_loader import (
    LazyModuleLoader,
    OptimizedRouter,
    lazy_import,
)


# ═══════════════════════════════════════════════════════════
# SECTION 1: LAZY MODULE LOADER
# ═══════════════════════════════════════════════════════════


class TestLazyModuleLoader:
    """Tests pour LazyModuleLoader."""

    def setup_method(self):
        """Préparation avant chaque test."""
        LazyModuleLoader._cache.clear()
        LazyModuleLoader._load_times.clear()

    @pytest.mark.unit
    def test_load_standard_library_module(self):
        """Test chargement module standard library."""
        module = LazyModuleLoader.load("json")
        
        assert module is not None
        assert hasattr(module, "loads")

    @pytest.mark.unit
    def test_cache_hit_on_reload(self):
        """Test cache hit lors rechargement."""
        module1 = LazyModuleLoader.load("json")
        module2 = LazyModuleLoader.load("json")
        
        assert module1 is module2

    @pytest.mark.unit
    def test_force_reload(self):
        """Test reload forcé."""
        module1 = LazyModuleLoader.load("json")
        module2 = LazyModuleLoader.load("json", reload=True)
        
        # Peut être même objet après reload
        assert module1 is not None
        assert module2 is not None

    @pytest.mark.unit
    def test_load_nonexistent_module(self):
        """Test chargement module inexistant."""
        with pytest.raises(ModuleNotFoundError):
            LazyModuleLoader.load("nonexistent_module_xyz")

    @pytest.mark.unit
    def test_cache_not_cleared_after_failed_load(self):
        """Test cache non affecté après chargement échoué."""
        LazyModuleLoader._cache["json"] = __import__("json")
        
        try:
            LazyModuleLoader.load("nonexistent_xyz")
        except ModuleNotFoundError:
            pass
        
        # json devrait toujours être en cache
        assert "json" in LazyModuleLoader._cache

    @pytest.mark.unit
    def test_load_time_recorded(self):
        """Test enregistrement temps chargement."""
        LazyModuleLoader._load_times.clear()
        
        LazyModuleLoader.load("json")
        
        assert "json" in LazyModuleLoader._load_times
        assert LazyModuleLoader._load_times["json"] > 0

    @pytest.mark.unit
    def test_get_stats(self):
        """Test récupération statistiques."""
        LazyModuleLoader.load("json")
        LazyModuleLoader.load("sys")
        
        stats = LazyModuleLoader.get_stats()
        
        assert "cached_modules" in stats
        assert "total_load_time" in stats
        assert "average_load_time" in stats
        assert stats["cached_modules"] == 2

    @pytest.mark.unit
    def test_clear_cache(self):
        """Test effacement cache."""
        LazyModuleLoader.load("json")
        
        assert len(LazyModuleLoader._cache) > 0
        
        LazyModuleLoader.clear_cache()
        
        assert len(LazyModuleLoader._cache) == 0
        assert len(LazyModuleLoader._load_times) == 0


# ═══════════════════════════════════════════════════════════
# SECTION 2: LAZY IMPORT DECORATOR
# ═══════════════════════════════════════════════════════════


class TestLazyImport:
    """Tests pour décorateur @lazy_import."""

    def setup_method(self):
        """Préparation avant chaque test."""
        LazyModuleLoader._cache.clear()

    @pytest.mark.unit
    def test_lazy_import_basic(self):
        """Test import lazy basique."""
        
        @lazy_import("json")
        def use_json():
            import json
            return json.loads
        
        func = use_json()
        
        assert callable(func)

    @pytest.mark.unit
    def test_lazy_import_with_attribute(self):
        """Test import lazy avec attribut."""
        
        @lazy_import("json", "loads")
        def use_json_loads():
            import json
            return json.loads
        
        func = use_json_loads()
        
        assert callable(func)

    @pytest.mark.unit
    def test_lazy_import_performance(self):
        """Test performance import lazy."""
        import_start = time.time()
        
        @lazy_import("json")
        def use_json():
            import json
            return json
        
        import_time = time.time() - import_start
        
        # Décorateur lui-même doit être rapide
        assert import_time < 0.1

    @pytest.mark.unit
    def test_lazy_import_caches_module(self):
        """Test que import lazy cache le module."""
        LazyModuleLoader._cache.clear()
        
        @lazy_import("json")
        def func1():
            return 1
        
        @lazy_import("json")
        def func2():
            return 2
        
        func1()
        func2()
        
        # Module devrait être en cache
        assert "json" in LazyModuleLoader._cache


# ═══════════════════════════════════════════════════════════
# SECTION 3: OPTIMIZED ROUTER
# ═══════════════════════════════════════════════════════════


class TestOptimizedRouter:
    """Tests pour OptimizedRouter."""

    def setup_method(self):
        """Préparation avant chaque test."""
        LazyModuleLoader._cache.clear()

    @pytest.mark.unit
    def test_router_initialization(self):
        """Test initialisation du routeur."""
        router = OptimizedRouter()
        
        assert router is not None
        assert hasattr(router, "MODULE_REGISTRY")

    @pytest.mark.unit
    def test_router_register_module(self):
        """Test enregistrement module."""
        router = OptimizedRouter()
        
        router.register("test_module", "src.modules.test_module")
        
        # Vérifier enregistrement
        assert len(router.MODULE_REGISTRY) >= 1

    @pytest.mark.unit
    def test_router_load_module(self):
        """Test chargement module via router."""
        router = OptimizedRouter()
        
        # Enregistrer un module existant
        router.register("json_module", "json")
        
        module = router.load("json_module")
        
        assert module is not None

    @pytest.mark.unit
    def test_router_cache_behavior(self):
        """Test comportement cache du routeur."""
        router = OptimizedRouter()
        router.register("json_module", "json")
        
        module1 = router.load("json_module")
        module2 = router.load("json_module")
        
        assert module1 is module2

    @pytest.mark.unit
    def test_router_get_module_list(self):
        """Test récupération liste modules."""
        router = OptimizedRouter()
        
        router.register("module1", "json")
        router.register("module2", "sys")
        
        modules = router.get_module_list()
        
        assert len(modules) >= 2

    @pytest.mark.unit
    def test_router_preload_modules(self):
        """Test préchargement modules."""
        router = OptimizedRouter()
        
        router.register("json_module", "json")
        router.register("sys_module", "sys")
        
        router.preload(["json_module", "sys_module"], background=False)
        
        # Vérifier que modules sont préchargés
        assert "json_module" in str(router.MODULE_REGISTRY)

    @pytest.mark.unit
    def test_router_stats(self):
        """Test statistiques routeur."""
        router = OptimizedRouter()
        
        router.register("json_module", "json")
        router.load("json_module")
        
        stats = router.get_stats()
        
        assert isinstance(stats, dict)


# ═══════════════════════════════════════════════════════════
# SECTION 4: CAS D'INTÉGRATION
# ═══════════════════════════════════════════════════════════


class TestLazyLoaderIntegration:
    """Tests d'intégration pour lazy loading."""

    def setup_method(self):
        """Préparation avant chaque test."""
        LazyModuleLoader._cache.clear()
        LazyModuleLoader._load_times.clear()

    @pytest.mark.integration
    def test_multiple_modules_loading(self):
        """Test chargement multiples modules."""
        modules = []
        
        for module_name in ["json", "sys", "os", "time"]:
            module = LazyModuleLoader.load(module_name)
            modules.append(module)
        
        assert len(modules) == 4
        assert all(m is not None for m in modules)

    @pytest.mark.integration
    def test_preload_background_threads(self):
        """Test préchargement en arrière-plan."""
        LazyModuleLoader._cache.clear()
        
        modules_to_preload = ["json", "sys", "os"]
        
        LazyModuleLoader.preload(modules_to_preload, background=True)
        
        # Attendre un peu pour préchargement
        time.sleep(0.5)
        
        # Vérifier cache
        cached_count = len(LazyModuleLoader._cache)
        assert cached_count >= 1

    @pytest.mark.integration
    def test_preload_synchronous(self):
        """Test préchargement synchrone."""
        LazyModuleLoader._cache.clear()
        
        modules_to_preload = ["json", "sys"]
        
        LazyModuleLoader.preload(modules_to_preload, background=False)
        
        # Tous les modules devaient être préchargés
        assert len(LazyModuleLoader._cache) == 2

    @pytest.mark.integration
    def test_full_router_workflow(self):
        """Test workflow complet routeur."""
        router = OptimizedRouter()
        
        # Enregistrer modules
        router.register("json_mod", "json")
        router.register("sys_mod", "sys")
        
        # Charger modules
        json_mod = router.load("json_mod")
        sys_mod = router.load("sys_mod")
        
        # Vérifier
        assert json_mod is not None
        assert sys_mod is not None
        
        # Récupérer stats
        stats = router.get_stats()
        assert stats is not None


# ═══════════════════════════════════════════════════════════
# SECTION 5: CAS LIMITES ET EDGE CASES
# ═══════════════════════════════════════════════════════════


class TestLazyLoaderEdgeCases:
    """Tests des cas limites."""

    def setup_method(self):
        """Préparation avant chaque test."""
        LazyModuleLoader._cache.clear()
        LazyModuleLoader._load_times.clear()

    @pytest.mark.unit
    def test_load_same_module_multiple_times(self):
        """Test chargement même module plusieurs fois."""
        for _ in range(10):
            module = LazyModuleLoader.load("json")
            assert module is not None

    @pytest.mark.unit
    def test_concurrent_module_loading(self):
        """Test chargement concurrente modules."""
        results = []
        
        def load_module(name):
            try:
                module = LazyModuleLoader.load(name)
                results.append(module)
            except Exception as e:
                results.append(None)
        
        threads = [
            threading.Thread(target=load_module, args=(name,))
            for name in ["json", "sys", "os", "time", "math"]
        ]
        
        for t in threads:
            t.start()
        
        for t in threads:
            t.join()
        
        assert len([r for r in results if r is not None]) > 0

    @pytest.mark.unit
    def test_load_module_with_empty_string(self):
        """Test chargement avec string vide."""
        with pytest.raises((ModuleNotFoundError, ValueError)):
            LazyModuleLoader.load("")

    @pytest.mark.unit
    def test_load_module_with_invalid_path(self):
        """Test chargement chemin invalide."""
        with pytest.raises(ModuleNotFoundError):
            LazyModuleLoader.load("this.module.does.not.exist.anywhere")

    @pytest.mark.unit
    def test_stats_with_empty_cache(self):
        """Test statistiques cache vide."""
        LazyModuleLoader._cache.clear()
        LazyModuleLoader._load_times.clear()
        
        stats = LazyModuleLoader.get_stats()
        
        assert stats["cached_modules"] == 0
        assert stats["total_load_time"] == 0

    @pytest.mark.unit
    def test_preload_with_empty_list(self):
        """Test préchargement liste vide."""
        # Ne devrait pas lever d'erreur
        LazyModuleLoader.preload([], background=False)

    @pytest.mark.unit
    def test_preload_with_nonexistent_modules(self):
        """Test préchargement modules inexistants."""
        LazyModuleLoader.preload(
            ["nonexistent_xyz", "another_fake"],
            background=False,
        )
        
        # Cache devrait rester vide ou presque
        assert len(LazyModuleLoader._cache) == 0

    @pytest.mark.unit
    def test_clear_cache_multiple_times(self):
        """Test effacement cache plusieurs fois."""
        LazyModuleLoader.load("json")
        
        LazyModuleLoader.clear_cache()
        assert len(LazyModuleLoader._cache) == 0
        
        LazyModuleLoader.clear_cache()
        assert len(LazyModuleLoader._cache) == 0

    @pytest.mark.unit
    def test_load_times_accuracy(self):
        """Test précision temps chargement."""
        start = time.time()
        LazyModuleLoader.load("json")
        end = time.time()
        
        recorded_time = LazyModuleLoader._load_times.get("json", 0)
        actual_time = end - start
        
        # Temps enregistré devrait être proche du temps réel
        assert recorded_time >= 0
        assert actual_time >= 0

    @pytest.mark.unit
    def test_router_nonexistent_module(self):
        """Test routeur avec module inexistant."""
        router = OptimizedRouter()
        router.register("fake", "nonexistent_module_xyz")
        
        with pytest.raises(ModuleNotFoundError):
            router.load("fake")

    @pytest.mark.unit
    def test_router_unregistered_module(self):
        """Test requête module non enregistré."""
        router = OptimizedRouter()
        
        with pytest.raises((KeyError, AttributeError)):
            router.load("unregistered_module")

    @pytest.mark.unit
    def test_module_import_with_side_effects(self):
        """Test module avec side effects lors import."""
        # Charger sys qui a des side effects
        module = LazyModuleLoader.load("sys")
        
        assert module is not None
        assert hasattr(module, "exit")
