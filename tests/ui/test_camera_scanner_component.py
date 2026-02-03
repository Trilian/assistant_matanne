import pytest
import importlib

@pytest.mark.unit
def test_import_camera_scanner_component():
    """Vérifie que le module camera_scanner s'importe sans erreur."""
    module = importlib.import_module("src.ui.components.camera_scanner")
    assert module is not None

# Ajoutez ici des tests pour le composant de scan caméra
