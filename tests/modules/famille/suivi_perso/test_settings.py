"""
Tests for suivi_perso/settings.py - Garmin settings and objectives UI
"""

from datetime import datetime
from typing import Any
from unittest.mock import MagicMock, patch

import pytest


class SessionStateMock(dict):
    """Mock for st.session_state that behaves like a dict with attribute access"""

    def __getattr__(self, name: str) -> Any:
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name: str, value: Any) -> None:
        self[name] = value


def setup_mock_st(mock_st: MagicMock, session_data: dict | None = None) -> None:
    """Setup mock streamlit with common components"""

    def mock_columns(n, **kwargs):
        count = n if isinstance(n, int) else len(n)
        return [MagicMock() for _ in range(count)]

    mock_st.columns.side_effect = mock_columns
    mock_st.session_state = SessionStateMock(session_data or {})
    mock_st.button.return_value = False
    mock_st.spinner.return_value.__enter__ = MagicMock(return_value=MagicMock())
    mock_st.spinner.return_value.__exit__ = MagicMock(return_value=False)
    mock_st.text_input.return_value = ""
    mock_st.number_input.return_value = 10000
    mock_st.rerun = MagicMock()  # Make rerun mockable


# ═══════════════════════════════════════════════════════════
# TESTS D'IMPORT
# ═══════════════════════════════════════════════════════════


class TestImports:
    """Verify module imports work"""

    def test_import_render_garmin_settings(self) -> None:
        from src.modules.famille.suivi_perso.settings import afficher_garmin_settings

        assert callable(afficher_garmin_settings)

    def test_import_render_objectifs(self) -> None:
        from src.modules.famille.suivi_perso.settings import afficher_objectifs

        assert callable(afficher_objectifs)


# ═══════════════════════════════════════════════════════════
# TESTS AFFICHER_GARMIN_SETTINGS
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestRenderGarminSettings:
    """Tests for afficher_garmin_settings function"""

    @patch("src.modules.famille.suivi_perso.settings.st")
    def test_render_garmin_settings_no_user(self, mock_st) -> None:
        from src.modules.famille.suivi_perso.settings import afficher_garmin_settings

        setup_mock_st(mock_st)

        afficher_garmin_settings({})

        mock_st.subheader.assert_called()

    @patch("src.modules.famille.suivi_perso.settings.st")
    def test_render_garmin_settings_garmin_not_connected(self, mock_st) -> None:
        from src.modules.famille.suivi_perso.settings import afficher_garmin_settings

        setup_mock_st(mock_st)
        mock_user = MagicMock()
        mock_user.id = 1

        afficher_garmin_settings({"user": mock_user, "garmin_connected": False})

        mock_st.subheader.assert_called()
        mock_st.info.assert_called()

    @patch("src.modules.famille.suivi_perso.settings.st")
    def test_render_garmin_settings_garmin_connected(self, mock_st) -> None:
        from src.modules.famille.suivi_perso.settings import afficher_garmin_settings

        setup_mock_st(mock_st)
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.garmin_token = MagicMock()
        mock_user.garmin_token.derniere_sync = datetime.now()

        afficher_garmin_settings({"user": mock_user, "garmin_connected": True})

        mock_st.success.assert_called()
        mock_st.caption.assert_called()

    @patch("src.modules.famille.suivi_perso.settings.get_garmin_service")
    @patch("src.modules.famille.suivi_perso.settings.st")
    def test_render_garmin_settings_sync_button(self, mock_st, mock_service) -> None:
        from src.modules.famille.suivi_perso.settings import afficher_garmin_settings

        setup_mock_st(mock_st)
        mock_st.button.side_effect = [True, False]  # First button (sync) clicked
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.garmin_token = None
        mock_service.return_value.sync_user_data.return_value = {
            "activities_synced": 5,
            "summaries_synced": 7,
        }

        afficher_garmin_settings({"user": mock_user, "garmin_connected": True})

        mock_service.return_value.sync_user_data.assert_called_once()

    @patch("src.modules.famille.suivi_perso.settings.get_garmin_service")
    @patch("src.modules.famille.suivi_perso.settings.st")
    def test_render_garmin_settings_sync_button_success_and_rerun(
        self, mock_st, mock_service
    ) -> None:
        """Test sync button verifies st.success and st.rerun are called on success"""
        from src.modules.famille.suivi_perso.settings import afficher_garmin_settings

        setup_mock_st(mock_st)
        mock_st.button.side_effect = [True, False]  # First button (sync) clicked
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.garmin_token = None
        mock_service.return_value.sync_user_data.return_value = {
            "activities_synced": 5,
            "summaries_synced": 7,
        }

        afficher_garmin_settings({"user": mock_user, "garmin_connected": True})

        mock_service.return_value.sync_user_data.assert_called_once_with(1, days_back=7)
        mock_st.success.assert_called()
        mock_st.rerun.assert_called()

    @patch("src.modules.famille.suivi_perso.settings.get_garmin_service")
    @patch("src.modules.famille.suivi_perso.settings.st")
    def test_render_garmin_settings_disconnect_button(self, mock_st, mock_service) -> None:
        from src.modules.famille.suivi_perso.settings import afficher_garmin_settings

        setup_mock_st(mock_st)
        mock_st.button.side_effect = [False, True]  # Second button (disconnect) clicked
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.garmin_token = None

        afficher_garmin_settings({"user": mock_user, "garmin_connected": True})

        mock_service.return_value.disconnect_user.assert_called_once_with(1)

    @patch("src.modules.famille.suivi_perso.settings.get_garmin_service")
    @patch("src.modules.famille.suivi_perso.settings.st")
    def test_render_garmin_settings_disconnect_button_success_and_rerun(
        self, mock_st, mock_service
    ) -> None:
        """Test disconnect button verifies st.success and st.rerun are called on success"""
        from src.modules.famille.suivi_perso.settings import afficher_garmin_settings

        setup_mock_st(mock_st)
        mock_st.button.side_effect = [False, True]  # Second button (disconnect) clicked
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.garmin_token = None

        afficher_garmin_settings({"user": mock_user, "garmin_connected": True})

        mock_service.return_value.disconnect_user.assert_called_once_with(1)
        mock_st.success.assert_called()
        mock_st.rerun.assert_called()

    @patch("src.modules.famille.suivi_perso.settings.get_garmin_service")
    @patch("src.modules.famille.suivi_perso.settings.st")
    def test_render_garmin_settings_connect_button(self, mock_st, mock_service) -> None:
        from src.modules.famille.suivi_perso.settings import afficher_garmin_settings

        setup_mock_st(mock_st)
        mock_st.button.side_effect = [True, False]  # Connect button clicked
        mock_user = MagicMock()
        mock_user.id = 1
        mock_service.return_value.get_authorization_url.return_value = (
            "https://auth.garmin.com/xxx",
            {"token": "abc"},
        )

        afficher_garmin_settings({"user": mock_user, "garmin_connected": False})

        mock_service.return_value.get_authorization_url.assert_called()

    @patch("src.modules.famille.suivi_perso.settings.get_garmin_service")
    @patch("src.modules.famille.suivi_perso.settings.st")
    def test_render_garmin_settings_validate_verification_with_valid_verifier(
        self, mock_st, mock_service
    ) -> None:
        """Test validation with valid verifier code - lines 73-80"""
        from src.modules.famille.suivi_perso.settings import afficher_garmin_settings

        setup_mock_st(mock_st)
        # Connect button clicked, then Validate button clicked
        mock_st.button.side_effect = [True, True]
        mock_st.text_input.return_value = "ABC123"  # Valid verifier code
        mock_user = MagicMock()
        mock_user.id = 1
        request_token = {"token": "abc"}
        mock_service.return_value.get_authorization_url.return_value = (
            "https://auth.garmin.com/xxx",
            request_token,
        )

        afficher_garmin_settings({"user": mock_user, "garmin_connected": False})

        mock_service.return_value.complete_authorization.assert_called_once_with(
            1, "ABC123", request_token
        )
        # Should call success and rerun
        success_calls = [
            call for call in mock_st.success.call_args_list if "Garmin connecte" in str(call)
        ]
        assert len(success_calls) > 0
        mock_st.rerun.assert_called()

    @patch("src.modules.famille.suivi_perso.settings.get_garmin_service")
    @patch("src.modules.famille.suivi_perso.settings.st")
    def test_render_garmin_settings_validate_verification_with_empty_verifier(
        self, mock_st, mock_service
    ) -> None:
        """Test validation with empty verifier code - lines 83-84"""
        from src.modules.famille.suivi_perso.settings import afficher_garmin_settings

        setup_mock_st(mock_st)
        # Connect button clicked, then Validate button clicked
        mock_st.button.side_effect = [True, True]
        mock_st.text_input.return_value = ""  # Empty verifier code
        mock_user = MagicMock()
        mock_user.id = 1
        mock_service.return_value.get_authorization_url.return_value = (
            "https://auth.garmin.com/xxx",
            {"token": "abc"},
        )

        afficher_garmin_settings({"user": mock_user, "garmin_connected": False})

        # Should not call complete_authorization
        mock_service.return_value.complete_authorization.assert_not_called()
        # Should show error
        mock_st.error.assert_called()

    @patch("src.modules.famille.suivi_perso.settings.get_garmin_service")
    @patch("src.modules.famille.suivi_perso.settings.st")
    def test_render_garmin_settings_validate_verification_with_exception(
        self, mock_st, mock_service
    ) -> None:
        """Test validation when complete_authorization raises exception - lines 81-82"""
        from src.modules.famille.suivi_perso.settings import afficher_garmin_settings

        setup_mock_st(mock_st)
        # Connect button clicked, then Validate button clicked
        mock_st.button.side_effect = [True, True]
        mock_st.text_input.return_value = "ABC123"  # Valid verifier code
        mock_user = MagicMock()
        mock_user.id = 1
        mock_service.return_value.get_authorization_url.return_value = (
            "https://auth.garmin.com/xxx",
            {"token": "abc"},
        )
        mock_service.return_value.complete_authorization.side_effect = Exception("Auth failed")

        afficher_garmin_settings({"user": mock_user, "garmin_connected": False})

        mock_service.return_value.complete_authorization.assert_called_once()
        # Should show error
        mock_st.error.assert_called()


# ═══════════════════════════════════════════════════════════
# TESTS AFFICHER_OBJECTIFS
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestRenderObjectifs:
    """Tests for afficher_objectifs function"""

    @patch("src.modules.famille.suivi_perso.settings.st")
    def test_render_objectifs_no_user(self, mock_st) -> None:
        from src.modules.famille.suivi_perso.settings import afficher_objectifs

        setup_mock_st(mock_st)

        afficher_objectifs({})

        mock_st.subheader.assert_called()

    @patch("src.modules.famille.suivi_perso.settings.st")
    def test_render_objectifs_displays_inputs(self, mock_st) -> None:
        from src.modules.famille.suivi_perso.settings import afficher_objectifs

        setup_mock_st(mock_st)
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.objectif_pas_quotidien = 10000
        mock_user.objectif_calories_brulees = 500
        mock_user.objectif_minutes_actives = 60

        afficher_objectifs({"user": mock_user})

        mock_st.subheader.assert_called()
        assert mock_st.number_input.call_count == 3

    @patch("src.services.famille.suivi_perso.obtenir_service_suivi_perso")
    @patch("src.modules.famille.suivi_perso.settings.st")
    def test_render_objectifs_save_button(self, mock_st, mock_svc_factory) -> None:
        from src.modules.famille.suivi_perso.settings import afficher_objectifs

        setup_mock_st(mock_st)
        mock_st.button.return_value = True
        mock_st.number_input.side_effect = [12000, 600, 75]

        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.objectif_pas_quotidien = 10000
        mock_user.objectif_calories_brulees = 500
        mock_user.objectif_minutes_actives = 60

        mock_service = MagicMock()
        mock_svc_factory.return_value = mock_service

        afficher_objectifs({"user": mock_user})

        mock_service.sauvegarder_objectifs.assert_called_once()
        mock_st.success.assert_called()

    @patch("src.services.famille.suivi_perso.obtenir_service_suivi_perso")
    @patch("src.modules.famille.suivi_perso.settings.st")
    def test_render_objectifs_save_button_success_and_rerun(
        self, mock_st, mock_svc_factory
    ) -> None:
        """Test save button verifies st.success and st.rerun are called on success"""
        from src.modules.famille.suivi_perso.settings import afficher_objectifs

        setup_mock_st(mock_st)
        mock_st.button.return_value = True
        mock_st.number_input.side_effect = [12000, 600, 75]

        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.objectif_pas_quotidien = 10000
        mock_user.objectif_calories_brulees = 500
        mock_user.objectif_minutes_actives = 60

        mock_service = MagicMock()
        mock_svc_factory.return_value = mock_service

        afficher_objectifs({"user": mock_user})

        mock_service.sauvegarder_objectifs.assert_called_once()
        mock_st.success.assert_called()
        mock_st.rerun.assert_called()

    @patch("src.services.famille.suivi_perso.obtenir_service_suivi_perso")
    @patch("src.modules.famille.suivi_perso.settings.st")
    def test_render_objectifs_save_button_with_exception(self, mock_st, mock_svc_factory) -> None:
        """Test save button handles exception properly"""
        from src.modules.famille.suivi_perso.settings import afficher_objectifs

        setup_mock_st(mock_st)
        mock_st.button.return_value = True
        mock_st.number_input.side_effect = [12000, 600, 75]

        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.objectif_pas_quotidien = 10000
        mock_user.objectif_calories_brulees = 500
        mock_user.objectif_minutes_actives = 60

        # Make the service raise an exception
        mock_svc_factory.side_effect = Exception("Database error")

        afficher_objectifs({"user": mock_user})

        # Should show error
        mock_st.error.assert_called()
        # Should not call rerun or success
        mock_st.rerun.assert_not_called()
