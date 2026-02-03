import pytest
import importlib

@pytest.mark.unit
def test_import_types_service():
    """Vérifie que le module types s'importe sans erreur."""
    module = importlib.import_module("src.services.types")
    assert module is not None

# Ajoutez ici des tests pour les fonctions principales du service
