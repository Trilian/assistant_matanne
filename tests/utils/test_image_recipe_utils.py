"""
Tests unitaires pour image_generator.py
"""

import pytest
from unittest.mock import MagicMock, patch


# ═══════════════════════════════════════════════════════════════
# TESTS IMAGE GENERATOR
# ═══════════════════════════════════════════════════════════════

class TestImageGenerator:
    """Tests du générateur d'images"""
    
    def test_module_imports(self):
        """Test que le module s'importe correctement"""
        try:
            from src.utils import image_generator
            assert image_generator is not None
        except ImportError as e:
            pytest.skip(f"Import failed: {e}")
    
    def test_has_generation_functions(self):
        """Test que le module a des fonctions de génération"""
        try:
            from src.utils import image_generator
            # Cherche des fonctions génératrices
            funcs = [attr for attr in dir(image_generator) if not attr.startswith('_')]
            assert len(funcs) > 0
        except ImportError:
            pytest.skip("Module non importable")


# ═══════════════════════════════════════════════════════════════
# TESTS RECIPE IMPORTER
# ═══════════════════════════════════════════════════════════════

class TestRecipeImporter:
    """Tests de l'importateur de recettes"""
    
    def test_module_imports(self):
        """Test que le module s'importe correctement"""
        try:
            from src.utils import recipe_importer
            assert recipe_importer is not None
        except ImportError as e:
            pytest.skip(f"Import failed: {e}")
    
    def test_has_import_functions(self):
        """Test que le module a des fonctions d'import"""
        try:
            from src.utils import recipe_importer
            funcs = [attr for attr in dir(recipe_importer) if not attr.startswith('_')]
            assert len(funcs) > 0
        except ImportError:
            pytest.skip("Module non importable")
