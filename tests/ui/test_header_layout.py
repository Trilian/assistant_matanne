import pytest
import importlib

@pytest.mark.unit
def test_import_header_layout():
    """Vérifie que le module header layout s'importe sans erreur."""
    module = importlib.import_module("src.ui.layout.header")
    assert module is not None

# Ajoutez ici des tests pour le layout header
