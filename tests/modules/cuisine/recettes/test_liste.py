"""Tests pour src/modules/cuisine/recettes/liste.py"""

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
    default_data = {"recettes_page": 0, "recettes_page_size": 9}
    if session_data:
        default_data.update(session_data)
    mock_st.session_state = SessionStateMock(default_data)

    def mock_columns(n, **kwargs):
        count = n if isinstance(n, int) else len(n)
        return [MagicMock() for _ in range(count)]

    mock_st.columns.side_effect = mock_columns
    mock_st.tabs.return_value = [MagicMock() for _ in range(4)]
    mock_st.selectbox.return_value = 9
    mock_st.button.return_value = False
    mock_st.text_input.return_value = ""
    mock_st.number_input.return_value = 60
    mock_st.slider.return_value = 0
    mock_st.checkbox.return_value = False
    mock_st.expander.return_value.__enter__ = MagicMock(return_value=MagicMock())
    mock_st.expander.return_value.__exit__ = MagicMock(return_value=False)


def create_mock_recette(id=1, nom="Tarte pommes"):
    recette = MagicMock()
    recette.id = id
    recette.nom = nom
    recette.difficulte = "facile"
    recette.url_image = None
    recette.temps_preparation = 30
    recette.temps_cuisson = 45
    recette.portions = 6
    recette.score_bio = 50
    recette.score_local = 30
    return recette


@pytest.mark.unit
class TestRenderListe:
    @patch("src.modules.cuisine.recettes.liste.get_recette_service")
    @patch("src.modules.cuisine.recettes.liste.st")
    def test_render_liste_basic(self, mock_st, mock_svc_factory) -> None:
        from src.modules.cuisine.recettes.liste import render_liste

        setup_mock_st(mock_st)
        mock_service = MagicMock()
        mock_service.get_liste_paginee.return_value = ([], 0)
        mock_svc_factory.return_value = mock_service
        render_liste()
        mock_st.columns.assert_called()

    @patch("src.modules.cuisine.recettes.liste.get_recette_service")
    @patch("src.modules.cuisine.recettes.liste.st")
    def test_render_liste_no_service(self, mock_st, mock_svc_factory) -> None:
        from src.modules.cuisine.recettes.liste import render_liste

        setup_mock_st(mock_st)
        mock_svc_factory.return_value = None
        render_liste()
        mock_st.error.assert_called()

    @patch("src.modules.cuisine.recettes.liste.get_recette_service")
    @patch("src.modules.cuisine.recettes.liste.st")
    def test_render_liste_with_recettes(self, mock_st, mock_svc_factory) -> None:
        from src.modules.cuisine.recettes.liste import render_liste

        setup_mock_st(mock_st)
        mock_service = MagicMock()
        recettes = [create_mock_recette(i, f"Recette {i}") for i in range(5)]
        mock_service.get_liste_paginee.return_value = (recettes, 5)
        mock_svc_factory.return_value = mock_service
        render_liste()


class TestImports:
    def test_import_render_liste(self) -> None:
        from src.modules.cuisine.recettes.liste import render_liste

        assert callable(render_liste)
