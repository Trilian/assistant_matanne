import pytest
import importlib

@pytest.mark.unit
def test_import_inventaire_ui():
    """Vérifie que le module inventaire UI s'importe sans erreur."""
    module = importlib.import_module("src.modules.cuisine.inventaire")
    assert module is not None

# Ajoutez ici des tests de rendu Streamlit, logique de composants, etc.
