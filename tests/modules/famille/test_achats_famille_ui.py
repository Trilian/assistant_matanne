import pytest
import importlib

@pytest.mark.unit
def test_import_achats_famille_ui():
    """Vérifie que le module achats_famille UI s'importe sans erreur."""
    module = importlib.import_module("src.modules.famille.achats_famille")
    assert module is not None

# Ajoutez ici des tests de rendu Streamlit, logique de composants, etc.
