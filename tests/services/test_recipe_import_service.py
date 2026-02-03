import pytest
import importlib

@pytest.mark.unit
def test_import_recipe_import_service():
    """Vérifie que le module recipe_import s'importe sans erreur."""
    module = importlib.import_module("src.services.recipe_import")
    assert module is not None

# Ajoutez ici des tests pour les fonctions principales du service
