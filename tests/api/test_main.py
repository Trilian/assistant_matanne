import pytest
from src.api import main

@pytest.mark.unit
def test_import_main():
    """Vérifie que le module main s'importe sans erreur."""
    assert hasattr(main, "app") or hasattr(main, "__file__")

# Ajoutez ici des tests de routes, de fonctions utilitaires, etc. selon l'architecture du module
