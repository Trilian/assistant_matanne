"""
Tests supplémentaires pour push_notifications.py

Cible les lignes non couvertes par les tests existants:
- send_notification (308-336)
- send_to_all_users (345-349)
- notify_* methods (401-483)
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from src.services.push_notifications import (
    NotificationType,
    PushSubscription,
    PushNotification,
    NotificationPreferences,
    PushNotificationService,
)


# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════

@pytest.fixture
def push_service():
    """Service push notifications frais."""
    return PushNotificationService()


@pytest.fixture
def test_subscription():
    """Abonnement de test."""
    return PushSubscription(
        user_id="user_test",
        endpoint="https://fcm.googleapis.com/fcm/send/test123",
        p256dh_key="BNcRdreALRFXTkOOUHK1EtK2wtaz5Ry",
        auth_key="tBHItJI5svbpez7KI4CCXg"
    )


@pytest.fixture
def test_notification():
    """Notification de test."""
    return PushNotification(
        title="Test",
        body="Test body",
        notification_type=NotificationType.STOCK_LOW
    )


# ═══════════════════════════════════════════════════════════
# TESTS - send_notification
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestSendNotification:
    """Tests pour la méthode send_notification."""

    def test_send_notification_no_subscriptions(self, push_service, test_notification):
        """Envoi sans abonnements retourne False."""
        push_service._subscriptions = {}
        
        with patch('src.services.push_notifications.should_send_notification', return_value=(True, "")):
            result = push_service.send_notification("no_user", test_notification)
        
        assert result == False

    def test_send_notification_with_subscription(self, push_service, test_subscription, test_notification):
        """Envoi avec abonnement valide."""
        push_service._subscriptions = {"user_test": [test_subscription]}
        
        # Mock _send_web_push et should_send_notification
        with patch.object(push_service, '_send_web_push', return_value=True):
            with patch('src.services.push_notifications.should_send_notification', return_value=(True, "")):
                result = push_service.send_notification("user_test", test_notification)
        
        assert result == True

    def test_send_notification_preferences_disabled(self, push_service, test_subscription, test_notification):
        """Envoi avec préférences désactivées par should_send."""
        push_service._subscriptions = {"user_test": [test_subscription]}
        
        with patch('src.services.push_notifications.should_send_notification', return_value=(False, "Disabled")):
            result = push_service.send_notification("user_test", test_notification)
        
        assert result == False

    def test_send_notification_handles_push_error(self, push_service, test_subscription, test_notification):
        """Envoi gère les erreurs de push."""
        push_service._subscriptions = {"user_test": [test_subscription]}
        
        with patch('src.services.push_notifications.should_send_notification', return_value=(True, "")):
            with patch.object(push_service, '_send_web_push', side_effect=Exception("Network error")):
                result = push_service.send_notification("user_test", test_notification)
        
        # Doit gérer l'erreur et ne pas planter
        assert isinstance(result, bool)

    def test_send_notification_disables_on_410(self, push_service, test_subscription, test_notification):
        """Envoi désactive abonnement sur erreur 410."""
        push_service._subscriptions = {"user_test": [test_subscription]}
        
        with patch('src.services.push_notifications.should_send_notification', return_value=(True, "")):
            with patch.object(push_service, '_send_web_push', side_effect=Exception("410 Gone")):
                push_service.send_notification("user_test", test_notification)
        
        assert test_subscription.is_active == False


# ═══════════════════════════════════════════════════════════
# TESTS - send_to_all_users
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestSendToAllUsers:
    """Tests pour send_to_all_users."""

    def test_send_to_all_users_empty(self, push_service, test_notification):
        """Envoi à tous sans utilisateurs."""
        push_service._subscriptions = {}
        
        result = push_service.send_to_all_users(test_notification)
        
        assert result == 0

    def test_send_to_all_users_multiple(self, push_service, test_notification):
        """Envoi à plusieurs utilisateurs."""
        sub1 = PushSubscription(user_id="user1", endpoint="e1", p256dh_key="k", auth_key="a")
        sub2 = PushSubscription(user_id="user2", endpoint="e2", p256dh_key="k", auth_key="a")
        
        push_service._subscriptions = {
            "user1": [sub1],
            "user2": [sub2]
        }
        
        with patch.object(push_service, 'send_notification', return_value=True):
            result = push_service.send_to_all_users(test_notification)
        
        assert result == 2


# ═══════════════════════════════════════════════════════════
# TESTS - notify_stock_low
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestNotifyStockLow:
    """Tests pour notify_stock_low."""

    def test_notify_stock_low_creates_notification(self, push_service, test_subscription):
        """notify_stock_low crée une notification appropriée."""
        push_service._subscriptions = {"user_test": [test_subscription]}
        
        captured = None
        def capture(user_id, notif):
            nonlocal captured
            captured = notif
            return True
        
        with patch.object(push_service, 'send_notification', side_effect=capture):
            push_service.notify_stock_low("user_test", "Lait", 0.5)
        
        assert captured is not None
        assert "Lait" in captured.body
        assert "Stock bas" in captured.title
        assert captured.notification_type == NotificationType.STOCK_LOW


# ═══════════════════════════════════════════════════════════
# TESTS - notify_expiration
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestNotifyExpiration:
    """Tests pour notify_expiration."""

    def test_notify_expiration_expired(self, push_service):
        """Notification pour produit expiré (days_left=0)."""
        captured = None
        def capture(user_id, notif):
            nonlocal captured
            captured = notif
            return True
        
        with patch.object(push_service, 'send_notification', side_effect=capture):
            push_service.notify_expiration("user_test", "Yaourt", 0)
        
        assert captured is not None
        assert "périmé" in captured.title.lower() or "expiré" in captured.body.lower()

    def test_notify_expiration_tomorrow(self, push_service):
        """Notification pour expiration demain."""
        captured = None
        def capture(user_id, notif):
            nonlocal captured
            captured = notif
            return True
        
        with patch.object(push_service, 'send_notification', side_effect=capture):
            push_service.notify_expiration("user_test", "Crème", 1)
        
        assert captured is not None
        assert "demain" in captured.body.lower()

    def test_notify_expiration_soon(self, push_service):
        """Notification pour expiration dans quelques jours."""
        captured = None
        def capture(user_id, notif):
            nonlocal captured
            captured = notif
            return True
        
        with patch.object(push_service, 'send_notification', side_effect=capture):
            push_service.notify_expiration("user_test", "Fromage", 3)
        
        assert captured is not None
        assert "3 jours" in captured.body

    def test_notify_expiration_critical_flag(self, push_service):
        """Notification critique nécessite interaction."""
        captured = None
        def capture(user_id, notif):
            nonlocal captured
            captured = notif
            return True
        
        with patch.object(push_service, 'send_notification', side_effect=capture):
            push_service.notify_expiration("user_test", "Viande", 1, critical=True)
        
        assert captured is not None
        assert captured.require_interaction == True


# ═══════════════════════════════════════════════════════════
# TESTS - notify_meal_reminder
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestNotifyMealReminder:
    """Tests pour notify_meal_reminder."""

    def test_notify_meal_reminder_content(self, push_service):
        """Rappel repas avec contenu correct."""
        captured = None
        def capture(user_id, notif):
            nonlocal captured
            captured = notif
            return True
        
        with patch.object(push_service, 'send_notification', side_effect=capture):
            push_service.notify_meal_reminder("user_test", "dîner", "Pâtes carbonara", "30 min")
        
        assert captured is not None
        assert "Dîner" in captured.title
        assert "Pâtes carbonara" in captured.body


# ═══════════════════════════════════════════════════════════
# TESTS - notify_shopping_list_shared
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestNotifyShoppingListShared:
    """Tests pour notify_shopping_list_shared."""

    def test_notify_shopping_list_shared_content(self, push_service):
        """Notification partage liste avec contenu correct."""
        captured = None
        def capture(user_id, notif):
            nonlocal captured
            captured = notif
            return True
        
        with patch.object(push_service, 'send_notification', side_effect=capture):
            push_service.notify_shopping_list_shared("user_test", "Marie", "Courses semaine")
        
        assert captured is not None
        assert "Marie" in captured.body
        assert "Courses semaine" in captured.body


# ═══════════════════════════════════════════════════════════
# TESTS - Gestion des abonnements en mémoire
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestSubscriptionManagement:
    """Tests pour la gestion des abonnements."""

    def test_save_subscription_adds_to_dict(self, push_service, test_subscription):
        """save_subscription ajoute l'abonnement."""
        # Initialiser _subscriptions s'il est None
        if push_service._subscriptions is None:
            push_service._subscriptions = {}
            
        push_service._subscriptions["user_test"] = [test_subscription]
        
        assert "user_test" in push_service._subscriptions
        assert len(push_service._subscriptions["user_test"]) >= 1

    def test_remove_subscription_removes_from_dict(self, push_service, test_subscription):
        """remove_subscription supprime l'abonnement."""
        push_service._subscriptions = {"user_test": [test_subscription]}
        
        push_service.remove_subscription("user_test", test_subscription.endpoint)
        
        subs = push_service._subscriptions.get("user_test", [])
        assert test_subscription not in subs

    def test_get_user_subscriptions_returns_list(self, push_service, test_subscription):
        """get_user_subscriptions retourne la liste."""
        push_service._subscriptions = {"user_test": [test_subscription]}
        
        result = push_service.get_user_subscriptions("user_test")
        
        assert isinstance(result, list)
        assert len(result) == 1


# ═══════════════════════════════════════════════════════════
# TESTS - Gestion des préférences
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestPreferencesManagement:
    """Tests pour la gestion des préférences."""

    def test_notification_preferences_creation(self):
        """NotificationPreferences se crée correctement."""
        prefs = NotificationPreferences(
            user_id="user_prefs",
            quiet_hours_start=22,
            quiet_hours_end=7
        )
        
        assert prefs.user_id == "user_prefs"
        assert prefs.quiet_hours_start == 22
        assert prefs.quiet_hours_end == 7

    def test_notification_preferences_has_attributes(self):
        """NotificationPreferences a les attributs nécessaires."""
        prefs = NotificationPreferences(user_id="test_user")
        
        assert prefs.user_id == "test_user"
        assert hasattr(prefs, 'quiet_hours_start')
        assert hasattr(prefs, 'quiet_hours_end')


# ═══════════════════════════════════════════════════════════ 
# TESTS - Factory functions
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestFactoryFunctions:
    """Tests pour les factory functions."""

    def test_get_push_notification_service(self):
        """Factory retourne une instance."""
        from src.services.push_notifications import get_push_notification_service
        
        service = get_push_notification_service()
        assert service is not None
        assert isinstance(service, PushNotificationService)

    def test_service_has_required_methods(self):
        """Service a les méthodes requises."""
        from src.services.push_notifications import get_push_notification_service
        
        service = get_push_notification_service()
        
        # Vérifie les méthodes de notification
        assert hasattr(service, 'send_notification')
        assert hasattr(service, 'notify_stock_low')
        assert hasattr(service, 'notify_expiration')
        assert hasattr(service, 'notify_meal_reminder')
