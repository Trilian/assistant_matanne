"""
Tests pour le module notifications (notifications.py) - VERSION CORRIGÃ‰E.

Tests couverts:
- Notification dataclass (pure Python, pas de mock nécessaire)
- NotificationType et NotificationCategory enums
- Sérialisation to_dict/from_dict
- Propriétés calculées (is_expired, age_str)
"""

from datetime import datetime, timedelta
from unittest.mock import patch

import pytest

from src.core.notifications import (
    Notification,
    NotificationCategory,
    NotificationType,
)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS ENUMS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestNotificationType:
    """Tests pour NotificationType enum."""

    def test_all_types_exist(self):
        """Test tous les types existent."""
        assert NotificationType.INFO
        assert NotificationType.SUCCESS
        assert NotificationType.WARNING
        assert NotificationType.ERROR
        assert NotificationType.ALERT

    def test_type_values(self):
        """Test valeurs des types."""
        assert NotificationType.INFO.value == "info"
        assert NotificationType.SUCCESS.value == "success"
        assert NotificationType.WARNING.value == "warning"
        assert NotificationType.ERROR.value == "error"
        assert NotificationType.ALERT.value == "alert"

    def test_type_from_string(self):
        """Test création depuis string."""
        assert NotificationType("info") == NotificationType.INFO
        assert NotificationType("success") == NotificationType.SUCCESS
        assert NotificationType("warning") == NotificationType.WARNING

    def test_invalid_type_raises(self):
        """Test type invalide lève une erreur."""
        with pytest.raises(ValueError):
            NotificationType("invalid")


class TestNotificationCategory:
    """Tests pour NotificationCategory enum."""

    def test_all_categories_exist(self):
        """Test toutes les catégories existent."""
        assert NotificationCategory.INVENTAIRE
        assert NotificationCategory.COURSES
        assert NotificationCategory.RECETTES
        assert NotificationCategory.PLANNING
        assert NotificationCategory.FAMILLE
        assert NotificationCategory.MAISON
        assert NotificationCategory.SYSTEME

    def test_category_values(self):
        """Test valeurs des catégories."""
        assert NotificationCategory.INVENTAIRE.value == "inventaire"
        assert NotificationCategory.COURSES.value == "courses"
        assert NotificationCategory.SYSTEME.value == "systeme"

    def test_category_from_string(self):
        """Test création depuis string."""
        assert NotificationCategory("inventaire") == NotificationCategory.INVENTAIRE
        assert NotificationCategory("planning") == NotificationCategory.PLANNING


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS NOTIFICATION DATACLASS (PURE PYTHON)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestNotificationCreation:
    """Tests création de Notification."""

    def test_create_minimal(self):
        """Test création minimale."""
        notif = Notification()
        
        assert notif.id is not None
        assert len(notif.id) == 8  # UUID[:8]
        assert notif.titre == ""
        assert notif.message == ""
        assert notif.type == NotificationType.INFO
        assert notif.category == NotificationCategory.SYSTEME
        assert notif.read is False
        assert notif.dismissed is False
        assert notif.priority == 0

    def test_create_with_message(self):
        """Test création avec message."""
        notif = Notification(
            titre="Test titre",
            message="Test message",
        )
        
        assert notif.titre == "Test titre"
        assert notif.message == "Test message"

    def test_create_with_type(self):
        """Test création avec type."""
        notif = Notification(
            type=NotificationType.WARNING,
            message="Attention!",
        )
        
        assert notif.type == NotificationType.WARNING

    def test_create_with_category(self):
        """Test création avec catégorie."""
        notif = Notification(
            category=NotificationCategory.INVENTAIRE,
            message="Stock bas",
        )
        
        assert notif.category == NotificationCategory.INVENTAIRE

    def test_create_with_all_fields(self):
        """Test création avec tous les champs."""
        now = datetime.now()
        expires = now + timedelta(hours=24)
        
        notif = Notification(
            id="test123",
            titre="Titre complet",
            message="Message complet",
            type=NotificationType.SUCCESS,
            category=NotificationCategory.RECETTES,
            icone="ðŸŽ‰",
            created_at=now,
            read=True,
            dismissed=False,
            action_label="Voir",
            action_module="recettes",
            action_data={"recette_id": 42},
            expires_at=expires,
            priority=2,
        )
        
        assert notif.id == "test123"
        assert notif.titre == "Titre complet"
        assert notif.message == "Message complet"
        assert notif.type == NotificationType.SUCCESS
        assert notif.category == NotificationCategory.RECETTES
        assert notif.icone == "ðŸŽ‰"
        assert notif.created_at == now
        assert notif.read is True
        assert notif.action_label == "Voir"
        assert notif.action_module == "recettes"
        assert notif.action_data == {"recette_id": 42}
        assert notif.expires_at == expires
        assert notif.priority == 2

    def test_auto_generated_id(self):
        """Test ID généré automatiquement est unique."""
        notif1 = Notification()
        notif2 = Notification()
        
        assert notif1.id != notif2.id

    def test_auto_generated_created_at(self):
        """Test created_at généré automatiquement."""
        before = datetime.now()
        notif = Notification()
        after = datetime.now()
        
        assert before <= notif.created_at <= after


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS PROPRIÃ‰TÃ‰S CALCULÃ‰ES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestNotificationIsExpired:
    """Tests pour la propriété is_expired."""

    def test_no_expiration(self):
        """Test sans date d'expiration."""
        notif = Notification(expires_at=None)
        assert notif.is_expired is False

    def test_not_expired(self):
        """Test non expiré."""
        future = datetime.now() + timedelta(hours=1)
        notif = Notification(expires_at=future)
        assert notif.is_expired is False

    def test_expired(self):
        """Test expiré."""
        past = datetime.now() - timedelta(hours=1)
        notif = Notification(expires_at=past)
        assert notif.is_expired is True

    def test_just_expired(self):
        """Test tout juste expiré."""
        past = datetime.now() - timedelta(seconds=1)
        notif = Notification(expires_at=past)
        assert notif.is_expired is True


class TestNotificationAgeStr:
    """Tests pour la propriété age_str."""

    def test_just_now(self):
        """Test à l'instant."""
        notif = Notification(created_at=datetime.now())
        assert notif.age_str == "Ã€ l'instant"

    def test_few_minutes_ago(self):
        """Test il y a quelques minutes."""
        notif = Notification(created_at=datetime.now() - timedelta(minutes=5))
        assert "5 min" in notif.age_str

    def test_one_hour_ago(self):
        """Test il y a une heure."""
        notif = Notification(created_at=datetime.now() - timedelta(hours=1, minutes=30))
        assert "1h" in notif.age_str

    def test_yesterday(self):
        """Test hier (la logique vérifie days == 1)."""
        # Note: age_str utilise delta.days qui est 0 si < 24h
        # Pour avoir "Hier", il faut delta.days == 1
        notif = Notification(created_at=datetime.now() - timedelta(days=1, hours=1))
        # Selon l'implémentation: delta.days == 1 retourne "Hier"
        assert notif.age_str == "Hier"

    def test_several_days_ago(self):
        """Test il y a plusieurs jours."""
        # delta.days > 1 retourne "Il y a X jours"
        notif = Notification(created_at=datetime.now() - timedelta(days=5, hours=1))
        assert "5 jours" in notif.age_str


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS SÃ‰RIALISATION
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestNotificationToDict:
    """Tests pour to_dict()."""

    def test_to_dict_minimal(self):
        """Test sérialisation minimale."""
        notif = Notification(
            id="abc123",
            message="Test",
            type=NotificationType.INFO,
        )
        
        data = notif.to_dict()
        
        assert data["id"] == "abc123"
        assert data["message"] == "Test"
        assert data["type"] == "info"
        assert data["category"] == "systeme"
        assert data["read"] is False
        assert "created_at" in data

    def test_to_dict_complete(self):
        """Test sérialisation complète."""
        notif = Notification(
            id="xyz789",
            titre="Titre",
            message="Message",
            type=NotificationType.WARNING,
            category=NotificationCategory.INVENTAIRE,
            icone="âš ï¸",
            read=True,
            dismissed=True,
            action_label="Action",
            action_module="inventaire",
            priority=1,
        )
        
        data = notif.to_dict()
        
        assert data["id"] == "xyz789"
        assert data["titre"] == "Titre"
        assert data["message"] == "Message"
        assert data["type"] == "warning"
        assert data["category"] == "inventaire"
        assert data["icone"] == "âš ï¸"
        assert data["read"] is True
        assert data["dismissed"] is True
        assert data["action_label"] == "Action"
        assert data["action_module"] == "inventaire"
        assert data["priority"] == 1

    def test_to_dict_datetime_serialized(self):
        """Test datetime est sérialisé en ISO."""
        now = datetime(2024, 1, 15, 10, 30, 0)
        notif = Notification(created_at=now)
        
        data = notif.to_dict()
        
        assert data["created_at"] == "2024-01-15T10:30:00"


class TestNotificationFromDict:
    """Tests pour from_dict()."""

    def test_from_dict_minimal(self):
        """Test désérialisation minimale."""
        data = {
            "id": "test123",
            "message": "Hello",
            "type": "success",
            "category": "courses",
            "created_at": "2024-01-15T10:30:00",
        }
        
        notif = Notification.from_dict(data)
        
        assert notif.id == "test123"
        assert notif.message == "Hello"
        assert notif.type == NotificationType.SUCCESS
        assert notif.category == NotificationCategory.COURSES
        assert notif.created_at == datetime(2024, 1, 15, 10, 30, 0)

    def test_from_dict_defaults(self):
        """Test valeurs par défaut lors de la désérialisation."""
        data = {}
        
        notif = Notification.from_dict(data)
        
        assert notif.titre == ""
        assert notif.message == ""
        assert notif.type == NotificationType.INFO
        assert notif.category == NotificationCategory.SYSTEME
        assert notif.read is False

    def test_from_dict_complete(self):
        """Test désérialisation complète."""
        data = {
            "id": "full123",
            "titre": "Titre complet",
            "message": "Message complet",
            "type": "error",
            "category": "famille",
            "icone": "âŒ",
            "created_at": "2024-06-01T14:00:00",
            "read": True,
            "dismissed": False,
            "action_label": "Corriger",
            "action_module": "famille",
            "priority": 2,
        }
        
        notif = Notification.from_dict(data)
        
        assert notif.id == "full123"
        assert notif.titre == "Titre complet"
        assert notif.message == "Message complet"
        assert notif.type == NotificationType.ERROR
        assert notif.category == NotificationCategory.FAMILLE
        assert notif.icone == "âŒ"
        assert notif.read is True
        assert notif.dismissed is False
        assert notif.action_label == "Corriger"
        assert notif.action_module == "famille"
        assert notif.priority == 2


class TestNotificationRoundTrip:
    """Tests de conversion aller-retour."""

    def test_roundtrip_preserves_data(self):
        """Test to_dict -> from_dict préserve les données."""
        original = Notification(
            titre="Original",
            message="Test roundtrip",
            type=NotificationType.WARNING,
            category=NotificationCategory.PLANNING,
            icone="ðŸ“…",
            read=True,
            action_label="Voir",
            priority=1,
        )
        
        data = original.to_dict()
        restored = Notification.from_dict(data)
        
        assert restored.titre == original.titre
        assert restored.message == original.message
        assert restored.type == original.type
        assert restored.category == original.category
        assert restored.icone == original.icone
        assert restored.read == original.read
        assert restored.action_label == original.action_label
        assert restored.priority == original.priority


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS PRIORITY
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestNotificationPriority:
    """Tests pour la priorité des notifications."""

    def test_default_priority(self):
        """Test priorité par défaut."""
        notif = Notification()
        assert notif.priority == 0

    def test_priority_normal(self):
        """Test priorité normale."""
        notif = Notification(priority=0)
        assert notif.priority == 0

    def test_priority_important(self):
        """Test priorité importante."""
        notif = Notification(priority=1)
        assert notif.priority == 1

    def test_priority_urgent(self):
        """Test priorité urgente."""
        notif = Notification(priority=2)
        assert notif.priority == 2


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS ICÃ”NES PAR DÃ‰FAUT
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestNotificationIcunes:
    """Tests pour les icônes."""

    def test_default_icone(self):
        """Test icône par défaut."""
        notif = Notification()
        assert notif.icone == "â„¹ï¸"

    def test_custom_icone(self):
        """Test icône personnalisée."""
        notif = Notification(icone="ðŸ””")
        assert notif.icone == "ðŸ””"

    def test_icone_preserved_in_roundtrip(self):
        """Test icône préservée après conversion."""
        original = Notification(icone="ðŸŽ¯")
        data = original.to_dict()
        restored = Notification.from_dict(data)
        assert restored.icone == "ðŸŽ¯"

