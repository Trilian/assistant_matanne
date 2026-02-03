import pytest
import importlib

@pytest.mark.unit
def test_import_data_component():
    """Vérifie que le module data s'importe sans erreur."""
    module = importlib.import_module("src.ui.components.data")
    assert module is not None

# Ajoutez ici des tests pour le composant data
