import pytest
import importlib

@pytest.mark.unit
def test_import_predictions_service():
    """Vérifie que le module predictions s'importe sans erreur."""
    module = importlib.import_module("src.services.predictions")
    assert module is not None

# Ajoutez ici des tests pour les fonctions principales du service
