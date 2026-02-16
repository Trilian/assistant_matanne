"""Tests pour le point d entree app() du calendrier unifie."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any
from unittest.mock import MagicMock, patch

import pytest


class SessionStateMock(dict):
    """Mock de st.session_state supportant l acces par attribut."""

    def __getattr__(self, name: str) -> Any:
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name: str, value: Any) -> None:
        self[name] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self[key] if key in self else default


def setup_mock_st(mock_st: MagicMock, session_data: dict | None = None) -> None:
    """Configure le mock Streamlit."""
    mock_st.columns.side_effect = lambda n: [
        MagicMock() for _ in range(n if isinstance(n, int) else len(n))
    ]
    mock_st.session_state = SessionStateMock(session_data or {})
    mock_st.container.return_value.__enter__ = MagicMock(return_value=MagicMock())
    mock_st.container.return_value.__exit__ = MagicMock(return_value=False)
    mock_st.expander.return_value.__enter__ = MagicMock(return_value=MagicMock())
    mock_st.expander.return_value.__exit__ = MagicMock(return_value=False)
    mock_st.form.return_value.__enter__ = MagicMock(return_value=MagicMock())
    mock_st.form.return_value.__exit__ = MagicMock(return_value=False)
    mock_st.spinner.return_value.__enter__ = MagicMock(return_value=MagicMock())
    mock_st.spinner.return_value.__exit__ = MagicMock(return_value=False)


class TestAppFunction:
    """Tests pour la fonction app() du calendrier unifie."""

    @patch("src.modules.planning.calendrier.charger_donnees_semaine")
    @patch("src.modules.planning.calendrier.st")
    def test_app_basic_render(self, mock_st: MagicMock, mock_charger: MagicMock) -> None:
        """Test du rendu basique de l app."""
        from src.modules.planning.calendrier import app

        setup_mock_st(mock_st, {"cal_semaine_debut": date.today()})
        mock_st.radio.return_value = "Grille"
        mock_charger.return_value = {
            "repas": [],
            "sessions_batch": [],
            "activites": [],
            "events": [],
            "courses_planifiees": [],
            "taches_menage": [],
        }

        app()

        mock_st.title.assert_called()

    @patch("src.modules.planning.calendrier.charger_donnees_semaine")
    @patch("src.modules.planning.calendrier.st")
    def test_app_vue_liste(self, mock_st: MagicMock, mock_charger: MagicMock) -> None:
        """Test avec la vue liste."""
        from src.modules.planning.calendrier import app

        setup_mock_st(mock_st, {"cal_semaine_debut": date.today()})
        mock_st.radio.return_value = "Liste detaillee"
        mock_charger.return_value = {
            "repas": [],
            "sessions_batch": [],
            "activites": [],
            "events": [],
            "courses_planifiees": [],
            "taches_menage": [],
        }

        app()

        mock_st.title.assert_called()

    @patch("src.modules.planning.calendrier.charger_donnees_semaine")
    @patch("src.modules.planning.calendrier.st")
    def test_app_without_session(self, mock_st: MagicMock, mock_charger: MagicMock) -> None:
        """Test sans session existante."""
        from src.modules.planning.calendrier import app

        setup_mock_st(mock_st)
        mock_st.radio.return_value = "Grille"
        mock_charger.return_value = {
            "repas": [],
            "sessions_batch": [],
            "activites": [],
            "events": [],
            "courses_planifiees": [],
            "taches_menage": [],
        }

        app()

        assert "cal_semaine_debut" in mock_st.session_state
