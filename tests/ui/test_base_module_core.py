import pytest
import importlib

@pytest.mark.unit
def test_import_base_module_core():
    """Vérifie que le module base_module core s'importe sans erreur."""
    module = importlib.import_module("src.ui.core.base_module")
    assert module is not None

# Ajoutez ici des tests pour le core des modules
