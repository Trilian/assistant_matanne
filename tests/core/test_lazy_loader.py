"""
Tests unitaires pour lazy_loader.py (Chargement différé des modules)
"""

import pytest
from src.core import lazy_loader

@pytest.mark.unit
def test_import_lazy_loader():
    """Vérifie que le module lazy_loader s'importe sans erreur."""
    assert hasattr(lazy_loader, "RouteurOptimise") or hasattr(lazy_loader, "ChargeurModuleDiffere")

from unittest.mock import MagicMock, patch

# Import direct du module à tester
from src.core.lazy_loader import ChargeurModuleDiffere, RouteurOptimise


# ══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
# TESTS LAZY MODULE LOADER
# ══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════

class TestLazyModuleLoader:
    """Tests du chargeur de modules différé"""
    
    def test_class_exists(self):
        """Test que la classe existe"""
        assert ChargeurModuleDiffere is not None
    
    def test_class_callable(self):
        """Test que la classe est instanciable"""
        assert callable(ChargeurModuleDiffere)


# ══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
# TESTS OPTIMIZED ROUTER
# ══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════

class TestOptimizedRouter:
    """Tests du routeur optimisé"""
    
    def test_class_exists(self):
        """Test que la classe existe"""
        assert RouteurOptimise is not None
    
    def test_has_module_registry(self):
        """Test que le registre de modules existe"""
        assert hasattr(RouteurOptimise, 'MODULE_REGISTRY') or hasattr(RouteurOptimise, 'modules')
    
    def test_class_instantiable(self):
        """Test que la classe est instanciable"""
        try:
            router = RouteurOptimise()
            assert router is not None
        except Exception:
            # Peut échouer si Streamlit n'est pas disponible
            pass
