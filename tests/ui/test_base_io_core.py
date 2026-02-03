import pytest
import importlib

@pytest.mark.unit
def test_import_base_io_core():
    """Vérifie que le module base_io core s'importe sans erreur."""
    module = importlib.import_module("src.ui.core.base_io")
    assert module is not None

# Ajoutez ici des tests pour le core IO
