import pytest
import importlib

@pytest.mark.unit
def test_import_sidebar_layout():
    """Vérifie que le module sidebar layout s'importe sans erreur."""
    module = importlib.import_module("src.ui.layout.sidebar")
    assert module is not None

# Ajoutez ici des tests pour le layout sidebar
