import pytest
import importlib

@pytest.mark.unit
def test_import_planning_service():
    """Vérifie que le module planning s'importe sans erreur."""
    module = importlib.import_module("src.services.planning")
    assert module is not None

# Ajoutez ici des tests pour les fonctions principales du service
