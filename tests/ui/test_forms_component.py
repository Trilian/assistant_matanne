import pytest
import importlib

@pytest.mark.unit
def test_import_forms_component():
    """Vérifie que le module forms s'importe sans erreur."""
    module = importlib.import_module("src.ui.components.forms")
    assert module is not None

# Ajoutez ici des tests pour le composant forms
