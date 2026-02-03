import pytest
import importlib

@pytest.mark.unit
def test_import_dashboard_widgets_component():
    """Vérifie que le module dashboard_widgets s'importe sans erreur."""
    module = importlib.import_module("src.ui.components.dashboard_widgets")
    assert module is not None

# Ajoutez ici des tests pour les widgets du tableau de bord
