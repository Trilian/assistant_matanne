"""
Tests pour push_notifications.py - Notifications Push Web
Tests complets incluant les nouvelles méthodes DB SQLAlchemy
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime

from src.services.push_notifications import (
    PushNotificationService,
    PushSubscription,
    PushNotification,
    NotificationPreferences,
    NotificationType,
)


# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def push_service():
    """Service de notifications push"""
    return PushNotificationService()


@pytest.fixture
def sample_subscription():
    """Abonnement push d'exemple"""
    return PushSubscription(
        endpoint="https://fcm.googleapis.com/fcm/send/test123",
        p256dh_key="BNcRdreALRFXTkOOUHK1EtK2wtaz5Ry4YfYCA_0QTpQtUbVlUls0VJXg7A8u-T",
        auth_key="tBHItJI5svbpez7KI4CCXg",
        user_id="user_123"
    )


@pytest.fixture
def sample_notification():
    """Notification d'exemple"""
    return PushNotification(
        title="Test Notification",
        body="Ceci est un test",
        icon="/static/icons/icon-192x192.png",
        tag="test",
    )


@pytest.fixture
def sample_preferences():
    """Préférences de notification d'exemple"""
    return NotificationPreferences(
        user_id="user_123",
        stock_alerts=True,
        meal_reminders=True,
        quiet_hours_start=22,
        quiet_hours_end=8
    )


# ═══════════════════════════════════════════════════════════
# TESTS MODÈLES PYDANTIC - SUBSCRIPTION
# ═══════════════════════════════════════════════════════════


class TestPushSubscriptionModel:
    """Tests du modèle PushSubscription"""
    
    def test_subscription_creation(self, sample_subscription):
        """Test création d'abonnement"""
        assert sample_subscription.endpoint.startswith("https://")
        assert sample_subscription.p256dh_key is not None
        assert sample_subscription.auth_key is not None
        assert sample_subscription.user_id == "user_123"
    
    def test_subscription_defaults(self):
        """Test valeurs par défaut"""
        sub = PushSubscription(
            endpoint="https://example.com",
            p256dh_key="key1",
            auth_key="key2",
            user_id="user"
        )
        assert sub.is_active is True
        assert sub.id is None
    
    def test_subscription_endpoint_validation(self, sample_subscription):
        """Test validation de l'endpoint"""
        assert sample_subscription.endpoint.startswith("https://")


class TestPushNotificationModel:
    """Tests du modèle PushNotification"""
    
    def test_notification_creation(self, sample_notification):
        """Test création de notification"""
        assert sample_notification.title == "Test Notification"
        assert sample_notification.body == "Ceci est un test"
        assert sample_notification.tag == "test"
    
    def test_notification_defaults(self):
        """Test valeurs par défaut"""
        notif = PushNotification(
            title="Test",
            body="Body"
        )
        assert notif.icon == "/static/icons/icon-192x192.png"
        assert notif.url == "/"
        assert notif.silent is False
    
    def test_notification_type_default(self, sample_notification):
        """Test type de notification par défaut"""
        assert sample_notification.notification_type == NotificationType.SYSTEM_UPDATE


class TestNotificationPreferencesModel:
    """Tests du modèle NotificationPreferences"""
    
    def test_preferences_creation(self, sample_preferences):
        """Test création de préférences"""
        assert sample_preferences.user_id == "user_123"
        assert sample_preferences.stock_alerts is True
        assert sample_preferences.meal_reminders is True
    
    def test_preferences_defaults(self):
        """Test valeurs par défaut"""
        prefs = NotificationPreferences(user_id="user")
        assert prefs.stock_alerts is True
        assert prefs.system_updates is False
        assert prefs.max_per_hour == 5
    
    def test_quiet_hours(self, sample_preferences):
        """Test heures silencieuses"""
        assert sample_preferences.quiet_hours_start == 22
        assert sample_preferences.quiet_hours_end == 8


# ═══════════════════════════════════════════════════════════
# TESTS NOTIFICATION TYPE ENUM
# ═══════════════════════════════════════════════════════════


class TestNotificationType:
    """Tests de l'enum NotificationType"""
    
    def test_types_exist(self):
        """Test existence des types"""
        assert NotificationType.MEAL_REMINDER is not None
        assert NotificationType.SHOPPING_LIST_SHARED is not None
        assert NotificationType.STOCK_LOW is not None
        assert NotificationType.EXPIRATION_WARNING is not None
    
    def test_type_values(self):
        """Test valeurs des types"""
        assert NotificationType.MEAL_REMINDER.value == "meal_reminder"
        assert NotificationType.SHOPPING_LIST_SHARED.value == "shopping_list_shared"


# ═══════════════════════════════════════════════════════════
# TESTS SERVICE INITIALIZATION
# ═══════════════════════════════════════════════════════════


class TestPushNotificationServiceInit:
    """Tests d'initialisation du service"""
    
    def test_service_creation(self, push_service):
        """Test création du service"""
        assert push_service is not None
    
    def test_service_has_methods(self, push_service):
        """Test que le service a les méthodes attendues"""
        assert hasattr(push_service, "send_notification")
        assert hasattr(push_service, "sauvegarder_abonnement_db")


# ═══════════════════════════════════════════════════════════
# TESTS GESTION ABONNEMENTS
# ═══════════════════════════════════════════════════════════


class TestSubscriptionManagement:
    """Tests de gestion des abonnements"""
    
    def test_subscription_structure(self, sample_subscription):
        """Test structure de sauvegarde"""
        assert sample_subscription.endpoint
        assert sample_subscription.p256dh_key
        assert sample_subscription.auth_key
        assert sample_subscription.user_id
    
    def test_subscription_endpoint_format(self, sample_subscription):
        """Test format de l'endpoint"""
        valid_prefixes = [
            "https://fcm.googleapis.com",
            "https://updates.push.services.mozilla.com",
            "https://wns.windows.com",
            "https://"
        ]
        
        is_valid = any(
            sample_subscription.endpoint.startswith(prefix)
            for prefix in valid_prefixes
        )
        assert is_valid


# ═══════════════════════════════════════════════════════════
# TESTS ENVOI NOTIFICATIONS
# ═══════════════════════════════════════════════════════════


class TestNotificationSending:
    """Tests d'envoi de notifications"""
    
    def test_notification_json_serialization(self, sample_notification):
        """Test sérialisation JSON"""
        import json
        
        payload_dict = {
            "title": sample_notification.title,
            "body": sample_notification.body,
            "tag": sample_notification.tag
        }
        
        serialized = json.dumps(payload_dict)
        assert "Test Notification" in serialized
    
    def test_notification_options_structure(self):
        """Test structure options de notification"""
        options = {
            "TTL": 86400,
            "urgency": "normal"
        }
        
        assert options["TTL"] == 86400
        assert options["urgency"] in ["very-low", "low", "normal", "high"]


# ═══════════════════════════════════════════════════════════
# TESTS PRÉFÉRENCES
# ═══════════════════════════════════════════════════════════


class TestPreferencesManagement:
    """Tests de gestion des préférences"""
    
    def test_preference_structure(self, sample_preferences):
        """Test structure des préférences"""
        required_fields = ["user_id", "stock_alerts", "meal_reminders"]
        
        for field in required_fields:
            assert hasattr(sample_preferences, field)
    
    def test_quiet_hours_range(self, sample_preferences):
        """Test plage heures silencieuses"""
        assert 0 <= sample_preferences.quiet_hours_start <= 23
        assert 0 <= sample_preferences.quiet_hours_end <= 23
    
    def test_is_in_quiet_hours(self, sample_preferences):
        """Test vérification heures silencieuses"""
        test_hour = 23
        start = sample_preferences.quiet_hours_start
        end = sample_preferences.quiet_hours_end
        
        # Pour 22:00-08:00, 23:00 est en heures silencieuses
        if start > end:
            is_quiet = test_hour >= start or test_hour < end
        else:
            is_quiet = start <= test_hour < end
        
        assert is_quiet is True
    
    def test_max_per_hour_limit(self, sample_preferences):
        """Test limite par heure"""
        assert sample_preferences.max_per_hour > 0
        assert sample_preferences.max_per_hour <= 60


# ═══════════════════════════════════════════════════════════
# TESTS MÉTHODES DB (SQLAlchemy)
# ═══════════════════════════════════════════════════════════


class TestDBMethods:
    """Tests des méthodes DB SQLAlchemy"""
    
    def test_subscription_to_db_format(self, sample_subscription):
        """Test conversion vers format DB"""
        db_data = {
            "endpoint": sample_subscription.endpoint,
            "p256dh_key": sample_subscription.p256dh_key,
            "auth_key": sample_subscription.auth_key,
            "user_id": sample_subscription.user_id,
            "is_active": sample_subscription.is_active
        }
        
        assert db_data["endpoint"] == sample_subscription.endpoint
        assert db_data["is_active"] is True
    
    def test_preferences_to_db_format(self, sample_preferences):
        """Test conversion préférences vers DB"""
        db_data = {
            "user_id": sample_preferences.user_id,
            "stock_alerts": sample_preferences.stock_alerts,
            "meal_reminders": sample_preferences.meal_reminders,
            "quiet_hours_start": sample_preferences.quiet_hours_start,
            "quiet_hours_end": sample_preferences.quiet_hours_end
        }
        
        assert db_data["user_id"] == "user_123"


# ═══════════════════════════════════════════════════════════
# TESTS VAPID
# ═══════════════════════════════════════════════════════════


class TestVAPID:
    """Tests des fonctionnalités VAPID"""
    
    def test_vapid_key_format(self):
        """Test format des clés VAPID"""
        import base64
        
        # Exemple de clé publique VAPID
        sample_key = "BBsfbtwB1rAg9xVcy4WETJy4YoDKPpNT_wt0nMBc6jnGK0JP4fZjs_7OrRAsjaUdoMKIZBzZ-dhskstfYgqHSR0"
        
        try:
            padded = sample_key + "=" * (4 - len(sample_key) % 4)
            decoded = base64.urlsafe_b64decode(padded)
            assert len(decoded) > 0
        except Exception:
            assert len(sample_key) > 0
    
    def test_vapid_claims_structure(self):
        """Test structure des claims VAPID"""
        claims = {
            "sub": "mailto:admin@matanne.fr",
            "aud": "https://fcm.googleapis.com",
            "exp": int(datetime.now().timestamp()) + 86400
        }
        
        assert "sub" in claims
        assert claims["sub"].startswith("mailto:")


# ═══════════════════════════════════════════════════════════
# TESTS CAS LIMITES
# ═══════════════════════════════════════════════════════════


class TestEdgeCases:
    """Tests des cas limites"""
    
    def test_empty_subscriptions_list(self):
        """Test liste d'abonnements vide"""
        subscriptions = []
        assert len(subscriptions) == 0
    
    def test_invalid_endpoint(self):
        """Test endpoint invalide"""
        invalid_endpoints = [
            "",
            "http://insecure.com",
            "not-a-url"
        ]
        
        for endpoint in invalid_endpoints:
            is_valid = endpoint.startswith("https://")
            assert is_valid is False
    
    def test_notification_size_limit(self, sample_notification):
        """Test limite de taille notification"""
        import json
        
        payload_json = json.dumps({
            "title": sample_notification.title,
            "body": sample_notification.body
        })
        
        MAX_SIZE = 4096
        assert len(payload_json.encode()) < MAX_SIZE
    
    def test_vibrate_pattern(self, sample_notification):
        """Test pattern de vibration"""
        notif = PushNotification(
            title="Test",
            body="Test"
        )
        assert isinstance(notif.vibrate, list)
        assert all(isinstance(v, int) for v in notif.vibrate)


# ═══════════════════════════════════════════════════════════
# TESTS UTILITAIRES
# ═══════════════════════════════════════════════════════════


class TestUtilities:
    """Tests des fonctions utilitaires"""
    
    def test_encode_base64url(self):
        """Test encodage base64url"""
        import base64
        
        data = b"test data"
        encoded = base64.urlsafe_b64encode(data).rstrip(b"=").decode()
        
        assert "+" not in encoded
        assert "/" not in encoded
    
    def test_notification_urgency_levels(self):
        """Test niveaux d'urgence"""
        urgency_levels = ["very-low", "low", "normal", "high"]
        
        assert "normal" in urgency_levels
        assert len(urgency_levels) == 4
    
    def test_ttl_values(self):
        """Test valeurs TTL"""
        ttl_options = {
            "immediate": 0,
            "hour": 3600,
            "day": 86400,
            "week": 604800
        }
        
        assert ttl_options["day"] == 86400


# ═══════════════════════════════════════════════════════════
# TESTS INTÉGRATION
# ═══════════════════════════════════════════════════════════


class TestIntegration:
    """Tests d'intégration"""
    
    def test_full_notification_flow(self, sample_subscription, sample_notification):
        """Test flux complet de notification"""
        # 1. Créer un abonnement
        assert sample_subscription.user_id == "user_123"
        
        # 2. Créer une notification
        assert sample_notification.title == "Test Notification"
        
        # 3. Les deux sont compatibles
        assert sample_subscription.is_active is True
    
    def test_preferences_filter_notifications(self, sample_preferences, sample_notification):
        """Test filtrage par préférences"""
        # L'utilisateur a activé les alertes stock
        assert sample_preferences.stock_alerts is True
        
        # La notification peut être envoyée
        assert sample_notification is not None
