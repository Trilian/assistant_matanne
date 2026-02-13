"""
Tests supplÃ©mentaires pour notifications.py - amÃ©lioration de la couverture

Cible les composants non couverts:
- NotificationType, NotificationCategory enums
- Notification dataclass (is_expired, age_str, to_dict, from_dict)
- NotificationManager class (add, get_all, mark_as_read, etc.)
- Helper functions (notify_info, notify_success, etc.)
- UI render functions (mocked)
"""

from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest


class TestNotificationType:
    """Tests pour NotificationType enum."""

    def test_info_value(self):
        """INFO a la valeur 'info'."""
        from src.core.notifications import NotificationType

        assert NotificationType.INFO.value == "info"

    def test_success_value(self):
        """SUCCESS a la valeur 'success'."""
        from src.core.notifications import NotificationType

        assert NotificationType.SUCCESS.value == "success"

    def test_warning_value(self):
        """WARNING a la valeur 'warning'."""
        from src.core.notifications import NotificationType

        assert NotificationType.WARNING.value == "warning"

    def test_error_value(self):
        """ERROR a la valeur 'error'."""
        from src.core.notifications import NotificationType

        assert NotificationType.ERROR.value == "error"

    def test_alert_value(self):
        """ALERT a la valeur 'alert'."""
        from src.core.notifications import NotificationType

        assert NotificationType.ALERT.value == "alert"


class TestNotificationCategory:
    """Tests pour NotificationCategory enum."""

    def test_inventaire_value(self):
        """INVENTAIRE a la valeur 'inventaire'."""
        from src.core.notifications import NotificationCategory

        assert NotificationCategory.INVENTAIRE.value == "inventaire"

    def test_courses_value(self):
        """COURSES a la valeur 'courses'."""
        from src.core.notifications import NotificationCategory

        assert NotificationCategory.COURSES.value == "courses"

    def test_systeme_value(self):
        """SYSTEME a la valeur 'systeme'."""
        from src.core.notifications import NotificationCategory

        assert NotificationCategory.SYSTEME.value == "systeme"


class TestNotification:
    """Tests pour Notification dataclass."""

    def test_notification_defaults(self):
        """Valeurs par dÃ©faut correctes."""
        from src.core.notifications import Notification, NotificationCategory, NotificationType

        notif = Notification(titre="Test", message="Message")

        assert notif.titre == "Test"
        assert notif.message == "Message"
        assert notif.type == NotificationType.INFO
        assert notif.category == NotificationCategory.SYSTEME
        assert notif.read is False
        assert notif.dismissed is False
        assert notif.priority == 0
        assert notif.id is not None

    def test_is_expired_false_when_no_expiry(self):
        """is_expired retourne False si pas d'expiration."""
        from src.core.notifications import Notification

        notif = Notification(titre="Test", expires_at=None)
        assert notif.is_expired is False

    def test_is_expired_true_when_past(self):
        """is_expired retourne True si date passÃ©e."""
        from src.core.notifications import Notification

        notif = Notification(titre="Test", expires_at=datetime.now() - timedelta(hours=1))
        assert notif.is_expired is True

    def test_is_expired_false_when_future(self):
        """is_expired retourne False si date future."""
        from src.core.notifications import Notification

        notif = Notification(titre="Test", expires_at=datetime.now() + timedelta(hours=1))
        assert notif.is_expired is False

    def test_age_str_instant(self):
        """age_str retourne 'Ã€ l'instant' pour notification rÃ©cente."""
        from src.core.notifications import Notification

        notif = Notification(titre="Test", created_at=datetime.now())
        assert notif.age_str == "Ã€ l'instant"

    def test_age_str_minutes(self):
        """age_str retourne format minutes."""
        from src.core.notifications import Notification

        notif = Notification(titre="Test", created_at=datetime.now() - timedelta(minutes=30))
        assert "min" in notif.age_str

    def test_age_str_hours(self):
        """age_str retourne format heures."""
        from src.core.notifications import Notification

        notif = Notification(titre="Test", created_at=datetime.now() - timedelta(hours=3))
        assert "h" in notif.age_str

    def test_age_str_yesterday(self):
        """age_str retourne 'Hier' pour notification d'hier."""
        from src.core.notifications import Notification

        notif = Notification(titre="Test", created_at=datetime.now() - timedelta(days=1))
        assert notif.age_str == "Hier"

    def test_age_str_days(self):
        """age_str retourne format jours."""
        from src.core.notifications import Notification

        notif = Notification(titre="Test", created_at=datetime.now() - timedelta(days=5))
        assert "jours" in notif.age_str

    def test_to_dict(self):
        """to_dict convertit correctement en dictionnaire."""
        from src.core.notifications import Notification, NotificationType

        notif = Notification(
            id="abc123",
            titre="Test",
            message="Message",
            type=NotificationType.WARNING,
            priority=1,
        )

        d = notif.to_dict()

        assert d["id"] == "abc123"
        assert d["titre"] == "Test"
        assert d["message"] == "Message"
        assert d["type"] == "warning"
        assert d["priority"] == 1
        assert "created_at" in d

    def test_to_dict_with_expires(self):
        """to_dict inclut expires_at."""
        from src.core.notifications import Notification

        expires = datetime.now() + timedelta(hours=1)
        notif = Notification(titre="Test", expires_at=expires)

        d = notif.to_dict()
        assert d["expires_at"] is not None

    def test_from_dict(self):
        """from_dict crÃ©e correctement depuis un dictionnaire."""
        from src.core.notifications import Notification, NotificationType

        data = {
            "id": "xyz789",
            "titre": "From Dict",
            "message": "Test message",
            "type": "error",
            "category": "inventaire",
            "priority": 2,
            "read": True,
            "created_at": datetime.now().isoformat(),
        }

        notif = Notification.from_dict(data)

        assert notif.id == "xyz789"
        assert notif.titre == "From Dict"
        assert notif.type == NotificationType.ERROR
        assert notif.priority == 2
        assert notif.read is True

    def test_from_dict_with_expires(self):
        """from_dict parse expires_at correctement."""
        from src.core.notifications import Notification

        expires = datetime.now() + timedelta(hours=2)
        data = {
            "titre": "Test",
            "expires_at": expires.isoformat(),
            "created_at": datetime.now().isoformat(),
        }

        notif = Notification.from_dict(data)
        assert notif.expires_at is not None

    def test_from_dict_handles_invalid_expires(self):
        """from_dict gÃ¨re expires_at invalide."""
        from src.core.notifications import Notification

        data = {
            "titre": "Test",
            "expires_at": "invalid-date",
            "created_at": datetime.now().isoformat(),
        }

        notif = Notification.from_dict(data)
        assert notif.expires_at is None


class TestNotificationManager:
    """Tests pour NotificationManager."""

    @pytest.fixture(autouse=True)
    def mock_session_state(self):
        """Mock st.session_state pour chaque test."""
        with patch("src.core.notifications.st") as mock_st:
            mock_st.session_state = {}
            yield mock_st

    def test_add_notification(self, mock_session_state):
        """Ajoute une notification."""
        from src.core.notifications import NotificationManager, NotificationType

        notif = NotificationManager.add(
            titre="Test Notif",
            message="Test message",
            type=NotificationType.INFO,
        )

        assert notif.titre == "Test Notif"
        assert notif.message == "Test message"
        assert len(mock_session_state.session_state.get("_notifications_store", [])) == 1

    def test_add_with_expiration(self, mock_session_state):
        """Ajoute notification avec expiration."""
        from src.core.notifications import NotificationManager

        notif = NotificationManager.add(
            titre="Expires Soon",
            expires_hours=24,
        )

        assert notif.expires_at is not None

    def test_add_auto_icon(self, mock_session_state):
        """Ajoute icÃ´ne automatique selon le type."""
        from src.core.notifications import NotificationManager, NotificationType

        notif_success = NotificationManager.add(
            titre="Success",
            type=NotificationType.SUCCESS,
        )
        assert notif_success.icone == "âœ…"

        notif_warning = NotificationManager.add(
            titre="Warning",
            type=NotificationType.WARNING,
        )
        assert notif_warning.icone == "âš ï¸"

        notif_error = NotificationManager.add(
            titre="Error",
            type=NotificationType.ERROR,
        )
        assert notif_error.icone == "âŒ"

    def test_max_notifications_limit(self, mock_session_state):
        """Limite le nombre de notifications."""
        from src.core.notifications import NotificationManager

        # Ajouter plus que le max
        for i in range(60):
            NotificationManager.add(titre=f"Notif {i}")

        store = mock_session_state.session_state.get("_notifications_store", [])
        assert len(store) <= NotificationManager.MAX_NOTIFICATIONS

    def test_get_all_empty(self, mock_session_state):
        """Retourne liste vide si pas de notifications."""
        from src.core.notifications import NotificationManager

        result = NotificationManager.get_all()
        assert result == []

    def test_get_all_filters_expired(self, mock_session_state):
        """Filtre les notifications expirÃ©es."""
        from src.core.notifications import NotificationManager

        # Ajouter notification expirÃ©e manuellement
        expired = {
            "id": "exp1",
            "titre": "Expired",
            "message": "",
            "type": "info",
            "category": "systeme",
            "icone": "â„¹ï¸",
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() - timedelta(hours=1)).isoformat(),
            "read": False,
            "dismissed": False,
            "priority": 0,
        }
        mock_session_state.session_state["_notifications_store"] = [expired]

        result = NotificationManager.get_all()
        assert len(result) == 0

    def test_get_all_filters_read(self, mock_session_state):
        """Filtre les notifications lues si demandÃ©."""
        from src.core.notifications import NotificationManager

        read_notif = {
            "id": "read1",
            "titre": "Read",
            "message": "",
            "type": "info",
            "category": "systeme",
            "icone": "â„¹ï¸",
            "created_at": datetime.now().isoformat(),
            "read": True,
            "dismissed": False,
            "priority": 0,
        }
        mock_session_state.session_state["_notifications_store"] = [read_notif]

        result = NotificationManager.get_all(include_read=False)
        assert len(result) == 0

        result = NotificationManager.get_all(include_read=True)
        assert len(result) == 1

    def test_get_all_filters_by_category(self, mock_session_state):
        """Filtre par catÃ©gorie."""
        from src.core.notifications import NotificationCategory, NotificationManager

        notif1 = {
            "id": "1",
            "titre": "Inventaire",
            "type": "info",
            "category": "inventaire",
            "icone": "â„¹ï¸",
            "created_at": datetime.now().isoformat(),
            "read": False,
            "dismissed": False,
            "priority": 0,
        }
        notif2 = {
            "id": "2",
            "titre": "Courses",
            "type": "info",
            "category": "courses",
            "icone": "â„¹ï¸",
            "created_at": datetime.now().isoformat(),
            "read": False,
            "dismissed": False,
            "priority": 0,
        }
        mock_session_state.session_state["_notifications_store"] = [notif1, notif2]

        result = NotificationManager.get_all(category=NotificationCategory.INVENTAIRE)
        assert len(result) == 1
        assert result[0].titre == "Inventaire"

    def test_get_unread_count(self, mock_session_state):
        """Compte les notifications non lues."""
        from src.core.notifications import NotificationManager

        notif1 = {
            "id": "1",
            "titre": "Unread",
            "type": "info",
            "category": "systeme",
            "icone": "â„¹ï¸",
            "created_at": datetime.now().isoformat(),
            "read": False,
            "dismissed": False,
            "priority": 0,
        }
        notif2 = {
            "id": "2",
            "titre": "Read",
            "type": "info",
            "category": "systeme",
            "icone": "â„¹ï¸",
            "created_at": datetime.now().isoformat(),
            "read": True,
            "dismissed": False,
            "priority": 0,
        }
        mock_session_state.session_state["_notifications_store"] = [notif1, notif2]

        count = NotificationManager.get_unread_count()
        assert count == 1

    def test_mark_as_read(self, mock_session_state):
        """Marque une notification comme lue."""
        from src.core.notifications import NotificationManager

        notif = {
            "id": "test123",
            "titre": "Test",
            "type": "info",
            "category": "systeme",
            "icone": "â„¹ï¸",
            "created_at": datetime.now().isoformat(),
            "read": False,
            "dismissed": False,
            "priority": 0,
        }
        mock_session_state.session_state["_notifications_store"] = [notif]

        result = NotificationManager.mark_as_read("test123")
        assert result is True
        assert mock_session_state.session_state["_notifications_store"][0]["read"] is True

    def test_mark_as_read_not_found(self, mock_session_state):
        """Retourne False si notification non trouvÃ©e."""
        from src.core.notifications import NotificationManager

        mock_session_state.session_state["_notifications_store"] = []

        result = NotificationManager.mark_as_read("nonexistent")
        assert result is False

    def test_mark_all_read(self, mock_session_state):
        """Marque toutes les notifications comme lues."""
        from src.core.notifications import NotificationManager

        notifications = [
            {"id": "1", "read": False, "category": "systeme"},
            {"id": "2", "read": False, "category": "systeme"},
            {"id": "3", "read": True, "category": "systeme"},
        ]
        mock_session_state.session_state["_notifications_store"] = notifications

        count = NotificationManager.mark_all_read()
        assert count == 2

    def test_dismiss(self, mock_session_state):
        """Ignore une notification."""
        from src.core.notifications import NotificationManager

        notif = {
            "id": "dismiss1",
            "titre": "Test",
            "dismissed": False,
        }
        mock_session_state.session_state["_notifications_store"] = [notif]

        result = NotificationManager.dismiss("dismiss1")
        assert result is True
        assert mock_session_state.session_state["_notifications_store"][0]["dismissed"] is True

    def test_clear_all(self, mock_session_state):
        """Supprime toutes les notifications."""
        from src.core.notifications import NotificationManager

        mock_session_state.session_state["_notifications_store"] = [
            {"id": "1"},
            {"id": "2"},
            {"id": "3"},
        ]

        count = NotificationManager.clear_all()
        assert count == 3
        assert mock_session_state.session_state["_notifications_store"] == []

    def test_clear_all_by_category(self, mock_session_state):
        """Supprime notifications d'une catÃ©gorie."""
        from src.core.notifications import NotificationCategory, NotificationManager

        mock_session_state.session_state["_notifications_store"] = [
            {"id": "1", "category": "inventaire"},
            {"id": "2", "category": "courses"},
            {"id": "3", "category": "inventaire"},
        ]

        count = NotificationManager.clear_all(category=NotificationCategory.INVENTAIRE)
        assert count == 2
        assert len(mock_session_state.session_state["_notifications_store"]) == 1

    def test_cleanup_expired(self, mock_session_state):
        """Nettoie les notifications expirÃ©es."""
        from src.core.notifications import NotificationManager

        expired = {
            "id": "exp",
            "expires_at": (datetime.now() - timedelta(hours=1)).isoformat(),
        }
        valid = {
            "id": "valid",
            "expires_at": (datetime.now() + timedelta(hours=1)).isoformat(),
        }
        no_expiry = {
            "id": "no_exp",
        }
        mock_session_state.session_state["_notifications_store"] = [expired, valid, no_expiry]

        removed = NotificationManager.cleanup_expired()
        assert removed == 1
        assert len(mock_session_state.session_state["_notifications_store"]) == 2


class TestHelperFunctions:
    """Tests pour les fonctions helper."""

    @pytest.fixture(autouse=True)
    def mock_session_state(self):
        """Mock st.session_state pour chaque test."""
        with patch("src.core.notifications.st") as mock_st:
            mock_st.session_state = {}
            yield mock_st

    def test_notify_info(self, mock_session_state):
        """notify_info crÃ©e notification INFO."""
        from src.core.notifications import NotificationType, notify_info

        notif = notify_info("Info Title", "Info message")

        assert notif.type == NotificationType.INFO
        assert notif.titre == "Info Title"

    def test_notify_success(self, mock_session_state):
        """notify_success crÃ©e notification SUCCESS."""
        from src.core.notifications import NotificationType, notify_success

        notif = notify_success("Success Title")

        assert notif.type == NotificationType.SUCCESS

    def test_notify_warning(self, mock_session_state):
        """notify_warning crÃ©e notification WARNING avec priority 1."""
        from src.core.notifications import NotificationType, notify_warning

        notif = notify_warning("Warning Title")

        assert notif.type == NotificationType.WARNING
        assert notif.priority == 1

    def test_notify_error(self, mock_session_state):
        """notify_error crÃ©e notification ERROR avec priority 2."""
        from src.core.notifications import NotificationType, notify_error

        notif = notify_error("Error Title")

        assert notif.type == NotificationType.ERROR
        assert notif.priority == 2

    def test_notify_stock_bas(self, mock_session_state):
        """notify_stock_bas crÃ©e notification stock bas."""
        from src.core.notifications import NotificationCategory, notify_stock_bas

        notif = notify_stock_bas("Lait", 0.5, 1.0)

        assert "stock bas" in notif.titre.lower()
        assert notif.category == NotificationCategory.INVENTAIRE
        assert notif.action_module == "cuisine.inventaire"

    def test_notify_peremption_soon(self, mock_session_state):
        """notify_peremption pour produit expirant bientÃ´t."""
        from src.core.notifications import NotificationType, notify_peremption

        notif = notify_peremption("Yaourt", 3)

        assert "expire" in notif.titre.lower()
        assert notif.type == NotificationType.WARNING
        assert notif.priority == 1

    def test_notify_peremption_expired(self, mock_session_state):
        """notify_peremption pour produit expirÃ©."""
        from src.core.notifications import NotificationType, notify_peremption

        notif = notify_peremption("Lait", 0)

        assert "EXPIRÃ‰" in notif.titre
        assert notif.type == NotificationType.ERROR
        assert notif.priority == 2


class TestUIComponents:
    """Tests pour les composants UI (avec mocks)."""

    @pytest.fixture(autouse=True)
    def mock_streamlit(self):
        """Mock streamlit pour les composants UI."""
        with patch("src.core.notifications.st") as mock_st:
            mock_st.session_state = {}
            mock_st.markdown = MagicMock()
            mock_st.expander = MagicMock()
            mock_st.columns = MagicMock(return_value=[MagicMock(), MagicMock()])
            mock_st.button = MagicMock(return_value=False)
            mock_st.info = MagicMock()
            mock_st.success = MagicMock()
            mock_st.warning = MagicMock()
            mock_st.error = MagicMock()
            yield mock_st

    def test_render_notification_badge_no_notifications(self, mock_streamlit):
        """Badge retourne 0 si pas de notifications."""
        from src.core.notifications import render_notification_badge

        count = render_notification_badge()
        assert count == 0

    def test_render_notification_badge_with_count(self, mock_streamlit):
        """Badge affiche le nombre de non-lues."""
        from src.core.notifications import render_notification_badge

        # Ajouter notification non-lue
        mock_streamlit.session_state["_notifications_store"] = [
            {
                "id": "1",
                "titre": "Test",
                "type": "info",
                "category": "systeme",
                "icone": "â„¹ï¸",
                "created_at": datetime.now().isoformat(),
                "read": False,
                "dismissed": False,
                "priority": 0,
            }
        ]

        count = render_notification_badge()
        assert count == 1
        mock_streamlit.markdown.assert_called_once()

    def test_render_toast_notifications(self, mock_streamlit):
        """Affiche les notifications rÃ©centes en toast."""
        from src.core.notifications import render_toast_notifications

        # Ajouter notification rÃ©cente
        mock_streamlit.session_state["_notifications_store"] = [
            {
                "id": "1",
                "titre": "Toast Test",
                "type": "success",
                "category": "systeme",
                "icone": "âœ…",
                "created_at": datetime.now().isoformat(),
                "read": False,
                "dismissed": False,
                "priority": 0,
            }
        ]

        render_toast_notifications()
        # Doit avoir appelÃ© st.success pour la notification success
        mock_streamlit.success.assert_called()
