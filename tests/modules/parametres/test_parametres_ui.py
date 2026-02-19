"""Tests complets pour le module parametres.py UI."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from unittest.mock import MagicMock, patch

import pytest


class SessionStateMock(dict):
    """Mock de st.session_state."""

    def __getattr__(self, name: str) -> Any:
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name: str, value: Any) -> None:
        self[name] = value


def setup_mock_st(mock_st: MagicMock, session_data: dict | None = None) -> None:
    """Configure le mock Streamlit."""
    mock_st.columns.side_effect = lambda n: [
        MagicMock() for _ in range(n if isinstance(n, int) else len(n))
    ]
    mock_st.tabs.return_value = [MagicMock() for _ in range(7)]
    mock_st.session_state = SessionStateMock(session_data or {"parametres_tab": "👨‍👩‍👧‍👦 Foyer"})
    for cm in ["container", "expander", "spinner", "form"]:
        getattr(mock_st, cm).return_value.__enter__ = MagicMock(return_value=MagicMock())
        getattr(mock_st, cm).return_value.__exit__ = MagicMock(return_value=False)


@pytest.mark.unit
class TestParametresUI:
    """Tests pour les fonctions UI du module parametres."""

    @patch("src.modules.parametres.afficher_about")
    @patch("src.modules.parametres.afficher_budget_config")
    @patch("src.modules.parametres.afficher_display_config")
    @patch("src.modules.parametres.afficher_cache_config")
    @patch("src.modules.parametres.afficher_database_config")
    @patch("src.modules.parametres.afficher_ia_config")
    @patch("src.modules.parametres.afficher_foyer_config")
    @patch("src.modules.parametres.st")
    def test_app_basic(self, mock_st, *mocks) -> None:
        """Test du rendu basique de app()."""
        from src.modules.parametres import app

        setup_mock_st(mock_st)
        app()
        mock_st.title.assert_called()
        mock_st.tabs.assert_called()  # Navigation par onglets

    @patch("src.modules.parametres.foyer.obtenir_etat")
    @patch("src.modules.parametres.foyer.st")
    def test_render_foyer_config(self, mock_st, mock_etat) -> None:
        """Test config foyer."""
        from src.modules.parametres import afficher_foyer_config

        setup_mock_st(mock_st)
        mock_etat.return_value = MagicMock(nom_utilisateur="Test")
        mock_st.text_input.return_value = "Test"
        mock_st.number_input.return_value = 2
        mock_st.checkbox.return_value = False
        mock_st.form_submit_button.return_value = False
        afficher_foyer_config()
        mock_st.markdown.assert_called()

    @patch("src.modules.parametres.ia.get_settings")
    @patch("src.modules.parametres.ia.st")
    def test_render_ia_config(self, mock_st, mock_settings) -> None:
        """Test config IA."""
        from src.modules.parametres import afficher_ia_config

        setup_mock_st(mock_st)
        mock_settings.return_value = MagicMock(MISTRAL_API_KEY="test_key")
        mock_st.text_input.return_value = ""
        mock_st.selectbox.return_value = "mistral-small-latest"
        mock_st.slider.return_value = 0.7
        mock_st.form_submit_button.return_value = False
        afficher_ia_config()
        mock_st.markdown.assert_called()

    @patch("src.modules.parametres.database.get_db_info")
    @patch("src.modules.parametres.database.health_check")
    @patch("src.modules.parametres.database.st")
    def test_render_database_config(self, mock_st, mock_health, mock_info) -> None:
        """Test config database."""
        from src.modules.parametres import afficher_database_config

        setup_mock_st(mock_st)
        mock_health.return_value = {"status": "healthy", "tables": 10}
        mock_info.return_value = {"version": "14.0", "size": "50MB"}
        mock_st.button.return_value = False
        afficher_database_config()
        mock_st.markdown.assert_called()

    @patch("src.modules.parametres.cache.Cache")
    @patch("src.modules.parametres.cache.SemanticCache")
    @patch("src.modules.parametres.cache.st")
    def test_render_cache_config(self, mock_st, mock_sem, mock_cache) -> None:
        """Test config cache."""
        from src.modules.parametres import afficher_cache_config

        setup_mock_st(mock_st)
        mock_st.button.return_value = False
        afficher_cache_config()
        mock_st.markdown.assert_called()

    @patch("src.modules.parametres.affichage.st")
    def test_render_display_config(self, mock_st) -> None:
        """Test config affichage."""
        from src.modules.parametres import afficher_display_config

        setup_mock_st(
            mock_st, {"display_mode_selection": "💻 Normal", "display_mode_key": "💻 Normal"}
        )
        mock_st.radio.return_value = "💻 Normal"  # Mode par défaut
        afficher_display_config()
        mock_st.markdown.assert_called()

    def test_render_budget_config_exists(self) -> None:
        """Test that afficher_budget_config exists."""
        from src.modules.parametres import afficher_budget_config

        assert callable(afficher_budget_config)

    @patch("src.modules.parametres.about.st")
    def test_render_about(self, mock_st) -> None:
        """Test page a propos."""
        from src.modules.parametres import afficher_about

        setup_mock_st(mock_st)
        afficher_about()
        mock_st.markdown.assert_called()


class TestImports:
    """Tests des imports."""

    def test_import_app(self) -> None:
        """Test import app."""
        from src.modules.parametres import app

        assert callable(app)

    def test_import_render_foyer_config(self) -> None:
        """Test import afficher_foyer_config."""
        from src.modules.parametres import afficher_foyer_config

        assert callable(afficher_foyer_config)

    def test_import_render_ia_config(self) -> None:
        """Test import afficher_ia_config."""
        from src.modules.parametres import afficher_ia_config

        assert callable(afficher_ia_config)

    def test_import_render_database_config(self) -> None:
        """Test import afficher_database_config."""
        from src.modules.parametres import afficher_database_config

        assert callable(afficher_database_config)

    def test_import_render_cache_config(self) -> None:
        """Test import afficher_cache_config."""
        from src.modules.parametres import afficher_cache_config

        assert callable(afficher_cache_config)

    def test_import_render_display_config(self) -> None:
        """Test import afficher_display_config."""
        from src.modules.parametres import afficher_display_config

        assert callable(afficher_display_config)

    def test_import_render_budget_config(self) -> None:
        """Test import afficher_budget_config."""
        from src.modules.parametres import afficher_budget_config

        assert callable(afficher_budget_config)

    def test_import_render_about(self) -> None:
        """Test import afficher_about."""
        from src.modules.parametres import afficher_about

        assert callable(afficher_about)
