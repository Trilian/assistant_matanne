import pytest
import importlib

@pytest.mark.unit
def test_import_google_calendar_sync_component():
    """Vérifie que le module google_calendar_sync s'importe sans erreur."""
    module = importlib.import_module("src.ui.components.google_calendar_sync")
    assert module is not None

# Ajoutez ici des tests pour le composant Google Calendar Sync
