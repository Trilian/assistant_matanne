"""
Tests complets pour src/ui/components/google_calendar_sync.py
Couverture cible: >80%
"""

from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch


# Helper pour créer un mock session_state qui supporte dict ET attributs
class MockSessionState(dict):
    """Mock de session_state Streamlit."""

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key) from None

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError:
            raise AttributeError(key) from None


# ═══════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════


class TestConstantes:
    """Tests pour les constantes."""

    def test_google_scopes(self):
        """Test GOOGLE_SCOPES existe."""
        from src.ui.integrations import GOOGLE_SCOPES

        assert GOOGLE_SCOPES is not None
        assert len(GOOGLE_SCOPES) >= 1
        assert "calendar" in GOOGLE_SCOPES[0].lower()

    def test_redirect_uri(self):
        """Test REDIRECT_URI_LOCAL."""
        from src.ui.integrations import REDIRECT_URI_LOCAL

        assert REDIRECT_URI_LOCAL is not None
        assert "localhost" in REDIRECT_URI_LOCAL


# ═══════════════════════════════════════════════════════════
# VÉRIFIER CONFIG GOOGLE
# ═══════════════════════════════════════════════════════════


class TestVerifierConfigGoogle:
    """Tests pour verifier_config_google."""

    def test_import(self):
        """Test import réussi."""
        from src.ui.integrations import verifier_config_google

        assert verifier_config_google is not None

    @patch("src.ui.integrations.google_calendar.obtenir_parametres")
    def test_config_ok(self, mock_params):
        """Test configuration valide."""
        from src.ui.integrations import verifier_config_google

        mock_params.return_value = MagicMock(
            GOOGLE_CLIENT_ID="test_id", GOOGLE_CLIENT_SECRET="test_secret"
        )

        ok, message = verifier_config_google()

        assert ok is True
        assert message == "Configuration OK"

    @patch("src.ui.integrations.google_calendar.obtenir_parametres")
    def test_missing_client_id(self, mock_params):
        """Test client_id manquant."""
        from src.ui.integrations import verifier_config_google

        mock_params.return_value = MagicMock(
            GOOGLE_CLIENT_ID="", GOOGLE_CLIENT_SECRET="test_secret"
        )

        ok, message = verifier_config_google()

        assert ok is False
        assert "GOOGLE_CLIENT_ID" in message

    @patch("src.ui.integrations.google_calendar.obtenir_parametres")
    def test_missing_client_secret(self, mock_params):
        """Test client_secret manquant."""
        from src.ui.integrations import verifier_config_google

        mock_config = MagicMock()
        mock_config.GOOGLE_CLIENT_ID = "test_id"
        mock_config.GOOGLE_CLIENT_SECRET = ""
        mock_params.return_value = mock_config

        ok, message = verifier_config_google()

        assert ok is False
        assert "GOOGLE_CLIENT_SECRET" in message


# ═══════════════════════════════════════════════════════════
# RENDER CONFIG GOOGLE
# ═══════════════════════════════════════════════════════════


class TestRenderGoogleCalendarConfig:
    """Tests pour render_google_calendar_config."""

    def test_import(self):
        """Test import réussi."""
        from src.ui.integrations import render_google_calendar_config

        assert render_google_calendar_config is not None

    @patch("streamlit.session_state", MockSessionState())
    @patch("streamlit.markdown")
    @patch("streamlit.warning")
    @patch("streamlit.expander")
    @patch("src.ui.integrations.google_calendar.verifier_config_google")
    def test_render_config_not_ok(self, mock_verif, mock_exp, mock_warn, mock_md):
        """Test render quand config non valide."""
        from src.ui.integrations import render_google_calendar_config

        mock_verif.return_value = (False, "Config manquante")
        mock_exp.return_value.__enter__ = MagicMock()
        mock_exp.return_value.__exit__ = MagicMock()

        render_google_calendar_config()

        mock_warn.assert_called()
        mock_exp.assert_called()

    @patch("streamlit.session_state", MockSessionState())
    @patch("streamlit.markdown")
    @patch("streamlit.success")
    @patch("streamlit.info")
    @patch("streamlit.button", return_value=False)
    @patch("src.ui.integrations.google_calendar.verifier_config_google")
    def test_render_config_ok_not_connected(
        self, mock_verif, mock_btn, mock_info, mock_success, mock_md
    ):
        """Test render config OK mais non connecté."""
        from src.ui.integrations import render_google_calendar_config

        mock_verif.return_value = (True, "Configuration OK")

        render_google_calendar_config()

        mock_success.assert_called()
        mock_info.assert_called()

    @patch(
        "streamlit.session_state",
        MockSessionState(
            {"google_calendar_config": MagicMock(name="Mon Cal", last_sync=datetime.now())}
        ),
    )
    @patch("streamlit.markdown")
    @patch("streamlit.success")
    @patch("streamlit.caption")
    @patch("streamlit.columns")
    @patch("streamlit.button", return_value=False)
    @patch("src.ui.integrations.google_calendar.verifier_config_google")
    def test_render_config_connected(
        self, mock_verif, mock_btn, mock_cols, mock_caption, mock_success, mock_md
    ):
        """Test render quand connecté."""
        from src.ui.integrations import render_google_calendar_config

        mock_verif.return_value = (True, "Configuration OK")

        mock_cols.return_value = [MagicMock(), MagicMock(), MagicMock()]
        for col in mock_cols.return_value:
            col.__enter__ = MagicMock(return_value=col)
            col.__exit__ = MagicMock()

        render_google_calendar_config()

        mock_caption.assert_called()  # Affiche dernière sync

    @patch(
        "streamlit.session_state",
        MockSessionState(
            {"google_calendar_config": MagicMock(name="Cal", last_sync=datetime.now())}
        ),
    )
    @patch("streamlit.markdown")
    @patch("streamlit.success")
    @patch("streamlit.caption")
    @patch("streamlit.columns")
    @patch("streamlit.button")
    @patch("streamlit.spinner")
    @patch("streamlit.rerun")
    @patch("src.ui.integrations.google_calendar.verifier_config_google")
    @patch("src.ui.integrations.google_calendar.get_calendar_sync_service")
    def test_render_sync_button(
        self,
        mock_service,
        mock_verif,
        mock_rerun,
        mock_spinner,
        mock_btn,
        mock_cols,
        mock_caption,
        mock_success,
        mock_md,
    ):
        """Test clic sur bouton sync."""
        from src.ui.integrations import render_google_calendar_config

        mock_verif.return_value = (True, "Configuration OK")
        mock_btn.side_effect = [True, False, False]  # Sync cliqué

        mock_cols.return_value = [MagicMock(), MagicMock(), MagicMock()]
        for col in mock_cols.return_value:
            col.__enter__ = MagicMock(return_value=col)
            col.__exit__ = MagicMock()

        mock_spinner.return_value.__enter__ = MagicMock()
        mock_spinner.return_value.__exit__ = MagicMock()

        mock_sync_result = MagicMock(success=True, events_imported=5)
        mock_service.return_value.sync_google_calendar.return_value = mock_sync_result

        render_google_calendar_config()

        mock_service.return_value.sync_google_calendar.assert_called()

    @patch(
        "streamlit.session_state",
        MockSessionState(
            {"google_calendar_config": MagicMock(name="Cal", last_sync=datetime.now())}
        ),
    )
    @patch("streamlit.markdown")
    @patch("streamlit.success")
    @patch("streamlit.caption")
    @patch("streamlit.columns")
    @patch("streamlit.button")
    @patch("streamlit.rerun")
    @patch("src.ui.integrations.google_calendar.verifier_config_google")
    def test_render_disconnect_button(
        self, mock_verif, mock_rerun, mock_btn, mock_cols, mock_caption, mock_success, mock_md
    ):
        """Test bouton déconnexion."""
        import streamlit as st

        from src.ui.integrations import render_google_calendar_config

        mock_verif.return_value = (True, "Configuration OK")
        mock_btn.side_effect = [False, False, True]  # Déconnecter cliqué

        mock_cols.return_value = [MagicMock(), MagicMock(), MagicMock()]
        for col in mock_cols.return_value:
            col.__enter__ = MagicMock(return_value=col)
            col.__exit__ = MagicMock()

        try:
            render_google_calendar_config()
        except Exception:
            pass

        assert st.session_state.get("google_calendar_config") is None


# ═══════════════════════════════════════════════════════════
# RENDER SYNC STATUS
# ═══════════════════════════════════════════════════════════


class TestRenderSyncStatus:
    """Tests pour render_sync_status."""

    def test_import(self):
        """Test import réussi."""
        from src.ui.integrations import render_sync_status

        assert render_sync_status is not None

    @patch("streamlit.session_state", MockSessionState())
    def test_no_config(self):
        """Test sans config."""
        from src.ui.integrations import render_sync_status

        # Ne doit pas lever d'erreur
        render_sync_status()

    @patch(
        "streamlit.session_state",
        MockSessionState({"google_calendar_config": MagicMock(last_sync=None)}),
    )
    def test_no_last_sync(self):
        """Test sans dernière sync."""
        from src.ui.integrations import render_sync_status

        render_sync_status()

    @patch(
        "streamlit.session_state",
        MockSessionState({"google_calendar_config": MagicMock(last_sync=datetime.now())}),
    )
    @patch("streamlit.success")
    def test_sync_recent(self, mock_success):
        """Test sync récente (<5 min)."""
        from src.ui.integrations import render_sync_status

        render_sync_status()

        mock_success.assert_called()

    @patch("streamlit.session_state", MockSessionState())
    @patch("streamlit.info")
    def test_sync_minutes_ago(self, mock_info):
        """Test sync il y a quelques minutes."""
        import streamlit as st

        from src.ui.integrations import render_sync_status

        st.session_state["google_calendar_config"] = MagicMock(
            last_sync=datetime.now() - timedelta(minutes=30)
        )

        render_sync_status()

        mock_info.assert_called()

    @patch("streamlit.session_state", MockSessionState())
    @patch("streamlit.warning")
    def test_sync_hours_ago(self, mock_warning):
        """Test sync il y a quelques heures."""
        import streamlit as st

        from src.ui.integrations import render_sync_status

        st.session_state["google_calendar_config"] = MagicMock(
            last_sync=datetime.now() - timedelta(hours=5)
        )

        render_sync_status()

        mock_warning.assert_called()

    @patch("streamlit.session_state", MockSessionState())
    @patch("streamlit.error")
    def test_sync_days_ago(self, mock_error):
        """Test sync il y a plusieurs jours."""
        import streamlit as st

        from src.ui.integrations import render_sync_status

        st.session_state["google_calendar_config"] = MagicMock(
            last_sync=datetime.now() - timedelta(days=3)
        )

        render_sync_status()

        mock_error.assert_called()


# ═══════════════════════════════════════════════════════════
# QUICK SYNC BUTTON
# ═══════════════════════════════════════════════════════════


class TestRenderQuickSyncButton:
    """Tests pour render_quick_sync_button."""

    def test_import(self):
        """Test import réussi."""
        from src.ui.integrations import render_quick_sync_button

        assert render_quick_sync_button is not None

    @patch("streamlit.session_state", MockSessionState())
    def test_no_config_quick_sync(self):
        """Test sans config."""
        from src.ui.integrations import render_quick_sync_button

        # Ne doit rien afficher
        render_quick_sync_button()

    @patch("streamlit.session_state", MockSessionState({"google_calendar_config": MagicMock()}))
    @patch("streamlit.button", return_value=False)
    def test_button_displayed(self, mock_btn):
        """Test bouton affiché quand connecté."""
        from src.ui.integrations import render_quick_sync_button

        render_quick_sync_button()

        mock_btn.assert_called()

    @patch("streamlit.session_state", MockSessionState({"google_calendar_config": MagicMock()}))
    @patch("streamlit.button", return_value=True)
    @patch("streamlit.toast")
    @patch("src.ui.integrations.google_calendar.get_calendar_sync_service")
    def test_sync_success(self, mock_service, mock_toast, mock_btn):
        """Test sync réussie."""
        from src.ui.integrations import render_quick_sync_button

        mock_result = MagicMock(success=True, events_imported=3)
        mock_service.return_value.sync_google_calendar.return_value = mock_result

        render_quick_sync_button()

        mock_toast.assert_called()
        assert "3" in str(mock_toast.call_args)

    @patch("streamlit.session_state", MockSessionState({"google_calendar_config": MagicMock()}))
    @patch("streamlit.button", return_value=True)
    @patch("streamlit.toast")
    @patch("src.ui.integrations.google_calendar.get_calendar_sync_service")
    def test_sync_failure(self, mock_service, mock_toast, mock_btn):
        """Test sync échouée."""
        from src.ui.integrations import render_quick_sync_button

        mock_result = MagicMock(success=False, message="Erreur réseau")
        mock_service.return_value.sync_google_calendar.return_value = mock_result

        render_quick_sync_button()

        mock_toast.assert_called()


# ═══════════════════════════════════════════════════════════
# CONNECT FLOW
# ═══════════════════════════════════════════════════════════


class TestConnectFlow:
    """Tests pour le flux de connexion."""

    @patch("streamlit.session_state", MockSessionState())
    @patch("streamlit.markdown")
    @patch("streamlit.success")
    @patch("streamlit.info")
    @patch("streamlit.button", return_value=True)
    @patch("streamlit.text_input", return_value="")
    @patch("src.ui.integrations.google_calendar.verifier_config_google")
    @patch("src.ui.integrations.google_calendar.get_calendar_sync_service")
    def test_connect_button_shows_auth_url(
        self, mock_service, mock_verif, mock_input, mock_btn, mock_info, mock_success, mock_md
    ):
        """Test bouton connexion affiche URL auth."""
        from src.ui.integrations import render_google_calendar_config

        mock_verif.return_value = (True, "Configuration OK")
        mock_service.return_value.get_google_auth_url.return_value = "https://auth.google.com/..."

        render_google_calendar_config()

        mock_service.return_value.get_google_auth_url.assert_called()

    @patch("streamlit.session_state", MockSessionState())
    @patch("streamlit.markdown")
    @patch("streamlit.success")
    @patch("streamlit.info")
    @patch("streamlit.button")
    @patch("streamlit.text_input", return_value="auth_code_123")
    @patch("streamlit.spinner")
    @patch("streamlit.rerun")
    @patch("src.ui.integrations.google_calendar.verifier_config_google")
    @patch("src.ui.integrations.google_calendar.get_calendar_sync_service")
    def test_validate_auth_code(
        self,
        mock_service,
        mock_verif,
        mock_rerun,
        mock_spinner,
        mock_input,
        mock_btn,
        mock_info,
        mock_success,
        mock_md,
    ):
        """Test validation code auth."""
        import streamlit as st

        from src.ui.integrations import render_google_calendar_config

        mock_verif.return_value = (True, "Configuration OK")
        mock_btn.side_effect = [True, True]  # Connect + Valider

        mock_spinner.return_value.__enter__ = MagicMock()
        mock_spinner.return_value.__exit__ = MagicMock()

        mock_config = MagicMock()
        mock_service.return_value.get_google_auth_url.return_value = "https://auth.google.com"
        mock_service.return_value.handle_google_callback.return_value = mock_config

        try:
            render_google_calendar_config()
        except Exception:
            pass

        assert st.session_state.get("google_calendar_config") == mock_config

    @patch("streamlit.session_state", MockSessionState())
    @patch("streamlit.markdown")
    @patch("streamlit.success")
    @patch("streamlit.info")
    @patch("streamlit.button", return_value=True)
    @patch("streamlit.error")
    @patch("src.ui.integrations.google_calendar.verifier_config_google")
    @patch("src.ui.integrations.google_calendar.get_calendar_sync_service")
    def test_connect_error(
        self, mock_service, mock_verif, mock_error, mock_btn, mock_info, mock_success, mock_md
    ):
        """Test erreur connexion."""
        from src.ui.integrations import render_google_calendar_config

        mock_verif.return_value = (True, "Configuration OK")
        mock_service.return_value.get_google_auth_url.side_effect = ValueError("API Error")

        render_google_calendar_config()

        mock_error.assert_called()


# ═══════════════════════════════════════════════════════════
# INTÉGRATION
# ═══════════════════════════════════════════════════════════


class TestIntegration:
    """Tests d'intégration."""

    def test_all_exports(self):
        """Test tous les exports."""
        from src.ui.integrations import (
            render_google_calendar_config,
            render_quick_sync_button,
            render_sync_status,
            verifier_config_google,
        )

        assert verifier_config_google is not None
        assert render_google_calendar_config is not None
        assert render_sync_status is not None
        assert render_quick_sync_button is not None
