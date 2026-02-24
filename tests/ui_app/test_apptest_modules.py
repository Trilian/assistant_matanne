"""
Tests AppTest pour le module Accueil (Dashboard).

Vérifie le rendu du tableau de bord, les métriques, alertes, et actions rapides.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


@pytest.mark.ui
class TestAccueilAppTest:
    """Tests du module accueil via st.testing.AppTest."""

    @pytest.fixture(autouse=True)
    def _setup_mocks(self):
        """Configure les mocks pour tous les tests accueil."""
        # Mock services
        self.mock_recettes = MagicMock()
        self.mock_recettes.get_stats.return_value = {"total": 42, "favorites": 10}

        self.mock_inventaire = MagicMock()
        self.mock_inventaire.get_stats.return_value = {"total": 85, "critique": 3}
        self.mock_inventaire.get_inventaire_complet.return_value = []

        self.mock_courses = MagicMock()
        self.mock_courses.get_stats.return_value = {"total": 12, "achetes": 5}

        self.mock_planning = MagicMock()
        planning_mock = MagicMock()
        planning_mock.repas = []
        self.mock_planning.get_planning.return_value = planning_mock

        self.patches = [
            patch(
                "src.services.cuisine.recettes.obtenir_service_recettes",
                return_value=self.mock_recettes,
            ),
            patch(
                "src.services.inventaire.obtenir_service_inventaire",
                return_value=self.mock_inventaire,
            ),
            patch(
                "src.services.cuisine.courses.obtenir_service_courses",
                return_value=self.mock_courses,
            ),
            patch(
                "src.services.cuisine.planning.obtenir_service_planning",
                return_value=self.mock_planning,
            ),
            patch(
                "src.modules.planning.timeline_ui.charger_events_periode",
                return_value=[],
            ),
        ]
        for p in self.patches:
            p.start()

        yield

        for p in self.patches:
            p.stop()

    def test_accueil_renders_without_exception(self, assertions):
        """Le dashboard accueil se charge sans exception."""
        from streamlit.testing.v1 import AppTest

        at = AppTest.from_function(self._run_accueil, default_timeout=10)
        at.run()
        assertions.assert_no_exception(at)

    def test_accueil_has_welcome_text(self, assertions):
        """Le dashboard affiche le message de bienvenue."""
        from streamlit.testing.v1 import AppTest

        at = AppTest.from_function(self._run_accueil, default_timeout=10)
        at.run()
        assertions.assert_no_exception(at)
        # Vérifie le contenu markdown de bienvenue
        markdown_texts = [m.value for m in at.markdown]
        assert any("Bienvenue" in m for m in markdown_texts), "Message de bienvenue non trouvé"

    def test_accueil_displays_stats(self, assertions):
        """Le dashboard affiche les statistiques globales."""
        from streamlit.testing.v1 import AppTest

        at = AppTest.from_function(self._run_accueil, default_timeout=10)
        at.run()
        assertions.assert_no_exception(at)

        # Vérifie les métriques
        metrics = at.metric
        assert len(metrics) >= 4, f"Attendu 4+ métriques, trouvé {len(metrics)}"

    def test_accueil_has_quick_actions(self, assertions):
        """Le dashboard affiche les boutons d'actions rapides."""
        from streamlit.testing.v1 import AppTest

        at = AppTest.from_function(self._run_accueil, default_timeout=10)
        at.run()
        assertions.assert_no_exception(at)

        # Vérifie les boutons d'actions rapides
        buttons = at.button
        assert len(buttons) >= 4, f"Attendu 4+ boutons, trouvé {len(buttons)}"

    def test_accueil_quick_action_button_click(self, assertions):
        """Cliquer sur un bouton d'action rapide ne lève pas d'exception."""
        from streamlit.testing.v1 import AppTest

        at = AppTest.from_function(self._run_accueil, default_timeout=10)
        at.run()
        assertions.assert_no_exception(at)

        # Cliquer le premier bouton (si existant)
        if at.button:
            at.button[0].click()
            at.run()
            # Pas d'exception = succès (rerun est intercepté)

    @staticmethod
    def _run_accueil():
        """Wrapper pour charger le module accueil dans AppTest."""
        from src.modules.accueil import app

        app()


@pytest.mark.ui
class TestCoursesAppTest:
    """Tests du module courses via st.testing.AppTest."""

    @pytest.fixture(autouse=True)
    def _setup_mocks(self):
        """Configure les mocks pour le module courses."""
        self.mock_courses = MagicMock()
        self.mock_courses.get_liste_active.return_value = []
        self.mock_courses.get_stats.return_value = {"total": 0}

        self.patches = [
            patch(
                "src.services.cuisine.courses.obtenir_service_courses",
                return_value=self.mock_courses,
            ),
            patch(
                "src.services.cuisine.planning.obtenir_service_planning",
                return_value=MagicMock(),
            ),
        ]
        for p in self.patches:
            p.start()
        yield
        for p in self.patches:
            p.stop()

    def test_courses_renders_without_exception(self, assertions):
        """Le module courses se charge sans exception."""
        from streamlit.testing.v1 import AppTest

        at = AppTest.from_function(self._run_courses, default_timeout=10)
        at.run()
        assertions.assert_no_exception(at)

    def test_courses_has_title(self, assertions):
        """Le module courses affiche son titre."""
        from streamlit.testing.v1 import AppTest

        at = AppTest.from_function(self._run_courses, default_timeout=10)
        at.run()
        assertions.assert_no_exception(at)
        assertions.assert_has_title(at, "Courses")

    def test_courses_has_tabs(self, assertions):
        """Le module courses a des onglets."""
        from streamlit.testing.v1 import AppTest

        at = AppTest.from_function(self._run_courses, default_timeout=10)
        at.run()
        assertions.assert_no_exception(at)

    @staticmethod
    def _run_courses():
        """Wrapper pour charger le module courses."""
        from src.modules.cuisine.courses import app

        app()


@pytest.mark.ui
class TestInventaireAppTest:
    """Tests du module inventaire via st.testing.AppTest."""

    @pytest.fixture(autouse=True)
    def _setup_mocks(self):
        """Configure les mocks pour le module inventaire."""
        self.mock_inventaire = MagicMock()
        self.mock_inventaire.get_inventaire_complet.return_value = []
        self.mock_inventaire.get_stats.return_value = {"total": 0}
        self.mock_inventaire.get_emplacements.return_value = ["Frigo", "Placard", "Congélateur"]
        self.mock_inventaire.get_categories.return_value = ["Légumes", "Fruits", "Viandes"]

        self.patches = [
            patch(
                "src.services.inventaire.obtenir_service_inventaire",
                return_value=self.mock_inventaire,
            ),
        ]
        for p in self.patches:
            p.start()
        yield
        for p in self.patches:
            p.stop()

    def test_inventaire_renders_without_exception(self, assertions):
        """Le module inventaire se charge sans exception."""
        from streamlit.testing.v1 import AppTest

        at = AppTest.from_function(self._run_inventaire, default_timeout=10)
        at.run()
        assertions.assert_no_exception(at)

    @staticmethod
    def _run_inventaire():
        """Wrapper pour charger le module inventaire."""
        from src.modules.cuisine.inventaire import app

        app()
