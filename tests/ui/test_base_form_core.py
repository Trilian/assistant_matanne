import pytest
import importlib

@pytest.mark.unit
def test_import_base_form_core():
    """Vérifie que le module base_form core s'importe sans erreur."""
    module = importlib.import_module("src.ui.core.base_form")
    assert module is not None

# Ajoutez ici des tests pour le core des formulaires
