import pytest
import importlib

@pytest.mark.unit
def test_import_dynamic_component():
    """Vérifie que le module dynamic s'importe sans erreur."""
    module = importlib.import_module("src.ui.components.dynamic")
    assert module is not None

# Ajoutez ici des tests pour le composant dynamic
