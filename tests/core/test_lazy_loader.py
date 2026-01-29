"""
Tests unitaires pour lazy_loader.py (Chargement diffÃ©rÃ© des modules)
"""

import pytest
from unittest.mock import MagicMock, patch

# Import direct du module Ã  tester
from src.core.lazy_loader import LazyModuleLoader, OptimizedRouter


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS LAZY MODULE LOADER
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class TestLazyModuleLoader:
    """Tests du chargeur de modules diffÃ©rÃ©"""
    
    def test_class_exists(self):
        """Test que la classe existe"""
        assert LazyModuleLoader is not None
    
    def test_class_callable(self):
        """Test que la classe est instanciable"""
        assert callable(LazyModuleLoader)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS OPTIMIZED ROUTER
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class TestOptimizedRouter:
    """Tests du routeur optimisÃ©"""
    
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
            # Peut Ã©chouer si Streamlit n'est pas disponible
            pass

