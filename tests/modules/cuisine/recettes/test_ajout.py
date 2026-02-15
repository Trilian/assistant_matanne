"""
Tests pour src/modules/cuisine/recettes/ajout.py
"""

from unittest.mock import MagicMock, patch

import pytest


class SessionStateMock(dict):
    def __getattr__(self, key):
        return self.get(key)

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        if key in self:
            del self[key]


def setup_mock_st(mock_st, session_state=None):
    mock_st.session_state = session_state or SessionStateMock()
    mock_st.subheader = MagicMock()
    mock_st.error = MagicMock()
    mock_st.success = MagicMock()
    mock_st.warning = MagicMock()
    mock_st.caption = MagicMock()
    mock_st.markdown = MagicMock()
    mock_st.balloons = MagicMock()
    mock_st.text_input = MagicMock(return_value="")
    mock_st.text_area = MagicMock(return_value="")
    mock_st.number_input = MagicMock(return_value=1)
    mock_st.selectbox = MagicMock(return_value="dejeuner")
    mock_st.file_uploader = MagicMock(return_value=None)
    mock_st.button = MagicMock(return_value=False)

    def mock_columns(*args, **kwargs):
        n = len(args[0]) if args and isinstance(args[0], list) else args[0] if args else 2
        return [
            MagicMock(__enter__=MagicMock(return_value=MagicMock()), __exit__=MagicMock())
            for _ in range(n)
        ]

    mock_st.columns = MagicMock(side_effect=mock_columns)
    return mock_st


class TestImports:
    def test_import_render_ajouter_manuel(self):
        from src.modules.cuisine.recettes.ajout import render_ajouter_manuel

        assert callable(render_ajouter_manuel)

    def test_all_exports(self):
        from src.modules.cuisine.recettes.ajout import __all__

        assert "render_ajouter_manuel" in __all__


class TestRenderAjouterManuel:
    @patch("src.modules.cuisine.recettes.ajout.st")
    def test_render_ajouter_manuel_basic(self, mock_st):
        setup_mock_st(mock_st)
        mock_st.number_input.return_value = 3
        from src.modules.cuisine.recettes.ajout import render_ajouter_manuel

        render_ajouter_manuel()
        mock_st.subheader.assert_called()
        mock_st.button.assert_called()

    @patch("src.modules.cuisine.recettes.ajout.st")
    def test_render_ajouter_manuel_init_session_state(self, mock_st):
        session = SessionStateMock()
        setup_mock_st(mock_st, session)
        mock_st.number_input.return_value = 3
        from src.modules.cuisine.recettes.ajout import render_ajouter_manuel

        render_ajouter_manuel()
        assert mock_st.session_state.form_num_ingredients == 3

    @patch("src.modules.cuisine.recettes.ajout.st")
    def test_render_ajouter_manuel_submit_no_nom(self, mock_st):
        setup_mock_st(mock_st)
        mock_st.button.return_value = True
        mock_st.text_input.return_value = ""
        mock_st.number_input.return_value = 3
        from src.modules.cuisine.recettes.ajout import render_ajouter_manuel

        render_ajouter_manuel()
        mock_st.error.assert_called()

    @patch("src.modules.cuisine.recettes.ajout.st")
    def test_render_ajouter_manuel_submit_no_ingredients(self, mock_st):
        setup_mock_st(mock_st)
        mock_st.button.return_value = True

        def text_input_side_effect(label, *args, **kwargs):
            if "Nom" in label:
                return "Ma Recette"
            return ""

        mock_st.text_input.side_effect = text_input_side_effect
        mock_st.number_input.return_value = 3
        from src.modules.cuisine.recettes.ajout import render_ajouter_manuel

        render_ajouter_manuel()
        mock_st.error.assert_called()

    @patch("src.modules.cuisine.recettes.ajout.st")
    def test_render_ajouter_manuel_submit_no_etapes(self, mock_st):
        setup_mock_st(mock_st)
        mock_st.button.return_value = True
        call_count = [0]

        def text_input_side_effect(label, *args, **kwargs):
            if "Nom" in label:
                return "Ma Recette"
            if "dient" in label:
                call_count[0] += 1
                if call_count[0] == 1:
                    return "Farine"
            return ""

        mock_st.text_input.side_effect = text_input_side_effect
        mock_st.text_area.return_value = ""
        mock_st.number_input.return_value = 1
        from src.modules.cuisine.recettes.ajout import render_ajouter_manuel

        render_ajouter_manuel()
        mock_st.error.assert_called()

    @patch("src.modules.cuisine.recettes.ajout.get_recette_service")
    @patch("src.modules.cuisine.recettes.ajout.st")
    def test_render_ajouter_manuel_service_none(self, mock_st, mock_get_service):
        setup_mock_st(mock_st)
        mock_st.button.return_value = True
        mock_get_service.return_value = None
        input_calls = [0]

        def text_input_side_effect(label, *args, **kwargs):
            if "Nom" in label:
                return "Ma Recette"
            if "dient" in label:
                input_calls[0] += 1
                if input_calls[0] == 1:
                    return "Farine"
            return ""

        mock_st.text_input.side_effect = text_input_side_effect
        area_calls = [0]

        def text_area_side_effect(label, *args, **kwargs):
            if "tape" in label:
                area_calls[0] += 1
                if area_calls[0] == 1:
                    return "Melanger"
            return ""

        mock_st.text_area.side_effect = text_area_side_effect
        mock_st.number_input.return_value = 1
        from src.modules.cuisine.recettes.ajout import render_ajouter_manuel

        render_ajouter_manuel()
        mock_st.error.assert_called()

    @patch("src.core.database.obtenir_contexte_db")
    @patch("src.modules.cuisine.recettes.ajout.get_recette_service")
    @patch("src.modules.cuisine.recettes.ajout.st")
    def test_render_ajouter_manuel_success(self, mock_st, mock_get_service, mock_db_ctx):
        session = SessionStateMock()
        session["form_nom"] = "test"
        setup_mock_st(mock_st, session)
        mock_st.button.return_value = True
        mock_st.file_uploader.return_value = None
        mock_service = MagicMock()
        mock_recette = MagicMock()
        mock_recette.nom = "Ma Recette"
        mock_service.create_complete.return_value = mock_recette
        mock_get_service.return_value = mock_service
        mock_db = MagicMock()
        mock_db_ctx.return_value.__enter__ = MagicMock(return_value=mock_db)
        mock_db_ctx.return_value.__exit__ = MagicMock(return_value=False)
        input_calls = [0]

        def text_input_side_effect(label, *args, **kwargs):
            if "Nom" in label:
                return "Ma Recette"
            if "dient" in label:
                input_calls[0] += 1
                if input_calls[0] == 1:
                    return "Farine"
            return ""

        mock_st.text_input.side_effect = text_input_side_effect
        area_calls = [0]

        def text_area_side_effect(label, *args, **kwargs):
            if "tape" in label:
                area_calls[0] += 1
                if area_calls[0] == 1:
                    return "Melanger"
            return ""

        mock_st.text_area.side_effect = text_area_side_effect
        mock_st.number_input.return_value = 1
        from src.modules.cuisine.recettes.ajout import render_ajouter_manuel

        render_ajouter_manuel()
        mock_st.success.assert_called()
        mock_st.balloons.assert_called()

    @patch("src.core.database.obtenir_contexte_db")
    @patch("src.modules.cuisine.recettes.ajout.get_recette_service")
    @patch("src.modules.cuisine.recettes.ajout.st")
    def test_render_ajouter_manuel_validation_error(self, mock_st, mock_get_service, mock_db_ctx):
        from src.core.errors_base import ErreurValidation

        setup_mock_st(mock_st)
        mock_st.button.return_value = True
        mock_service = MagicMock()
        mock_service.create_complete.side_effect = ErreurValidation("Erreur")
        mock_get_service.return_value = mock_service
        mock_db = MagicMock()
        mock_db_ctx.return_value.__enter__ = MagicMock(return_value=mock_db)
        mock_db_ctx.return_value.__exit__ = MagicMock(return_value=False)
        input_calls = [0]

        def text_input_side_effect(label, *args, **kwargs):
            if "Nom" in label:
                return "Ma Recette"
            if "dient" in label:
                input_calls[0] += 1
                if input_calls[0] == 1:
                    return "Farine"
            return ""

        mock_st.text_input.side_effect = text_input_side_effect
        area_calls = [0]

        def text_area_side_effect(label, *args, **kwargs):
            if "tape" in label:
                area_calls[0] += 1
                if area_calls[0] == 1:
                    return "Melanger"
            return ""

        mock_st.text_area.side_effect = text_area_side_effect
        mock_st.number_input.return_value = 1
        from src.modules.cuisine.recettes.ajout import render_ajouter_manuel

        render_ajouter_manuel()
        mock_st.error.assert_called()

    @patch("src.core.database.obtenir_contexte_db")
    @patch("src.modules.cuisine.recettes.ajout.get_recette_service")
    @patch("src.modules.cuisine.recettes.ajout.st")
    def test_render_ajouter_manuel_generic_error(self, mock_st, mock_get_service, mock_db_ctx):
        setup_mock_st(mock_st)
        mock_st.button.return_value = True
        mock_service = MagicMock()
        mock_service.create_complete.side_effect = Exception("DB Error")
        mock_get_service.return_value = mock_service
        mock_db = MagicMock()
        mock_db_ctx.return_value.__enter__ = MagicMock(return_value=mock_db)
        mock_db_ctx.return_value.__exit__ = MagicMock(return_value=False)
        input_calls = [0]

        def text_input_side_effect(label, *args, **kwargs):
            if "Nom" in label:
                return "Ma Recette"
            if "dient" in label:
                input_calls[0] += 1
                if input_calls[0] == 1:
                    return "Farine"
            return ""

        mock_st.text_input.side_effect = text_input_side_effect
        area_calls = [0]

        def text_area_side_effect(label, *args, **kwargs):
            if "tape" in label:
                area_calls[0] += 1
                if area_calls[0] == 1:
                    return "Melanger"
            return ""

        mock_st.text_area.side_effect = text_area_side_effect
        mock_st.number_input.return_value = 1
        from src.modules.cuisine.recettes.ajout import render_ajouter_manuel

        render_ajouter_manuel()
        mock_st.error.assert_called()

    @patch("src.modules.cuisine.recettes.ajout.st")
    def test_render_ajouter_manuel_form_fields_displayed(self, mock_st):
        setup_mock_st(mock_st)
        mock_st.number_input.return_value = 3
        from src.modules.cuisine.recettes.ajout import render_ajouter_manuel

        render_ajouter_manuel()
        assert mock_st.text_input.call_count > 0
        assert mock_st.text_area.call_count > 0
        assert mock_st.number_input.call_count > 0
        assert mock_st.selectbox.call_count > 0
        mock_st.file_uploader.assert_called()
