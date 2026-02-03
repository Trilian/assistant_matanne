import pytest
import importlib

@pytest.mark.unit
def test_import_inventaire_service():
    """Vérifie que le module inventaire s'importe sans erreur."""
    module = importlib.import_module("src.services.inventaire")
    assert module is not None

# Ajoutez ici des tests pour les fonctions principales du service
