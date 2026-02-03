import pytest
import importlib

@pytest.mark.unit
def test_import_spinners_feedback():
    """Vérifie que le module spinners feedback s'importe sans erreur."""
    module = importlib.import_module("src.ui.feedback.spinners")
    assert module is not None

# Ajoutez ici des tests pour le feedback des spinners
