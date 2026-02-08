"""
Tests unitaires pour push_notifications_utils.py.

Ces tests vérifient les fonctions pures du module push_notifications_utils
sans nécessiter de base de données ni de dépendances externes.
"""

import pytest
import json
from datetime import datetime, timedelta


class TestNotificationTypeMapping:
    """Tests pour le mapping des types de notification."""
    
    def test_get_notification_type_mapping_returns_dict(self):
        """Test que le mapping retourne un dict."""
        from src.services.push_notifications_utils import get_notification_type_mapping
        
        mapping = get_notification_type_mapping()
        
        assert isinstance(mapping, dict)
        assert len(mapping) > 0
    
    def test_get_notification_type_mapping_all_types(self):
        """Test que tous les types sont mappés."""
        from src.services.push_notifications_utils import (
            get_notification_type_mapping, NotificationType
        )
        
        mapping = get_notification_type_mapping()
        
        for notif_type in NotificationType:
            assert notif_type in mapping


class TestCheckNotificationTypeEnabled:
    """Tests pour la vérification des types activés."""
    
    def test_type_enabled(self):
        """Test type activé."""
        from src.services.push_notifications_utils import (
            check_notification_type_enabled, NotificationType
        )
        
        prefs = {"stock_alerts": True}
        result = check_notification_type_enabled(NotificationType.STOCK_LOW, prefs)
        
        assert result is True
    
    def test_type_disabled(self):
        """Test type désactivé."""
        from src.services.push_notifications_utils import (
            check_notification_type_enabled, NotificationType
        )
        
        prefs = {"system_updates": False}
        result = check_notification_type_enabled(NotificationType.SYSTEM_UPDATE, prefs)
        
        assert result is False
    
    def test_type_not_in_prefs_defaults_true(self):
        """Test type absent des préférences."""
        from src.services.push_notifications_utils import (
            check_notification_type_enabled, NotificationType
        )
        
        prefs = {}
        result = check_notification_type_enabled(NotificationType.STOCK_LOW, prefs)
        
        assert result is True
    
    def test_string_type(self):
        """Test avec type en string."""
        from src.services.push_notifications_utils import check_notification_type_enabled
        
        prefs = {"stock_alerts": True}
        result = check_notification_type_enabled("stock_low", prefs)
        
        assert result is True
    
    def test_unknown_string_type(self):
        """Test avec type inconnu."""
        from src.services.push_notifications_utils import check_notification_type_enabled
        
        result = check_notification_type_enabled("unknown_type", {})
        
        assert result is True  # Par défaut, activer


class TestQuietHours:
    """Tests pour les heures silencieuses."""
    
    def test_is_quiet_hours_during_quiet(self):
        """Test pendant les heures silencieuses."""
        from src.services.push_notifications_utils import is_quiet_hours
        
        # 23h, silence 22h->7h
        assert is_quiet_hours(23, 22, 7) is True
        assert is_quiet_hours(0, 22, 7) is True
        assert is_quiet_hours(6, 22, 7) is True
    
    def test_is_quiet_hours_outside_quiet(self):
        """Test hors heures silencieuses."""
        from src.services.push_notifications_utils import is_quiet_hours
        
        # 10h, silence 22h->7h
        assert is_quiet_hours(10, 22, 7) is False
        assert is_quiet_hours(21, 22, 7) is False
    
    def test_is_quiet_hours_no_quiet(self):
        """Test sans heures silencieuses."""
        from src.services.push_notifications_utils import is_quiet_hours
        
        assert is_quiet_hours(10, None, None) is False
    
    def test_is_quiet_hours_same_day_range(self):
        """Test plage même jour (1h->6h)."""
        from src.services.push_notifications_utils import is_quiet_hours
        
        assert is_quiet_hours(3, 1, 6) is True
        assert is_quiet_hours(0, 1, 6) is False
        assert is_quiet_hours(7, 1, 6) is False
    
    def test_is_quiet_hours_invalid_hour(self):
        """Test avec heure invalide."""
        from src.services.push_notifications_utils import is_quiet_hours
        
        assert is_quiet_hours(25, 22, 7) is False
        assert is_quiet_hours(-1, 22, 7) is False
    
    def test_can_send_during_quiet_hours_critical(self):
        """Test notification critique pendant silence."""
        from src.services.push_notifications_utils import (
            can_send_during_quiet_hours, NotificationType
        )
        
        assert can_send_during_quiet_hours(NotificationType.EXPIRATION_CRITICAL) is True
    
    def test_can_send_during_quiet_hours_normal(self):
        """Test notification normale pendant silence."""
        from src.services.push_notifications_utils import (
            can_send_during_quiet_hours, NotificationType
        )
        
        assert can_send_during_quiet_hours(NotificationType.MEAL_REMINDER) is False


class TestShouldSendNotification:
    """Tests pour la décision d'envoi."""
    
    def test_should_send_normal_case(self):
        """Test cas normal."""
        from src.services.push_notifications_utils import (
            should_send_notification, NotificationType
        )
        
        prefs = {
            "stock_alerts": True,
            "quiet_hours_start": 22,
            "quiet_hours_end": 7,
            "max_per_hour": 5,
        }
        
        should_send, reason = should_send_notification(
            NotificationType.STOCK_LOW, prefs, current_hour=10
        )
        
        assert should_send is True
        assert reason == ""
    
    def test_should_send_type_disabled(self):
        """Test type désactivé."""
        from src.services.push_notifications_utils import (
            should_send_notification, NotificationType
        )
        
        prefs = {"stock_alerts": False}
        
        should_send, reason = should_send_notification(
            NotificationType.STOCK_LOW, prefs
        )
        
        assert should_send is False
        assert "désactivé" in reason
    
    def test_should_send_quiet_hours(self):
        """Test pendant heures silencieuses."""
        from src.services.push_notifications_utils import (
            should_send_notification, NotificationType
        )
        
        prefs = {
            "meal_reminders": True,
            "quiet_hours_start": 22,
            "quiet_hours_end": 7,
        }
        
        should_send, reason = should_send_notification(
            NotificationType.MEAL_REMINDER, prefs, current_hour=23
        )
        
        assert should_send is False
        assert "silencieuses" in reason
    
    def test_should_send_critical_during_quiet(self):
        """Test critique pendant silence."""
        from src.services.push_notifications_utils import (
            should_send_notification, NotificationType
        )
        
        prefs = {
            "expiration_alerts": True,
            "quiet_hours_start": 22,
            "quiet_hours_end": 7,
        }
        
        should_send, reason = should_send_notification(
            NotificationType.EXPIRATION_CRITICAL, prefs, current_hour=23
        )
        
        assert should_send is True
    
    def test_should_send_limit_reached(self):
        """Test limite par heure atteinte."""
        from src.services.push_notifications_utils import (
            should_send_notification, NotificationType
        )
        
        prefs = {"stock_alerts": True, "max_per_hour": 5}
        
        should_send, reason = should_send_notification(
            NotificationType.STOCK_LOW, prefs, sent_count_this_hour=5
        )
        
        assert should_send is False
        assert "Limite" in reason


class TestBuildPayload:
    """Tests pour la construction de payloads."""
    
    def test_build_push_payload_basic(self):
        """Test payload basique."""
        from src.services.push_notifications_utils import build_push_payload
        
        notif = {"title": "Test", "body": "Message"}
        payload = build_push_payload(notif)
        
        assert isinstance(payload, str)
        data = json.loads(payload)
        assert data["title"] == "Test"
        assert data["body"] == "Message"
    
    def test_build_push_payload_with_actions(self):
        """Test payload avec actions."""
        from src.services.push_notifications_utils import build_push_payload
        
        notif = {
            "title": "Test",
            "body": "Message",
            "actions": [{"action": "view", "title": "Voir"}]
        }
        payload = build_push_payload(notif)
        
        data = json.loads(payload)
        assert len(data["actions"]) == 1
    
    def test_build_push_payload_with_timestamp(self):
        """Test payload avec timestamp datetime."""
        from src.services.push_notifications_utils import build_push_payload
        
        notif = {
            "title": "Test",
            "body": "Message",
            "timestamp": datetime(2024, 1, 15, 10, 30)
        }
        payload = build_push_payload(notif)
        
        data = json.loads(payload)
        assert "2024-01-15" in data["timestamp"]
    
    def test_build_subscription_info(self):
        """Test construction info abonnement."""
        from src.services.push_notifications_utils import build_subscription_info
        
        sub = {
            "endpoint": "https://push.example.com",
            "p256dh_key": "abc123",
            "auth_key": "xyz789"
        }
        
        info = build_subscription_info(sub)
        
        assert info["endpoint"] == "https://push.example.com"
        assert info["keys"]["p256dh"] == "abc123"
        assert info["keys"]["auth"] == "xyz789"


class TestCreateNotifications:
    """Tests pour la création de notifications prédéfinies."""
    
    def test_create_stock_notification(self):
        """Test notification stock bas."""
        from src.services.push_notifications_utils import create_stock_notification
        
        notif = create_stock_notification("Lait", 0.5, "L")
        
        assert "Stock bas" in notif["title"]
        assert "Lait" in notif["body"]
        assert "0.5 L" in notif["body"]
        assert notif["notification_type"] == "stock_low"
    
    def test_create_stock_notification_without_unit(self):
        """Test notification stock sans unité."""
        from src.services.push_notifications_utils import create_stock_notification
        
        notif = create_stock_notification("Oeufs", 3)
        
        assert "3" in notif["body"]
    
    def test_create_expiration_notification_expired(self):
        """Test notification produit périmé."""
        from src.services.push_notifications_utils import create_expiration_notification
        
        notif = create_expiration_notification("Yaourt", -1)
        
        assert "périmé" in notif["title"].lower() or "périmé" in notif["body"].lower()
        assert notif["require_interaction"] is True
    
    def test_create_expiration_notification_tomorrow(self):
        """Test notification expire demain."""
        from src.services.push_notifications_utils import create_expiration_notification
        
        notif = create_expiration_notification("Lait", 1)
        
        assert "demain" in notif["title"].lower() or "demain" in notif["body"].lower()
    
    def test_create_expiration_notification_warning(self):
        """Test notification proche."""
        from src.services.push_notifications_utils import create_expiration_notification
        
        notif = create_expiration_notification("Fromage", 3)
        
        assert "3 jours" in notif["body"]
        assert notif["notification_type"] == "expiration_warning"
    
    def test_create_meal_reminder_notification(self):
        """Test notification rappel repas."""
        from src.services.push_notifications_utils import create_meal_reminder_notification
        
        notif = create_meal_reminder_notification("déjeuner", "Pâtes carbonara", "30 min")
        
        assert "Pâtes carbonara" in notif["body"]
        assert "30 min" in notif["title"]
    
    def test_create_shopping_shared_notification(self):
        """Test notification liste partagée."""
        from src.services.push_notifications_utils import create_shopping_shared_notification
        
        notif = create_shopping_shared_notification("Marie", "Courses hebdo")
        
        assert "Marie" in notif["body"]
        assert "Courses hebdo" in notif["body"]
    
    def test_create_activity_reminder_notification(self):
        """Test notification rappel activité."""
        from src.services.push_notifications_utils import create_activity_reminder_notification
        
        notif = create_activity_reminder_notification("Piscine", "1h", "Centre aquatique")
        
        assert "Piscine" in notif["body"]
        assert "Centre aquatique" in notif["body"]
    
    def test_create_activity_reminder_without_location(self):
        """Test notification activité sans lieu."""
        from src.services.push_notifications_utils import create_activity_reminder_notification
        
        notif = create_activity_reminder_notification("Réunion", "15 min")
        
        assert "Réunion" in notif["body"]
        assert notif["notification_type"] == "activity_reminder"
    
    def test_create_milestone_reminder_notification(self):
        """Test notification jalon enfant."""
        from src.services.push_notifications_utils import create_milestone_reminder_notification
        
        notif = create_milestone_reminder_notification("Jules", "Moteur", "Premiers pas")
        
        assert "Jules" in notif["title"]
        assert "Premiers pas" in notif["body"]


class TestCounterUtils:
    """Tests pour les utilitaires de compteur."""
    
    def test_generate_count_key(self):
        """Test génération clé compteur."""
        from src.services.push_notifications_utils import generate_count_key
        
        dt = datetime(2024, 1, 15, 14, 30)
        key = generate_count_key("user123", dt)
        
        assert key == "user123_2024011514"
    
    def test_generate_count_key_default_time(self):
        """Test génération clé avec heure courante."""
        from src.services.push_notifications_utils import generate_count_key
        
        key = generate_count_key("user123")
        
        assert key.startswith("user123_")
        assert len(key) == len("user123_") + 10
    
    def test_parse_count_key_valid(self):
        """Test parsing clé valide."""
        from src.services.push_notifications_utils import parse_count_key
        
        user_id, dt = parse_count_key("user123_2024011514")
        
        assert user_id == "user123"
        assert dt.year == 2024
        assert dt.hour == 14
    
    def test_parse_count_key_invalid(self):
        """Test parsing clé invalide (sans underscore)."""
        from src.services.push_notifications_utils import parse_count_key
        
        user_id, dt = parse_count_key("nounderscore")
        
        assert user_id == "nounderscore"
        assert dt is None
    
    def test_should_reset_counter_same_hour(self):
        """Test reset compteur même heure."""
        from src.services.push_notifications_utils import should_reset_counter
        
        assert should_reset_counter("user_2024011514", "user_2024011514") is False
    
    def test_should_reset_counter_new_hour(self):
        """Test reset compteur nouvelle heure."""
        from src.services.push_notifications_utils import should_reset_counter
        
        assert should_reset_counter("user_2024011514", "user_2024011515") is True


class TestValidation:
    """Tests pour la validation."""
    
    def test_validate_subscription_valid(self):
        """Test validation abonnement valide."""
        from src.services.push_notifications_utils import validate_subscription
        
        sub = {
            "endpoint": "https://push.example.com/abc",
            "keys": {"p256dh": "key1", "auth": "key2"}
        }
        
        is_valid, error = validate_subscription(sub)
        
        assert is_valid is True
        assert error == ""
    
    def test_validate_subscription_no_endpoint(self):
        """Test validation sans endpoint."""
        from src.services.push_notifications_utils import validate_subscription
        
        is_valid, error = validate_subscription({"keys": {}})
        
        assert is_valid is False
        assert "Endpoint" in error
    
    def test_validate_subscription_http_endpoint(self):
        """Test validation endpoint HTTP."""
        from src.services.push_notifications_utils import validate_subscription
        
        sub = {"endpoint": "http://insecure.com", "keys": {"p256dh": "a", "auth": "b"}}
        
        is_valid, error = validate_subscription(sub)
        
        assert is_valid is False
        assert "HTTPS" in error
    
    def test_validate_subscription_missing_keys(self):
        """Test validation clés manquantes."""
        from src.services.push_notifications_utils import validate_subscription
        
        sub = {"endpoint": "https://push.example.com", "keys": {}}
        
        is_valid, error = validate_subscription(sub)
        
        assert is_valid is False
    
    def test_validate_preferences_valid(self):
        """Test validation préférences valides."""
        from src.services.push_notifications_utils import validate_preferences
        
        prefs = {
            "quiet_hours_start": 22,
            "quiet_hours_end": 7,
            "max_per_hour": 5
        }
        
        is_valid, warnings = validate_preferences(prefs)
        
        assert is_valid is True
        assert len(warnings) == 0
    
    def test_validate_preferences_invalid_hours(self):
        """Test validation heures invalides."""
        from src.services.push_notifications_utils import validate_preferences
        
        prefs = {"quiet_hours_start": 25}  # Invalide
        
        is_valid, warnings = validate_preferences(prefs)
        
        assert is_valid is False
        assert len(warnings) > 0
    
    def test_validate_preferences_low_max_per_hour(self):
        """Test validation max_per_hour trop bas."""
        from src.services.push_notifications_utils import validate_preferences
        
        prefs = {"max_per_hour": 0}
        
        is_valid, warnings = validate_preferences(prefs)
        
        assert is_valid is False


class TestEdgeCases:
    """Tests pour les cas limites."""
    
    def test_notification_with_special_characters(self):
        """Test notification avec caractères spéciaux."""
        from src.services.push_notifications_utils import create_stock_notification
        
        notif = create_stock_notification("Bœuf haché (émincé)", 500, "g")
        
        assert "Bœuf" in notif["body"]
    
    def test_empty_preferences(self):
        """Test avec préférences vides."""
        from src.services.push_notifications_utils import (
            should_send_notification, NotificationType
        )
        
        should_send, reason = should_send_notification(NotificationType.STOCK_LOW, {})
        
        assert should_send is True
    
    def test_payload_with_empty_data(self):
        """Test payload avec data vide."""
        from src.services.push_notifications_utils import build_push_payload
        
        notif = {"title": "Test", "body": "Message", "data": {}}
        payload = build_push_payload(notif)
        
        data = json.loads(payload)
        assert "url" in data["data"]
    
    def test_quiet_hours_edge_midnight(self):
        """Test heures silencieuses à minuit."""
        from src.services.push_notifications_utils import is_quiet_hours
        
        # À minuit pile
        assert is_quiet_hours(0, 22, 7) is True
        assert is_quiet_hours(0, 0, 6) is True
    
    def test_expiration_exactly_today(self):
        """Test péremption aujourd'hui (0 jours)."""
        from src.services.push_notifications_utils import create_expiration_notification
        
        notif = create_expiration_notification("Lait", 0)
        
        assert "périmé" in notif["body"].lower() or "expiré" in notif["body"].lower()


class TestNotificationTypeEnum:
    """Tests pour l'enum NotificationType."""
    
    def test_notification_types_values(self):
        """Test valeurs de l'enum."""
        from src.services.push_notifications_utils import NotificationType
        
        assert NotificationType.STOCK_LOW.value == "stock_low"
        assert NotificationType.MEAL_REMINDER.value == "meal_reminder"
    
    def test_notification_type_from_string(self):
        """Test création depuis string."""
        from src.services.push_notifications_utils import NotificationType
        
        notif_type = NotificationType("stock_low")
        
        assert notif_type == NotificationType.STOCK_LOW
    
    def test_notification_type_invalid_string(self):
        """Test création depuis string invalide."""
        from src.services.push_notifications_utils import NotificationType
        
        with pytest.raises(ValueError):
            NotificationType("invalid_type")
