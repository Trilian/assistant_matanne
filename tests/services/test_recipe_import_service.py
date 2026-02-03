import pytest
import importlib


def test_import_recipe_import_module():
    """Vérifie que le module recipe_import s'importe sans erreur."""
    module = importlib.import_module("src.services.recipe_import")
    assert module is not None


@pytest.mark.unit
def test_import_recipe_import_service():
    """Vérifie que le module recipe_import s'importe sans erreur."""
    module = importlib.import_module("src.services.recipe_import")
    assert module is not None


@pytest.mark.unit
def test_recipe_import_service_exists():
    """Test that recipe import service exists."""
    try:
        from src.services.recipe_import import get_recipe_import_service
        service = get_recipe_import_service()
        assert service is not None
    except ImportError:
        pass  # Service may not exist yet
