import importlib

import pytest


@pytest.mark.unit
def test_import_batch_cooking_detaille_ui():
    """Vérifie que le module batch_cooking_detaille s'importe sans erreur."""
    module = importlib.import_module("src.modules.cuisine.batch_cooking_detaille")
    assert module is not None


# Ajoutez ici des tests de rendu Streamlit, logique de composants, etc.
