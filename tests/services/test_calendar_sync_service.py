import pytest
import importlib

@pytest.mark.unit
def test_import_calendar_sync_service():
    """Vérifie que le module calendar_sync s'importe sans erreur."""
    module = importlib.import_module("src.services.calendar_sync")
    assert module is not None

# Ajoutez ici des tests pour les fonctions principales du service
