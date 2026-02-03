import pytest
import importlib

@pytest.mark.unit
def test_import_io_service():
    """Vérifie que le module io_service s'importe sans erreur."""
    module = importlib.import_module("src.services.io_service")
    assert module is not None

# Ajoutez ici des tests pour les fonctions principales du service
