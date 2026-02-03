import pytest
import importlib

@pytest.mark.unit
def test_import_notifications_push_module():
def test_import_push_notifications_module():
    """Vérifie que le module push_notifications s'importe sans erreur."""
    module = importlib.import_module("src.services.push_notifications")
    assert module is not None

# Ajoutez ici des tests pour les fonctions principales du service
