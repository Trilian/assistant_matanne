import pytest
import importlib

@pytest.mark.unit
def test_import_notifications_service():
    """Vérifie que le module notifications s'importe sans erreur."""
    module = importlib.import_module("src.services.notifications")
    assert module is not None

# Ajoutez ici des tests pour les fonctions principales du service
