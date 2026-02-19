"""
Tests pour src/modules/cuisine/courses/suggestions_ia.py

Couverture complète des fonctions UI suggestions IA courses.
"""

from unittest.mock import MagicMock, patch


class MockSessionState(dict):
    """Mock pour session_state qui supporte l'accès par attribut."""

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name) from None

    def __setattr__(self, name, value):
        self[name] = value

    def get(self, key, default=None):
        return super().get(key, default)


class TestRenderSuggestionsIA:
    """Tests pour render_suggestions_ia()."""

    def test_import(self):
        """Test import réussi."""
        from src.modules.cuisine.courses.suggestions_ia import render_suggestions_ia

        assert render_suggestions_ia is not None

    @patch("src.modules.cuisine.courses.suggestions_ia.obtenir_service_recettes")
    @patch("src.modules.cuisine.courses.suggestions_ia.get_inventaire_service")
    @patch("src.modules.cuisine.courses.suggestions_ia.get_courses_service")
    @patch("src.modules.cuisine.courses.suggestions_ia.st")
    def test_render_tabs(self, mock_st, mock_courses, mock_inv, mock_recettes):
        """Test affichage des onglets."""
        from src.modules.cuisine.courses.suggestions_ia import render_suggestions_ia

        mock_courses.return_value = MagicMock()
        mock_inv.return_value = MagicMock()
        mock_recettes.return_value = MagicMock()

        tab1, tab2 = MagicMock(), MagicMock()
        mock_st.tabs.return_value = [tab1, tab2]
        tab1.__enter__ = MagicMock(return_value=tab1)
        tab1.__exit__ = MagicMock(return_value=False)
        tab2.__enter__ = MagicMock(return_value=tab2)
        tab2.__exit__ = MagicMock(return_value=False)

        mock_st.button.return_value = False
        mock_recettes.return_value.get_all.return_value = []

        render_suggestions_ia()

        mock_st.subheader.assert_called()
        mock_st.tabs.assert_called()

    @patch("src.modules.cuisine.courses.suggestions_ia.obtenir_service_recettes")
    @patch("src.modules.cuisine.courses.suggestions_ia.get_inventaire_service")
    @patch("src.modules.cuisine.courses.suggestions_ia.get_courses_service")
    @patch("src.modules.cuisine.courses.suggestions_ia.st")
    def test_render_inventaire_no_suggestions(self, mock_st, mock_courses, mock_inv, mock_recettes):
        """Test inventaire sans suggestions."""
        from src.modules.cuisine.courses.suggestions_ia import render_suggestions_ia

        svc = MagicMock()
        svc.generer_suggestions_ia_depuis_inventaire.return_value = []
        mock_courses.return_value = svc

        tab1, tab2 = MagicMock(), MagicMock()
        mock_st.tabs.return_value = [tab1, tab2]
        tab1.__enter__ = MagicMock(return_value=tab1)
        tab1.__exit__ = MagicMock(return_value=False)
        tab2.__enter__ = MagicMock(return_value=tab2)
        tab2.__exit__ = MagicMock(return_value=False)

        mock_st.button.return_value = True  # Analyze clicked
        mock_st.spinner.return_value.__enter__ = MagicMock()
        mock_st.spinner.return_value.__exit__ = MagicMock(return_value=False)
        mock_recettes.return_value.get_all.return_value = []

        render_suggestions_ia()

        mock_st.info.assert_called()

    @patch("src.modules.cuisine.courses.suggestions_ia.obtenir_service_recettes")
    @patch("src.modules.cuisine.courses.suggestions_ia.get_inventaire_service")
    @patch("src.modules.cuisine.courses.suggestions_ia.get_courses_service")
    @patch("src.modules.cuisine.courses.suggestions_ia.st")
    @patch("src.modules.cuisine.courses.suggestions_ia.pd")
    def test_render_inventaire_with_suggestions(
        self, mock_pd, mock_st, mock_courses, mock_inv, mock_recettes
    ):
        """Test inventaire avec suggestions."""
        from src.modules.cuisine.courses.suggestions_ia import render_suggestions_ia

        suggestion = MagicMock()
        suggestion.nom = "Lait"
        suggestion.quantite = 2
        suggestion.unite = "l"
        suggestion.priorite = "haute"
        suggestion.rayon = "Crèmerie"

        svc = MagicMock()
        svc.generer_suggestions_ia_depuis_inventaire.return_value = [suggestion]
        mock_courses.return_value = svc

        tab1, tab2 = MagicMock(), MagicMock()
        mock_st.tabs.return_value = [tab1, tab2]
        tab1.__enter__ = MagicMock(return_value=tab1)
        tab1.__exit__ = MagicMock(return_value=False)
        tab2.__enter__ = MagicMock(return_value=tab2)
        tab2.__exit__ = MagicMock(return_value=False)

        mock_st.button.side_effect = [True, False]  # Analyze then not add
        mock_st.spinner.return_value.__enter__ = MagicMock()
        mock_st.spinner.return_value.__exit__ = MagicMock(return_value=False)

        mock_df = MagicMock()
        mock_pd.DataFrame.return_value = mock_df

        mock_recettes.return_value.get_all.return_value = []

        render_suggestions_ia()

        mock_st.success.assert_called()
        mock_st.dataframe.assert_called()

    @patch("src.modules.cuisine.courses.suggestions_ia.obtenir_contexte_db")
    @patch("src.modules.cuisine.courses.suggestions_ia.obtenir_service_recettes")
    @patch("src.modules.cuisine.courses.suggestions_ia.get_inventaire_service")
    @patch("src.modules.cuisine.courses.suggestions_ia.get_courses_service")
    @patch("src.modules.cuisine.courses.suggestions_ia.st")
    @patch("src.modules.cuisine.courses.suggestions_ia.pd")
    @patch("src.modules.cuisine.courses.suggestions_ia.time")
    def test_render_add_all_suggestions(
        self, mock_time, mock_pd, mock_st, mock_courses, mock_inv, mock_recettes, mock_db
    ):
        """Test ajout toutes suggestions."""
        from src.modules.cuisine.courses.suggestions_ia import render_suggestions_ia

        suggestion = MagicMock()
        suggestion.nom = "Pain"
        suggestion.quantite = 1
        suggestion.unite = "pièce"
        suggestion.priorite = "moyenne"
        suggestion.rayon = "Boulangerie"

        svc = MagicMock()
        svc.generer_suggestions_ia_depuis_inventaire.return_value = [suggestion]
        mock_courses.return_value = svc

        tab1, tab2 = MagicMock(), MagicMock()
        mock_st.tabs.return_value = [tab1, tab2]
        tab1.__enter__ = MagicMock(return_value=tab1)
        tab1.__exit__ = MagicMock(return_value=False)
        tab2.__enter__ = MagicMock(return_value=tab2)
        tab2.__exit__ = MagicMock(return_value=False)

        # Analyze=True, Add=True
        mock_st.button.side_effect = [True, True]
        mock_st.spinner.return_value.__enter__ = MagicMock()
        mock_st.spinner.return_value.__exit__ = MagicMock(return_value=False)
        mock_st.session_state = MockSessionState({"courses_refresh": 0})

        mock_session = MagicMock()
        mock_ingredient = MagicMock()
        mock_ingredient.id = 1
        mock_session.query.return_value.filter.return_value.first.return_value = mock_ingredient
        mock_db.return_value = iter([mock_session])

        mock_recettes.return_value.get_all.return_value = []

        render_suggestions_ia()

        # Verify the service was used correctly
        svc.generer_suggestions_ia_depuis_inventaire.assert_called()
        mock_st.success.assert_called()

    @patch("src.modules.cuisine.courses.suggestions_ia.obtenir_contexte_db")
    @patch("src.modules.cuisine.courses.suggestions_ia.obtenir_service_recettes")
    @patch("src.modules.cuisine.courses.suggestions_ia.get_inventaire_service")
    @patch("src.modules.cuisine.courses.suggestions_ia.get_courses_service")
    @patch("src.modules.cuisine.courses.suggestions_ia.st")
    @patch("src.modules.cuisine.courses.suggestions_ia.pd")
    @patch("src.modules.cuisine.courses.suggestions_ia.time")
    def test_render_add_new_ingredient(
        self, mock_time, mock_pd, mock_st, mock_courses, mock_inv, mock_recettes, mock_db
    ):
        """Test ajout nouvel ingrédient."""
        from src.modules.cuisine.courses.suggestions_ia import render_suggestions_ia

        suggestion = MagicMock()
        suggestion.nom = "Nouveau"
        suggestion.quantite = 1
        suggestion.unite = "kg"
        suggestion.priorite = "basse"
        suggestion.rayon = "Autre"

        svc = MagicMock()
        svc.generer_suggestions_ia_depuis_inventaire.return_value = [suggestion]
        mock_courses.return_value = svc

        tab1, tab2 = MagicMock(), MagicMock()
        mock_st.tabs.return_value = [tab1, tab2]
        tab1.__enter__ = MagicMock(return_value=tab1)
        tab1.__exit__ = MagicMock(return_value=False)
        tab2.__enter__ = MagicMock(return_value=tab2)
        tab2.__exit__ = MagicMock(return_value=False)

        mock_st.button.side_effect = [True, True]
        mock_st.spinner.return_value.__enter__ = MagicMock()
        mock_st.spinner.return_value.__exit__ = MagicMock(return_value=False)
        mock_st.session_state = MockSessionState({"courses_refresh": 0})

        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = None  # No existing
        mock_db.return_value = iter([mock_session])

        mock_recettes.return_value.get_all.return_value = []

        render_suggestions_ia()

        # Verify suggestions were generated
        svc.generer_suggestions_ia_depuis_inventaire.assert_called()
        mock_st.success.assert_called()

    @patch("src.modules.cuisine.courses.suggestions_ia.obtenir_service_recettes")
    @patch("src.modules.cuisine.courses.suggestions_ia.get_inventaire_service")
    @patch("src.modules.cuisine.courses.suggestions_ia.get_courses_service")
    @patch("src.modules.cuisine.courses.suggestions_ia.st")
    def test_render_inventaire_exception(self, mock_st, mock_courses, mock_inv, mock_recettes):
        """Test gestion exception inventaire."""
        from src.modules.cuisine.courses.suggestions_ia import render_suggestions_ia

        svc = MagicMock()
        svc.generer_suggestions_ia_depuis_inventaire.side_effect = Exception("IA Error")
        mock_courses.return_value = svc

        tab1, tab2 = MagicMock(), MagicMock()
        mock_st.tabs.return_value = [tab1, tab2]
        tab1.__enter__ = MagicMock(return_value=tab1)
        tab1.__exit__ = MagicMock(return_value=False)
        tab2.__enter__ = MagicMock(return_value=tab2)
        tab2.__exit__ = MagicMock(return_value=False)

        mock_st.button.return_value = True
        mock_st.spinner.return_value.__enter__ = MagicMock()
        mock_st.spinner.return_value.__exit__ = MagicMock(return_value=False)
        mock_recettes.return_value.get_all.return_value = []

        render_suggestions_ia()

        mock_st.error.assert_called()

    @patch("src.modules.cuisine.courses.suggestions_ia.obtenir_service_recettes")
    @patch("src.modules.cuisine.courses.suggestions_ia.get_inventaire_service")
    @patch("src.modules.cuisine.courses.suggestions_ia.get_courses_service")
    @patch("src.modules.cuisine.courses.suggestions_ia.st")
    def test_render_recettes_service_unavailable(
        self, mock_st, mock_courses, mock_inv, mock_recettes
    ):
        """Test service recettes indisponible."""
        from src.modules.cuisine.courses.suggestions_ia import render_suggestions_ia

        mock_courses.return_value = MagicMock()
        mock_inv.return_value = MagicMock()
        mock_recettes.return_value = None

        tab1, tab2 = MagicMock(), MagicMock()
        mock_st.tabs.return_value = [tab1, tab2]
        tab1.__enter__ = MagicMock(return_value=tab1)
        tab1.__exit__ = MagicMock(return_value=False)
        tab2.__enter__ = MagicMock(return_value=tab2)
        tab2.__exit__ = MagicMock(return_value=False)

        mock_st.button.return_value = False

        render_suggestions_ia()

        mock_st.warning.assert_called()

    @patch("src.modules.cuisine.courses.suggestions_ia.obtenir_service_recettes")
    @patch("src.modules.cuisine.courses.suggestions_ia.get_inventaire_service")
    @patch("src.modules.cuisine.courses.suggestions_ia.get_courses_service")
    @patch("src.modules.cuisine.courses.suggestions_ia.st")
    def test_render_recettes_empty(self, mock_st, mock_courses, mock_inv, mock_recettes):
        """Test aucune recette disponible."""
        from src.modules.cuisine.courses.suggestions_ia import render_suggestions_ia

        mock_courses.return_value = MagicMock()
        mock_inv.return_value = MagicMock()
        recettes_svc = MagicMock()
        recettes_svc.get_all.return_value = []
        mock_recettes.return_value = recettes_svc

        tab1, tab2 = MagicMock(), MagicMock()
        mock_st.tabs.return_value = [tab1, tab2]
        tab1.__enter__ = MagicMock(return_value=tab1)
        tab1.__exit__ = MagicMock(return_value=False)
        tab2.__enter__ = MagicMock(return_value=tab2)
        tab2.__exit__ = MagicMock(return_value=False)

        mock_st.button.return_value = False

        render_suggestions_ia()

        mock_st.info.assert_called()

    @patch("src.modules.cuisine.courses.suggestions_ia.obtenir_service_recettes")
    @patch("src.modules.cuisine.courses.suggestions_ia.get_inventaire_service")
    @patch("src.modules.cuisine.courses.suggestions_ia.get_courses_service")
    @patch("src.modules.cuisine.courses.suggestions_ia.st")
    def test_render_recettes_with_data(self, mock_st, mock_courses, mock_inv, mock_recettes):
        """Test avec recettes disponibles."""
        from src.modules.cuisine.courses.suggestions_ia import render_suggestions_ia

        mock_courses.return_value = MagicMock()
        mock_inv.return_value = MagicMock()

        recette = MagicMock()
        recette.id = 1
        recette.nom = "Pizza"

        recettes_svc = MagicMock()
        recettes_svc.get_all.return_value = [recette]
        recettes_svc.get_by_id_full.return_value = None
        mock_recettes.return_value = recettes_svc

        tab1, tab2 = MagicMock(), MagicMock()
        mock_st.tabs.return_value = [tab1, tab2]
        tab1.__enter__ = MagicMock(return_value=tab1)
        tab1.__exit__ = MagicMock(return_value=False)
        tab2.__enter__ = MagicMock(return_value=tab2)
        tab2.__exit__ = MagicMock(return_value=False)

        mock_st.button.return_value = False
        mock_st.selectbox.return_value = 1

        render_suggestions_ia()

        mock_st.selectbox.assert_called()

    @patch("src.core.db.obtenir_contexte_db")
    @patch("src.modules.cuisine.courses.suggestions_ia.obtenir_service_recettes")
    @patch("src.modules.cuisine.courses.suggestions_ia.get_inventaire_service")
    @patch("src.modules.cuisine.courses.suggestions_ia.get_courses_service")
    @patch("src.modules.cuisine.courses.suggestions_ia.st")
    def test_render_add_ingredients_from_recette(
        self, mock_st, mock_courses, mock_inv, mock_recettes, mock_db
    ):
        """Test ajout ingrédients depuis recette."""
        from src.modules.cuisine.courses.suggestions_ia import render_suggestions_ia

        courses_svc = MagicMock()
        mock_courses.return_value = courses_svc
        mock_inv.return_value = MagicMock()

        ingredient = MagicMock()
        ingredient.ingredient = MagicMock()
        ingredient.ingredient.nom = "Tomates"
        ingredient.ingredient.unite = "kg"
        ingredient.quantite = 0.5

        recette = MagicMock()
        recette.id = 1
        recette.nom = "Salade"
        recette.ingredients = [ingredient]

        recettes_svc = MagicMock()
        recettes_svc.get_all.return_value = [recette]
        recettes_svc.get_by_id_full.return_value = recette
        mock_recettes.return_value = recettes_svc

        tab1, tab2 = MagicMock(), MagicMock()
        mock_st.tabs.return_value = [tab1, tab2]
        tab1.__enter__ = MagicMock(return_value=tab1)
        tab1.__exit__ = MagicMock(return_value=False)
        tab2.__enter__ = MagicMock(return_value=tab2)
        tab2.__exit__ = MagicMock(return_value=False)

        mock_st.button.side_effect = [False, True]  # Add ingredients from recipe
        mock_st.selectbox.return_value = 1
        mock_st.session_state = MockSessionState({"courses_refresh": 0})

        mock_session = MagicMock()
        mock_db_ing = MagicMock()
        mock_db_ing.id = 10
        mock_session.query.return_value.filter.return_value.first.return_value = mock_db_ing
        mock_db.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_db.return_value.__exit__ = MagicMock(return_value=False)

        render_suggestions_ia()

        courses_svc.create.assert_called()
        mock_st.success.assert_called()

    @patch("src.modules.cuisine.courses.suggestions_ia.obtenir_service_recettes")
    @patch("src.modules.cuisine.courses.suggestions_ia.get_inventaire_service")
    @patch("src.modules.cuisine.courses.suggestions_ia.get_courses_service")
    @patch("src.modules.cuisine.courses.suggestions_ia.st")
    def test_render_recette_no_ingredients(self, mock_st, mock_courses, mock_inv, mock_recettes):
        """Test recette sans ingrédients."""
        from src.modules.cuisine.courses.suggestions_ia import render_suggestions_ia

        mock_courses.return_value = MagicMock()
        mock_inv.return_value = MagicMock()

        recette = MagicMock()
        recette.id = 1
        recette.nom = "Vide"
        recette.ingredients = []

        recettes_svc = MagicMock()
        recettes_svc.get_all.return_value = [recette]
        recettes_svc.get_by_id_full.return_value = recette
        mock_recettes.return_value = recettes_svc

        tab1, tab2 = MagicMock(), MagicMock()
        mock_st.tabs.return_value = [tab1, tab2]
        tab1.__enter__ = MagicMock(return_value=tab1)
        tab1.__exit__ = MagicMock(return_value=False)
        tab2.__enter__ = MagicMock(return_value=tab2)
        tab2.__exit__ = MagicMock(return_value=False)

        mock_st.button.side_effect = [False, True]  # Add clicked
        mock_st.selectbox.return_value = 1
        mock_st.session_state = MockSessionState({})

        render_suggestions_ia()

        mock_st.warning.assert_called()

    @patch("src.modules.cuisine.courses.suggestions_ia.obtenir_service_recettes")
    @patch("src.modules.cuisine.courses.suggestions_ia.get_inventaire_service")
    @patch("src.modules.cuisine.courses.suggestions_ia.get_courses_service")
    @patch("src.modules.cuisine.courses.suggestions_ia.st")
    @patch("src.modules.cuisine.courses.suggestions_ia.logger")
    def test_render_recettes_exception(
        self, mock_logger, mock_st, mock_courses, mock_inv, mock_recettes
    ):
        """Test exception onglet recettes."""
        from src.modules.cuisine.courses.suggestions_ia import render_suggestions_ia

        mock_courses.return_value = MagicMock()
        mock_inv.return_value = MagicMock()
        mock_recettes.return_value.get_all.side_effect = Exception("DB Error")

        tab1, tab2 = MagicMock(), MagicMock()
        mock_st.tabs.return_value = [tab1, tab2]
        tab1.__enter__ = MagicMock(return_value=tab1)
        tab1.__exit__ = MagicMock(return_value=False)
        tab2.__enter__ = MagicMock(return_value=tab2)
        tab2.__exit__ = MagicMock(return_value=False)

        mock_st.button.return_value = False

        render_suggestions_ia()

        mock_st.error.assert_called()
        mock_logger.error.assert_called()

    @patch("src.modules.cuisine.courses.suggestions_ia.obtenir_contexte_db")
    @patch("src.modules.cuisine.courses.suggestions_ia.obtenir_service_recettes")
    @patch("src.modules.cuisine.courses.suggestions_ia.get_inventaire_service")
    @patch("src.modules.cuisine.courses.suggestions_ia.get_courses_service")
    @patch("src.modules.cuisine.courses.suggestions_ia.st")
    @patch("src.modules.cuisine.courses.suggestions_ia.logger")
    def test_render_add_ingredients_error(
        self, mock_logger, mock_st, mock_courses, mock_inv, mock_recettes, mock_db
    ):
        """Test erreur ajout ingrédients."""
        from src.modules.cuisine.courses.suggestions_ia import render_suggestions_ia

        mock_courses.return_value = MagicMock()
        mock_inv.return_value = MagicMock()

        ingredient = MagicMock()
        ingredient.ingredient = MagicMock()
        ingredient.ingredient.nom = "Test"
        ingredient.quantite = 1

        recette = MagicMock()
        recette.id = 1
        recette.nom = "Test"
        recette.ingredients = [ingredient]

        recettes_svc = MagicMock()
        recettes_svc.get_all.return_value = [recette]
        recettes_svc.get_by_id_full.return_value = recette
        mock_recettes.return_value = recettes_svc

        tab1, tab2 = MagicMock(), MagicMock()
        mock_st.tabs.return_value = [tab1, tab2]
        tab1.__enter__ = MagicMock(return_value=tab1)
        tab1.__exit__ = MagicMock(return_value=False)
        tab2.__enter__ = MagicMock(return_value=tab2)
        tab2.__exit__ = MagicMock(return_value=False)

        mock_st.button.side_effect = [False, True]
        mock_st.selectbox.return_value = 1
        mock_st.session_state = MockSessionState({})

        mock_db.return_value.__enter__ = MagicMock(side_effect=Exception("DB Error"))
        mock_db.return_value.__exit__ = MagicMock(return_value=False)

        render_suggestions_ia()

        mock_st.error.assert_called()
        mock_logger.error.assert_called()

    @patch("src.core.db.obtenir_contexte_db")
    @patch("src.modules.cuisine.courses.suggestions_ia.obtenir_service_recettes")
    @patch("src.modules.cuisine.courses.suggestions_ia.get_inventaire_service")
    @patch("src.modules.cuisine.courses.suggestions_ia.get_courses_service")
    @patch("src.modules.cuisine.courses.suggestions_ia.st")
    @patch("src.modules.cuisine.courses.suggestions_ia.time")
    def test_render_ingredient_direct_nom_attribute(
        self, mock_time, mock_st, mock_courses, mock_inv, mock_recettes, mock_db
    ):
        """Test ingrédient avec nom direct (sans .ingredient)."""
        from src.modules.cuisine.courses.suggestions_ia import render_suggestions_ia

        courses_svc = MagicMock()
        mock_courses.return_value = courses_svc
        mock_inv.return_value = MagicMock()

        # Ingrédient sans attribut .ingredient (a directement .nom)
        ingredient = MagicMock(spec=["nom"])
        ingredient.nom = "Sel"
        # Pas de .ingredient, .quantite

        recette = MagicMock()
        recette.id = 1
        recette.nom = "Test"
        recette.ingredients = [ingredient]

        recettes_svc = MagicMock()
        recettes_svc.get_all.return_value = [recette]
        recettes_svc.get_by_id_full.return_value = recette
        mock_recettes.return_value = recettes_svc

        tab1, tab2 = MagicMock(), MagicMock()
        mock_st.tabs.return_value = [tab1, tab2]
        tab1.__enter__ = MagicMock(return_value=tab1)
        tab1.__exit__ = MagicMock(return_value=False)
        tab2.__enter__ = MagicMock(return_value=tab2)
        tab2.__exit__ = MagicMock(return_value=False)

        mock_st.button.side_effect = [False, True]
        mock_st.selectbox.return_value = 1
        mock_st.session_state = MockSessionState({"courses_refresh": 0})

        mock_session = MagicMock()
        mock_db_ing = MagicMock()
        mock_db_ing.id = 10
        mock_session.query.return_value.filter.return_value.first.return_value = mock_db_ing
        mock_db.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_db.return_value.__exit__ = MagicMock(return_value=False)

        render_suggestions_ia()

        courses_svc.create.assert_called()
        mock_st.success.assert_called()

    @patch("src.core.db.obtenir_contexte_db")
    @patch("src.modules.cuisine.courses.suggestions_ia.obtenir_service_recettes")
    @patch("src.modules.cuisine.courses.suggestions_ia.get_inventaire_service")
    @patch("src.modules.cuisine.courses.suggestions_ia.get_courses_service")
    @patch("src.modules.cuisine.courses.suggestions_ia.st")
    @patch("src.modules.cuisine.courses.suggestions_ia.time")
    def test_render_ingredient_nom_empty_skip(
        self, mock_time, mock_st, mock_courses, mock_inv, mock_recettes, mock_db
    ):
        """Test ingrédient avec nom vide est ignoré."""
        from src.modules.cuisine.courses.suggestions_ia import render_suggestions_ia

        courses_svc = MagicMock()
        mock_courses.return_value = courses_svc
        mock_inv.return_value = MagicMock()

        # Ingrédient avec nom vide (doit être ignoré)
        ingredient_empty = MagicMock()
        ingredient_empty.ingredient = MagicMock()
        ingredient_empty.ingredient.nom = ""  # Nom vide
        ingredient_empty.quantite = 1

        # Ingrédient valide
        ingredient_valid = MagicMock()
        ingredient_valid.ingredient = MagicMock()
        ingredient_valid.ingredient.nom = "Poivre"
        ingredient_valid.ingredient.unite = "g"
        ingredient_valid.quantite = 10

        recette = MagicMock()
        recette.id = 1
        recette.nom = "Test"
        recette.ingredients = [ingredient_empty, ingredient_valid]

        recettes_svc = MagicMock()
        recettes_svc.get_all.return_value = [recette]
        recettes_svc.get_by_id_full.return_value = recette
        mock_recettes.return_value = recettes_svc

        tab1, tab2 = MagicMock(), MagicMock()
        mock_st.tabs.return_value = [tab1, tab2]
        tab1.__enter__ = MagicMock(return_value=tab1)
        tab1.__exit__ = MagicMock(return_value=False)
        tab2.__enter__ = MagicMock(return_value=tab2)
        tab2.__exit__ = MagicMock(return_value=False)

        mock_st.button.side_effect = [False, True]
        mock_st.selectbox.return_value = 1
        mock_st.session_state = MockSessionState({"courses_refresh": 0})

        mock_session = MagicMock()
        mock_db_ing = MagicMock()
        mock_db_ing.id = 10
        mock_session.query.return_value.filter.return_value.first.return_value = mock_db_ing
        mock_db.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_db.return_value.__exit__ = MagicMock(return_value=False)

        render_suggestions_ia()

        # Seulement un appel pour l'ingrédient valide
        assert courses_svc.create.call_count == 1
        mock_st.success.assert_called()

    @patch("src.core.db.obtenir_contexte_db")
    @patch("src.modules.cuisine.courses.suggestions_ia.obtenir_service_recettes")
    @patch("src.modules.cuisine.courses.suggestions_ia.get_inventaire_service")
    @patch("src.modules.cuisine.courses.suggestions_ia.get_courses_service")
    @patch("src.modules.cuisine.courses.suggestions_ia.st")
    @patch("src.modules.cuisine.courses.suggestions_ia.time")
    def test_render_create_new_ingredient_from_recette(
        self, mock_time, mock_st, mock_courses, mock_inv, mock_recettes, mock_db
    ):
        """Test création nouvel ingrédient depuis recette."""
        from src.modules.cuisine.courses.suggestions_ia import render_suggestions_ia

        courses_svc = MagicMock()
        mock_courses.return_value = courses_svc
        mock_inv.return_value = MagicMock()

        ingredient = MagicMock()
        ingredient.ingredient = MagicMock()
        ingredient.ingredient.nom = "NouvelIngredient"
        ingredient.ingredient.unite = "ml"
        ingredient.quantite = 200

        recette = MagicMock()
        recette.id = 1
        recette.nom = "Test"
        recette.ingredients = [ingredient]

        recettes_svc = MagicMock()
        recettes_svc.get_all.return_value = [recette]
        recettes_svc.get_by_id_full.return_value = recette
        mock_recettes.return_value = recettes_svc

        tab1, tab2 = MagicMock(), MagicMock()
        mock_st.tabs.return_value = [tab1, tab2]
        tab1.__enter__ = MagicMock(return_value=tab1)
        tab1.__exit__ = MagicMock(return_value=False)
        tab2.__enter__ = MagicMock(return_value=tab2)
        tab2.__exit__ = MagicMock(return_value=False)

        mock_st.button.side_effect = [False, True]
        mock_st.selectbox.return_value = 1
        mock_st.session_state = MockSessionState({"courses_refresh": 0})

        mock_session = MagicMock()
        # Ingrédient non existant en DB
        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_db.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_db.return_value.__exit__ = MagicMock(return_value=False)

        render_suggestions_ia()

        # Vérifier que add et flush ont été appelés pour créer l'ingrédient
        mock_session.add.assert_called()
        mock_session.flush.assert_called()
        mock_st.success.assert_called()


class TestSuggestionsIAModule:
    """Tests module-level."""

    def test_all_exports(self):
        """Test __all__ exports."""
        from src.modules.cuisine.courses import suggestions_ia

        assert "render_suggestions_ia" in suggestions_ia.__all__
