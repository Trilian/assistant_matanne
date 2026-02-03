import pytest
import importlib

@pytest.mark.unit
def test_import_action_history_service():
    """Vérifie que le module action_history s'importe sans erreur."""
    module = importlib.import_module("src.services.action_history")
    assert module is not None

# Ajoutez ici des tests pour les fonctions principales du service
