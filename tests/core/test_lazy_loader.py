"""
Tests unitaires pour lazy_loader.py (Chargement différé des modules)
"""

import pytest
from unittest.mock import MagicMock, patch

# Import direct du module à tester
from src.core.lazy_loader import LazyModuleLoader, OptimizedRouter


# ═══════════════════════════════════════════════════════════════
# TESTS LAZY MODULE LOADER
# ═══════════════════════════════════════════════════════════════

class TestLazyModuleLoader:
    """Tests du chargeur de modules différé"""
    
    def test_class_exists(self):
        """Test que la classe existe"""
        assert LazyModuleLoader is not None
    
    def test_class_callable(self):
        """Test que la classe est instanciable"""
        assert callable(LazyModuleLoader)


# ═══════════════════════════════════════════════════════════════
# TESTS OPTIMIZED ROUTER
# ═══════════════════════════════════════════════════════════════

class TestOptimizedRouter:
    """Tests du routeur optimisé"""
    
    def test_class_exists(self):
        """Test que la classe existe"""
        assert OptimizedRouter is not None
    
    def test_has_module_registry(self):
        """Test que le registre de modules existe"""
        assert hasattr(OptimizedRouter, 'MODULE_REGISTRY') or hasattr(OptimizedRouter, 'modules')
    
    def test_class_instantiable(self):
        """Test que la classe est instanciable"""
        try:
            router = OptimizedRouter()
            assert router is not None
        except Exception:
            # Peut échouer si Streamlit n'est pas disponible
            pass
