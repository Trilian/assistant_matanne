import pytest
import importlib

@pytest.mark.unit
def test_import_courses_ui():
    """Vérifie que le module courses UI s'importe sans erreur."""
    module = importlib.import_module("src.modules.cuisine.courses")
    assert module is not None

# Ajoutez ici des tests de rendu Streamlit, logique de composants, etc.
