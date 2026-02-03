import pytest
import importlib

@pytest.mark.unit
def test_import_base_ai_service():
    """Vérifie que le module base_ai_service s'importe sans erreur."""
    module = importlib.import_module("src.services.base_ai_service")
    assert module is not None

# Ajoutez ici des tests pour les fonctions principales du service
