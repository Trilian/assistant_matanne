"""
Tests pour src/modules/cuisine/courses/liste_active.py

Couverture complète des fonctions UI liste active courses.
"""

from contextlib import contextmanager
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


def make_db_context(mock_session):
    """Crée un contexte DB mock."""

    @contextmanager
    def db_context():
        yield mock_session

    return db_context


def make_db_context_error(error):
    """Crée un contexte DB qui lève une erreur."""

    @contextmanager
    def db_context():
        raise error
        yield

    return db_context


class TestRenderListeActive:
    """Tests pour render_liste_active()."""

    def test_import(self):
        """Test import réussi."""
        from src.modules.cuisine.courses.liste_active import render_liste_active

        assert render_liste_active is not None

    @patch("src.modules.cuisine.courses.liste_active.get_inventaire_service")
    @patch("src.modules.cuisine.courses.liste_active.get_courses_service")
    @patch("src.modules.cuisine.courses.liste_active.st")
    def test_render_liste_active_service_unavailable(
        self, mock_st, mock_courses_service, mock_inv_service
    ):
        """Test service indisponible."""
        from src.modules.cuisine.courses.liste_active import render_liste_active

        mock_courses_service.return_value = None
        render_liste_active()
        mock_st.error.assert_called()

    @patch("src.modules.cuisine.courses.liste_active.get_inventaire_service")
    @patch("src.modules.cuisine.courses.liste_active.get_courses_service")
    @patch("src.modules.cuisine.courses.liste_active.st")
    def test_render_liste_active_empty(self, mock_st, mock_courses_service, mock_inv_service):
        """Test liste vide."""
        from src.modules.cuisine.courses.liste_active import render_liste_active

        mock_service = MagicMock()
        mock_service.get_liste_courses.return_value = []
        mock_courses_service.return_value = mock_service

        mock_inv = MagicMock()
        mock_inv.get_alertes.return_value = {"stock_bas": []}
        mock_inv_service.return_value = mock_inv

        mock_st.columns.return_value = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
        mock_st.session_state = MockSessionState({"new_article_mode": False, "courses_refresh": 0})
        mock_st.button.return_value = False

        render_liste_active()

        mock_st.info.assert_called()

    @patch("src.modules.cuisine.courses.liste_active.get_inventaire_service")
    @patch("src.modules.cuisine.courses.liste_active.get_courses_service")
    @patch("src.modules.cuisine.courses.liste_active.st")
    def test_render_liste_active_with_articles(
        self, mock_st, mock_courses_service, mock_inv_service
    ):
        """Test avec articles."""
        from src.modules.cuisine.courses.liste_active import render_liste_active

        mock_service = MagicMock()
        mock_service.get_liste_courses.side_effect = [
            [
                {
                    "id": 1,
                    "ingredient_nom": "Tomates",
                    "quantite_necessaire": 2.0,
                    "unite": "kg",
                    "priorite": "haute",
                    "rayon_magasin": "Fruits et légumes",
                    "notes": "Bio",
                    "suggere_par_ia": False,
                }
            ],
            [],  # achetes=True
        ]
        mock_courses_service.return_value = mock_service

        mock_inv = MagicMock()
        mock_inv.get_alertes.return_value = {"stock_bas": []}
        mock_inv_service.return_value = mock_inv

        mock_st.columns.return_value = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
        mock_st.session_state = MockSessionState(
            {
                "new_article_mode": False,
                "edit_article_id": None,
                "courses_refresh": 0,
            }
        )
        mock_st.button.return_value = False
        mock_st.selectbox.side_effect = ["Toutes", "Tous les rayons"]
        mock_st.text_input.return_value = ""
        expander_mock = MagicMock()
        mock_st.expander.return_value.__enter__ = MagicMock(return_value=expander_mock)
        mock_st.expander.return_value.__exit__ = MagicMock(return_value=False)

        render_liste_active()

        mock_st.metric.assert_called()

    @patch("src.modules.cuisine.courses.liste_active.get_inventaire_service")
    @patch("src.modules.cuisine.courses.liste_active.get_courses_service")
    @patch("src.modules.cuisine.courses.liste_active.st")
    @patch("src.modules.cuisine.courses.liste_active.logger")
    def test_render_liste_active_exception(
        self, mock_logger, mock_st, mock_courses_service, mock_inv_service
    ):
        """Test gestion erreur."""
        from src.modules.cuisine.courses.liste_active import render_liste_active

        mock_service = MagicMock()
        mock_service.get_liste_courses.side_effect = Exception("DB error")
        mock_courses_service.return_value = mock_service

        mock_st.columns.return_value = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
        mock_st.session_state = MockSessionState({})

        render_liste_active()

        mock_st.error.assert_called()
        mock_logger.error.assert_called()

    @patch("src.modules.cuisine.courses.liste_active.get_inventaire_service")
    @patch("src.modules.cuisine.courses.liste_active.get_courses_service")
    @patch("src.modules.cuisine.courses.liste_active.st")
    def test_render_liste_active_search(self, mock_st, mock_courses_service, mock_inv_service):
        """Test recherche."""
        from src.modules.cuisine.courses.liste_active import render_liste_active

        mock_service = MagicMock()
        mock_service.get_liste_courses.side_effect = [
            [
                {
                    "id": 1,
                    "ingredient_nom": "Pommes",
                    "quantite_necessaire": 1.0,
                    "unite": "kg",
                    "priorite": "moyenne",
                    "rayon_magasin": "Fruits",
                    "notes": None,
                    "suggere_par_ia": False,
                }
            ],
            [],
        ]
        mock_courses_service.return_value = mock_service

        mock_inv = MagicMock()
        mock_inv.get_alertes.return_value = {"stock_bas": []}
        mock_inv_service.return_value = mock_inv

        # Multiple columns calls: 4 for metrics, 3 for filters, then 3 for actions
        mock_st.columns.side_effect = [
            [MagicMock(), MagicMock(), MagicMock(), MagicMock()],  # metrics
            [MagicMock(), MagicMock(), MagicMock()],  # filters
            [MagicMock(), MagicMock(), MagicMock()],  # actions
        ]
        mock_st.session_state = MockSessionState(
            {"new_article_mode": False, "edit_article_id": None, "courses_refresh": 0}
        )
        mock_st.button.return_value = False
        mock_st.selectbox.side_effect = ["Toutes", "Tous les rayons"]
        mock_st.text_input.return_value = "pom"  # Recherche
        expander_mock = MagicMock()
        mock_st.expander.return_value.__enter__ = MagicMock(return_value=expander_mock)
        mock_st.expander.return_value.__exit__ = MagicMock(return_value=False)

        render_liste_active()

        mock_st.success.assert_called()


class TestRenderRayonArticles:
    """Tests pour render_rayon_articles()."""

    def test_import(self):
        """Test import."""
        from src.modules.cuisine.courses.liste_active import render_rayon_articles

        assert render_rayon_articles is not None

    @patch("src.modules.cuisine.courses.liste_active.st")
    def test_render_rayon_articles_basic(self, mock_st):
        """Test affichage articles rayon."""
        from src.modules.cuisine.courses.liste_active import render_rayon_articles

        mock_service = MagicMock()
        articles = [
            {
                "id": 1,
                "ingredient_nom": "Lait",
                "quantite_necessaire": 1.0,
                "unite": "l",
                "priorite": "moyenne",
                "notes": None,
                "suggere_par_ia": False,
            }
        ]

        mock_st.columns.return_value = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
        mock_st.button.return_value = False
        mock_st.session_state = MockSessionState({"edit_article_id": None, "courses_refresh": 0})

        render_rayon_articles(mock_service, "Crèmerie", articles)

        mock_st.write.assert_called()

    @patch("src.modules.cuisine.courses.liste_active.st")
    def test_render_rayon_articles_with_notes_and_ia(self, mock_st):
        """Test avec notes et badge IA."""
        from src.modules.cuisine.courses.liste_active import render_rayon_articles

        mock_service = MagicMock()
        articles = [
            {
                "id": 2,
                "ingredient_nom": "Pain",
                "quantite_necessaire": 2.0,
                "unite": "pièce",
                "priorite": "haute",
                "notes": "Complet",
                "suggere_par_ia": True,
            }
        ]

        mock_st.columns.return_value = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
        mock_st.button.return_value = False
        mock_st.session_state = MockSessionState({"edit_article_id": None, "courses_refresh": 0})

        render_rayon_articles(mock_service, "Boulangerie", articles)

        mock_st.write.assert_called()

    @patch("src.modules.cuisine.courses.liste_active.st")
    def test_render_rayon_articles_mark_bought(self, mock_st):
        """Test marquer acheté."""
        from src.modules.cuisine.courses.liste_active import render_rayon_articles

        mock_service = MagicMock()
        articles = [
            {
                "id": 3,
                "ingredient_nom": "Fromage",
                "quantite_necessaire": 0.5,
                "unite": "kg",
                "priorite": "basse",
                "notes": None,
                "suggere_par_ia": False,
            }
        ]

        mock_st.columns.return_value = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
        mock_st.button.side_effect = [True, False, False]  # First button clicked
        mock_st.session_state = MockSessionState({"edit_article_id": None, "courses_refresh": 0})

        render_rayon_articles(mock_service, "Crèmerie", articles)

        mock_service.update.assert_called()
        mock_st.success.assert_called()

    @patch("src.modules.cuisine.courses.liste_active.st")
    def test_render_rayon_articles_delete(self, mock_st):
        """Test supprimer article."""
        from src.modules.cuisine.courses.liste_active import render_rayon_articles

        mock_service = MagicMock()
        articles = [
            {
                "id": 4,
                "ingredient_nom": "Yaourt",
                "quantite_necessaire": 6.0,
                "unite": "pièce",
                "priorite": "moyenne",
                "notes": None,
                "suggere_par_ia": False,
            }
        ]

        mock_st.columns.return_value = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
        mock_st.button.side_effect = [False, False, True]  # Delete button clicked
        mock_st.session_state = MockSessionState({"edit_article_id": None, "courses_refresh": 0})

        render_rayon_articles(mock_service, "Crèmerie", articles)

        mock_service.delete.assert_called_with(4)
        mock_st.success.assert_called()

    @patch("src.modules.cuisine.courses.liste_active.st")
    def test_render_rayon_articles_update_error(self, mock_st):
        """Test erreur lors de la mise à jour."""
        from src.modules.cuisine.courses.liste_active import render_rayon_articles

        mock_service = MagicMock()
        mock_service.update.side_effect = Exception("Update failed")
        articles = [
            {
                "id": 6,
                "ingredient_nom": "Oeufs",
                "quantite_necessaire": 12,
                "unite": "pièce",
                "priorite": "haute",
                "notes": None,
                "suggere_par_ia": False,
            }
        ]

        mock_st.columns.return_value = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
        mock_st.button.side_effect = [True, False, False]
        mock_st.session_state = MockSessionState({"edit_article_id": None, "courses_refresh": 0})

        render_rayon_articles(mock_service, "Crèmerie", articles)

        mock_st.error.assert_called()

    @patch("src.modules.cuisine.courses.liste_active.st")
    def test_render_rayon_articles_delete_error(self, mock_st):
        """Test erreur lors de suppression."""
        from src.modules.cuisine.courses.liste_active import render_rayon_articles

        mock_service = MagicMock()
        mock_service.delete.side_effect = Exception("Delete failed")
        articles = [
            {
                "id": 7,
                "ingredient_nom": "Test",
                "quantite_necessaire": 1,
                "unite": "kg",
                "priorite": "basse",
                "notes": None,
                "suggere_par_ia": False,
            }
        ]

        mock_st.columns.return_value = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
        mock_st.button.side_effect = [False, False, True]
        mock_st.session_state = MockSessionState({"edit_article_id": None, "courses_refresh": 0})

        render_rayon_articles(mock_service, "Rayon", articles)

        mock_st.error.assert_called()

    @patch(
        "src.modules.cuisine.courses.liste_active.PRIORITY_EMOJIS",
        {"haute": "🔴", "moyenne": "🟡", "basse": "🟢"},
    )
    @patch("src.modules.cuisine.courses.liste_active.RAYONS_DEFAULT", ["Crèmerie", "Autre"])
    @patch("src.modules.cuisine.courses.liste_active.st")
    def test_render_rayon_articles_edit_inline_form(self, mock_st):
        """Test formulaire édition inline affiché."""
        from src.modules.cuisine.courses.liste_active import render_rayon_articles

        mock_service = MagicMock()
        articles = [
            {
                "id": 10,
                "ingredient_nom": "EditTest",
                "quantite_necessaire": 2.0,
                "unite": "kg",
                "priorite": "moyenne",
                "rayon_magasin": "Crèmerie",
                "notes": "Note",
                "suggere_par_ia": False,
            }
        ]

        # Multiple columns calls: 4 for article row, 2 for form controls, 2 for buttons
        mock_st.columns.side_effect = [
            [MagicMock(), MagicMock(), MagicMock(), MagicMock()],  # Article row
            [MagicMock(), MagicMock()],  # Form controls (quantité, priorité)
            [MagicMock(), MagicMock()],  # Form buttons (save, cancel)
        ]
        mock_st.button.return_value = False
        mock_st.session_state = MockSessionState(
            {"edit_article_id": 10, "courses_refresh": 0}
        )  # Edit mode ON

        form_mock = MagicMock()
        mock_st.form.return_value.__enter__ = MagicMock(return_value=form_mock)
        mock_st.form.return_value.__exit__ = MagicMock(return_value=False)
        mock_st.number_input.return_value = 3.0
        mock_st.selectbox.side_effect = ["moyenne", "Crèmerie"]
        mock_st.text_area.return_value = "Updated note"
        mock_st.form_submit_button.return_value = False

        render_rayon_articles(mock_service, "Crèmerie", articles)

        mock_st.divider.assert_called()


class TestRenderAjouterArticle:
    """Tests pour render_ajouter_article()."""

    def test_import(self):
        """Test import."""
        from src.modules.cuisine.courses.liste_active import render_ajouter_article

        assert render_ajouter_article is not None

    @patch("src.modules.cuisine.courses.liste_active.get_courses_service")
    @patch("src.modules.cuisine.courses.liste_active.st")
    def test_render_ajouter_article_service_unavailable(self, mock_st, mock_service):
        """Test service indisponible."""
        from src.modules.cuisine.courses.liste_active import render_ajouter_article

        mock_service.return_value = None
        render_ajouter_article()
        mock_st.error.assert_called()

    @patch("src.modules.cuisine.courses.liste_active.get_courses_service")
    @patch("src.modules.cuisine.courses.liste_active.st")
    def test_render_ajouter_article_empty_name(self, mock_st, mock_service):
        """Test nom vide."""
        from src.modules.cuisine.courses.liste_active import render_ajouter_article

        mock_service.return_value = MagicMock()

        form_mock = MagicMock()
        mock_st.form.return_value.__enter__ = MagicMock(return_value=form_mock)
        mock_st.form.return_value.__exit__ = MagicMock(return_value=False)
        mock_st.columns.return_value = [MagicMock(), MagicMock()]
        mock_st.text_input.return_value = ""  # Empty name
        mock_st.selectbox.return_value = "kg"
        mock_st.number_input.return_value = 1.0
        mock_st.text_area.return_value = ""
        mock_st.form_submit_button.return_value = True

        render_ajouter_article()

        mock_st.error.assert_called()

    @patch("src.core.models.Ingredient")
    @patch("src.core.db.obtenir_contexte_db")
    @patch("src.modules.cuisine.courses.liste_active.get_courses_service")
    @patch("src.modules.cuisine.courses.liste_active.st")
    def test_render_ajouter_article_success_existing_ingredient(
        self, mock_st, mock_service, mock_db, mock_ingredient_class
    ):
        """Test ajout réussi avec ingrédient existant."""
        from src.modules.cuisine.courses.liste_active import render_ajouter_article

        svc = MagicMock()
        mock_service.return_value = svc

        form_mock = MagicMock()
        mock_st.form.return_value.__enter__ = MagicMock(return_value=form_mock)
        mock_st.form.return_value.__exit__ = MagicMock(return_value=False)
        mock_st.columns.return_value = [MagicMock(), MagicMock()]
        mock_st.text_input.return_value = "Carottes"
        mock_st.selectbox.side_effect = ["kg", "moyenne", "Fruits et légumes"]
        mock_st.number_input.return_value = 2.0
        mock_st.text_area.return_value = "Bio"
        mock_st.form_submit_button.return_value = True
        mock_st.session_state = MockSessionState({"new_article_mode": True, "courses_refresh": 0})

        mock_session = MagicMock()
        mock_ingredient = MagicMock()
        mock_ingredient.id = 10
        mock_session.query.return_value.filter.return_value.first.return_value = mock_ingredient
        mock_db.return_value = make_db_context(mock_session)()

        render_ajouter_article()

        svc.create.assert_called()
        mock_st.success.assert_called()

    @patch("src.core.models.Ingredient")
    @patch("src.core.db.obtenir_contexte_db")
    @patch("src.modules.cuisine.courses.liste_active.get_courses_service")
    @patch("src.modules.cuisine.courses.liste_active.st")
    def test_render_ajouter_article_success_new_ingredient(
        self, mock_st, mock_service, mock_db, mock_ingredient_class
    ):
        """Test ajout réussi avec nouvel ingrédient."""
        from src.modules.cuisine.courses.liste_active import render_ajouter_article

        svc = MagicMock()
        mock_service.return_value = svc

        form_mock = MagicMock()
        mock_st.form.return_value.__enter__ = MagicMock(return_value=form_mock)
        mock_st.form.return_value.__exit__ = MagicMock(return_value=False)
        mock_st.columns.return_value = [MagicMock(), MagicMock()]
        mock_st.text_input.return_value = "Nouvel Ingrédient"
        mock_st.selectbox.side_effect = ["pièce", "haute", "Autre"]
        mock_st.number_input.return_value = 1.0
        mock_st.text_area.return_value = ""
        mock_st.form_submit_button.return_value = True
        mock_st.session_state = MockSessionState({"new_article_mode": True, "courses_refresh": 0})

        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = (
            None  # No existing ingredient
        )

        new_ingredient = MagicMock()
        new_ingredient.id = 99
        mock_ingredient_class.return_value = new_ingredient

        mock_db.return_value = make_db_context(mock_session)()

        render_ajouter_article()

        mock_session.add.assert_called()
        svc.create.assert_called()

    @patch("src.core.models.Ingredient")
    @patch("src.core.db.obtenir_contexte_db")
    @patch("src.modules.cuisine.courses.liste_active.get_courses_service")
    @patch("src.modules.cuisine.courses.liste_active.st")
    @patch("src.modules.cuisine.courses.liste_active.logger")
    def test_render_ajouter_article_error(
        self, mock_logger, mock_st, mock_service, mock_db, mock_ingredient_class
    ):
        """Test erreur ajout."""
        from src.modules.cuisine.courses.liste_active import render_ajouter_article

        svc = MagicMock()
        mock_service.return_value = svc

        form_mock = MagicMock()
        mock_st.form.return_value.__enter__ = MagicMock(return_value=form_mock)
        mock_st.form.return_value.__exit__ = MagicMock(return_value=False)
        mock_st.columns.return_value = [MagicMock(), MagicMock()]
        mock_st.text_input.return_value = "Test"
        mock_st.selectbox.side_effect = ["kg", "haute", "Autre"]
        mock_st.number_input.return_value = 1.0
        mock_st.text_area.return_value = ""
        mock_st.form_submit_button.return_value = True
        mock_st.session_state = MockSessionState({"new_article_mode": True, "courses_refresh": 0})

        mock_db.return_value = make_db_context_error(Exception("DB Error"))()

        render_ajouter_article()

        mock_st.error.assert_called()
        mock_logger.error.assert_called()


class TestRenderPrintView:
    """Tests pour render_print_view()."""

    def test_import(self):
        """Test import."""
        from src.modules.cuisine.courses.liste_active import render_print_view

        assert render_print_view is not None

    @patch("src.modules.cuisine.courses.liste_active.st")
    def test_render_print_view_basic(self, mock_st):
        """Test vue impression basique."""
        from src.modules.cuisine.courses.liste_active import render_print_view

        liste = [
            {
                "ingredient_nom": "Pain",
                "quantite_necessaire": 1,
                "unite": "pièce",
                "rayon_magasin": "Boulangerie",
            }
        ]

        render_print_view(liste)

        mock_st.subheader.assert_called()
        mock_st.text_area.assert_called()

    @patch("src.modules.cuisine.courses.liste_active.st")
    def test_render_print_view_multiple_rayons(self, mock_st):
        """Test impression plusieurs rayons."""
        from src.modules.cuisine.courses.liste_active import render_print_view

        liste = [
            {
                "ingredient_nom": "Lait",
                "quantite_necessaire": 2,
                "unite": "l",
                "rayon_magasin": "Crèmerie",
            },
            {
                "ingredient_nom": "Pain",
                "quantite_necessaire": 1,
                "unite": "pièce",
                "rayon_magasin": "Boulangerie",
            },
            {
                "ingredient_nom": "Yaourt",
                "quantite_necessaire": 4,
                "unite": "pièce",
                "rayon_magasin": "Crèmerie",
            },
        ]

        render_print_view(liste)

        mock_st.text_area.assert_called()

    @patch("src.modules.cuisine.courses.liste_active.st")
    def test_render_print_view_empty(self, mock_st):
        """Test impression liste vide."""
        from src.modules.cuisine.courses.liste_active import render_print_view

        render_print_view([])

        mock_st.text_area.assert_called()

    @patch("src.modules.cuisine.courses.liste_active.st")
    def test_render_print_view_autre_rayon(self, mock_st):
        """Test rayon 'Autre' par défaut."""
        from src.modules.cuisine.courses.liste_active import render_print_view

        liste = [
            {
                "ingredient_nom": "Article",
                "quantite_necessaire": 1,
                "unite": "pièce",
                "rayon_magasin": None,
            }
        ]

        render_print_view(liste)

        mock_st.text_area.assert_called()


class TestListeActiveModule:
    """Tests module-level."""

    def test_all_exports(self):
        """Test __all__ exports."""
        from src.modules.cuisine.courses import liste_active

        assert "render_liste_active" in liste_active.__all__
        assert "render_rayon_articles" in liste_active.__all__
        assert "render_ajouter_article" in liste_active.__all__
        assert "render_print_view" in liste_active.__all__


class TestRenderListeActiveAdditional:
    """Tests supplémentaires pour couverture branches manquantes."""

    @patch("src.modules.cuisine.courses.liste_active.get_inventaire_service")
    @patch("src.modules.cuisine.courses.liste_active.get_courses_service")
    @patch("src.modules.cuisine.courses.liste_active.st")
    def test_render_liste_inventaire_service_none(
        self, mock_st, mock_courses_service, mock_inv_service
    ):
        """Test quand inventaire_service est None (ligne 37)."""
        from src.modules.cuisine.courses.liste_active import render_liste_active

        mock_service = MagicMock()
        mock_service.get_liste_courses.side_effect = [
            [
                {
                    "id": 1,
                    "ingredient_nom": "Test",
                    "quantite_necessaire": 1.0,
                    "unite": "kg",
                    "priorite": "haute",
                    "rayon_magasin": "Autre",
                    "notes": None,
                    "suggere_par_ia": False,
                }
            ],
            [],
        ]
        mock_courses_service.return_value = mock_service
        mock_inv_service.return_value = None  # Inventaire service None

        mock_st.columns.return_value = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
        mock_st.session_state = MockSessionState(
            {"new_article_mode": False, "edit_article_id": None, "courses_refresh": 0}
        )
        mock_st.button.return_value = False
        mock_st.selectbox.side_effect = ["Toutes", "Tous les rayons"]
        mock_st.text_input.return_value = ""
        expander_mock = MagicMock()
        mock_st.expander.return_value.__enter__ = MagicMock(return_value=expander_mock)
        mock_st.expander.return_value.__exit__ = MagicMock(return_value=False)

        render_liste_active()

        # Vérifier que metric a été appelé (sans stock_bas)
        mock_st.metric.assert_called()

    @patch("src.modules.cuisine.courses.liste_active.get_inventaire_service")
    @patch("src.modules.cuisine.courses.liste_active.get_courses_service")
    @patch("src.modules.cuisine.courses.liste_active.st")
    def test_render_liste_empty_generate_ia_clicked(
        self, mock_st, mock_courses_service, mock_inv_service
    ):
        """Test bouton générer suggestions IA cliqué (lignes 49-50)."""
        from src.modules.cuisine.courses.liste_active import render_liste_active

        mock_service = MagicMock()
        mock_service.get_liste_courses.return_value = []  # Liste vide
        mock_courses_service.return_value = mock_service

        mock_inv = MagicMock()
        mock_inv.get_alertes.return_value = {"stock_bas": []}
        mock_inv_service.return_value = mock_inv

        mock_st.columns.return_value = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
        mock_st.session_state = MockSessionState({"new_article_mode": True, "courses_refresh": 0})
        mock_st.button.return_value = True  # Button clicked

        render_liste_active()

        mock_st.rerun.assert_called()

    @patch("src.modules.cuisine.courses.liste_active.get_inventaire_service")
    @patch("src.modules.cuisine.courses.liste_active.get_courses_service")
    @patch("src.modules.cuisine.courses.liste_active.st")
    def test_render_liste_filter_by_priority(self, mock_st, mock_courses_service, mock_inv_service):
        """Test filtre par priorité (lignes 74-75)."""
        from src.modules.cuisine.courses.liste_active import render_liste_active

        mock_service = MagicMock()
        mock_service.get_liste_courses.side_effect = [
            [
                {
                    "id": 1,
                    "ingredient_nom": "Item1",
                    "quantite_necessaire": 1.0,
                    "unite": "kg",
                    "priorite": "haute",
                    "rayon_magasin": "Autre",
                    "notes": None,
                    "suggere_par_ia": False,
                },
                {
                    "id": 2,
                    "ingredient_nom": "Item2",
                    "quantite_necessaire": 2.0,
                    "unite": "kg",
                    "priorite": "basse",
                    "rayon_magasin": "Autre",
                    "notes": None,
                    "suggere_par_ia": False,
                },
            ],
            [],
        ]
        mock_courses_service.return_value = mock_service

        mock_inv = MagicMock()
        mock_inv.get_alertes.return_value = {"stock_bas": []}
        mock_inv_service.return_value = mock_inv

        # Multiple columns calls: 4 for metrics, 3 for filters, 3 for actions, 4 for article row
        mock_st.columns.side_effect = [
            [MagicMock(), MagicMock(), MagicMock(), MagicMock()],  # metrics
            [MagicMock(), MagicMock(), MagicMock()],  # filters
            [MagicMock(), MagicMock(), MagicMock()],  # actions
            [MagicMock(), MagicMock(), MagicMock(), MagicMock()],  # article row
        ]
        mock_st.session_state = MockSessionState(
            {"new_article_mode": False, "edit_article_id": None, "courses_refresh": 0}
        )
        mock_st.button.return_value = False
        mock_st.selectbox.side_effect = ["🔴 Haute", "Tous les rayons"]  # Filter by priority
        mock_st.text_input.return_value = ""
        expander_mock = MagicMock()
        mock_st.expander.return_value.__enter__ = MagicMock(return_value=expander_mock)
        mock_st.expander.return_value.__exit__ = MagicMock(return_value=False)

        render_liste_active()

        # Vérifie que le filtre par priorité fonctionne (1 sur 2 articles)
        mock_st.success.assert_called()

    @patch("src.modules.cuisine.courses.liste_active.get_inventaire_service")
    @patch("src.modules.cuisine.courses.liste_active.get_courses_service")
    @patch("src.modules.cuisine.courses.liste_active.st")
    def test_render_liste_filter_by_rayon(self, mock_st, mock_courses_service, mock_inv_service):
        """Test filtre par rayon (ligne 80)."""
        from src.modules.cuisine.courses.liste_active import render_liste_active

        mock_service = MagicMock()
        mock_service.get_liste_courses.side_effect = [
            [
                {
                    "id": 1,
                    "ingredient_nom": "Lait",
                    "quantite_necessaire": 1.0,
                    "unite": "l",
                    "priorite": "moyenne",
                    "rayon_magasin": "Crèmerie",
                    "notes": None,
                    "suggere_par_ia": False,
                },
                {
                    "id": 2,
                    "ingredient_nom": "Pain",
                    "quantite_necessaire": 1.0,
                    "unite": "pièce",
                    "priorite": "moyenne",
                    "rayon_magasin": "Boulangerie",
                    "notes": None,
                    "suggere_par_ia": False,
                },
            ],
            [],
        ]
        mock_courses_service.return_value = mock_service

        mock_inv = MagicMock()
        mock_inv.get_alertes.return_value = {"stock_bas": []}
        mock_inv_service.return_value = mock_inv

        # Multiple columns calls
        mock_st.columns.side_effect = [
            [MagicMock(), MagicMock(), MagicMock(), MagicMock()],  # metrics
            [MagicMock(), MagicMock(), MagicMock()],  # filters
            [MagicMock(), MagicMock(), MagicMock()],  # actions
            [MagicMock(), MagicMock(), MagicMock(), MagicMock()],  # article row
        ]
        mock_st.session_state = MockSessionState(
            {"new_article_mode": False, "edit_article_id": None, "courses_refresh": 0}
        )
        mock_st.button.return_value = False
        mock_st.selectbox.side_effect = ["Toutes", "Crèmerie"]  # Filter by rayon
        mock_st.text_input.return_value = ""
        expander_mock = MagicMock()
        mock_st.expander.return_value.__enter__ = MagicMock(return_value=expander_mock)
        mock_st.expander.return_value.__exit__ = MagicMock(return_value=False)

        render_liste_active()

        mock_st.success.assert_called()

    @patch("src.modules.cuisine.courses.liste_active.render_print_view")
    @patch("src.modules.cuisine.courses.liste_active.get_inventaire_service")
    @patch("src.modules.cuisine.courses.liste_active.get_courses_service")
    @patch("src.modules.cuisine.courses.liste_active.st")
    def test_render_liste_print_button_clicked(
        self, mock_st, mock_courses_service, mock_inv_service, mock_print_view
    ):
        """Test bouton imprimer cliqué (ligne 284)."""
        from src.modules.cuisine.courses.liste_active import render_liste_active

        mock_service = MagicMock()
        mock_service.get_liste_courses.side_effect = [
            [
                {
                    "id": 1,
                    "ingredient_nom": "Test",
                    "quantite_necessaire": 1.0,
                    "unite": "kg",
                    "priorite": "haute",
                    "rayon_magasin": "Autre",
                    "notes": None,
                    "suggere_par_ia": False,
                }
            ],
            [],
        ]
        mock_courses_service.return_value = mock_service

        mock_inv = MagicMock()
        mock_inv.get_alertes.return_value = {"stock_bas": []}
        mock_inv_service.return_value = mock_inv

        # Multiple columns calls: 4 stats, 3 filters, 4 article row, 3 actions
        mock_st.columns.side_effect = [
            [MagicMock(), MagicMock(), MagicMock(), MagicMock()],  # stats
            [MagicMock(), MagicMock(), MagicMock()],  # filters
            [MagicMock(), MagicMock(), MagicMock(), MagicMock()],  # article row
            [MagicMock(), MagicMock(), MagicMock()],  # actions
        ]
        mock_st.session_state = MockSessionState(
            {"new_article_mode": False, "edit_article_id": None, "courses_refresh": 0}
        )
        # Buttons: mark(F), edit(F), delete(F), add(F), print(T), clear(F)
        mock_st.button.side_effect = [False, False, False, False, True, False]
        mock_st.selectbox.side_effect = ["Toutes", "Tous les rayons"]
        mock_st.text_input.return_value = ""
        expander_mock = MagicMock()
        mock_st.expander.return_value.__enter__ = MagicMock(return_value=expander_mock)
        mock_st.expander.return_value.__exit__ = MagicMock(return_value=False)

        render_liste_active()

        mock_print_view.assert_called()


class TestRenderRayonArticlesAdditional:
    """Tests supplémentaires pour render_rayon_articles."""

    @patch(
        "src.modules.cuisine.courses.liste_active.PRIORITY_EMOJIS",
        {"haute": "🔴", "moyenne": "🟡", "basse": "🟢"},
    )
    @patch("src.modules.cuisine.courses.liste_active.RAYONS_DEFAULT", ["Crèmerie", "Autre"])
    @patch("src.modules.cuisine.courses.liste_active.st")
    def test_render_rayon_edit_form_save_success(self, mock_st):
        """Test sauvegarde formulaire édition réussie (lignes 97-106)."""
        from src.modules.cuisine.courses.liste_active import render_rayon_articles

        mock_service = MagicMock()
        articles = [
            {
                "id": 10,
                "ingredient_nom": "EditTest",
                "quantite_necessaire": 2.0,
                "unite": "kg",
                "priorite": "moyenne",
                "rayon_magasin": "Crèmerie",
                "notes": "Note",
                "suggere_par_ia": False,
            }
        ]

        mock_st.columns.side_effect = [
            [MagicMock(), MagicMock(), MagicMock(), MagicMock()],
            [MagicMock(), MagicMock()],
            [MagicMock(), MagicMock()],
        ]
        mock_st.button.return_value = False
        mock_st.session_state = MockSessionState({"edit_article_id": 10, "courses_refresh": 0})

        form_mock = MagicMock()
        mock_st.form.return_value.__enter__ = MagicMock(return_value=form_mock)
        mock_st.form.return_value.__exit__ = MagicMock(return_value=False)
        mock_st.number_input.return_value = 3.0
        mock_st.selectbox.side_effect = ["haute", "Autre"]
        mock_st.text_area.return_value = "New note"
        mock_st.form_submit_button.side_effect = [True, False]  # Save clicked, Cancel not

        render_rayon_articles(mock_service, "Crèmerie", articles)

        mock_service.update.assert_called()
        mock_st.success.assert_called()

    @patch(
        "src.modules.cuisine.courses.liste_active.PRIORITY_EMOJIS",
        {"haute": "🔴", "moyenne": "🟡", "basse": "🟢"},
    )
    @patch("src.modules.cuisine.courses.liste_active.RAYONS_DEFAULT", ["Crèmerie", "Autre"])
    @patch("src.modules.cuisine.courses.liste_active.st")
    def test_render_rayon_edit_form_cancel(self, mock_st):
        """Test annulation formulaire édition (lignes 172-173)."""
        from src.modules.cuisine.courses.liste_active import render_rayon_articles

        mock_service = MagicMock()
        articles = [
            {
                "id": 11,
                "ingredient_nom": "CancelTest",
                "quantite_necessaire": 1.0,
                "unite": "pièce",
                "priorite": "basse",
                "rayon_magasin": "Crèmerie",
                "notes": "",
                "suggere_par_ia": False,
            }
        ]

        mock_st.columns.side_effect = [
            [MagicMock(), MagicMock(), MagicMock(), MagicMock()],
            [MagicMock(), MagicMock()],
            [MagicMock(), MagicMock()],
        ]
        mock_st.button.return_value = False
        mock_st.session_state = MockSessionState({"edit_article_id": 11, "courses_refresh": 0})

        form_mock = MagicMock()
        mock_st.form.return_value.__enter__ = MagicMock(return_value=form_mock)
        mock_st.form.return_value.__exit__ = MagicMock(return_value=False)
        mock_st.number_input.return_value = 1.0
        mock_st.selectbox.side_effect = ["basse", "Crèmerie"]
        mock_st.text_area.return_value = ""
        mock_st.form_submit_button.side_effect = [False, True]  # Save not, Cancel clicked

        render_rayon_articles(mock_service, "Crèmerie", articles)

        mock_st.rerun.assert_called()

    @patch(
        "src.modules.cuisine.courses.liste_active.PRIORITY_EMOJIS",
        {"haute": "🔴", "moyenne": "🟡", "basse": "🟢"},
    )
    @patch("src.modules.cuisine.courses.liste_active.RAYONS_DEFAULT", ["Crèmerie", "Autre"])
    @patch("src.modules.cuisine.courses.liste_active.st")
    def test_render_rayon_edit_form_save_error(self, mock_st):
        """Test erreur sauvegarde formulaire édition."""
        from src.modules.cuisine.courses.liste_active import render_rayon_articles

        mock_service = MagicMock()
        mock_service.update.side_effect = Exception("Update failed")
        articles = [
            {
                "id": 12,
                "ingredient_nom": "ErrorTest",
                "quantite_necessaire": 1.0,
                "unite": "kg",
                "priorite": "moyenne",
                "rayon_magasin": "Crèmerie",
                "notes": "",
                "suggere_par_ia": False,
            }
        ]

        mock_st.columns.side_effect = [
            [MagicMock(), MagicMock(), MagicMock(), MagicMock()],
            [MagicMock(), MagicMock()],
            [MagicMock(), MagicMock()],
        ]
        mock_st.button.return_value = False
        mock_st.session_state = MockSessionState({"edit_article_id": 12, "courses_refresh": 0})

        form_mock = MagicMock()
        mock_st.form.return_value.__enter__ = MagicMock(return_value=form_mock)
        mock_st.form.return_value.__exit__ = MagicMock(return_value=False)
        mock_st.number_input.return_value = 1.0
        mock_st.selectbox.side_effect = ["moyenne", "Crèmerie"]
        mock_st.text_area.return_value = ""
        mock_st.form_submit_button.side_effect = [True, False]  # Save clicked

        render_rayon_articles(mock_service, "Crèmerie", articles)

        mock_st.error.assert_called()

    @patch(
        "src.modules.cuisine.courses.liste_active.PRIORITY_EMOJIS",
        {"haute": "🔴", "moyenne": "🟡", "basse": "🟢"},
    )
    @patch("src.modules.cuisine.courses.liste_active.RAYONS_DEFAULT", ["Rayon", "Autre"])
    @patch("src.modules.cuisine.courses.liste_active.st")
    def test_render_rayon_articles_edit_button_clicked(self, mock_st):
        """Test bouton édition cliqué."""
        from src.modules.cuisine.courses.liste_active import render_rayon_articles

        mock_service = MagicMock()
        articles = [
            {
                "id": 13,
                "ingredient_nom": "EditBtn",
                "quantite_necessaire": 1.0,
                "unite": "kg",
                "priorite": "moyenne",
                "rayon_magasin": "Rayon",
                "notes": None,
                "suggere_par_ia": False,
            }
        ]

        # 3 columns calls: article row (4), form inputs (2), form buttons (2)
        mock_st.columns.side_effect = [
            [MagicMock(), MagicMock(), MagicMock(), MagicMock()],  # article row
            [MagicMock(), MagicMock()],  # form input columns
            [MagicMock(), MagicMock()],  # form button columns
        ]
        # Boutons: mark bought=False, edit=True, delete=False
        mock_st.button.side_effect = [False, True, False]
        mock_st.session_state = MockSessionState({"edit_article_id": None, "courses_refresh": 0})

        # Setup form mock since edit form will be shown after button click
        form_mock = MagicMock()
        mock_st.form.return_value.__enter__ = MagicMock(return_value=form_mock)
        mock_st.form.return_value.__exit__ = MagicMock(return_value=False)
        mock_st.number_input.return_value = 1.0
        mock_st.selectbox.side_effect = ["moyenne", "Rayon"]
        mock_st.text_area.return_value = ""
        mock_st.form_submit_button.side_effect = [False, False]  # Save=F, Cancel=F

        render_rayon_articles(mock_service, "Rayon", articles)

        mock_st.rerun.assert_called()
