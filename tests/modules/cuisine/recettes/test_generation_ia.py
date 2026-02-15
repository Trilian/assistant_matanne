"""
Tests pour src/modules/cuisine/recettes/generation_ia.py
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
    mock_st.info = MagicMock()
    mock_st.warning = MagicMock()
    mock_st.success = MagicMock()
    mock_st.divider = MagicMock()
    mock_st.toast = MagicMock()
    mock_st.write = MagicMock()
    mock_st.markdown = MagicMock()
    mock_st.caption = MagicMock()
    mock_st.metric = MagicMock()
    mock_st.radio = MagicMock(return_value="Personnalise")
    mock_st.selectbox = MagicMock(return_value="dejeuner")
    mock_st.slider = MagicMock(return_value=3)
    mock_st.number_input = MagicMock(return_value=3)
    mock_st.text_input = MagicMock(return_value="")
    mock_st.text_area = MagicMock(return_value="")
    mock_st.button = MagicMock(return_value=False)
    mock_st.form_submit_button = MagicMock(return_value=False)
    mock_st.form = MagicMock(return_value=MagicMock(__enter__=MagicMock(), __exit__=MagicMock()))
    mock_st.spinner = MagicMock(return_value=MagicMock(__enter__=MagicMock(), __exit__=MagicMock()))
    mock_st.container = MagicMock(
        return_value=MagicMock(__enter__=MagicMock(), __exit__=MagicMock())
    )
    mock_st.expander = MagicMock(
        return_value=MagicMock(__enter__=MagicMock(), __exit__=MagicMock())
    )

    def mock_columns(*args, **kwargs):
        n = len(args[0]) if args and isinstance(args[0], list) else args[0] if args else 2
        return [
            MagicMock(__enter__=MagicMock(return_value=MagicMock()), __exit__=MagicMock())
            for _ in range(n)
        ]

    mock_st.columns = MagicMock(side_effect=mock_columns)
    return mock_st


class TestImports:
    def test_import_render_generer_ia(self):
        from src.modules.cuisine.recettes.generation_ia import render_generer_ia

        assert callable(render_generer_ia)

    def test_import_render_recherche_specifique(self):
        from src.modules.cuisine.recettes.generation_ia import _render_recherche_specifique

        assert callable(_render_recherche_specifique)

    def test_import_render_mode_personnalise(self):
        from src.modules.cuisine.recettes.generation_ia import _render_mode_personnalise

        assert callable(_render_mode_personnalise)

    def test_import_render_suggestion_card(self):
        from src.modules.cuisine.recettes.generation_ia import _render_suggestion_card

        assert callable(_render_suggestion_card)


class TestRenderGenererIa:
    @patch("src.modules.cuisine.recettes.generation_ia.st")
    @patch("src.modules.cuisine.recettes.generation_ia.get_recette_service")
    def test_render_generer_ia_service_none(self, mock_get_service, mock_st):
        setup_mock_st(mock_st)
        mock_get_service.return_value = None
        from src.modules.cuisine.recettes.generation_ia import render_generer_ia

        render_generer_ia()
        mock_st.error.assert_called()

    @patch("src.modules.cuisine.recettes.generation_ia.st")
    @patch("src.modules.cuisine.recettes.generation_ia.get_recette_service")
    def test_render_generer_ia_mode_personnalise(self, mock_get_service, mock_st):
        setup_mock_st(mock_st)
        mock_st.radio.return_value = "Personnalise"
        mock_get_service.return_value = MagicMock()
        from src.modules.cuisine.recettes.generation_ia import render_generer_ia

        render_generer_ia()
        mock_st.radio.assert_called()

    @patch("src.modules.cuisine.recettes.generation_ia.st")
    @patch("src.modules.cuisine.recettes.generation_ia.get_recette_service")
    def test_render_generer_ia_mode_recherche(self, mock_get_service, mock_st):
        setup_mock_st(mock_st)
        mock_st.radio.return_value = "Recherche specifique"
        mock_get_service.return_value = MagicMock()
        from src.modules.cuisine.recettes.generation_ia import render_generer_ia

        render_generer_ia()
        mock_st.radio.assert_called()


class TestRenderRechercheSpecifique:
    @patch("src.modules.cuisine.recettes.generation_ia.st")
    def test_render_recherche_specifique_basic(self, mock_st):
        setup_mock_st(mock_st)
        from src.modules.cuisine.recettes.generation_ia import _render_recherche_specifique

        _render_recherche_specifique(MagicMock())
        mock_st.info.assert_called()

    @patch("src.modules.cuisine.recettes.generation_ia.st")
    def test_render_recherche_specifique_submit_no_recette(self, mock_st):
        setup_mock_st(mock_st)
        mock_st.form_submit_button.return_value = True
        mock_st.text_input.return_value = ""
        mock_service = MagicMock()
        from src.modules.cuisine.recettes.generation_ia import _render_recherche_specifique

        _render_recherche_specifique(mock_service)
        mock_service.generer_variantes_recette_ia.assert_not_called()

    @patch("src.modules.cuisine.recettes.generation_ia.st")
    def test_render_recherche_specifique_submit_success(self, mock_st):
        setup_mock_st(mock_st)
        mock_st.form_submit_button.return_value = True
        mock_st.text_input.return_value = "Pates"
        mock_service = MagicMock()
        mock_sug = MagicMock(
            nom="Pates Carbonara",
            difficulte="facile",
            description="Desc",
            temps_preparation=15,
            temps_cuisson=20,
            portions=4,
            ingredients=[],
            etapes=[],
        )
        mock_service.generer_variantes_recette_ia.return_value = [mock_sug]
        from src.modules.cuisine.recettes.generation_ia import _render_recherche_specifique

        _render_recherche_specifique(mock_service)
        mock_st.success.assert_called()

    @patch("src.modules.cuisine.recettes.generation_ia.st")
    def test_render_recherche_specifique_no_results(self, mock_st):
        setup_mock_st(mock_st)
        mock_st.form_submit_button.return_value = True
        mock_st.text_input.return_value = "Recette rare"
        mock_service = MagicMock()
        mock_service.generer_variantes_recette_ia.return_value = []
        from src.modules.cuisine.recettes.generation_ia import _render_recherche_specifique

        _render_recherche_specifique(mock_service)
        mock_st.warning.assert_called()

    @patch("src.modules.cuisine.recettes.generation_ia.st")
    def test_render_recherche_specifique_error(self, mock_st):
        setup_mock_st(mock_st)
        mock_st.form_submit_button.return_value = True
        mock_st.text_input.return_value = "Pates"
        mock_service = MagicMock()
        mock_service.generer_variantes_recette_ia.side_effect = Exception("Erreur")
        from src.modules.cuisine.recettes.generation_ia import _render_recherche_specifique

        _render_recherche_specifique(mock_service)
        mock_st.error.assert_called()


class TestRenderModePersonnalise:
    @patch("src.modules.cuisine.recettes.generation_ia.st")
    def test_render_mode_personnalise_basic(self, mock_st):
        setup_mock_st(mock_st)
        from src.modules.cuisine.recettes.generation_ia import _render_mode_personnalise

        _render_mode_personnalise(MagicMock())
        mock_st.info.assert_called()

    @patch("src.modules.cuisine.recettes.generation_ia.st")
    def test_render_mode_personnalise_submit_missing_fields(self, mock_st):
        setup_mock_st(mock_st)
        mock_st.form_submit_button.return_value = True
        mock_st.selectbox.return_value = ""
        mock_service = MagicMock()
        from src.modules.cuisine.recettes.generation_ia import _render_mode_personnalise

        _render_mode_personnalise(mock_service)
        mock_service.generer_recettes_ia.assert_not_called()

    @patch("src.modules.cuisine.recettes.generation_ia.st")
    def test_render_mode_personnalise_submit_success(self, mock_st):
        setup_mock_st(mock_st)
        mock_st.form_submit_button.return_value = True
        mock_st.selectbox.return_value = "dejeuner"
        mock_service = MagicMock()
        mock_sug = MagicMock(
            nom="Salade",
            difficulte="facile",
            description="Desc",
            temps_preparation=10,
            temps_cuisson=0,
            portions=2,
            ingredients=[],
            etapes=[],
        )
        mock_service.generer_recettes_ia.return_value = [mock_sug]
        from src.modules.cuisine.recettes.generation_ia import _render_mode_personnalise

        _render_mode_personnalise(mock_service)
        mock_st.success.assert_called()

    @patch("src.modules.cuisine.recettes.generation_ia.st")
    def test_render_mode_personnalise_with_ingredients(self, mock_st):
        setup_mock_st(mock_st)
        mock_st.form_submit_button.return_value = True
        mock_st.selectbox.return_value = "diner"
        mock_st.text_area.return_value = "tomate, oignon, ail"
        mock_service = MagicMock()
        mock_service.generer_recettes_ia.return_value = []
        from src.modules.cuisine.recettes.generation_ia import _render_mode_personnalise

        _render_mode_personnalise(mock_service)
        call_args = mock_service.generer_recettes_ia.call_args
        assert call_args[1].get("ingredients_dispo") == ["tomate", "oignon", "ail"]

    @patch("src.modules.cuisine.recettes.generation_ia.st")
    def test_render_mode_personnalise_error(self, mock_st):
        setup_mock_st(mock_st)
        mock_st.form_submit_button.return_value = True
        mock_st.selectbox.return_value = "dejeuner"
        mock_service = MagicMock()
        mock_service.generer_recettes_ia.side_effect = Exception("Erreur")
        from src.modules.cuisine.recettes.generation_ia import _render_mode_personnalise

        _render_mode_personnalise(mock_service)
        mock_st.error.assert_called()


class TestRenderSuggestionCard:
    @patch("src.modules.cuisine.recettes.generation_ia.st")
    def test_render_suggestion_card_basic(self, mock_st):
        setup_mock_st(mock_st)
        mock_sug = MagicMock(
            nom="Test",
            difficulte="facile",
            description="Desc",
            temps_preparation=15,
            temps_cuisson=30,
            portions=4,
            ingredients=[],
            etapes=[],
        )
        from src.modules.cuisine.recettes.generation_ia import _render_suggestion_card

        _render_suggestion_card(mock_sug, 1, MagicMock())
        mock_st.container.assert_called()

    @patch("src.modules.cuisine.recettes.generation_ia.st")
    def test_render_suggestion_card_variant(self, mock_st):
        setup_mock_st(mock_st)
        mock_sug = MagicMock(
            nom="Variante",
            difficulte="moyen",
            description=None,
            temps_preparation=20,
            temps_cuisson=40,
            portions=6,
            ingredients=[],
            etapes=[],
        )
        from src.modules.cuisine.recettes.generation_ia import _render_suggestion_card

        _render_suggestion_card(mock_sug, 2, MagicMock(), is_variant=True)
        mock_st.container.assert_called()

    @patch("src.modules.cuisine.recettes.generation_ia.st")
    def test_render_suggestion_card_with_ingredients_dict(self, mock_st):
        setup_mock_st(mock_st)
        mock_sug = MagicMock(
            nom="Recette",
            difficulte="difficile",
            description="Desc",
            temps_preparation=30,
            temps_cuisson=60,
            portions=8,
            ingredients=[{"nom": "farine", "quantite": 250, "unite": "g"}],
            etapes=[],
        )
        from src.modules.cuisine.recettes.generation_ia import _render_suggestion_card

        _render_suggestion_card(mock_sug, 1, MagicMock())
        mock_st.markdown.assert_called()

    @patch("src.modules.cuisine.recettes.generation_ia.st")
    def test_render_suggestion_card_with_etapes(self, mock_st):
        setup_mock_st(mock_st)
        mock_sug = MagicMock(
            nom="Recette",
            difficulte="facile",
            description="Desc",
            temps_preparation=10,
            temps_cuisson=15,
            portions=2,
            ingredients=[],
            etapes=["Etape 1", "Etape 2"],
        )
        from src.modules.cuisine.recettes.generation_ia import _render_suggestion_card

        _render_suggestion_card(mock_sug, 1, MagicMock())
        mock_st.expander.assert_called()

    @patch("src.modules.cuisine.recettes.generation_ia.st")
    def test_render_suggestion_card_button_shown(self, mock_st):
        setup_mock_st(mock_st)
        mock_sug = MagicMock(
            nom="Test",
            difficulte="facile",
            description="Desc",
            temps_preparation=10,
            temps_cuisson=20,
            portions=4,
            ingredients=[],
            etapes=[],
        )
        from src.modules.cuisine.recettes.generation_ia import _render_suggestion_card

        _render_suggestion_card(mock_sug, 1, MagicMock())
        mock_st.button.assert_called()

    @patch("src.modules.cuisine.recettes.generation_ia.st")
    def test_render_suggestion_card_with_type_repas_saison(self, mock_st):
        setup_mock_st(mock_st)
        mock_sug = MagicMock(
            nom="Recette",
            difficulte="facile",
            description=None,
            temps_preparation=5,
            temps_cuisson=5,
            portions=1,
            ingredients=None,
            etapes=None,
        )
        from src.modules.cuisine.recettes.generation_ia import _render_suggestion_card

        _render_suggestion_card(mock_sug, 1, MagicMock(), type_repas="dejeuner", saison="ete")
        mock_st.container.assert_called()
