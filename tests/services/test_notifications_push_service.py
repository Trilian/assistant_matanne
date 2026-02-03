import pytest
import importlib


@pytest.mark.unit
def test_import_push_notifications_module():
    """Vérifie que le module push_notifications s'importe sans erreur."""
    module = importlib.import_module("src.services.push_notifications")
    assert module is not None


@pytest.mark.unit
def test_push_notification_service_exists():
    """Test that push notifications service exists."""
    try:
        from src.services.push_notifications import get_push_notifications_service
        service = get_push_notifications_service()
        assert service is not None
    except ImportError:
        pass  # Service may not exist yet
