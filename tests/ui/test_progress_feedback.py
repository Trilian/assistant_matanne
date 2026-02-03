import pytest
import importlib

@pytest.mark.unit
def test_import_progress_feedback():
    """Vérifie que le module progress feedback s'importe sans erreur."""
    module = importlib.import_module("src.ui.feedback.progress")
    assert module is not None

# Ajoutez ici des tests pour le feedback de progression
