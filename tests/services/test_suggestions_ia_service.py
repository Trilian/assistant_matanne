import pytest
import importlib

@pytest.mark.unit
def test_import_suggestions_ia_service():
    """Vérifie que le module suggestions_ia s'importe sans erreur."""
    module = importlib.import_module("src.services.suggestions_ia")
    assert module is not None

# Ajoutez ici des tests pour les fonctions principales du service
