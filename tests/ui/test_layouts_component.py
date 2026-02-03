import pytest
import importlib

@pytest.mark.unit
def test_import_layouts_component():
    """Vérifie que le module layouts s'importe sans erreur."""
    module = importlib.import_module("src.ui.components.layouts")
    assert module is not None

# Ajoutez ici des tests pour le composant layouts
