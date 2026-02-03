import pytest
import importlib

@pytest.mark.unit
def test_import_planning_unified_service():
    """Vérifie que le module planning_unified s'importe sans erreur."""
    module = importlib.import_module("src.services.planning_unified")
    assert module is not None

# Ajoutez ici des tests pour les fonctions principales du service
