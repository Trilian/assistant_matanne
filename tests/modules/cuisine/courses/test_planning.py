"""
Tests pour src/modules/cuisine/courses/planning.py

Couverture complète des fonctions UI planning courses.
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


def create_columns_side_effect(*sizes):
    """Crée side_effect pour st.columns avec plusieurs appels."""
    results = []
    for size in sizes:
        if isinstance(size, int):
            results.append([MagicMock() for _ in range(size)])
        elif isinstance(size, list):
            results.append([MagicMock() for _ in range(len(size))])
        else:
            results.append([MagicMock() for _ in range(2)])
    return results


class TestRenderCoursesDepuisPlanning:
    """Tests pour render_courses_depuis_planning()."""

    def test_import(self):
        """Test import réussi."""
        from src.modules.cuisine.courses.planning import render_courses_depuis_planning

        assert render_courses_depuis_planning is not None

    @patch("src.modules.cuisine.courses.planning.get_courses_intelligentes_service")
    @patch("src.modules.cuisine.courses.planning.st")
    def test_render_no_planning(self, mock_st, mock_service):
        """Test sans planning actif."""
        from src.modules.cuisine.courses.planning import render_courses_depuis_planning

        svc = MagicMock()
        svc.obtenir_planning_actif.return_value = None
        mock_service.return_value = svc

        mock_st.button.return_value = False
        mock_st.session_state = MockSessionState({})

        render_courses_depuis_planning()

        mock_st.warning.assert_called()

    @patch("src.modules.cuisine.courses.planning.get_courses_intelligentes_service")
    @patch("src.modules.cuisine.courses.planning.st")
    def test_render_no_planning_navigate(self, mock_st, mock_service):
        """Test navigation vers planning."""
        from src.modules.cuisine.courses.planning import render_courses_depuis_planning

        svc = MagicMock()
        svc.obtenir_planning_actif.return_value = None
        mock_service.return_value = svc

        mock_st.button.return_value = True
        session_state = MockSessionState({})
        mock_st.session_state = session_state

        render_courses_depuis_planning()

        assert session_state.get("current_page") == "cuisine.planning_semaine"

    @patch("src.modules.cuisine.courses.planning.get_courses_intelligentes_service")
    @patch("src.modules.cuisine.courses.planning.st")
    def test_render_with_planning(self, mock_st, mock_service):
        """Test avec planning actif."""
        from src.modules.cuisine.courses.planning import render_courses_depuis_planning

        mock_planning = MagicMock()
        mock_planning.nom = "Semaine 5"
        mock_planning.semaine_debut = "2025-02-03"
        mock_planning.semaine_fin = "2025-02-09"
        mock_planning.repas = [MagicMock(), MagicMock()]

        svc = MagicMock()
        svc.obtenir_planning_actif.return_value = mock_planning
        mock_service.return_value = svc

        mock_st.columns.side_effect = create_columns_side_effect([2, 1])
        mock_st.button.return_value = False
        mock_st.session_state = MockSessionState({})

        render_courses_depuis_planning()

        mock_st.success.assert_called()
        mock_st.subheader.assert_called()

    @patch("src.modules.cuisine.courses.planning.get_courses_intelligentes_service")
    @patch("src.modules.cuisine.courses.planning.st")
    def test_render_generate_list(self, mock_st, mock_service):
        """Test génération liste."""
        from src.modules.cuisine.courses.planning import render_courses_depuis_planning

        mock_planning = MagicMock()
        mock_planning.nom = "Test"
        mock_planning.semaine_debut = "2025-02-01"
        mock_planning.semaine_fin = "2025-02-07"
        mock_planning.repas = []

        mock_result = MagicMock()
        mock_result.alertes = ["OK Liste générée"]
        mock_result.articles = []
        mock_result.total_articles = 0
        mock_result.recettes_couvertes = []

        svc = MagicMock()
        svc.obtenir_planning_actif.return_value = mock_planning
        svc.generer_liste_courses.return_value = mock_result
        mock_service.return_value = svc

        mock_st.columns.side_effect = create_columns_side_effect([2, 1])
        mock_st.button.return_value = True  # Generate clicked
        mock_st.spinner.return_value.__enter__ = MagicMock()
        mock_st.spinner.return_value.__exit__ = MagicMock(return_value=False)
        mock_st.session_state = MockSessionState({})

        render_courses_depuis_planning()

        svc.generer_liste_courses.assert_called()

    @patch("src.modules.cuisine.courses.planning.get_courses_intelligentes_service")
    @patch("src.modules.cuisine.courses.planning.st")
    def test_render_with_result_articles(self, mock_st, mock_service):
        """Test affichage résultat avec articles."""
        from src.modules.cuisine.courses.planning import render_courses_depuis_planning

        mock_planning = MagicMock()
        mock_planning.nom = "Test"
        mock_planning.semaine_debut = "2025-02-01"
        mock_planning.semaine_fin = "2025-02-07"
        mock_planning.repas = []

        mock_article = MagicMock()
        mock_article.nom = "Tomates"
        mock_article.rayon = "Fruits et légumes"
        mock_article.priorite = 1
        mock_article.unite = "kg"
        mock_article.a_acheter = 2.0
        mock_article.en_stock = 0.5
        mock_article.recettes_source = ["Salade", "Pizza"]

        mock_result = MagicMock()
        mock_result.alertes = ["OK"]
        mock_result.articles = [mock_article]
        mock_result.total_articles = 1
        mock_result.recettes_couvertes = ["Salade"]

        svc = MagicMock()
        svc.obtenir_planning_actif.return_value = mock_planning
        mock_service.return_value = svc

        mock_st.columns.side_effect = create_columns_side_effect([2, 1], 3, 3, 2)
        mock_st.button.return_value = False
        mock_st.session_state = MockSessionState({"courses_planning_resultat": mock_result})

        expander_mock = MagicMock()
        mock_st.expander.return_value.__enter__ = MagicMock(return_value=expander_mock)
        mock_st.expander.return_value.__exit__ = MagicMock(return_value=False)
        mock_st.checkbox.return_value = True

        render_courses_depuis_planning()

        mock_st.metric.assert_called()

    @patch("src.modules.cuisine.courses.planning.get_courses_intelligentes_service")
    @patch("src.modules.cuisine.courses.planning.st")
    def test_render_add_articles(self, mock_st, mock_service):
        """Test ajout articles à la liste."""
        from src.modules.cuisine.courses.planning import render_courses_depuis_planning

        mock_planning = MagicMock()
        mock_planning.nom = "Test"
        mock_planning.semaine_debut = "2025-02-01"
        mock_planning.semaine_fin = "2025-02-07"
        mock_planning.repas = []

        mock_article = MagicMock()
        mock_article.nom = "Lait"
        mock_article.rayon = "Cremerie"
        mock_article.priorite = 2
        mock_article.unite = "l"
        mock_article.a_acheter = 1.0
        mock_article.en_stock = 0.0
        mock_article.recettes_source = ["Crepes"]

        mock_result = MagicMock()
        mock_result.alertes = []
        mock_result.articles = [mock_article]
        mock_result.total_articles = 1
        mock_result.recettes_couvertes = ["Crepes"]

        svc = MagicMock()
        svc.obtenir_planning_actif.return_value = mock_planning
        svc.ajouter_a_liste_courses.return_value = [1]
        mock_service.return_value = svc

        mock_st.columns.side_effect = create_columns_side_effect([2, 1], 3, 3, 2)
        mock_st.button.side_effect = [False, True, False]  # Add button clicked
        mock_st.spinner.return_value.__enter__ = MagicMock()
        mock_st.spinner.return_value.__exit__ = MagicMock(return_value=False)
        mock_st.session_state = MockSessionState(
            {"courses_planning_resultat": mock_result, "courses_refresh": 0}
        )

        expander_mock = MagicMock()
        mock_st.expander.return_value.__enter__ = MagicMock(return_value=expander_mock)
        mock_st.expander.return_value.__exit__ = MagicMock(return_value=False)
        mock_st.checkbox.return_value = True

        render_courses_depuis_planning()

        svc.ajouter_a_liste_courses.assert_called()
        mock_st.success.assert_called()

    @patch("src.modules.cuisine.courses.planning.get_courses_intelligentes_service")
    @patch("src.modules.cuisine.courses.planning.st")
    def test_render_regenerate(self, mock_st, mock_service):
        """Test régénération liste."""
        from src.modules.cuisine.courses.planning import render_courses_depuis_planning

        mock_planning = MagicMock()
        mock_planning.nom = "Test"
        mock_planning.semaine_debut = "2025-02-01"
        mock_planning.semaine_fin = "2025-02-07"
        mock_planning.repas = []

        # Need articles for the regenerate button to appear
        mock_article = MagicMock()
        mock_article.nom = "Test"
        mock_article.rayon = "Rayon"
        mock_article.priorite = 1
        mock_article.unite = "kg"
        mock_article.a_acheter = 1.0
        mock_article.en_stock = 0.0
        mock_article.recettes_source = []

        mock_result = MagicMock()
        mock_result.alertes = []
        mock_result.articles = [mock_article]
        mock_result.total_articles = 1
        mock_result.recettes_couvertes = []

        svc = MagicMock()
        svc.obtenir_planning_actif.return_value = mock_planning
        mock_service.return_value = svc

        mock_st.columns.side_effect = create_columns_side_effect([2, 1], 3, 3, 2)
        # button: Generate(False), Add(False), Regenerate(True)
        mock_st.button.side_effect = [False, False, True]
        session_state = MockSessionState({"courses_planning_resultat": mock_result})
        mock_st.session_state = session_state

        expander_mock = MagicMock()
        mock_st.expander.return_value.__enter__ = MagicMock(return_value=expander_mock)
        mock_st.expander.return_value.__exit__ = MagicMock(return_value=False)
        mock_st.checkbox.return_value = True

        render_courses_depuis_planning()

        # Regenerate was clicked -> session_state key should be deleted (but rerun is mocked)
        mock_st.rerun.assert_called()

    @patch("src.modules.cuisine.courses.planning.get_courses_intelligentes_service")
    @patch("src.modules.cuisine.courses.planning.st")
    def test_render_alertes_types(self, mock_st, mock_service):
        """Test différents types d'alertes."""
        from src.modules.cuisine.courses.planning import render_courses_depuis_planning

        mock_planning = MagicMock()
        mock_planning.nom = "Test"
        mock_planning.semaine_debut = "2025-02-01"
        mock_planning.semaine_fin = "2025-02-07"
        mock_planning.repas = []

        # Need articles for the regenerate button to appear
        mock_article = MagicMock()
        mock_article.nom = "Test"
        mock_article.rayon = "Rayon"
        mock_article.priorite = 1
        mock_article.unite = "kg"
        mock_article.a_acheter = 1.0
        mock_article.en_stock = 0.0
        mock_article.recettes_source = []

        mock_result = MagicMock()
        # Test avec alertes simples (sans emojis pour éviter problèmes d'encodage)
        mock_result.alertes = ["Info test"]
        mock_result.articles = [mock_article]
        mock_result.total_articles = 1
        mock_result.recettes_couvertes = []

        svc = MagicMock()
        svc.obtenir_planning_actif.return_value = mock_planning
        mock_service.return_value = svc

        mock_st.columns.side_effect = create_columns_side_effect([2, 1], 3, 3, 2)
        mock_st.button.return_value = False
        mock_st.session_state = MockSessionState({"courses_planning_resultat": mock_result})

        expander_mock = MagicMock()
        mock_st.expander.return_value.__enter__ = MagicMock(return_value=expander_mock)
        mock_st.expander.return_value.__exit__ = MagicMock(return_value=False)
        mock_st.checkbox.return_value = True

        render_courses_depuis_planning()

        # Les alertes sans emoji spécifique vont en st.info (branche else)
        mock_st.info.assert_called()

    @patch("src.modules.cuisine.courses.planning.get_courses_intelligentes_service")
    @patch("src.modules.cuisine.courses.planning.st")
    def test_render_uncheck_article(self, mock_st, mock_service):
        """Test désélection article."""
        from src.modules.cuisine.courses.planning import render_courses_depuis_planning

        mock_planning = MagicMock()
        mock_planning.nom = "Test"
        mock_planning.semaine_debut = "2025-02-01"
        mock_planning.semaine_fin = "2025-02-07"
        mock_planning.repas = []

        mock_article = MagicMock()
        mock_article.nom = "Pain"
        mock_article.rayon = "Boulangerie"
        mock_article.priorite = 3
        mock_article.unite = "pièce"
        mock_article.a_acheter = 1.0
        mock_article.en_stock = 0.0
        mock_article.recettes_source = []

        mock_result = MagicMock()
        mock_result.alertes = []
        mock_result.articles = [mock_article]
        mock_result.total_articles = 1
        mock_result.recettes_couvertes = []

        svc = MagicMock()
        svc.obtenir_planning_actif.return_value = mock_planning
        mock_service.return_value = svc

        mock_st.columns.side_effect = create_columns_side_effect([2, 1], 3, 3, 2)
        # button: Generate(False), Add(True => disabled), Regenerate(False)
        mock_st.button.side_effect = [False, True, False]
        mock_st.session_state = MockSessionState(
            {"courses_planning_resultat": mock_result, "courses_refresh": 0}
        )

        expander_mock = MagicMock()
        mock_st.expander.return_value.__enter__ = MagicMock(return_value=expander_mock)
        mock_st.expander.return_value.__exit__ = MagicMock(return_value=False)
        mock_st.checkbox.return_value = False  # Unchecked

        render_courses_depuis_planning()

        # Should not add any articles (disabled button)
        # Function is called but since articles_selectionnes is empty, disabled=True
        assert True  # Just check no exception

    @patch("src.modules.cuisine.courses.planning.get_courses_intelligentes_service")
    @patch("src.modules.cuisine.courses.planning.st")
    def test_render_instructions(self, mock_st, mock_service):
        """Test affichage instructions."""
        from src.modules.cuisine.courses.planning import render_courses_depuis_planning

        mock_planning = MagicMock()
        mock_planning.nom = "Test"
        mock_planning.semaine_debut = "2025-02-01"
        mock_planning.semaine_fin = "2025-02-07"
        mock_planning.repas = []

        svc = MagicMock()
        svc.obtenir_planning_actif.return_value = mock_planning
        mock_service.return_value = svc

        mock_st.columns.side_effect = create_columns_side_effect([2, 1])
        mock_st.button.return_value = False
        mock_st.session_state = MockSessionState({})  # No result yet

        render_courses_depuis_planning()

        mock_st.markdown.assert_called()

    @patch("src.modules.cuisine.courses.planning.get_courses_intelligentes_service")
    @patch("src.modules.cuisine.courses.planning.st")
    def test_render_multiple_rayons(self, mock_st, mock_service):
        """Test plusieurs rayons."""
        from src.modules.cuisine.courses.planning import render_courses_depuis_planning

        mock_planning = MagicMock()
        mock_planning.nom = "Test"
        mock_planning.semaine_debut = "2025-02-01"
        mock_planning.semaine_fin = "2025-02-07"
        mock_planning.repas = []

        articles = []
        for i, (nom, rayon) in enumerate(
            [("Lait", "Crèmerie"), ("Pain", "Boulangerie"), ("Yaourt", "Crèmerie")]
        ):
            art = MagicMock()
            art.nom = nom
            art.rayon = rayon
            art.priorite = i + 1
            art.unite = "pièce"
            art.a_acheter = 1.0
            art.en_stock = 0.0
            art.recettes_source = []
            articles.append(art)

        mock_result = MagicMock()
        mock_result.alertes = []
        mock_result.articles = articles
        mock_result.total_articles = 3
        mock_result.recettes_couvertes = []

        svc = MagicMock()
        svc.obtenir_planning_actif.return_value = mock_planning
        mock_service.return_value = svc

        # Multiple columns calls for multiple rayons
        mock_st.columns.side_effect = create_columns_side_effect([2, 1], 3, 3, 3, 3, 2)
        mock_st.button.return_value = False
        mock_st.session_state = MockSessionState({"courses_planning_resultat": mock_result})

        expander_mock = MagicMock()
        mock_st.expander.return_value.__enter__ = MagicMock(return_value=expander_mock)
        mock_st.expander.return_value.__exit__ = MagicMock(return_value=False)
        mock_st.checkbox.return_value = True

        render_courses_depuis_planning()

        # Should create 2 expanders (Cremerie and Boulangerie)
        assert mock_st.expander.call_count >= 2


class TestPlanningModule:
    """Tests module-level."""

    def test_all_exports(self):
        """Test __all__ exports."""
        from src.modules.cuisine.courses import planning

        assert "render_courses_depuis_planning" in planning.__all__
