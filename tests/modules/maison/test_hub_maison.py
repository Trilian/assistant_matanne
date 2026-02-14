"""Tests pour hub_maison.py."""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

import pytest


class SessionStateMock(dict):
    def __getattr__(self, name: str) -> Any:
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name: str, value: Any) -> None:
        self[name] = value


def setup_mock_st(mock_st: MagicMock, session_data: dict | None = None) -> None:
    mock_st.columns.side_effect = lambda n: [
        MagicMock() for _ in range(n if isinstance(n, int) else len(n))
    ]
    mock_st.tabs.return_value = [MagicMock() for _ in range(6)]
    mock_st.session_state = SessionStateMock(session_data or {})
    mock_st.button.return_value = False
    for cm in ["container", "expander", "spinner", "form"]:
        getattr(mock_st, cm).return_value.__enter__ = MagicMock(return_value=MagicMock())
        getattr(mock_st, cm).return_value.__exit__ = MagicMock(return_value=False)


@pytest.mark.unit
class TestGetStats:
    def test_get_stats_projets_fallback(self) -> None:
        with patch("src.modules.maison.hub_maison.obtenir_contexte_db") as mock_db:
            mock_db.side_effect = Exception("DB Error")
            from src.modules.maison.hub_maison import get_stats_projets

            result = get_stats_projets()
            assert result == {"total": 0, "en_cours": 0}

    def test_get_stats_jardin_fallback(self) -> None:
        with patch("src.modules.maison.hub_maison.obtenir_contexte_db") as mock_db:
            mock_db.side_effect = Exception("DB Error")
            from src.modules.maison.hub_maison import get_stats_jardin

            result = get_stats_jardin()
            assert result == {"zones": 0, "etat_moyen": 0, "surface": 2600}

    def test_get_stats_menage_fallback(self) -> None:
        with patch("src.modules.maison.hub_maison.obtenir_contexte_db") as mock_db:
            mock_db.side_effect = Exception("DB Error")
            from src.modules.maison.hub_maison import get_stats_menage

            result = get_stats_menage()
            assert result == {"a_faire": 0, "urgentes": 0}

    def test_get_stats_meubles_fallback(self) -> None:
        with patch("src.modules.maison.hub_maison.obtenir_contexte_db") as mock_db:
            mock_db.side_effect = Exception("DB Error")
            from src.modules.maison.hub_maison import get_stats_meubles

            result = get_stats_meubles()
            assert result == {"en_attente": 0, "budget_estime": 0}

    def test_get_stats_eco_fallback(self) -> None:
        with patch("src.modules.maison.hub_maison.obtenir_contexte_db") as mock_db:
            mock_db.side_effect = Exception("DB Error")
            from src.modules.maison.hub_maison import get_stats_eco

            result = get_stats_eco()
            assert result == {"actions": 0, "economie_mensuelle": 0}

    def test_get_stats_depenses_fallback(self) -> None:
        with patch("src.modules.maison.hub_maison.obtenir_contexte_db") as mock_db:
            mock_db.side_effect = Exception("DB Error")
            from src.modules.maison.hub_maison import get_stats_depenses

            result = get_stats_depenses()
            assert result == {"total_mois": 0, "nb_categories": 0}


@pytest.mark.unit
class TestRenderCards:
    @patch("src.modules.maison.hub_maison.st")
    @patch("src.modules.maison.hub_maison.get_stats_projets")
    def test_render_card_projets(self, mock_stats, mock_st) -> None:
        from src.modules.maison.hub_maison import render_card_projets

        setup_mock_st(mock_st)
        mock_stats.return_value = {"total": 2, "en_cours": 1}
        render_card_projets()
        mock_st.button.assert_called()

    @patch("src.modules.maison.hub_maison.st")
    @patch("src.modules.maison.hub_maison.get_stats_jardin")
    def test_render_card_jardin(self, mock_stats, mock_st) -> None:
        from src.modules.maison.hub_maison import render_card_jardin

        setup_mock_st(mock_st)
        mock_stats.return_value = {"zones": 3, "etat_moyen": 3.5, "surface": 600}
        render_card_jardin()
        mock_st.button.assert_called()

    @patch("src.modules.maison.hub_maison.st")
    @patch("src.modules.maison.hub_maison.get_stats_menage")
    def test_render_card_menage(self, mock_stats, mock_st) -> None:
        from src.modules.maison.hub_maison import render_card_menage

        setup_mock_st(mock_st)
        mock_stats.return_value = {"a_faire": 5, "urgentes": 1}
        render_card_menage()
        mock_st.button.assert_called()

    @patch("src.modules.maison.hub_maison.st")
    @patch("src.modules.maison.hub_maison.get_stats_meubles")
    def test_render_card_meubles(self, mock_stats, mock_st) -> None:
        from src.modules.maison.hub_maison import render_card_meubles

        setup_mock_st(mock_st)
        mock_stats.return_value = {"en_attente": 2, "budget_estime": 1500}
        render_card_meubles()
        mock_st.button.assert_called()

    @patch("src.modules.maison.hub_maison.st")
    @patch("src.modules.maison.hub_maison.get_stats_eco")
    def test_render_card_eco(self, mock_stats, mock_st) -> None:
        from src.modules.maison.hub_maison import render_card_eco

        setup_mock_st(mock_st)
        mock_stats.return_value = {"actions": 5, "economie_mensuelle": 75}
        render_card_eco()
        mock_st.button.assert_called()

    @patch("src.modules.maison.hub_maison.st")
    @patch("src.modules.maison.hub_maison.get_stats_depenses")
    def test_render_card_depenses(self, mock_stats, mock_st) -> None:
        from src.modules.maison.hub_maison import render_card_depenses

        setup_mock_st(mock_st)
        mock_stats.return_value = {"total_mois": 500, "nb_categories": 3}
        render_card_depenses()
        mock_st.button.assert_called()


@pytest.mark.unit
class TestRenderPages:
    @patch("src.modules.maison.hub_maison.st")
    def test_render_page_content_projets(self, mock_st) -> None:
        from src.modules.maison.hub_maison import render_page_content

        setup_mock_st(mock_st, {"maison_page": "projets"})
        with patch("src.modules.maison.projets.app"):
            render_page_content()

    @patch("src.modules.maison.hub_maison.st")
    def test_render_page_content_jardin(self, mock_st) -> None:
        from src.modules.maison.hub_maison import render_page_content

        setup_mock_st(mock_st, {"maison_page": "jardin"})
        with patch("src.modules.maison.jardin.app"):
            render_page_content()

    @patch("src.modules.maison.hub_maison.render_page_content")
    def test_app(self, mock_content) -> None:
        from src.modules.maison.hub_maison import app

        app()
        mock_content.assert_called()


class TestImports:
    def test_import_app(self) -> None:
        from src.modules.maison.hub_maison import app

        assert callable(app)

    def test_import_render_hub(self) -> None:
        from src.modules.maison.hub_maison import render_hub

        assert callable(render_hub)

    def test_import_get_stats_projets(self) -> None:
        from src.modules.maison.hub_maison import get_stats_projets

        assert callable(get_stats_projets)
