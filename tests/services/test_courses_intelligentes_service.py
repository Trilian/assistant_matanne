import pytest
import importlib

@pytest.mark.unit
def test_import_courses_intelligentes_service():
    """Vérifie que le module courses_intelligentes s'importe sans erreur."""
    module = importlib.import_module("src.services.courses_intelligentes")
    assert module is not None

# Ajoutez ici des tests pour les fonctions principales du service
