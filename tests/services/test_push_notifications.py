"""
Tests pour le service de notifications push.

Couvre:
- NotificationType (enum)
- PushSubscription (modèle Pydantic)
- PushNotification (modèle Pydantic)
- NotificationPreferences (modèle Pydantic)
- PushNotificationService (service)
"""

import pytest
from datetime import datetime, time
from unittest.mock import MagicMock, patch

from src.services.push_notifications import (
    NotificationType,
    PushSubscription,
    PushNotification,
    NotificationPreferences,
    PushNotificationService,
    VAPID_PUBLIC_KEY,
    VAPID_EMAIL,
)


# ═══════════════════════════════════════════════════════════
# TESTS CONFIGURATION
# ═══════════════════════════════════════════════════════════


class TestConfiguration:
    """Tests pour la configuration VAPID."""
    
    def test_vapid_public_key_exists(self):
        assert VAPID_PUBLIC_KEY is not None
        assert len(VAPID_PUBLIC_KEY) > 0
    
    def test_vapid_email_format(self):
        assert "mailto:" in VAPID_EMAIL


# ═══════════════════════════════════════════════════════════
# TESTS ENUM NOTIFICATION TYPE
# ═══════════════════════════════════════════════════════════


class TestNotificationType:
    """Tests pour l'enum NotificationType."""
    
    def test_stock_low(self):
        assert NotificationType.STOCK_LOW.value == "stock_low"
    
    def test_expiration_warning(self):
        assert NotificationType.EXPIRATION_WARNING.value == "expiration_warning"
    
    def test_expiration_critical(self):
        assert NotificationType.EXPIRATION_CRITICAL.value == "expiration_critical"
    
    def test_meal_reminder(self):
        assert NotificationType.MEAL_REMINDER.value == "meal_reminder"
    
    def test_activity_reminder(self):
        assert NotificationType.ACTIVITY_REMINDER.value == "activity_reminder"
    
    def test_shopping_list_shared(self):
        assert NotificationType.SHOPPING_LIST_SHARED.value == "shopping_list_shared"
    
    def test_shopping_list_updated(self):
        assert NotificationType.SHOPPING_LIST_UPDATED.value == "shopping_list_updated"
    
    def test_milestone_reminder(self):
        assert NotificationType.MILESTONE_REMINDER.value == "milestone_reminder"
    
    def test_health_check_reminder(self):
        assert NotificationType.HEALTH_CHECK_REMINDER.value == "health_check_reminder"
    
    def test_system_update(self):
        assert NotificationType.SYSTEM_UPDATE.value == "system_update"
    
    def test_sync_complete(self):
        assert NotificationType.SYNC_COMPLETE.value == "sync_complete"


# ═══════════════════════════════════════════════════════════
# TESTS PUSH SUBSCRIPTION
# ═══════════════════════════════════════════════════════════


class TestPushSubscription:
    """Tests pour le modèle PushSubscription."""
    
    def test_create_subscription(self):
        sub = PushSubscription(
            user_id="user123",
            endpoint="https://example.com/push/123",
            p256dh_key="keydata",
            auth_key="authdata",
        )
        assert sub.user_id == "user123"
        assert sub.endpoint == "https://example.com/push/123"
    
    def test_subscription_defaults(self):
        sub = PushSubscription(
            user_id="user",
            endpoint="endpoint",
            p256dh_key="key",
            auth_key="auth",
        )
        assert sub.id is None
        assert sub.user_agent is None
        assert sub.last_used is None
        assert sub.is_active is True
    
    def test_subscription_with_user_agent(self):
        sub = PushSubscription(
            user_id="user",
            endpoint="endpoint",
            p256dh_key="key",
            auth_key="auth",
            user_agent="Chrome/120",
        )
        assert sub.user_agent == "Chrome/120"
    
    def test_subscription_inactive(self):
        sub = PushSubscription(
            user_id="user",
            endpoint="endpoint",
            p256dh_key="key",
            auth_key="auth",
            is_active=False,
        )
        assert sub.is_active is False


# ═══════════════════════════════════════════════════════════
# TESTS PUSH NOTIFICATION
# ═══════════════════════════════════════════════════════════


class TestPushNotification:
    """Tests pour le modèle PushNotification."""
    
    def test_create_notification(self):
        notif = PushNotification(
            title="Test Title",
            body="Test Body",
        )
        assert notif.title == "Test Title"
        assert notif.body == "Test Body"
    
    def test_notification_defaults(self):
        notif = PushNotification(title="Title", body="Body")
        assert notif.icon == "/static/icons/icon-192x192.png"
        assert notif.badge == "/static/icons/badge-72x72.png"
        assert notif.notification_type == NotificationType.SYSTEM_UPDATE
        assert notif.url == "/"
        assert notif.silent is False
        assert notif.require_interaction is False
    
    def test_notification_with_type(self):
        notif = PushNotification(
            title="Stock Alert",
            body="Lait is running low",
            notification_type=NotificationType.STOCK_LOW,
        )
        assert notif.notification_type == NotificationType.STOCK_LOW
    
    def test_notification_with_custom_vibrate(self):
        notif = PushNotification(
            title="Title",
            body="Body",
            vibrate=[200, 100, 200, 100, 200],
        )
        assert len(notif.vibrate) == 5
    
    def test_notification_with_actions(self):
        notif = PushNotification(
            title="Title",
            body="Body",
            actions=[
                {"action": "view", "title": "View"},
                {"action": "dismiss", "title": "Dismiss"},
            ],
        )
        assert len(notif.actions) == 2
    
    def test_notification_with_data(self):
        notif = PushNotification(
            title="Title",
            body="Body",
            data={"key": "value", "id": 123},
        )
        assert notif.data["key"] == "value"
        assert notif.data["id"] == 123
    
    def test_notification_silent_mode(self):
        notif = PushNotification(
            title="Background sync",
            body="Synced",
            silent=True,
        )
        assert notif.silent is True


# ═══════════════════════════════════════════════════════════
# TESTS NOTIFICATION PREFERENCES
# ═══════════════════════════════════════════════════════════


class TestNotificationPreferences:
    """Tests pour le modèle NotificationPreferences."""
    
    def test_create_preferences(self):
        prefs = NotificationPreferences(user_id="user123")
        assert prefs.user_id == "user123"
    
    def test_preferences_defaults(self):
        prefs = NotificationPreferences(user_id="user")
        assert prefs.stock_alerts is True
        assert prefs.expiration_alerts is True
        assert prefs.meal_reminders is True
        assert prefs.activity_reminders is True
        assert prefs.shopping_updates is True
        assert prefs.family_reminders is True
        assert prefs.system_updates is False  # Désactivé par défaut
    
    def test_preferences_quiet_hours(self):
        prefs = NotificationPreferences(user_id="user")
        assert prefs.quiet_hours_start == 22
        assert prefs.quiet_hours_end == 7
    
    def test_preferences_custom_quiet_hours(self):
        prefs = NotificationPreferences(
            user_id="user",
            quiet_hours_start=23,
            quiet_hours_end=8,
        )
        assert prefs.quiet_hours_start == 23
        assert prefs.quiet_hours_end == 8
    
    def test_preferences_max_per_hour(self):
        prefs = NotificationPreferences(user_id="user")
        assert prefs.max_per_hour == 5
    
    def test_preferences_digest_mode(self):
        prefs = NotificationPreferences(
            user_id="user",
            digest_mode=True,
        )
        assert prefs.digest_mode is True
    
    def test_preferences_all_disabled(self):
        prefs = NotificationPreferences(
            user_id="user",
            stock_alerts=False,
            expiration_alerts=False,
            meal_reminders=False,
            activity_reminders=False,
            shopping_updates=False,
            family_reminders=False,
        )
        assert prefs.stock_alerts is False
        assert prefs.family_reminders is False


# ═══════════════════════════════════════════════════════════
# TESTS PUSH NOTIFICATION SERVICE
# ═══════════════════════════════════════════════════════════


class TestPushNotificationService:
    """Tests pour le service PushNotificationService."""
    
    @pytest.fixture
    def service(self):
        return PushNotificationService()
    
    def test_init(self, service):
        assert service._subscriptions == {}
        assert service._preferences == {}
        assert service._sent_count == {}
    
    def test_save_subscription(self, service):
        sub_info = {
            "endpoint": "https://push.example.com/123",
            "keys": {
                "p256dh": "key_p256dh",
                "auth": "key_auth",
            }
        }
        
        with patch.object(service, '_save_subscription_to_db'):
            result = service.save_subscription("user1", sub_info)
        
        assert result.user_id == "user1"
        assert result.endpoint == "https://push.example.com/123"
        assert "user1" in service._subscriptions
    
    def test_save_subscription_duplicate(self, service):
        sub_info = {
            "endpoint": "https://push.example.com/123",
            "keys": {
                "p256dh": "key_p256dh",
                "auth": "key_auth",
            }
        }
        
        with patch.object(service, '_save_subscription_to_db'):
            service.save_subscription("user1", sub_info)
            # Deuxième appel avec même endpoint
            service.save_subscription("user1", sub_info)
        
        # Ne devrait pas dupliquer
        assert len(service._subscriptions["user1"]) == 1
    
    def test_remove_subscription(self, service):
        sub_info = {
            "endpoint": "https://push.example.com/123",
            "keys": {
                "p256dh": "key_p256dh",
                "auth": "key_auth",
            }
        }
        
        with patch.object(service, '_save_subscription_to_db'):
            service.save_subscription("user1", sub_info)
        
        with patch.object(service, '_remove_subscription_from_db'):
            service.remove_subscription("user1", "https://push.example.com/123")
        
        assert len(service._subscriptions["user1"]) == 0
    
    def test_remove_subscription_nonexistent_user(self, service):
        with patch.object(service, '_remove_subscription_from_db'):
            # Ne devrait pas lever d'exception
            service.remove_subscription("nonexistent", "endpoint")


class TestPushNotificationServiceMethods:
    """Tests pour les méthodes du service."""
    
    @pytest.fixture
    def service(self):
        return PushNotificationService()
    
    def test_has_subscriptions_internal(self, service):
        """Test dictionnaire interne des abonnements."""
        assert isinstance(service._subscriptions, dict)
    
    def test_has_preferences_internal(self, service):
        """Test dictionnaire interne des préférences."""
        assert isinstance(service._preferences, dict)
    
    def test_has_sent_count_internal(self, service):
        """Test dictionnaire de comptage."""
        assert isinstance(service._sent_count, dict)
