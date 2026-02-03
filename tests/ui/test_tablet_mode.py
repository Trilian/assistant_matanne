import pytest
import importlib

@pytest.mark.unit
def test_import_tablet_mode():
    """Vérifie que le module tablet_mode s'importe sans erreur."""
    module = importlib.import_module("src.ui.tablet_mode")
    assert module is not None

# Ajoutez ici des tests pour le mode tablette
