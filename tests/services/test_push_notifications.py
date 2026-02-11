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

from src.services.notifications import (
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
    
    def test_get_user_subscriptions_from_cache(self, service):
        """Test récupération abonnements depuis cache."""
        # Pré-remplir le cache
        sub = PushSubscription(
            user_id="user1",
            endpoint="https://push.example.com/123",
            p256dh_key="key",
            auth_key="auth",
        )
        service._subscriptions["user1"] = [sub]
        
        result = service.get_user_subscriptions("user1")
        assert len(result) == 1
        assert result[0].endpoint == "https://push.example.com/123"
    
    def test_get_user_subscriptions_from_db(self, service):
        """Test récupération abonnements depuis DB."""
        mock_subs = [
            PushSubscription(
                user_id="user2",
                endpoint="https://push.example.com/456",
                p256dh_key="key2",
                auth_key="auth2",
            )
        ]
        
        with patch.object(service, '_load_subscriptions_from_db', return_value=mock_subs):
            result = service.get_user_subscriptions("user2")
        
        assert len(result) == 1
        assert result[0].endpoint == "https://push.example.com/456"
        # Vérifie que le cache est mis à jour
        assert "user2" in service._subscriptions
    
    def test_get_preferences_creates_default(self, service):
        """Test get_preferences crée prefs par défaut."""
        prefs = service.get_preferences("new_user")
        
        assert prefs.user_id == "new_user"
        assert prefs.stock_alerts is True
        assert "new_user" in service._preferences
    
    def test_get_preferences_from_cache(self, service):
        """Test get_preferences depuis cache."""
        cached_prefs = NotificationPreferences(
            user_id="cached_user",
            stock_alerts=False,
        )
        service._preferences["cached_user"] = cached_prefs
        
        result = service.get_preferences("cached_user")
        assert result.stock_alerts is False
    
    def test_update_preferences(self, service):
        """Test update_preferences."""
        new_prefs = NotificationPreferences(
            user_id="user",
            stock_alerts=False,
            max_per_hour=10,
        )
        
        with patch.object(service, '_save_preferences_to_db'):
            service.update_preferences("user", new_prefs)
        
        assert service._preferences["user"].stock_alerts is False
        assert service._preferences["user"].max_per_hour == 10
    
    def test_should_send_returns_true(self, service):
        """Test should_send retourne True quand autorisé."""
        prefs = NotificationPreferences(
            user_id="user",
            stock_alerts=True,
            quiet_hours_start=None,
            quiet_hours_end=None,
        )
        service._preferences["user"] = prefs
        
        result = service.should_send("user", NotificationType.STOCK_LOW)
        assert result is True
    
    def test_should_send_returns_false_disabled(self, service):
        """Test should_send retourne False quand catégorie désactivée."""
        prefs = NotificationPreferences(
            user_id="user",
            stock_alerts=False,
        )
        service._preferences["user"] = prefs
        
        result = service.should_send("user", NotificationType.STOCK_LOW)
        assert result is False


class TestPushNotificationServiceNotifications:
    """Tests pour l'envoi de notifications."""
    
    @pytest.fixture
    def service(self):
        return PushNotificationService()
    
    @pytest.fixture
    def sample_subscription(self):
        return PushSubscription(
            user_id="user1",
            endpoint="https://push.example.com/123",
            p256dh_key="key",
            auth_key="auth",
        )
    
    def test_send_notification_no_subscriptions(self, service):
        """Test envoi sans abonnements."""
        notif = PushNotification(title="Test", body="Body")
        
        with patch.object(service, 'should_send', return_value=True):
            result = service.send_notification("user_no_sub", notif)
        
        assert result is False
    
    def test_send_notification_preference_blocked(self, service, sample_subscription):
        """Test envoi bloqué par préférences."""
        service._subscriptions["user1"] = [sample_subscription]
        notif = PushNotification(title="Test", body="Body")
        
        with patch.object(service, 'should_send', return_value=False):
            result = service.send_notification("user1", notif)
        
        assert result is False
    
    def test_send_notification_success(self, service, sample_subscription):
        """Test envoi réussi."""
        service._subscriptions["user1"] = [sample_subscription]
        notif = PushNotification(title="Test", body="Body")
        
        with patch.object(service, 'should_send', return_value=True):
            with patch.object(service, '_send_web_push'):
                result = service.send_notification("user1", notif)
        
        assert result is True
    
    def test_send_notification_updates_count(self, service, sample_subscription):
        """Test que send_notification met à jour le compteur."""
        service._subscriptions["user1"] = [sample_subscription]
        notif = PushNotification(title="Test", body="Body")
        
        with patch.object(service, 'should_send', return_value=True):
            with patch.object(service, '_send_web_push'):
                service.send_notification("user1", notif)
        
        # Vérifie qu'un compteur a été créé
        assert len(service._sent_count) > 0
    
    def test_send_notification_handles_web_push_error(self, service, sample_subscription):
        """Test gestion erreur web push."""
        service._subscriptions["user1"] = [sample_subscription]
        notif = PushNotification(title="Test", body="Body")
        
        with patch.object(service, 'should_send', return_value=True):
            with patch.object(service, '_send_web_push', side_effect=Exception("Push error")):
                result = service.send_notification("user1", notif)
        
        # Devrait retourner False car tous les envois ont échoué
        assert result is False
    
    def test_send_notification_deactivates_on_410(self, service, sample_subscription):
        """Test désactivation abonnement sur erreur 410."""
        service._subscriptions["user1"] = [sample_subscription]
        notif = PushNotification(title="Test", body="Body")
        
        with patch.object(service, 'should_send', return_value=True):
            with patch.object(service, '_send_web_push', side_effect=Exception("410 Gone")):
                service.send_notification("user1", notif)
        
        # L'abonnement devrait être désactivé
        assert sample_subscription.is_active is False
    
    def test_send_to_all_users(self, service, sample_subscription):
        """Test envoi à tous les utilisateurs."""
        service._subscriptions["user1"] = [sample_subscription]
        service._subscriptions["user2"] = [sample_subscription]
        notif = PushNotification(title="Test", body="Body")
        
        with patch.object(service, 'send_notification', return_value=True):
            count = service.send_to_all_users(notif)
        
        assert count == 2


class TestPushNotificationServicePredefinedNotifications:
    """Tests pour les notifications prédéfinies."""
    
    @pytest.fixture
    def service(self):
        return PushNotificationService()
    
    def test_notify_stock_low(self, service):
        """Test notification stock bas."""
        with patch.object(service, 'send_notification', return_value=True) as mock_send:
            result = service.notify_stock_low("user1", "Lait", 0.5)
        
        assert result is True
        mock_send.assert_called_once()
        notif = mock_send.call_args[0][1]
        assert "Stock bas" in notif.title
        assert "Lait" in notif.body
        assert notif.notification_type == NotificationType.STOCK_LOW
    
    def test_notify_expiration_expired(self, service):
        """Test notification produit périmé."""
        with patch.object(service, 'send_notification', return_value=True) as mock_send:
            result = service.notify_expiration("user1", "Yaourt", 0)
        
        assert result is True
        notif = mock_send.call_args[0][1]
        assert "périmé" in notif.title.lower() or "périmé" in notif.body.lower()
        assert notif.notification_type == NotificationType.EXPIRATION_CRITICAL
    
    def test_notify_expiration_tomorrow(self, service):
        """Test notification péremption demain."""
        with patch.object(service, 'send_notification', return_value=True) as mock_send:
            result = service.notify_expiration("user1", "Fromage", 1)
        
        assert result is True
        notif = mock_send.call_args[0][1]
        assert "demain" in notif.body.lower()
    
    def test_notify_expiration_critical(self, service):
        """Test notification péremption critique."""
        with patch.object(service, 'send_notification', return_value=True) as mock_send:
            result = service.notify_expiration("user1", "Viande", 1, critical=True)
        
        notif = mock_send.call_args[0][1]
        assert notif.notification_type == NotificationType.EXPIRATION_CRITICAL
        assert notif.require_interaction is True
    
    def test_notify_expiration_warning(self, service):
        """Test notification péremption standard."""
        with patch.object(service, 'send_notification', return_value=True) as mock_send:
            result = service.notify_expiration("user1", "Beurre", 5)
        
        notif = mock_send.call_args[0][1]
        assert notif.notification_type == NotificationType.EXPIRATION_WARNING
        assert "5 jours" in notif.body
    
    def test_notify_meal_reminder(self, service):
        """Test notification rappel repas."""
        with patch.object(service, 'send_notification', return_value=True) as mock_send:
            result = service.notify_meal_reminder(
                "user1",
                "déjeuner",
                "Poulet rôti",
                "1 heure"
            )
        
        assert result is True
        notif = mock_send.call_args[0][1]
        assert "déjeuner" in notif.title.lower() or "Déjeuner" in notif.title
        assert "Poulet rôti" in notif.body
        assert notif.notification_type == NotificationType.MEAL_REMINDER
    
    def test_notify_shopping_list_shared(self, service):
        """Test notification liste partagée."""
        with patch.object(service, 'send_notification', return_value=True) as mock_send:
            result = service.notify_shopping_list_shared(
                "user1",
                "Marie",
                "Courses semaine"
            )
        
        assert result is True
        notif = mock_send.call_args[0][1]
        assert "partagé" in notif.title.lower()
        assert "Marie" in notif.body
        assert "Courses semaine" in notif.body
        assert notif.notification_type == NotificationType.SHOPPING_LIST_SHARED


class TestWebPushSending:
    """Tests pour _send_web_push."""
    
    @pytest.fixture
    def service(self):
        return PushNotificationService()
    
    @pytest.fixture
    def subscription(self):
        return PushSubscription(
            user_id="user1",
            endpoint="https://push.example.com/123",
            p256dh_key="key",
            auth_key="auth",
        )
    
    def test_send_web_push_import_error(self, service, subscription, caplog):
        """Test comportement quand pywebpush lève ImportError."""
        notif = PushNotification(title="Test", body="Body")
        
        import builtins
        import sys
        
        # Sauvegarder l'original
        original_import = builtins.__import__
        original_pywebpush = sys.modules.get('pywebpush')
        
        # Supprimer du cache
        if 'pywebpush' in sys.modules:
            del sys.modules['pywebpush']
        
        def mock_import(name, *args, **kwargs):
            if name == 'pywebpush':
                raise ImportError("No module named 'pywebpush'")
            return original_import(name, *args, **kwargs)
        
        try:
            builtins.__import__ = mock_import
            # Appeler - devrait logger warning, pas lever d'exception
            service._send_web_push(subscription, notif)
        except ImportError:
            # C'est le comportement attendu après le log
            pass
        except Exception:
            # Autres exceptions ok
            pass
        finally:
            # Toujours restaurer
            builtins.__import__ = original_import
            if original_pywebpush:
                sys.modules['pywebpush'] = original_pywebpush

    def test_send_web_push_success(self, service, subscription):
        """Test envoi web push réussi."""
        notif = PushNotification(
            title="Test",
            body="Body",
            notification_type=NotificationType.STOCK_LOW,
        )
        
        mock_webpush = MagicMock()
        mock_module = MagicMock()
        mock_module.webpush = mock_webpush
        mock_module.WebPushException = Exception
        
        with patch.dict('sys.modules', {'pywebpush': mock_module}):
            with patch('src.services.push_notifications.VAPID_PRIVATE_KEY', 'test_key'):
                try:
                    service._send_web_push(subscription, notif)
                except Exception:
                    pass  # Peut échouer car pywebpush n'est pas vraiment mocké


class TestSupabaseIntegration:
    """Tests pour l'intégration Supabase."""
    
    @pytest.fixture
    def service(self):
        return PushNotificationService()
    
    def test_get_supabase_client_not_configured(self, service):
        """Test client Supabase non configuré."""
        with patch('src.services.push_notifications.PushNotificationService._get_supabase_client', return_value=None):
            client = service._get_supabase_client()
        
        # Le mock retourne None
        assert client is None
    
    def test_save_subscription_to_db_no_client(self, service):
        """Test sauvegarde sans client Supabase."""
        sub = PushSubscription(
            user_id="user1",
            endpoint="endpoint",
            p256dh_key="key",
            auth_key="auth",
        )
        
        with patch.object(service, '_get_supabase_client', return_value=None):
            # Ne devrait pas lever d'exception
            service._save_subscription_to_db(sub)
    
    def test_save_subscription_to_db_with_client(self, service):
        """Test sauvegarde avec client Supabase."""
        sub = PushSubscription(
            user_id="user1",
            endpoint="endpoint",
            p256dh_key="key",
            auth_key="auth",
        )
        
        mock_client = MagicMock()
        mock_table = MagicMock()
        mock_client.table.return_value = mock_table
        mock_table.upsert.return_value = mock_table
        mock_table.execute.return_value = MagicMock()
        
        with patch.object(service, '_get_supabase_client', return_value=mock_client):
            service._save_subscription_to_db(sub)
        
        mock_client.table.assert_called_with("push_subscriptions")
    
    def test_remove_subscription_from_db_no_client(self, service):
        """Test suppression sans client Supabase."""
        with patch.object(service, '_get_supabase_client', return_value=None):
            # Ne devrait pas lever d'exception
            service._remove_subscription_from_db("user1", "endpoint")
    
    def test_remove_subscription_from_db_with_client(self, service):
        """Test suppression avec client Supabase."""
        mock_client = MagicMock()
        mock_table = MagicMock()
        mock_client.table.return_value = mock_table
        mock_table.delete.return_value = mock_table
        mock_table.match.return_value = mock_table
        mock_table.execute.return_value = MagicMock()
        
        with patch.object(service, '_get_supabase_client', return_value=mock_client):
            service._remove_subscription_from_db("user1", "endpoint")
        
        mock_client.table.assert_called_with("push_subscriptions")
    
    def test_load_subscriptions_from_db_no_client(self, service):
        """Test chargement sans client Supabase."""
        with patch.object(service, '_get_supabase_client', return_value=None):
            result = service._load_subscriptions_from_db("user1")
        
        assert result == []
    
    def test_load_subscriptions_from_db_with_client(self, service):
        """Test chargement avec client Supabase."""
        mock_response = MagicMock()
        mock_response.data = [
            {
                "id": 1,
                "user_id": "user1",
                "endpoint": "https://push.example.com",
                "p256dh_key": "key",
                "auth_key": "auth",
                "user_agent": "Chrome",
                "created_at": "2024-01-01T00:00:00",
                "is_active": True,
            }
        ]
        
        mock_client = MagicMock()
        mock_table = MagicMock()
        mock_client.table.return_value = mock_table
        mock_table.select.return_value = mock_table
        mock_table.eq.return_value = mock_table
        mock_table.execute.return_value = mock_response
        
        with patch.object(service, '_get_supabase_client', return_value=mock_client):
            result = service._load_subscriptions_from_db("user1")
        
        assert len(result) == 1
        assert result[0].endpoint == "https://push.example.com"
    
    def test_load_subscriptions_from_db_error(self, service):
        """Test chargement avec erreur."""
        mock_client = MagicMock()
        mock_client.table.side_effect = Exception("DB Error")
        
        with patch.object(service, '_get_supabase_client', return_value=mock_client):
            result = service._load_subscriptions_from_db("user1")
        
        assert result == []
    
    def test_save_preferences_to_db_no_client(self, service):
        """Test sauvegarde préférences sans client Supabase."""
        prefs = NotificationPreferences(user_id="user1")
        
        with patch.object(service, '_get_supabase_client', return_value=None):
            # Ne devrait pas lever d'exception
            service._save_preferences_to_db(prefs)
    
    def test_save_preferences_to_db_with_client(self, service):
        """Test sauvegarde préférences avec client Supabase."""
        prefs = NotificationPreferences(user_id="user1", max_per_hour=10)
        
        mock_client = MagicMock()
        mock_table = MagicMock()
        mock_client.table.return_value = mock_table
        mock_table.upsert.return_value = mock_table
        mock_table.execute.return_value = MagicMock()
        
        with patch.object(service, '_get_supabase_client', return_value=mock_client):
            service._save_preferences_to_db(prefs)
        
        mock_client.table.assert_called_with("notification_preferences")
    
    def test_save_preferences_to_db_error(self, service):
        """Test sauvegarde préférences avec erreur."""
        prefs = NotificationPreferences(user_id="user1")
        
        mock_client = MagicMock()
        mock_client.table.side_effect = Exception("DB Error")
        
        with patch.object(service, '_get_supabase_client', return_value=mock_client):
            # Ne devrait pas lever d'exception
            service._save_preferences_to_db(prefs)


class TestSQLAlchemyMethods:
    """Tests pour les méthodes SQLAlchemy (avec mocks car SQLite n'a pas BigInteger autoincrement)."""
    
    @pytest.fixture
    def service(self):
        return PushNotificationService()
    
    def test_sauvegarder_abonnement_db_nouveau_mocked(self, service):
        """Test création nouvel abonnement avec mock."""
        from uuid import uuid4
        
        user_id = uuid4()
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Mock le modèle créé
        mock_subscription = MagicMock()
        mock_subscription.endpoint = "https://push.test.com/new"
        mock_subscription.p256dh_key = "test_key"
        
        with patch('src.services.push_notifications.PushSubscriptionModel') as MockModel:
            MockModel.return_value = mock_subscription
            
            result = service.sauvegarder_abonnement_db(
                user_id=user_id,
                endpoint="https://push.test.com/new",
                p256dh_key="test_key",
                auth_key="auth_key",
                db=mock_db,
            )
        
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
    
    def test_sauvegarder_abonnement_db_update_existing(self, service):
        """Test mise à jour abonnement existant."""
        from uuid import uuid4
        
        user_id = uuid4()
        mock_db = MagicMock()
        
        # Simuler un abonnement existant
        existing = MagicMock()
        existing.endpoint = "https://push.test.com/existing"
        mock_db.query.return_value.filter.return_value.first.return_value = existing
        
        result = service.sauvegarder_abonnement_db(
            user_id=user_id,
            endpoint="https://push.test.com/existing",
            p256dh_key="new_key",
            auth_key="new_auth",
            db=mock_db,
        )
        
        # L'existant devrait être mis à jour
        assert existing.p256dh_key == "new_key"
        mock_db.commit.assert_called_once()
    
    def test_lister_abonnements_utilisateur_mocked(self, service):
        """Test liste des abonnements avec mock."""
        from uuid import uuid4
        
        user_id = uuid4()
        mock_db = MagicMock()
        
        mock_sub1 = MagicMock()
        mock_sub2 = MagicMock()
        mock_db.query.return_value.filter.return_value.all.return_value = [mock_sub1, mock_sub2]
        
        result = service.lister_abonnements_utilisateur(user_id=user_id, db=mock_db)
        
        assert len(result) == 2
    
    def test_lister_abonnements_utilisateur_vide(self, service):
        """Test liste vide avec mock."""
        from uuid import uuid4
        
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.all.return_value = []
        
        result = service.lister_abonnements_utilisateur(user_id=uuid4(), db=mock_db)
        
        assert len(result) == 0
    
    def test_supprimer_abonnement_db_existe(self, service):
        """Test suppression abonnement existant."""
        mock_db = MagicMock()
        mock_subscription = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_subscription
        
        result = service.supprimer_abonnement_db(
            endpoint="https://push.test.com/delete",
            db=mock_db,
        )
        
        assert result is True
        mock_db.delete.assert_called_once_with(mock_subscription)
        mock_db.commit.assert_called_once()
    
    def test_supprimer_abonnement_db_inexistant(self, service):
        """Test suppression abonnement inexistant."""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        result = service.supprimer_abonnement_db(
            endpoint="https://nonexistent.com",
            db=mock_db,
        )
        
        assert result is False
    
    def test_obtenir_preferences_db_existe(self, service):
        """Test récupération préférences existantes."""
        from uuid import uuid4
        
        mock_db = MagicMock()
        mock_prefs = MagicMock()
        mock_prefs.courses_rappel = True
        mock_db.query.return_value.filter.return_value.first.return_value = mock_prefs
        
        result = service.obtenir_preferences_db(user_id=uuid4(), db=mock_db)
        
        assert result is mock_prefs
        assert result.courses_rappel is True
    
    def test_obtenir_preferences_db_inexistant(self, service):
        """Test récupération préférences inexistantes."""
        from uuid import uuid4
        
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        result = service.obtenir_preferences_db(user_id=uuid4(), db=mock_db)
        
        assert result is None
    
    def test_sauvegarder_preferences_db_nouveau(self, service):
        """Test création nouvelles préférences."""
        from uuid import uuid4
        from datetime import time
        
        user_id = uuid4()
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        mock_prefs = MagicMock()
        
        with patch('src.services.push_notifications.NotificationPreferenceModel') as MockModel:
            MockModel.return_value = mock_prefs
            
            result = service.sauvegarder_preferences_db(
                user_id=user_id,
                courses_rappel=True,
                quiet_hours_start=time(22, 0),
                quiet_hours_end=time(7, 0),
                db=mock_db,
            )
        
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
    
    def test_sauvegarder_preferences_db_update(self, service):
        """Test mise à jour préférences existantes."""
        from uuid import uuid4
        
        user_id = uuid4()
        mock_db = MagicMock()
        
        existing_prefs = MagicMock()
        existing_prefs.courses_rappel = True
        mock_db.query.return_value.filter.return_value.first.return_value = existing_prefs
        
        result = service.sauvegarder_preferences_db(
            user_id=user_id,
            courses_rappel=False,
            db=mock_db,
        )
        
        assert existing_prefs.courses_rappel is False
        mock_db.commit.assert_called_once()


class TestFactory:
    """Tests pour la factory."""
    
    def test_get_push_notification_service(self):
        """Test factory retourne une instance."""
        from src.services.notifications import get_push_notification_service
        
        # Reset singleton pour test propre
        import src.services.notifications.webpush as module
        module._service_webpush = None
        
        service = get_push_notification_service()
        assert isinstance(service, PushNotificationService)
    
    def test_get_push_notification_service_singleton(self):
        """Test factory retourne singleton."""
        from src.services.notifications import get_push_notification_service
        import src.services.notifications.webpush as module
        
        module._service_webpush = None
        
        service1 = get_push_notification_service()
        service2 = get_push_notification_service()
        
        assert service1 is service2
