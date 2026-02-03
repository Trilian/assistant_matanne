import pytest
import importlib

@pytest.mark.unit
def test_import_backup_service():
    """Vérifie que le module backup s'importe sans erreur."""
    module = importlib.import_module("src.services.backup")
    assert module is not None

# Ajoutez ici des tests pour les fonctions principales du service
