import pytest
import importlib

@pytest.mark.unit
def test_import_toasts_feedback():
    """Vérifie que le module toasts feedback s'importe sans erreur."""
    module = importlib.import_module("src.ui.feedback.toasts")
    assert module is not None

# Ajoutez ici des tests pour le feedback des toasts
