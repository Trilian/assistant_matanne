import pytest
import importlib

@pytest.mark.unit
def test_import_batch_cooking_service():
    """Vérifie que le module batch_cooking s'importe sans erreur."""
    module = importlib.import_module("src.services.batch_cooking")
    assert module is not None

# Ajoutez ici des tests pour les fonctions principales du service
