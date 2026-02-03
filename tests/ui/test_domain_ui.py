import pytest
import importlib

@pytest.mark.unit
def test_import_domain_ui():
    """Vérifie que le module domain UI s'importe sans erreur."""
    module = importlib.import_module("src.ui.domain")
    assert module is not None

# Ajoutez ici des tests pour le module UI domain
