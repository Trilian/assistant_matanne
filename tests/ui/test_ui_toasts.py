"""
Tests pour src/ui/feedback/toasts.py
Gestion des notifications toast
"""

from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# FIXTURES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.fixture
def mock_streamlit():
    """Mock Streamlit avec session_state"""
    with patch("src.ui.feedback.toasts.st") as mock_st:
        mock_st.session_state = {}
        mock_st.success = MagicMock()
        mock_st.error = MagicMock()
        mock_st.warning = MagicMock()
        mock_st.info = MagicMock()
        mock_st.container = MagicMock(return_value=MagicMock(__enter__=MagicMock(), __exit__=MagicMock()))
        yield mock_st


@pytest.fixture
def reset_toast_manager():
    """Reset ToastManager entre les tests"""
    with patch("src.ui.feedback.toasts.st") as mock_st:
        mock_st.session_state = {}
        yield
        mock_st.session_state = {}


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS TOAST MANAGER
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestToastManager:
    """Tests pour ToastManager"""

    def test_init_creates_session_state(self, mock_streamlit):
        """Test initialisation crée la clé session_state"""
        from src.ui.feedback.toasts import ToastManager

        ToastManager._init()

        assert ToastManager.TOAST_KEY in mock_streamlit.session_state
        assert mock_streamlit.session_state[ToastManager.TOAST_KEY] == []

    def test_init_preserves_existing_state(self, mock_streamlit):
        """Test init ne réinitialise pas un état existant"""
        from src.ui.feedback.toasts import ToastManager

        # Préparation
        existing_toasts = [{"message": "existing"}]
        mock_streamlit.session_state[ToastManager.TOAST_KEY] = existing_toasts

        ToastManager._init()

        assert mock_streamlit.session_state[ToastManager.TOAST_KEY] == existing_toasts

    def test_show_adds_toast(self, mock_streamlit):
        """Test show() ajoute un toast"""
        from src.ui.feedback.toasts import ToastManager

        ToastManager.show("Test message", "success", 3)

        toasts = mock_streamlit.session_state[ToastManager.TOAST_KEY]
        assert len(toasts) == 1
        assert toasts[0]["message"] == "Test message"
        assert toasts[0]["type"] == "success"

    def test_show_multiple_toasts(self, mock_streamlit):
        """Test plusieurs toasts"""
        from src.ui.feedback.toasts import ToastManager

        ToastManager.show("Message 1", "success")
        ToastManager.show("Message 2", "error")
        ToastManager.show("Message 3", "warning")

        toasts = mock_streamlit.session_state[ToastManager.TOAST_KEY]
        assert len(toasts) == 3

    def test_show_sets_expiration(self, mock_streamlit):
        """Test show() définit l'expiration"""
        from src.ui.feedback.toasts import ToastManager

        before = datetime.now()
        ToastManager.show("Test", "info", duration=5)
        after = datetime.now()

        toast = mock_streamlit.session_state[ToastManager.TOAST_KEY][0]

        # Vérifier que expires_at est ~5 secondes dans le futur
        expected_min = before + timedelta(seconds=5)
        expected_max = after + timedelta(seconds=5)

        assert toast["expires_at"] >= expected_min
        assert toast["expires_at"] <= expected_max

    def test_render_filters_expired(self, mock_streamlit):
        """Test render() filtre les toasts expirés"""
        from src.ui.feedback.toasts import ToastManager

        # Créer un toast expiré
        mock_streamlit.session_state[ToastManager.TOAST_KEY] = [
            {
                "message": "Expiré",
                "type": "info",
                "created_at": datetime.now() - timedelta(seconds=10),
                "expires_at": datetime.now() - timedelta(seconds=5),
            }
        ]

        ToastManager.render()

        # Le toast expiré doit être supprimé
        assert len(mock_streamlit.session_state[ToastManager.TOAST_KEY]) == 0

    def test_render_displays_active_toasts(self, mock_streamlit):
        """Test render() affiche les toasts actifs"""
        from src.ui.feedback.toasts import ToastManager

        # Créer un toast actif
        mock_streamlit.session_state[ToastManager.TOAST_KEY] = [
            {
                "message": "Actif",
                "type": "success",
                "created_at": datetime.now(),
                "expires_at": datetime.now() + timedelta(seconds=10),
            }
        ]

        # Mock container context
        mock_container = MagicMock()
        mock_container.__enter__ = MagicMock(return_value=None)
        mock_container.__exit__ = MagicMock(return_value=None)
        mock_streamlit.container.return_value = mock_container

        ToastManager.render()

        mock_streamlit.success.assert_called_once_with("Actif")

    def test_render_displays_max_3_toasts(self, mock_streamlit):
        """Test render() affiche max 3 toasts"""
        from src.ui.feedback.toasts import ToastManager

        # Créer 5 toasts actifs
        mock_streamlit.session_state[ToastManager.TOAST_KEY] = [
            {
                "message": f"Toast {i}",
                "type": "info",
                "created_at": datetime.now(),
                "expires_at": datetime.now() + timedelta(seconds=10),
            }
            for i in range(5)
        ]

        mock_container = MagicMock()
        mock_container.__enter__ = MagicMock(return_value=None)
        mock_container.__exit__ = MagicMock(return_value=None)
        mock_streamlit.container.return_value = mock_container

        ToastManager.render()

        # Seulement 3 appels (les 3 derniers)
        assert mock_streamlit.info.call_count == 3

    def test_render_correct_type_functions(self, mock_streamlit):
        """Test render() utilise les bonnes fonctions par type"""
        from src.ui.feedback.toasts import ToastManager

        mock_streamlit.session_state[ToastManager.TOAST_KEY] = [
            {"message": "Success", "type": "success", "created_at": datetime.now(), "expires_at": datetime.now() + timedelta(seconds=10)},
            {"message": "Error", "type": "error", "created_at": datetime.now(), "expires_at": datetime.now() + timedelta(seconds=10)},
            {"message": "Warning", "type": "warning", "created_at": datetime.now(), "expires_at": datetime.now() + timedelta(seconds=10)},
        ]

        mock_container = MagicMock()
        mock_container.__enter__ = MagicMock(return_value=None)
        mock_container.__exit__ = MagicMock(return_value=None)
        mock_streamlit.container.return_value = mock_container

        ToastManager.render()

        mock_streamlit.success.assert_called_with("Success")
        mock_streamlit.error.assert_called_with("Error")
        mock_streamlit.warning.assert_called_with("Warning")

    def test_render_unknown_type_uses_info(self, mock_streamlit):
        """Test type inconnu utilise info"""
        from src.ui.feedback.toasts import ToastManager

        mock_streamlit.session_state[ToastManager.TOAST_KEY] = [
            {"message": "Unknown", "type": "unknown_type", "created_at": datetime.now(), "expires_at": datetime.now() + timedelta(seconds=10)}
        ]

        mock_container = MagicMock()
        mock_container.__enter__ = MagicMock(return_value=None)
        mock_container.__exit__ = MagicMock(return_value=None)
        mock_streamlit.container.return_value = mock_container

        ToastManager.render()

        mock_streamlit.info.assert_called_with("Unknown")

    def test_render_no_active_toasts(self, mock_streamlit):
        """Test render() sans toasts actifs"""
        from src.ui.feedback.toasts import ToastManager

        mock_streamlit.session_state[ToastManager.TOAST_KEY] = []

        ToastManager.render()

        # Aucune fonction d'affichage appelée
        mock_streamlit.success.assert_not_called()
        mock_streamlit.error.assert_not_called()
        mock_streamlit.warning.assert_not_called()
        mock_streamlit.info.assert_not_called()


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS HELPER FUNCTIONS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestShowSuccess:
    """Tests pour show_success()"""

    def test_show_success_default(self, mock_streamlit):
        """Test show_success() par défaut"""
        from src.ui.feedback.toasts import show_success

        show_success("Sauvegarde réussie")

        toast = mock_streamlit.session_state["toast_notifications"][0]
        assert toast["message"] == "Sauvegarde réussie"
        assert toast["type"] == "success"

    def test_show_success_custom_duration(self, mock_streamlit):
        """Test show_success() avec durée personnalisée"""
        from src.ui.feedback.toasts import show_success

        before = datetime.now()
        show_success("Test", duration=10)
        after = datetime.now()

        toast = mock_streamlit.session_state["toast_notifications"][0]

        # Vérifier durée ~10 secondes
        expected_min = before + timedelta(seconds=10)
        expected_max = after + timedelta(seconds=10)

        assert toast["expires_at"] >= expected_min
        assert toast["expires_at"] <= expected_max


class TestShowError:
    """Tests pour show_error()"""

    def test_show_error_default(self, mock_streamlit):
        """Test show_error() par défaut"""
        from src.ui.feedback.toasts import show_error

        show_error("Erreur critique")

        toast = mock_streamlit.session_state["toast_notifications"][0]
        assert toast["message"] == "Erreur critique"
        assert toast["type"] == "error"

    def test_show_error_default_duration_is_5(self, mock_streamlit):
        """Test show_error() durée par défaut = 5s"""
        from src.ui.feedback.toasts import show_error

        before = datetime.now()
        show_error("Test")
        after = datetime.now()

        toast = mock_streamlit.session_state["toast_notifications"][0]

        # Vérifier durée ~5 secondes (défaut pour error)
        expected_min = before + timedelta(seconds=5)
        expected_max = after + timedelta(seconds=5)

        assert toast["expires_at"] >= expected_min
        assert toast["expires_at"] <= expected_max


class TestShowWarning:
    """Tests pour show_warning()"""

    def test_show_warning_default(self, mock_streamlit):
        """Test show_warning() par défaut"""
        from src.ui.feedback.toasts import show_warning

        show_warning("Attention!")

        toast = mock_streamlit.session_state["toast_notifications"][0]
        assert toast["message"] == "Attention!"
        assert toast["type"] == "warning"

    def test_show_warning_default_duration_is_4(self, mock_streamlit):
        """Test show_warning() durée par défaut = 4s"""
        from src.ui.feedback.toasts import show_warning

        before = datetime.now()
        show_warning("Test")
        after = datetime.now()

        toast = mock_streamlit.session_state["toast_notifications"][0]

        expected_min = before + timedelta(seconds=4)
        expected_max = after + timedelta(seconds=4)

        assert toast["expires_at"] >= expected_min
        assert toast["expires_at"] <= expected_max


class TestShowInfo:
    """Tests pour show_info()"""

    def test_show_info_default(self, mock_streamlit):
        """Test show_info() par défaut"""
        from src.ui.feedback.toasts import show_info

        show_info("Information")

        toast = mock_streamlit.session_state["toast_notifications"][0]
        assert toast["message"] == "Information"
        assert toast["type"] == "info"

    def test_show_info_default_duration_is_3(self, mock_streamlit):
        """Test show_info() durée par défaut = 3s"""
        from src.ui.feedback.toasts import show_info

        before = datetime.now()
        show_info("Test")
        after = datetime.now()

        toast = mock_streamlit.session_state["toast_notifications"][0]

        expected_min = before + timedelta(seconds=3)
        expected_max = after + timedelta(seconds=3)

        assert toast["expires_at"] >= expected_min
        assert toast["expires_at"] <= expected_max

