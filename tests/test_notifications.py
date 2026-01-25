"""
Tests pour le module notifications (notifications.py).

Tests couverts:
- Notification dataclass
- NotificationManager (CRUD, filtres, persistance)
- Helpers (notify_info, notify_success, etc.)
- Notifications spécialisées (stock, péremption)
"""

from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest


# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def mock_session_state():
    """Mock streamlit session_state."""
    state = {}
    with patch("streamlit.session_state", state):
        yield state


@pytest.fixture
def notification_manager(mock_session_state):
    """Instance NotificationManager fraîche."""
    from src.core.notifications import NotificationManager
    
    # Reset singleton-like behavior
    mock_session_state.clear()
    manager = NotificationManager()
    yield manager


# ═══════════════════════════════════════════════════════════
# TESTS NOTIFICATION DATACLASS
# ═══════════════════════════════════════════════════════════


class TestNotificationDataclass:
    """Tests pour la dataclass Notification."""
    
    def test_create_notification(self):
        """Test création basique."""
        from src.core.notifications import Notification, NotificationType
        
        notif = Notification(
            type=NotificationType.INFO,
            message="Test message",
        )
        
        assert notif.message == "Test message"
        assert notif.type == NotificationType.INFO
        assert notif.id is not None
        assert notif.read is False
        assert notif.created_at is not None
    
    def test_notification_with_all_fields(self):
        """Test création avec tous les champs."""
        from src.core.notifications import Notification, NotificationType
        
        notif = Notification(
            type=NotificationType.WARNING,
            message="Alert!",
            title="Important",
            action_url="/settings",
            action_label="Configure",
            data={"key": "value"},
        )
        
        assert notif.title == "Important"
        assert notif.action_url == "/settings"
        assert notif.data["key"] == "value"
    
    def test_notification_to_dict(self):
        """Test sérialisation en dict."""
        from src.core.notifications import Notification, NotificationType
        
        notif = Notification(
            type=NotificationType.SUCCESS,
            message="Done!",
        )
        
        data = notif.to_dict()
        
        assert data["message"] == "Done!"
        assert data["type"] == "success"
        assert "id" in data
        assert "created_at" in data
    
    def test_notification_from_dict(self):
        """Test désérialisation depuis dict."""
        from src.core.notifications import Notification, NotificationType
        
        data = {
            "id": "test-123",
            "type": "error",
            "message": "Error occurred",
            "read": True,
            "created_at": datetime.now().isoformat(),
        }
        
        notif = Notification.from_dict(data)
        
        assert notif.id == "test-123"
        assert notif.type == NotificationType.ERROR
        assert notif.message == "Error occurred"
        assert notif.read is True


# ═══════════════════════════════════════════════════════════
# TESTS NOTIFICATION MANAGER
# ═══════════════════════════════════════════════════════════


class TestNotificationManager:
    """Tests pour NotificationManager."""
    
    def test_add_notification(self, notification_manager):
        """Test ajout notification."""
        from src.core.notifications import NotificationType
        
        notif = notification_manager.add(
            type=NotificationType.INFO,
            message="Test notification",
        )
        
        assert notif.id is not None
        assert notification_manager.count() == 1
    
    def test_add_multiple(self, notification_manager):
        """Test ajout plusieurs notifications."""
        from src.core.notifications import NotificationType
        
        notification_manager.add(NotificationType.INFO, "First")
        notification_manager.add(NotificationType.WARNING, "Second")
        notification_manager.add(NotificationType.ERROR, "Third")
        
        assert notification_manager.count() == 3
    
    def test_get_all(self, notification_manager):
        """Test récupération de toutes les notifications."""
        from src.core.notifications import NotificationType
        
        notification_manager.add(NotificationType.INFO, "Info")
        notification_manager.add(NotificationType.SUCCESS, "Success")
        
        all_notifs = notification_manager.get_all()
        
        assert len(all_notifs) == 2
    
    def test_get_unread(self, notification_manager):
        """Test récupération non lues."""
        from src.core.notifications import NotificationType
        
        notif1 = notification_manager.add(NotificationType.INFO, "Unread 1")
        notif2 = notification_manager.add(NotificationType.INFO, "Unread 2")
        
        # Marquer une comme lue
        notification_manager.mark_as_read(notif1.id)
        
        unread = notification_manager.get_unread()
        
        assert len(unread) == 1
        assert unread[0].message == "Unread 2"
    
    def test_get_by_type(self, notification_manager):
        """Test filtrage par type."""
        from src.core.notifications import NotificationType
        
        notification_manager.add(NotificationType.INFO, "Info")
        notification_manager.add(NotificationType.WARNING, "Warning")
        notification_manager.add(NotificationType.INFO, "Info 2")
        
        infos = notification_manager.get_by_type(NotificationType.INFO)
        
        assert len(infos) == 2
    
    def test_mark_as_read(self, notification_manager):
        """Test marquer comme lu."""
        from src.core.notifications import NotificationType
        
        notif = notification_manager.add(NotificationType.INFO, "To read")
        
        assert notif.read is False
        
        notification_manager.mark_as_read(notif.id)
        
        updated = notification_manager.get_by_id(notif.id)
        assert updated.read is True
    
    def test_mark_all_as_read(self, notification_manager):
        """Test marquer toutes comme lues."""
        from src.core.notifications import NotificationType
        
        notification_manager.add(NotificationType.INFO, "N1")
        notification_manager.add(NotificationType.INFO, "N2")
        notification_manager.add(NotificationType.INFO, "N3")
        
        notification_manager.mark_all_as_read()
        
        unread = notification_manager.get_unread()
        assert len(unread) == 0
    
    def test_delete(self, notification_manager):
        """Test suppression."""
        from src.core.notifications import NotificationType
        
        notif = notification_manager.add(NotificationType.INFO, "To delete")
        
        result = notification_manager.delete(notif.id)
        
        assert result is True
        assert notification_manager.count() == 0
    
    def test_delete_nonexistent(self, notification_manager):
        """Test suppression inexistante."""
        result = notification_manager.delete("nonexistent-id")
        assert result is False
    
    def test_clear_all(self, notification_manager):
        """Test vidage complet."""
        from src.core.notifications import NotificationType
        
        notification_manager.add(NotificationType.INFO, "N1")
        notification_manager.add(NotificationType.INFO, "N2")
        
        count = notification_manager.clear_all()
        
        assert count == 2
        assert notification_manager.count() == 0
    
    def test_clear_read(self, notification_manager):
        """Test suppression des lues seulement."""
        from src.core.notifications import NotificationType
        
        notif1 = notification_manager.add(NotificationType.INFO, "Read")
        notification_manager.add(NotificationType.INFO, "Unread")
        
        notification_manager.mark_as_read(notif1.id)
        
        count = notification_manager.clear_read()
        
        assert count == 1
        assert notification_manager.count() == 1
    
    def test_max_notifications(self, mock_session_state):
        """Test limite max notifications."""
        from src.core.notifications import NotificationManager, NotificationType
        
        manager = NotificationManager(max_notifications=5)
        
        # Ajouter plus que la limite
        for i in range(7):
            manager.add(NotificationType.INFO, f"Notification {i}")
        
        # Doit garder seulement les 5 plus récentes
        assert manager.count() == 5
    
    def test_unread_count(self, notification_manager):
        """Test compteur non lues."""
        from src.core.notifications import NotificationType
        
        notification_manager.add(NotificationType.INFO, "N1")
        notif2 = notification_manager.add(NotificationType.INFO, "N2")
        notification_manager.add(NotificationType.INFO, "N3")
        
        notification_manager.mark_as_read(notif2.id)
        
        assert notification_manager.unread_count() == 2


# ═══════════════════════════════════════════════════════════
# TESTS HELPERS
# ═══════════════════════════════════════════════════════════


class TestNotificationHelpers:
    """Tests pour les fonctions helper."""
    
    def test_notify_info(self, mock_session_state):
        """Test notify_info."""
        from src.core.notifications import notify_info, NotificationType
        
        notif = notify_info("Info message")
        
        assert notif.type == NotificationType.INFO
        assert notif.message == "Info message"
    
    def test_notify_success(self, mock_session_state):
        """Test notify_success."""
        from src.core.notifications import notify_success, NotificationType
        
        notif = notify_success("Success!", title="Bravo")
        
        assert notif.type == NotificationType.SUCCESS
        assert notif.title == "Bravo"
    
    def test_notify_warning(self, mock_session_state):
        """Test notify_warning."""
        from src.core.notifications import notify_warning, NotificationType
        
        notif = notify_warning("Warning!")
        
        assert notif.type == NotificationType.WARNING
    
    def test_notify_error(self, mock_session_state):
        """Test notify_error."""
        from src.core.notifications import notify_error, NotificationType
        
        notif = notify_error("Error occurred")
        
        assert notif.type == NotificationType.ERROR


# ═══════════════════════════════════════════════════════════
# TESTS NOTIFICATIONS SPÉCIALISÉES
# ═══════════════════════════════════════════════════════════


class TestSpecializedNotifications:
    """Tests pour les notifications spécialisées."""
    
    def test_notify_stock_bas(self, mock_session_state):
        """Test notification stock bas."""
        from src.core.notifications import notify_stock_bas, NotificationType
        
        notif = notify_stock_bas("Tomates", 2, 5)
        
        assert notif.type == NotificationType.WARNING
        assert "Tomates" in notif.message
        assert "2" in notif.message
    
    def test_notify_peremption(self, mock_session_state):
        """Test notification péremption."""
        from src.core.notifications import notify_peremption, NotificationType
        
        notif = notify_peremption("Yaourt", days_remaining=2)
        
        assert notif.type == NotificationType.WARNING
        assert "Yaourt" in notif.message
        assert "2" in notif.message
    
    def test_notify_peremption_urgent(self, mock_session_state):
        """Test notification péremption urgente."""
        from src.core.notifications import notify_peremption, NotificationType
        
        notif = notify_peremption("Lait", days_remaining=0)
        
        # Péremption immédiate = erreur
        assert notif.type == NotificationType.ERROR


# ═══════════════════════════════════════════════════════════
# TESTS PERSISTENCE
# ═══════════════════════════════════════════════════════════


class TestNotificationPersistence:
    """Tests persistance des notifications."""
    
    def test_session_persistence(self, mock_session_state):
        """Test persistance dans session_state."""
        from src.core.notifications import NotificationManager, NotificationType
        
        # Première instance
        manager1 = NotificationManager()
        manager1.add(NotificationType.INFO, "Persisted")
        
        # Deuxième instance (même session)
        manager2 = NotificationManager()
        
        # Doit voir la même notification
        assert manager2.count() == 1
        assert manager2.get_all()[0].message == "Persisted"


# ═══════════════════════════════════════════════════════════
# TESTS EDGE CASES
# ═══════════════════════════════════════════════════════════


class TestNotificationEdgeCases:
    """Tests cas limites."""
    
    def test_empty_message(self, notification_manager):
        """Test message vide."""
        from src.core.notifications import NotificationType
        
        notif = notification_manager.add(NotificationType.INFO, "")
        assert notif.message == ""
    
    def test_very_long_message(self, notification_manager):
        """Test message très long."""
        from src.core.notifications import NotificationType
        
        long_message = "A" * 10000
        notif = notification_manager.add(NotificationType.INFO, long_message)
        
        assert len(notif.message) == 10000
    
    def test_special_characters(self, notification_manager):
        """Test caractères spéciaux."""
        from src.core.notifications import NotificationType
        
        special_msg = "Émojis: 🎉 Accents: éàü Symboles: <>&\""
        notif = notification_manager.add(NotificationType.INFO, special_msg)
        
        assert notif.message == special_msg
    
    def test_get_nonexistent_id(self, notification_manager):
        """Test get avec ID inexistant."""
        result = notification_manager.get_by_id("nonexistent")
        assert result is None
    
    def test_ordering(self, notification_manager):
        """Test ordre des notifications (plus récentes en premier)."""
        from src.core.notifications import NotificationType
        import time
        
        notification_manager.add(NotificationType.INFO, "First")
        time.sleep(0.01)
        notification_manager.add(NotificationType.INFO, "Second")
        time.sleep(0.01)
        notification_manager.add(NotificationType.INFO, "Third")
        
        all_notifs = notification_manager.get_all()
        
        # Plus récentes en premier
        assert all_notifs[0].message == "Third"
        assert all_notifs[2].message == "First"
