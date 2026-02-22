"""Tests complets pour le module rapports.py UI."""

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
    mock_st.tabs.return_value = [MagicMock() for _ in range(4)]
    mock_st.session_state = SessionStateMock(session_data or {})
    for cm in ["container", "expander", "spinner", "form"]:
        getattr(mock_st, cm).return_value.__enter__ = MagicMock(return_value=MagicMock())
        getattr(mock_st, cm).return_value.__exit__ = MagicMock(return_value=False)


@pytest.mark.unit
class TestRapportsUI:
    """Tests pour les fonctions UI du module rapports."""

    @patch("src.modules.utilitaires.rapports.afficher_historique")
    @patch("src.modules.utilitaires.rapports.afficher_analyse_gaspillage")
    @patch("src.modules.utilitaires.rapports.afficher_rapport_budget")
    @patch("src.modules.utilitaires.rapports.afficher_rapport_stocks")
    @patch("src.modules.utilitaires.rapports.st")
    def test_app_basic(self, mock_st, *mocks) -> None:
        """Test du rendu basique de app()."""
        from src.modules.utilitaires.rapports import app

        setup_mock_st(mock_st)
        app()
        mock_st.markdown.assert_called()
        mock_st.tabs.assert_called_once()

    @patch("src.modules.utilitaires.rapports.get_rapports_service")
    @patch("src.modules.utilitaires.rapports.st")
    def test_render_rapport_stocks(self, mock_st, mock_srv) -> None:
        """Test rapport stocks."""
        from src.modules.utilitaires.rapports import afficher_rapport_stocks

        setup_mock_st(mock_st)
        mock_st.selectbox.return_value = (7, "Derniers 7 jours")
        mock_st.button.return_value = False
        afficher_rapport_stocks()
        mock_st.subheader.assert_called()

    @patch("src.modules.utilitaires.rapports.get_rapports_service")
    @patch("src.modules.utilitaires.rapports.st")
    def test_render_rapport_budget(self, mock_st, mock_srv) -> None:
        """Test rapport budget."""
        from src.modules.utilitaires.rapports import afficher_rapport_budget

        setup_mock_st(mock_st)
        mock_st.selectbox.return_value = (30, "Dernier mois")
        mock_st.button.return_value = False
        afficher_rapport_budget()
        mock_st.subheader.assert_called()

    @patch("src.modules.utilitaires.rapports.get_rapports_service")
    @patch("src.modules.utilitaires.rapports.st")
    def test_render_analyse_gaspillage(self, mock_st, mock_srv) -> None:
        """Test analyse gaspillage."""
        from src.modules.utilitaires.rapports import afficher_analyse_gaspillage

        setup_mock_st(mock_st)
        mock_st.selectbox.return_value = (90, "3 mois")
        mock_st.button.return_value = False
        afficher_analyse_gaspillage()
        mock_st.subheader.assert_called()

    @patch("src.modules.utilitaires.rapports.get_rapports_service")
    @patch("src.modules.utilitaires.rapports.st")
    def test_render_historique_empty(self, mock_st, mock_srv) -> None:
        """Test historique vide."""
        from src.modules.utilitaires.rapports import afficher_historique

        setup_mock_st(mock_st)
        mock_srv.return_value.get_historique_rapports.return_value = []
        afficher_historique()
        mock_st.subheader.assert_called()

    @patch("src.modules.utilitaires.rapports.get_rapports_service")
    @patch("src.modules.utilitaires.rapports.st")
    def test_render_historique_with_data(self, mock_st, mock_srv) -> None:
        """Test historique avec donnees."""
        from src.modules.utilitaires.rapports import afficher_historique

        setup_mock_st(mock_st)
        mock_srv.return_value.get_historique_rapports.return_value = [
            {"date": "2024-01-01", "type": "stocks", "fichier": "rapport.pdf"},
            {"date": "2024-01-02", "type": "budget", "fichier": "budget.pdf"},
        ]
        afficher_historique()
        mock_st.subheader.assert_called()


@pytest.mark.unit
class TestGetRapportsService:
    """Tests pour get_rapports_service."""

    @patch("src.services.rapports.ServiceRapportsPDF")
    @patch("src.modules.utilitaires.rapports.st")
    def test_creates_service(self, mock_st, mock_cls) -> None:
        """Test creation service."""
        from src.modules.utilitaires.rapports import get_rapports_service

        mock_st.session_state = SessionStateMock({})
        get_rapports_service()
        mock_cls.assert_called_once()

    @patch("src.services.rapports.ServiceRapportsPDF")
    @patch("src.modules.utilitaires.rapports.st")
    def test_returns_cached_service(self, mock_st, mock_cls) -> None:
        """Test retourne service cache."""
        from src.modules.utilitaires.rapports import get_rapports_service

        cached = MagicMock()
        mock_st.session_state = SessionStateMock({"rapports_service": cached})
        result = get_rapports_service()
        assert result == cached


class TestImports:
    """Tests des imports."""

    def test_import_app(self) -> None:
        """Test import app."""
        from src.modules.utilitaires.rapports import app

        assert callable(app)

    def test_import_get_rapports_service(self) -> None:
        """Test import get_rapports_service."""
        from src.modules.utilitaires.rapports import get_rapports_service

        assert callable(get_rapports_service)

    def test_import_render_rapport_stocks(self) -> None:
        """Test import afficher_rapport_stocks."""
        from src.modules.utilitaires.rapports import afficher_rapport_stocks

        assert callable(afficher_rapport_stocks)

    def test_import_render_rapport_budget(self) -> None:
        """Test import afficher_rapport_budget."""
        from src.modules.utilitaires.rapports import afficher_rapport_budget

        assert callable(afficher_rapport_budget)

    def test_import_render_analyse_gaspillage(self) -> None:
        """Test import afficher_analyse_gaspillage."""
        from src.modules.utilitaires.rapports import afficher_analyse_gaspillage

        assert callable(afficher_analyse_gaspillage)

    def test_import_render_historique(self) -> None:
        """Test import afficher_historique."""
        from src.modules.utilitaires.rapports import afficher_historique

        assert callable(afficher_historique)
