"""
Tests complets pour src/services/push_notifications.py

Couverture cible: >80%
"""

import pytest
from datetime import datetime, timedelta, time
from unittest.mock import Mock, patch, MagicMock


# ═══════════════════════════════════════════════════════════
# TESTS ENUMS ET TYPES
# ═══════════════════════════════════════════════════════════


class TestNotificationType:
    """Tests enum NotificationType."""

    def test_import_enum(self):
        from src.services.push_notifications import NotificationType
        assert NotificationType is not None

    def test_enum_values(self):
        from src.services.push_notifications import NotificationType
        
        # Alertes importantes
        assert NotificationType.STOCK_LOW == "stock_low"
        assert NotificationType.EXPIRATION_WARNING == "expiration_warning"
        assert NotificationType.EXPIRATION_CRITICAL == "expiration_critical"
        
        # Planning
        assert NotificationType.MEAL_REMINDER == "meal_reminder"
        assert NotificationType.ACTIVITY_REMINDER == "activity_reminder"
        
        # Courses
        assert NotificationType.SHOPPING_LIST_SHARED == "shopping_list_shared"
        assert NotificationType.SHOPPING_LIST_UPDATED == "shopping_list_updated"
        
        # Famille
        assert NotificationType.MILESTONE_REMINDER == "milestone_reminder"
        assert NotificationType.HEALTH_CHECK_REMINDER == "health_check_reminder"
        
        # Système
        assert NotificationType.SYSTEM_UPDATE == "system_update"
        assert NotificationType.SYNC_COMPLETE == "sync_complete"

    def test_enum_count(self):
        from src.services.push_notifications import NotificationType
        assert len(NotificationType) == 11


# ═══════════════════════════════════════════════════════════
# TESTS SCHÉMAS PYDANTIC
# ═══════════════════════════════════════════════════════════


class TestPushSubscription:
    """Tests schéma PushSubscription."""

    def test_import_schema(self):
        from src.services.push_notifications import PushSubscription
        assert PushSubscription is not None

    def test_creation_valide(self):
        from src.services.push_notifications import PushSubscription
        
        sub = PushSubscription(
            user_id="user123",
            endpoint="https://push.example.com/subscription",
            p256dh_key="BNcRdre...",
            auth_key="tBHIt..."
        )
        
        assert sub.user_id == "user123"
        assert sub.endpoint.startswith("https://")
        assert sub.is_active is True

    def test_valeurs_optionnelles(self):
        from src.services.push_notifications import PushSubscription
        
        sub = PushSubscription(
            user_id="user123",
            endpoint="https://push.example.com/sub",
            p256dh_key="key123",
            auth_key="auth123",
            user_agent="Mozilla/5.0",
            is_active=False
        )
        
        assert sub.user_agent == "Mozilla/5.0"
        assert sub.is_active is False


class TestPushNotification:
    """Tests schéma PushNotification."""

    def test_creation_basique(self):
        from src.services.push_notifications import PushNotification, NotificationType
        
        notif = PushNotification(
            title="Test",
            body="Message de test"
        )
        
        assert notif.title == "Test"
        assert notif.body == "Message de test"
        assert notif.notification_type == NotificationType.SYSTEM_UPDATE

    def test_notification_complete(self):
        from src.services.push_notifications import PushNotification, NotificationType
        
        notif = PushNotification(
            title="Stock bas",
            body="Lait en stock bas",
            icon="/icons/warning.png",
            badge="/icons/badge.png",
            tag="stock_lait",
            notification_type=NotificationType.STOCK_LOW,
            url="/inventaire",
            data={"article_id": 123},
            actions=[{"action": "view", "title": "Voir"}],
            vibrate=[200, 100, 200],
            require_interaction=True,
            silent=False
        )
        
        assert notif.notification_type == NotificationType.STOCK_LOW
        assert notif.tag == "stock_lait"
        assert notif.require_interaction is True

    def test_valeurs_par_defaut(self):
        from src.services.push_notifications import PushNotification
        
        notif = PushNotification(title="Test", body="Test")
        
        assert notif.url == "/"
        assert notif.data == {}
        assert notif.actions == []
        assert notif.vibrate == [100, 50, 100]
        assert notif.require_interaction is False
        assert notif.silent is False


class TestNotificationPreferences:
    """Tests schéma NotificationPreferences."""

    def test_creation_valide(self):
        from src.services.push_notifications import NotificationPreferences
        
        prefs = NotificationPreferences(user_id="user123")
        
        assert prefs.user_id == "user123"

    def test_valeurs_par_defaut(self):
        from src.services.push_notifications import NotificationPreferences
        
        prefs = NotificationPreferences(user_id="user123")
        
        # Catégories activées par défaut
        assert prefs.stock_alerts is True
        assert prefs.expiration_alerts is True
        assert prefs.meal_reminders is True
        assert prefs.activity_reminders is True
        assert prefs.shopping_updates is True
        assert prefs.family_reminders is True
        assert prefs.system_updates is False  # Désactivé par défaut
        
        # Horaires de silence
        assert prefs.quiet_hours_start == 22
        assert prefs.quiet_hours_end == 7
        
        # Fréquence
        assert prefs.max_per_hour == 5
        assert prefs.digest_mode is False

    def test_preferences_personnalisees(self):
        from src.services.push_notifications import NotificationPreferences
        
        prefs = NotificationPreferences(
            user_id="user456",
            stock_alerts=False,
            meal_reminders=False,
            quiet_hours_start=21,
            quiet_hours_end=8,
            max_per_hour=3,
            digest_mode=True
        )
        
        assert prefs.stock_alerts is False
        assert prefs.quiet_hours_start == 21
        assert prefs.digest_mode is True


# ═══════════════════════════════════════════════════════════
# TESTS CONFIGURATION
# ═══════════════════════════════════════════════════════════


class TestPushNotificationsConfig:
    """Tests configuration VAPID."""

    def test_vapid_public_key_defined(self):
        from src.services.push_notifications import VAPID_PUBLIC_KEY
        
        assert VAPID_PUBLIC_KEY is not None
        assert len(VAPID_PUBLIC_KEY) > 0

    def test_vapid_email_defined(self):
        from src.services.push_notifications import VAPID_EMAIL
        
        assert VAPID_EMAIL is not None
        assert VAPID_EMAIL.startswith("mailto:")


# ═══════════════════════════════════════════════════════════
# TESTS UTILS IMPORTS
# ═══════════════════════════════════════════════════════════


class TestPushNotificationsUtilsImports:
    """Tests imports depuis push_notifications_utils."""

    def test_imports_utils(self):
        from src.services.push_notifications_utils import (
            check_notification_type_enabled,
            is_quiet_hours,
            can_send_during_quiet_hours,
            should_send_notification,
            build_push_payload,
            build_subscription_info,
            create_stock_notification,
            create_expiration_notification,
            create_meal_reminder_notification,
        )
        
        assert check_notification_type_enabled is not None
        assert is_quiet_hours is not None
        assert build_push_payload is not None

    def test_check_notification_type_enabled(self):
        from src.services.push_notifications_utils import check_notification_type_enabled, NotificationType
        
        prefs = {
            "stock_alerts": True,
            "meal_reminders": False
        }
        
        assert check_notification_type_enabled(NotificationType.STOCK_LOW, prefs) is True
        assert check_notification_type_enabled(NotificationType.MEAL_REMINDER, prefs) is False

    def test_is_quiet_hours(self):
        from src.services.push_notifications_utils import is_quiet_hours
        
        # Test pendant les heures silencieuses
        assert is_quiet_hours(23, 22, 7) is True  # 23h dans période 22h-7h
        assert is_quiet_hours(10, 22, 7) is False  # 10h hors période
        assert is_quiet_hours(10, None, None) is False  # Pas de silence

    def test_build_push_payload(self):
        from src.services.push_notifications_utils import build_push_payload
        
        notif = {
            "title": "Test",
            "body": "Message test"
        }
        
        payload = build_push_payload(notif)
        
        assert isinstance(payload, str)
        assert "Test" in payload

    def test_create_stock_notification(self):
        from src.services.push_notifications_utils import create_stock_notification
        
        notif = create_stock_notification("Lait", 0.5, "L")
        
        assert notif is not None
        assert isinstance(notif, dict)
        assert "Lait" in notif["body"] or "Lait" in notif["title"]

    def test_create_expiration_notification(self):
        from src.services.push_notifications_utils import create_expiration_notification
        
        notif = create_expiration_notification("Yaourt", 2)
        
        assert notif is not None
        assert isinstance(notif, dict)
        assert "Yaourt" in notif["body"] or "Yaourt" in notif["title"]

    def test_create_meal_reminder_notification(self):
        from src.services.push_notifications_utils import create_meal_reminder_notification
        
        notif = create_meal_reminder_notification("Poulet rôti", "déjeuner", "12:30")
        
        assert notif is not None
        assert isinstance(notif, dict)


# ═══════════════════════════════════════════════════════════
# TESTS MODELS IMPORTS
# ═══════════════════════════════════════════════════════════


class TestPushNotificationsModels:
    """Tests imports modèles DB."""

    def test_import_models(self):
        from src.core.models import (
            PushSubscription as PushSubscriptionModel,
            NotificationPreference as NotificationPreferenceModel,
        )
        
        assert PushSubscriptionModel is not None
        assert NotificationPreferenceModel is not None


# ═══════════════════════════════════════════════════════════
# TESTS EDGE CASES
# ═══════════════════════════════════════════════════════════


class TestPushNotificationsEdgeCases:
    """Tests cas limites."""

    def test_notification_empty_actions(self):
        from src.services.push_notifications import PushNotification
        
        notif = PushNotification(
            title="Test",
            body="Test",
            actions=[]
        )
        
        assert notif.actions == []

    def test_notification_multiple_actions(self):
        from src.services.push_notifications import PushNotification
        
        notif = PushNotification(
            title="Test",
            body="Test",
            actions=[
                {"action": "view", "title": "Voir"},
                {"action": "dismiss", "title": "Ignorer"},
                {"action": "snooze", "title": "Rappeler plus tard"}
            ]
        )
        
        assert len(notif.actions) == 3

    def test_preferences_quiet_hours_none(self):
        from src.services.push_notifications import NotificationPreferences
        
        prefs = NotificationPreferences(
            user_id="test",
            quiet_hours_start=None,
            quiet_hours_end=None
        )
        
        assert prefs.quiet_hours_start is None
        assert prefs.quiet_hours_end is None

    def test_notification_with_data(self):
        from src.services.push_notifications import PushNotification
        
        notif = PushNotification(
            title="Test",
            body="Test",
            data={
                "article_id": 123,
                "action_type": "view_stock",
                "priority": "high",
                "nested": {"key": "value"}
            }
        )
        
        assert notif.data["article_id"] == 123
        assert notif.data["nested"]["key"] == "value"

    def test_vibration_pattern(self):
        from src.services.push_notifications import PushNotification
        
        # Pattern personnalisé
        notif = PushNotification(
            title="Urgent",
            body="Message urgent",
            vibrate=[300, 100, 300, 100, 300]
        )
        
        assert len(notif.vibrate) == 5

    def test_silent_notification(self):
        from src.services.push_notifications import PushNotification
        
        notif = PushNotification(
            title="Background sync",
            body="Syncing...",
            silent=True
        )
        
        assert notif.silent is True


class TestPushNotificationsIntegration:
    """Tests d'intégration."""

    def test_workflow_notification_stock(self):
        from src.services.push_notifications_utils import (
            check_notification_type_enabled,
            create_stock_notification,
            NotificationType
        )
        
        # Créer préférences comme dict
        prefs = {
            "stock_alerts": True
        }
        
        # Vérifier si on peut envoyer
        can_send = check_notification_type_enabled(NotificationType.STOCK_LOW, prefs)
        assert can_send is True
        
        # Créer notification
        notif = create_stock_notification("Lait", 0.5, "L")
        assert notif is not None
        assert isinstance(notif, dict)

    def test_workflow_meal_reminder(self):
        from src.services.push_notifications_utils import (
            check_notification_type_enabled,
            create_meal_reminder_notification,
            NotificationType
        )
        
        prefs = {
            "meal_reminders": True
        }
        
        can_send = check_notification_type_enabled(NotificationType.MEAL_REMINDER, prefs)
        assert can_send is True
        
        notif = create_meal_reminder_notification("Salade César", "dîner", "19:00")
        assert notif is not None
        assert isinstance(notif, dict)

    def test_all_notification_types_have_preferences(self):
        from src.services.push_notifications import NotificationType, NotificationPreferences
        
        prefs = NotificationPreferences(user_id="test")
        
        # Chaque type de notification devrait avoir une préférence correspondante
        preference_mapping = {
            NotificationType.STOCK_LOW: prefs.stock_alerts,
            NotificationType.EXPIRATION_WARNING: prefs.expiration_alerts,
            NotificationType.EXPIRATION_CRITICAL: prefs.expiration_alerts,
            NotificationType.MEAL_REMINDER: prefs.meal_reminders,
            NotificationType.ACTIVITY_REMINDER: prefs.activity_reminders,
            NotificationType.SHOPPING_LIST_SHARED: prefs.shopping_updates,
            NotificationType.SHOPPING_LIST_UPDATED: prefs.shopping_updates,
            NotificationType.MILESTONE_REMINDER: prefs.family_reminders,
            NotificationType.HEALTH_CHECK_REMINDER: prefs.family_reminders,
            NotificationType.SYSTEM_UPDATE: prefs.system_updates,
            NotificationType.SYNC_COMPLETE: prefs.system_updates,
        }
        
        # Vérifier que toutes les valeurs sont des booléens
        for notif_type, pref_value in preference_mapping.items():
            assert isinstance(pref_value, bool), f"{notif_type} preference is not bool"
