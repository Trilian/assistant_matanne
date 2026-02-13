"""
Tests pour src/modules/cuisine/courses/modeles.py

Couverture complète des fonctions UI modèles courses.
"""

from contextlib import contextmanager
from unittest.mock import MagicMock, patch


def make_db_context(mock_session):
    """Crée un contexte DB mock."""

    @contextmanager
    def db_context():
        yield mock_session

    return db_context


class TestRenderModeles:
    """Tests pour render_modeles()."""

    def test_import(self):
        """Test import réussi."""
        from src.modules.cuisine.courses.modeles import render_modeles

        assert render_modeles is not None

    @patch("src.modules.cuisine.courses.modeles.get_courses_service")
    @patch("src.modules.cuisine.courses.modeles.st")
    def test_render_modeles_empty(self, mock_st, mock_service):
        """Test sans modèles."""
        from src.modules.cuisine.courses.modeles import render_modeles

        svc = MagicMock()
        svc.get_modeles.return_value = []
        svc.get_liste_courses.return_value = []
        mock_service.return_value = svc

        tab1, tab2 = MagicMock(), MagicMock()
        mock_st.tabs.return_value = [tab1, tab2]
        tab1.__enter__ = MagicMock(return_value=tab1)
        tab1.__exit__ = MagicMock(return_value=False)
        tab2.__enter__ = MagicMock(return_value=tab2)
        tab2.__exit__ = MagicMock(return_value=False)

        render_modeles()

        mock_st.subheader.assert_called()
        mock_st.info.assert_called()

    @patch("src.modules.cuisine.courses.modeles.get_courses_service")
    @patch("src.modules.cuisine.courses.modeles.st")
    def test_render_modeles_with_modeles(self, mock_st, mock_service):
        """Test avec modèles existants."""
        from src.modules.cuisine.courses.modeles import render_modeles

        modele = {
            "id": 1,
            "nom": "Courses hebdo",
            "description": "Liste standard",
            "articles": [
                {
                    "nom": "Lait",
                    "quantite": 2,
                    "unite": "l",
                    "rayon": "Crèmerie",
                    "priorite": "haute",
                    "notes": None,
                },
            ],
            "cree_le": "2025-01-01T10:00:00",
        }

        svc = MagicMock()
        svc.get_modeles.return_value = [modele]
        svc.get_liste_courses.return_value = []
        mock_service.return_value = svc

        tab1, tab2 = MagicMock(), MagicMock()
        mock_st.tabs.return_value = [tab1, tab2]
        tab1.__enter__ = MagicMock(return_value=tab1)
        tab1.__exit__ = MagicMock(return_value=False)
        tab2.__enter__ = MagicMock(return_value=tab2)
        tab2.__exit__ = MagicMock(return_value=False)

        container_mock = MagicMock()
        mock_st.container.return_value.__enter__ = MagicMock(return_value=container_mock)
        mock_st.container.return_value.__exit__ = MagicMock(return_value=False)

        expander_mock = MagicMock()
        mock_st.expander.return_value.__enter__ = MagicMock(return_value=expander_mock)
        mock_st.expander.return_value.__exit__ = MagicMock(return_value=False)

        mock_st.columns.return_value = [MagicMock(), MagicMock(), MagicMock()]
        mock_st.button.return_value = False
        mock_st.session_state = {"courses_refresh": 0}

        render_modeles()

        mock_st.write.assert_called()

    @patch("src.modules.cuisine.courses.modeles.get_courses_service")
    @patch("src.modules.cuisine.courses.modeles.st")
    def test_render_modeles_with_modele_notes(self, mock_st, mock_service):
        """Test avec modèles ayant des notes."""
        from src.modules.cuisine.courses.modeles import render_modeles

        modele = {
            "id": 2,
            "nom": "Test Notes",
            "description": None,
            "articles": [
                {
                    "nom": "Article",
                    "quantite": 1,
                    "unite": "kg",
                    "rayon": "Autre",
                    "priorite": "moyenne",
                    "notes": "Note importante",
                },
            ],
            "cree_le": "2025-01-01",
        }

        svc = MagicMock()
        svc.get_modeles.return_value = [modele]
        svc.get_liste_courses.return_value = []
        mock_service.return_value = svc

        tab1, tab2 = MagicMock(), MagicMock()
        mock_st.tabs.return_value = [tab1, tab2]
        tab1.__enter__ = MagicMock(return_value=tab1)
        tab1.__exit__ = MagicMock(return_value=False)
        tab2.__enter__ = MagicMock(return_value=tab2)
        tab2.__exit__ = MagicMock(return_value=False)

        container_mock = MagicMock()
        mock_st.container.return_value.__enter__ = MagicMock(return_value=container_mock)
        mock_st.container.return_value.__exit__ = MagicMock(return_value=False)

        expander_mock = MagicMock()
        mock_st.expander.return_value.__enter__ = MagicMock(return_value=expander_mock)
        mock_st.expander.return_value.__exit__ = MagicMock(return_value=False)

        mock_st.columns.return_value = [MagicMock(), MagicMock(), MagicMock()]
        mock_st.button.return_value = False
        mock_st.session_state = {"courses_refresh": 0}

        render_modeles()

        mock_st.caption.assert_called()

    @patch("src.modules.cuisine.courses.modeles.get_courses_service")
    @patch("src.modules.cuisine.courses.modeles.st")
    def test_render_modeles_load_modele(self, mock_st, mock_service):
        """Test charger modèle."""
        from src.modules.cuisine.courses.modeles import render_modeles

        modele = {
            "id": 2,
            "nom": "Test",
            "description": None,
            "articles": [],
            "cree_le": "2025-02-01T10:00:00",
        }

        svc = MagicMock()
        svc.get_modeles.return_value = [modele]
        svc.get_liste_courses.return_value = []
        svc.appliquer_modele.return_value = [1, 2, 3]  # 3 articles created
        mock_service.return_value = svc

        tab1, tab2 = MagicMock(), MagicMock()
        mock_st.tabs.return_value = [tab1, tab2]
        tab1.__enter__ = MagicMock(return_value=tab1)
        tab1.__exit__ = MagicMock(return_value=False)
        tab2.__enter__ = MagicMock(return_value=tab2)
        tab2.__exit__ = MagicMock(return_value=False)

        container_mock = MagicMock()
        mock_st.container.return_value.__enter__ = MagicMock(return_value=container_mock)
        mock_st.container.return_value.__exit__ = MagicMock(return_value=False)

        expander_mock = MagicMock()
        mock_st.expander.return_value.__enter__ = MagicMock(return_value=expander_mock)
        mock_st.expander.return_value.__exit__ = MagicMock(return_value=False)

        mock_st.columns.return_value = [MagicMock(), MagicMock(), MagicMock()]
        mock_st.button.side_effect = [True, False]  # Load button clicked
        mock_st.session_state = {"courses_refresh": 0}

        render_modeles()

        svc.appliquer_modele.assert_called_with(2)
        mock_st.success.assert_called()

    @patch("src.modules.cuisine.courses.modeles.get_courses_service")
    @patch("src.modules.cuisine.courses.modeles.st")
    def test_render_modeles_load_empty_result(self, mock_st, mock_service):
        """Test charger modèle sans articles."""
        from src.modules.cuisine.courses.modeles import render_modeles

        modele = {
            "id": 3,
            "nom": "Vide",
            "description": None,
            "articles": [],
            "cree_le": "2025-01-01",
        }

        svc = MagicMock()
        svc.get_modeles.return_value = [modele]
        svc.get_liste_courses.return_value = []
        svc.appliquer_modele.return_value = []  # No articles
        mock_service.return_value = svc

        tab1, tab2 = MagicMock(), MagicMock()
        mock_st.tabs.return_value = [tab1, tab2]
        tab1.__enter__ = MagicMock(return_value=tab1)
        tab1.__exit__ = MagicMock(return_value=False)
        tab2.__enter__ = MagicMock(return_value=tab2)
        tab2.__exit__ = MagicMock(return_value=False)

        container_mock = MagicMock()
        mock_st.container.return_value.__enter__ = MagicMock(return_value=container_mock)
        mock_st.container.return_value.__exit__ = MagicMock(return_value=False)

        expander_mock = MagicMock()
        mock_st.expander.return_value.__enter__ = MagicMock(return_value=expander_mock)
        mock_st.expander.return_value.__exit__ = MagicMock(return_value=False)

        mock_st.columns.return_value = [MagicMock(), MagicMock(), MagicMock()]
        mock_st.button.side_effect = [True, False]
        mock_st.session_state = {"courses_refresh": 0}

        render_modeles()

        mock_st.warning.assert_called()

    @patch("src.modules.cuisine.courses.modeles.get_courses_service")
    @patch("src.modules.cuisine.courses.modeles.st")
    def test_render_modeles_delete_modele(self, mock_st, mock_service):
        """Test supprimer modèle."""
        from src.modules.cuisine.courses.modeles import render_modeles

        modele = {
            "id": 4,
            "nom": "A suppr",
            "description": None,
            "articles": [],
            "cree_le": "2025-01-01",
        }

        svc = MagicMock()
        svc.get_modeles.return_value = [modele]
        svc.get_liste_courses.return_value = []
        mock_service.return_value = svc

        tab1, tab2 = MagicMock(), MagicMock()
        mock_st.tabs.return_value = [tab1, tab2]
        tab1.__enter__ = MagicMock(return_value=tab1)
        tab1.__exit__ = MagicMock(return_value=False)
        tab2.__enter__ = MagicMock(return_value=tab2)
        tab2.__exit__ = MagicMock(return_value=False)

        container_mock = MagicMock()
        mock_st.container.return_value.__enter__ = MagicMock(return_value=container_mock)
        mock_st.container.return_value.__exit__ = MagicMock(return_value=False)

        expander_mock = MagicMock()
        mock_st.expander.return_value.__enter__ = MagicMock(return_value=expander_mock)
        mock_st.expander.return_value.__exit__ = MagicMock(return_value=False)

        mock_st.columns.return_value = [MagicMock(), MagicMock(), MagicMock()]
        mock_st.button.side_effect = [False, True]  # Delete button clicked
        mock_st.session_state = {"courses_refresh": 0}

        render_modeles()

        svc.delete_modele.assert_called_with(4)
        mock_st.success.assert_called()

    @patch("src.modules.cuisine.courses.modeles.get_courses_service")
    @patch("src.modules.cuisine.courses.modeles.st")
    def test_render_modeles_delete_error(self, mock_st, mock_service):
        """Test erreur suppression modèle."""
        from src.modules.cuisine.courses.modeles import render_modeles

        modele = {
            "id": 5,
            "nom": "Erreur",
            "description": None,
            "articles": [],
            "cree_le": "2025-01-01",
        }

        svc = MagicMock()
        svc.get_modeles.return_value = [modele]
        svc.get_liste_courses.return_value = []
        svc.delete_modele.side_effect = Exception("Delete error")
        mock_service.return_value = svc

        tab1, tab2 = MagicMock(), MagicMock()
        mock_st.tabs.return_value = [tab1, tab2]
        tab1.__enter__ = MagicMock(return_value=tab1)
        tab1.__exit__ = MagicMock(return_value=False)
        tab2.__enter__ = MagicMock(return_value=tab2)
        tab2.__exit__ = MagicMock(return_value=False)

        container_mock = MagicMock()
        mock_st.container.return_value.__enter__ = MagicMock(return_value=container_mock)
        mock_st.container.return_value.__exit__ = MagicMock(return_value=False)

        expander_mock = MagicMock()
        mock_st.expander.return_value.__enter__ = MagicMock(return_value=expander_mock)
        mock_st.expander.return_value.__exit__ = MagicMock(return_value=False)

        mock_st.columns.return_value = [MagicMock(), MagicMock(), MagicMock()]
        mock_st.button.side_effect = [False, True]
        mock_st.session_state = {"courses_refresh": 0}

        render_modeles()

        mock_st.error.assert_called()

    @patch("src.modules.cuisine.courses.modeles.get_courses_service")
    @patch("src.modules.cuisine.courses.modeles.st")
    def test_render_modeles_create_empty_name(self, mock_st, mock_service):
        """Test création modèle nom vide."""
        from src.modules.cuisine.courses.modeles import render_modeles

        svc = MagicMock()
        svc.get_modeles.return_value = []
        svc.get_liste_courses.return_value = [
            {
                "ingredient_id": 1,
                "ingredient_nom": "Test",
                "quantite_necessaire": 1,
                "unite": "kg",
                "rayon_magasin": "R",
                "priorite": "moyenne",
                "notes": None,
            }
        ]
        mock_service.return_value = svc

        tab1, tab2 = MagicMock(), MagicMock()
        mock_st.tabs.return_value = [tab1, tab2]
        tab1.__enter__ = MagicMock(return_value=tab1)
        tab1.__exit__ = MagicMock(return_value=False)
        tab2.__enter__ = MagicMock(return_value=tab2)
        tab2.__exit__ = MagicMock(return_value=False)

        mock_st.columns.return_value = [MagicMock(), MagicMock()]
        mock_st.text_input.return_value = ""  # Empty name
        mock_st.text_area.return_value = ""
        mock_st.button.return_value = True  # Save clicked
        mock_st.session_state = {}

        render_modeles()

        mock_st.error.assert_called()

    @patch("src.modules.cuisine.courses.modeles.get_courses_service")
    @patch("src.modules.cuisine.courses.modeles.st")
    def test_render_modeles_create_success(self, mock_st, mock_service):
        """Test création modèle réussie."""
        from src.modules.cuisine.courses.modeles import render_modeles

        svc = MagicMock()
        svc.get_modeles.return_value = []
        svc.get_liste_courses.return_value = [
            {
                "ingredient_id": 1,
                "ingredient_nom": "Lait",
                "quantite_necessaire": 2,
                "unite": "l",
                "rayon_magasin": "Crèmerie",
                "priorite": "haute",
                "notes": "Bio",
            }
        ]
        svc.create_modele.return_value = 10
        mock_service.return_value = svc

        tab1, tab2 = MagicMock(), MagicMock()
        mock_st.tabs.return_value = [tab1, tab2]
        tab1.__enter__ = MagicMock(return_value=tab1)
        tab1.__exit__ = MagicMock(return_value=False)
        tab2.__enter__ = MagicMock(return_value=tab2)
        tab2.__exit__ = MagicMock(return_value=False)

        mock_st.columns.return_value = [MagicMock(), MagicMock()]
        mock_st.text_input.return_value = "Mon modèle"
        mock_st.text_area.return_value = "Description test"
        mock_st.button.return_value = True
        mock_st.session_state = {}

        render_modeles()

        svc.create_modele.assert_called()
        mock_st.success.assert_called()
        mock_st.balloons.assert_called()

    @patch("src.modules.cuisine.courses.modeles.get_courses_service")
    @patch("src.modules.cuisine.courses.modeles.st")
    @patch("src.modules.cuisine.courses.modeles.logger")
    def test_render_modeles_create_error(self, mock_logger, mock_st, mock_service):
        """Test erreur création modèle."""
        from src.modules.cuisine.courses.modeles import render_modeles

        svc = MagicMock()
        svc.get_modeles.return_value = []
        svc.get_liste_courses.return_value = [
            {
                "ingredient_id": 1,
                "ingredient_nom": "X",
                "quantite_necessaire": 1,
                "unite": "kg",
                "rayon_magasin": "R",
                "priorite": "basse",
                "notes": None,
            }
        ]
        svc.create_modele.side_effect = Exception("DB Error")
        mock_service.return_value = svc

        tab1, tab2 = MagicMock(), MagicMock()
        mock_st.tabs.return_value = [tab1, tab2]
        tab1.__enter__ = MagicMock(return_value=tab1)
        tab1.__exit__ = MagicMock(return_value=False)
        tab2.__enter__ = MagicMock(return_value=tab2)
        tab2.__exit__ = MagicMock(return_value=False)

        mock_st.columns.return_value = [MagicMock(), MagicMock()]
        mock_st.text_input.return_value = "Nom valide"
        mock_st.text_area.return_value = ""
        mock_st.button.return_value = True
        mock_st.session_state = {}

        render_modeles()

        mock_st.error.assert_called()
        mock_logger.error.assert_called()

    @patch("src.modules.cuisine.courses.modeles.get_courses_service")
    @patch("src.modules.cuisine.courses.modeles.st")
    def test_render_modeles_new_tab_empty_list(self, mock_st, mock_service):
        """Test onglet nouveau avec liste vide."""
        from src.modules.cuisine.courses.modeles import render_modeles

        svc = MagicMock()
        svc.get_modeles.return_value = []
        svc.get_liste_courses.return_value = []  # Empty list
        mock_service.return_value = svc

        tab1, tab2 = MagicMock(), MagicMock()
        mock_st.tabs.return_value = [tab1, tab2]
        tab1.__enter__ = MagicMock(return_value=tab1)
        tab1.__exit__ = MagicMock(return_value=False)
        tab2.__enter__ = MagicMock(return_value=tab2)
        tab2.__exit__ = MagicMock(return_value=False)

        render_modeles()

        mock_st.warning.assert_called()

    @patch("src.modules.cuisine.courses.modeles.get_courses_service")
    @patch("src.modules.cuisine.courses.modeles.st")
    @patch("src.modules.cuisine.courses.modeles.logger")
    def test_render_modeles_global_exception(self, mock_logger, mock_st, mock_service):
        """Test exception globale."""
        from src.modules.cuisine.courses.modeles import render_modeles

        mock_service.return_value.get_modeles.side_effect = Exception("Service error")

        render_modeles()

        mock_st.error.assert_called()
        mock_logger.error.assert_called()

    @patch("src.modules.cuisine.courses.modeles.get_courses_service")
    @patch("src.modules.cuisine.courses.modeles.st")
    def test_render_modeles_load_error_with_traceback(self, mock_st, mock_service):
        """Test charger modèle avec erreur et traceback."""
        from src.modules.cuisine.courses.modeles import render_modeles

        modele = {
            "id": 5,
            "nom": "Erreur",
            "description": None,
            "articles": [],
            "cree_le": "2025-01-01",
        }

        svc = MagicMock()
        svc.get_modeles.return_value = [modele]
        svc.get_liste_courses.return_value = []
        svc.appliquer_modele.side_effect = Exception("Erreur apply")
        mock_service.return_value = svc

        tab1, tab2 = MagicMock(), MagicMock()
        mock_st.tabs.return_value = [tab1, tab2]
        tab1.__enter__ = MagicMock(return_value=tab1)
        tab1.__exit__ = MagicMock(return_value=False)
        tab2.__enter__ = MagicMock(return_value=tab2)
        tab2.__exit__ = MagicMock(return_value=False)

        container_mock = MagicMock()
        mock_st.container.return_value.__enter__ = MagicMock(return_value=container_mock)
        mock_st.container.return_value.__exit__ = MagicMock(return_value=False)

        expander_mock = MagicMock()
        mock_st.expander.return_value.__enter__ = MagicMock(return_value=expander_mock)
        mock_st.expander.return_value.__exit__ = MagicMock(return_value=False)

        mock_st.columns.return_value = [MagicMock(), MagicMock(), MagicMock()]
        mock_st.button.side_effect = [True, False]
        mock_st.session_state = {"courses_refresh": 0}

        render_modeles()

        mock_st.error.assert_called()

    @patch("src.modules.cuisine.courses.modeles.get_courses_service")
    @patch("src.modules.cuisine.courses.modeles.st")
    def test_render_modeles_articles_all_priorities(self, mock_st, mock_service):
        """Test affichage articles avec toutes priorités."""
        from src.modules.cuisine.courses.modeles import render_modeles

        modele = {
            "id": 6,
            "nom": "Priorités",
            "description": "Test",
            "articles": [
                {
                    "nom": "A",
                    "quantite": 1,
                    "unite": "kg",
                    "rayon": "R",
                    "priorite": "haute",
                    "notes": None,
                },
                {
                    "nom": "B",
                    "quantite": 1,
                    "unite": "kg",
                    "rayon": "R",
                    "priorite": "moyenne",
                    "notes": None,
                },
                {
                    "nom": "C",
                    "quantite": 1,
                    "unite": "kg",
                    "rayon": "R",
                    "priorite": "basse",
                    "notes": None,
                },
            ],
            "cree_le": "2025-01-01",
        }

        svc = MagicMock()
        svc.get_modeles.return_value = [modele]
        svc.get_liste_courses.return_value = []
        mock_service.return_value = svc

        tab1, tab2 = MagicMock(), MagicMock()
        mock_st.tabs.return_value = [tab1, tab2]
        tab1.__enter__ = MagicMock(return_value=tab1)
        tab1.__exit__ = MagicMock(return_value=False)
        tab2.__enter__ = MagicMock(return_value=tab2)
        tab2.__exit__ = MagicMock(return_value=False)

        container_mock = MagicMock()
        mock_st.container.return_value.__enter__ = MagicMock(return_value=container_mock)
        mock_st.container.return_value.__exit__ = MagicMock(return_value=False)

        expander_mock = MagicMock()
        mock_st.expander.return_value.__enter__ = MagicMock(return_value=expander_mock)
        mock_st.expander.return_value.__exit__ = MagicMock(return_value=False)

        mock_st.columns.return_value = [MagicMock(), MagicMock(), MagicMock()]
        mock_st.button.return_value = False
        mock_st.session_state = {"courses_refresh": 0}

        render_modeles()

        # Should display articles with different priorities
        assert mock_st.write.call_count >= 3


class TestModelesModule:
    """Tests module-level."""

    def test_all_exports(self):
        """Test __all__ exports."""
        from src.modules.cuisine.courses import modeles

        assert "render_modeles" in modeles.__all__
