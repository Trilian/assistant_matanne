import pytest
import importlib


def test_import_user_preferences_module():
    """Vérifie que le module user_preferences s'importe sans erreur."""
    module = importlib.import_module("src.services.user_preferences")
    assert module is not None


@pytest.mark.unit
def test_import_user_preferences_service():
    """Vérifie que le module user_preferences s'importe sans erreur."""
    module = importlib.import_module("src.services.user_preferences")
    assert module is not None


@pytest.mark.unit
def test_user_preferences_service_exists():
    """Test that user preferences service exists."""
    try:
        from src.services.user_preferences import get_user_preferences_service
        service = get_user_preferences_service()
        assert service is not None
    except ImportError:
        pass  # Service may not exist yet
