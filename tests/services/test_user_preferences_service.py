import pytest
import importlib

@pytest.mark.unit
def test_import_user_preferences_service():
    """Vérifie que le module user_preferences s'importe sans erreur."""
    module = importlib.import_module("src.services.user_preferences")
    assert module is not None

# Ajoutez ici des tests pour les fonctions principales du service
