import pytest
import importlib

@pytest.mark.unit
def test_import_atoms_component():
    """Vérifie que le module atoms s'importe sans erreur."""
    module = importlib.import_module("src.ui.components.atoms")
    assert module is not None

# Ajoutez ici des tests pour les composants atomiques UI
