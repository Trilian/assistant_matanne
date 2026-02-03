import pytest
import importlib

@pytest.mark.unit
def test_import_footer_layout():
    """Vérifie que le module footer layout s'importe sans erreur."""
    module = importlib.import_module("src.ui.layout.footer")
    assert module is not None

# Ajoutez ici des tests pour le layout footer
