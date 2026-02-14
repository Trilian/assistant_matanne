"""
Tests pour src/modules/planning/calendar_sync_ui.py

Tests complets pour l'interface de synchronisation calendrier avec mocking Streamlit.
"""

from unittest.mock import MagicMock, patch

import pytest


class TestRenderCalendarSyncUI:
    """Tests pour render_calendar_sync_ui()"""

    @pytest.fixture
    def mock_st(self):
        """Mock streamlit"""
        with patch("src.modules.planning.calendar_sync_ui.st") as mock:
            tab_mock = MagicMock()
            tab_mock.__enter__ = MagicMock(return_value=tab_mock)
            tab_mock.__exit__ = MagicMock(return_value=False)
            mock.tabs.return_value = [tab_mock, tab_mock, tab_mock]
            mock.columns.return_value = [MagicMock(), MagicMock()]
            yield mock

    @pytest.fixture
    def mock_service(self):
        """Mock calendar sync service"""
        with patch("src.modules.planning.calendar_sync_ui.get_calendar_sync_service") as mock:
            mock_svc = MagicMock()
            mock.return_value = mock_svc
            yield mock_svc

    def test_affiche_subheader(self, mock_st, mock_service):
        """Vérifie l'affichage du titre"""
        from src.modules.planning.calendar_sync_ui import render_calendar_sync_ui

        render_calendar_sync_ui()

        mock_st.subheader.assert_called_once()
        assert "Synchronisation" in mock_st.subheader.call_args[0][0]

    def test_affiche_3_tabs(self, mock_st, mock_service):
        """Vérifie les 3 onglets"""
        from src.modules.planning.calendar_sync_ui import render_calendar_sync_ui

        render_calendar_sync_ui()

        mock_st.tabs.assert_called_once()
        args = mock_st.tabs.call_args[0][0]
        assert len(args) == 3


class TestRenderExportTab:
    """Tests pour _render_export_tab()"""

    @pytest.fixture
    def mock_st(self):
        """Mock streamlit"""
        with patch("src.modules.planning.calendar_sync_ui.st") as mock:
            mock.columns.return_value = [MagicMock(), MagicMock()]
            mock.checkbox.return_value = True
            mock.slider.return_value = 30
            mock.button.return_value = False
            yield mock

    @pytest.fixture
    def mock_service(self):
        """Mock service"""
        return MagicMock()

    def test_affiche_titre_export(self, mock_st, mock_service):
        """Vérifie le titre de l'onglet export"""
        from src.modules.planning.calendar_sync_ui import _render_export_tab

        _render_export_tab(mock_service)

        mock_st.markdown.assert_called()
        calls = [str(call) for call in mock_st.markdown.call_args_list]
        assert any("Exporter" in str(call) for call in calls)

    def test_affiche_checkbox_repas(self, mock_st, mock_service):
        """Vérifie la checkbox pour les repas"""
        from src.modules.planning.calendar_sync_ui import _render_export_tab

        _render_export_tab(mock_service)

        calls = [str(call) for call in mock_st.checkbox.call_args_list]
        assert any("repas" in str(call).lower() for call in calls)

    def test_affiche_checkbox_activites(self, mock_st, mock_service):
        """Vérifie la checkbox pour les activités"""
        from src.modules.planning.calendar_sync_ui import _render_export_tab

        _render_export_tab(mock_service)

        calls = [str(call) for call in mock_st.checkbox.call_args_list]
        assert any("activit" in str(call).lower() for call in calls)

    def test_affiche_slider_periode(self, mock_st, mock_service):
        """Vérifie le slider de période"""
        from src.modules.planning.calendar_sync_ui import _render_export_tab

        _render_export_tab(mock_service)

        mock_st.slider.assert_called()

    def test_bouton_generer(self, mock_st, mock_service):
        """Vérifie le bouton de génération"""
        from src.modules.planning.calendar_sync_ui import _render_export_tab

        _render_export_tab(mock_service)

        mock_st.button.assert_called()

    def test_genere_ical_au_clic(self, mock_st, mock_service):
        """Vérifie la génération iCal au clic"""
        mock_st.button.return_value = True
        mock_service.export_to_ical.return_value = "BEGIN:VCALENDAR..."

        with patch("src.modules.planning.calendar_sync_ui.get_auth_service") as mock_auth:
            mock_user = MagicMock()
            mock_user.id = "user123"
            mock_auth.return_value.get_current_user.return_value = mock_user

            from src.modules.planning.calendar_sync_ui import _render_export_tab

            _render_export_tab(mock_service)

            mock_service.export_to_ical.assert_called()

    def test_affiche_download_button(self, mock_st, mock_service):
        """Vérifie le bouton de téléchargement"""
        mock_st.button.return_value = True
        mock_service.export_to_ical.return_value = "BEGIN:VCALENDAR..."

        with patch("src.modules.planning.calendar_sync_ui.get_auth_service") as mock_auth:
            mock_user = MagicMock()
            mock_user.id = "user123"
            mock_auth.return_value.get_current_user.return_value = mock_user

            from src.modules.planning.calendar_sync_ui import _render_export_tab

            _render_export_tab(mock_service)

            mock_st.download_button.assert_called()


class TestRenderImportTab:
    """Tests pour _render_import_tab()"""

    @pytest.fixture
    def mock_st(self):
        """Mock streamlit"""
        with patch("src.modules.planning.calendar_sync_ui.st") as mock:
            mock.text_input.return_value = ""
            mock.button.return_value = False
            yield mock

    @pytest.fixture
    def mock_service(self):
        """Mock service"""
        return MagicMock()

    def test_affiche_titre_import(self, mock_st, mock_service):
        """Vérifie le titre de l'onglet import"""
        from src.modules.planning.calendar_sync_ui import _render_import_tab

        _render_import_tab(mock_service)

        mock_st.markdown.assert_called()

    def test_affiche_input_url(self, mock_st, mock_service):
        """Vérifie l'input URL"""
        from src.modules.planning.calendar_sync_ui import _render_import_tab

        _render_import_tab(mock_service)

        calls = [str(call) for call in mock_st.text_input.call_args_list]
        assert any("URL" in str(call) for call in calls)

    def test_affiche_input_nom(self, mock_st, mock_service):
        """Vérifie l'input nom du calendrier"""
        from src.modules.planning.calendar_sync_ui import _render_import_tab

        _render_import_tab(mock_service)

        calls = [str(call) for call in mock_st.text_input.call_args_list]
        assert any("Nom" in str(call) or "calendrier" in str(call).lower() for call in calls)

    def test_importer_au_clic(self, mock_st, mock_service):
        """Vérifie l'import au clic"""
        mock_st.text_input.side_effect = [
            "https://calendar.google.com/ical/test",
            "Mon Calendrier",
        ]
        mock_st.button.return_value = True

        result_mock = MagicMock()
        result_mock.success = True
        result_mock.message = "Import réussi"
        mock_service.import_from_ical_url.return_value = result_mock

        with patch("src.modules.planning.calendar_sync_ui.get_auth_service") as mock_auth:
            mock_user = MagicMock()
            mock_user.id = "user123"
            mock_auth.return_value.get_current_user.return_value = mock_user

            from src.modules.planning.calendar_sync_ui import _render_import_tab

            _render_import_tab(mock_service)

            mock_service.import_from_ical_url.assert_called()

    def test_affiche_success_import_reussi(self, mock_st, mock_service):
        """Vérifie le message de succès"""
        mock_st.text_input.side_effect = [
            "https://calendar.google.com/ical/test",
            "Mon Calendrier",
        ]
        mock_st.button.return_value = True

        result_mock = MagicMock()
        result_mock.success = True
        result_mock.message = "Import réussi"
        mock_service.import_from_ical_url.return_value = result_mock

        with patch("src.modules.planning.calendar_sync_ui.get_auth_service") as mock_auth:
            mock_user = MagicMock()
            mock_user.id = "user123"
            mock_auth.return_value.get_current_user.return_value = mock_user

            from src.modules.planning.calendar_sync_ui import _render_import_tab

            _render_import_tab(mock_service)

            mock_st.success.assert_called()

    def test_affiche_erreur_import_echoue(self, mock_st, mock_service):
        """Vérifie le message d'erreur"""
        mock_st.text_input.side_effect = [
            "https://calendar.google.com/ical/test",
            "Mon Calendrier",
        ]
        mock_st.button.return_value = True

        result_mock = MagicMock()
        result_mock.success = False
        result_mock.message = "Erreur d'import"
        mock_service.import_from_ical_url.return_value = result_mock

        with patch("src.modules.planning.calendar_sync_ui.get_auth_service") as mock_auth:
            mock_user = MagicMock()
            mock_user.id = "user123"
            mock_auth.return_value.get_current_user.return_value = mock_user

            from src.modules.planning.calendar_sync_ui import _render_import_tab

            _render_import_tab(mock_service)

            mock_st.error.assert_called()


class TestRenderConnectTab:
    """Tests pour _render_connect_tab()"""

    @pytest.fixture
    def mock_st(self):
        """Mock streamlit"""
        with patch("src.modules.planning.calendar_sync_ui.st") as mock:
            mock.button.return_value = False
            yield mock

    @pytest.fixture
    def mock_service(self):
        """Mock service"""
        return MagicMock()

    def test_affiche_titre_connecter(self, mock_st, mock_service):
        """Vérifie le titre de l'onglet connexion"""
        with patch("src.modules.planning.calendar_sync_ui.obtenir_parametres") as mock_params:
            mock_params.return_value = MagicMock(GOOGLE_CLIENT_ID=None)

            from src.modules.planning.calendar_sync_ui import _render_connect_tab

            _render_connect_tab(mock_service)

            mock_st.markdown.assert_called()

    def test_affiche_warning_google_non_configure(self, mock_st, mock_service):
        """Vérifie le warning si Google non configuré"""
        with patch("src.modules.planning.calendar_sync_ui.obtenir_parametres") as mock_params:
            mock_params.return_value = MagicMock(GOOGLE_CLIENT_ID=None)

            from src.modules.planning.calendar_sync_ui import _render_connect_tab

            _render_connect_tab(mock_service)

            mock_st.warning.assert_called()

    def test_affiche_bouton_google_si_configure(self, mock_st, mock_service):
        """Vérifie le bouton Google si configuré"""
        with patch("src.modules.planning.calendar_sync_ui.obtenir_parametres") as mock_params:
            mock_params.return_value = MagicMock(GOOGLE_CLIENT_ID="client_id_123")

            from src.modules.planning.calendar_sync_ui import _render_connect_tab

            _render_connect_tab(mock_service)

            calls = [str(call) for call in mock_st.button.call_args_list]
            assert any("Google" in str(call) for call in calls)

    def test_genere_auth_url_au_clic(self, mock_st, mock_service):
        """Vérifie la génération de l'URL d'auth"""
        mock_st.button.return_value = True
        mock_service.get_google_auth_url.return_value = "https://accounts.google.com/auth"

        with patch("src.modules.planning.calendar_sync_ui.obtenir_parametres") as mock_params:
            mock_params.return_value = MagicMock(GOOGLE_CLIENT_ID="client_id_123")

            from src.modules.planning.calendar_sync_ui import _render_connect_tab

            _render_connect_tab(mock_service)

            mock_service.get_google_auth_url.assert_called()


class TestCalendarSyncUIExports:
    """Tests des exports"""

    def test_import_render_calendar_sync_ui(self):
        """Vérifie l'import"""
        from src.modules.planning.calendar_sync_ui import render_calendar_sync_ui

        assert callable(render_calendar_sync_ui)
