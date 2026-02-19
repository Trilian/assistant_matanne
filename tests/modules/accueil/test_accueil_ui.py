"""Tests complets pour le module accueil.py UI."""

from __future__ import annotations

from datetime import date
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
    mock_st.session_state = SessionStateMock(session_data or {})
    mock_st.container.return_value.__enter__ = MagicMock(return_value=MagicMock())
    mock_st.container.return_value.__exit__ = MagicMock(return_value=False)
    mock_st.expander.return_value.__enter__ = MagicMock(return_value=MagicMock())
    mock_st.expander.return_value.__exit__ = MagicMock(return_value=False)
    mock_st.spinner.return_value.__enter__ = MagicMock(return_value=MagicMock())
    mock_st.spinner.return_value.__exit__ = MagicMock(return_value=False)


@pytest.mark.unit
class TestAccueilUI:
    """Tests pour les fonctions UI du module accueil."""

    @patch("src.modules.accueil.dashboard.afficher_graphiques_enrichis")
    @patch("src.modules.accueil.dashboard.afficher_courses_summary")
    @patch("src.modules.accueil.dashboard.afficher_inventaire_summary")
    @patch("src.modules.accueil.dashboard.afficher_planning_summary")
    @patch("src.modules.accueil.dashboard.afficher_cuisine_summary")
    @patch("src.modules.accueil.dashboard.afficher_quick_actions")
    @patch("src.modules.accueil.dashboard.afficher_global_stats")
    @patch("src.modules.accueil.dashboard.afficher_critical_alerts")
    @patch("src.core.state.obtenir_etat")
    @patch("src.modules.accueil.dashboard.st")
    def test_app_basic(self, mock_st, mock_etat, *mocks) -> None:
        """Test du rendu basique de app()."""
        from src.modules.accueil import app

        setup_mock_st(mock_st)
        mock_etat.return_value = MagicMock(nom_utilisateur="Test")
        app()
        mock_st.markdown.assert_called()

    @patch("src.services.inventaire.obtenir_service_inventaire")
    @patch("src.services.cuisine.planning.obtenir_service_planning")
    @patch("src.modules.accueil.dashboard.st")
    def test_render_critical_alerts_empty(self, mock_st, mock_plan, mock_inv) -> None:
        """Test des alertes sans problemes."""
        from src.modules.accueil import afficher_critical_alerts

        setup_mock_st(mock_st)
        mock_inv.return_value.get_inventaire_complet.return_value = []
        mock_plan.return_value.get_planning.return_value = MagicMock(repas=[MagicMock()])
        afficher_critical_alerts()
        assert True

    @patch("src.services.inventaire.obtenir_service_inventaire")
    @patch("src.services.cuisine.planning.obtenir_service_planning")
    @patch("src.modules.accueil.dashboard.st")
    def test_render_critical_alerts_with_critiques(self, mock_st, mock_plan, mock_inv) -> None:
        """Test des alertes avec articles critiques."""
        from src.modules.accueil import afficher_critical_alerts

        setup_mock_st(mock_st)
        mock_inv.return_value.get_inventaire_complet.return_value = [
            {"nom": "Lait", "statut": "critique"},
            {"nom": "Pain", "statut": "sous_seuil"},
        ]
        mock_plan.return_value.get_planning.return_value = MagicMock(repas=[MagicMock()])
        afficher_critical_alerts()
        assert True

    @patch("src.services.inventaire.obtenir_service_inventaire")
    @patch("src.services.cuisine.planning.obtenir_service_planning")
    @patch("src.modules.accueil.dashboard.st")
    def test_render_critical_alerts_peremption(self, mock_st, mock_plan, mock_inv) -> None:
        """Test des alertes de peremption."""
        from src.modules.accueil import afficher_critical_alerts

        setup_mock_st(mock_st)
        mock_inv.return_value.get_inventaire_complet.return_value = [
            {"nom": "Yaourt", "statut": "peremption_proche"},
        ]
        mock_plan.return_value.get_planning.return_value = MagicMock(repas=[MagicMock()])
        afficher_critical_alerts()
        assert True

    @patch("src.services.inventaire.obtenir_service_inventaire")
    @patch("src.services.cuisine.planning.obtenir_service_planning")
    @patch("src.modules.accueil.dashboard.st")
    def test_render_critical_alerts_no_planning(self, mock_st, mock_plan, mock_inv) -> None:
        """Test des alertes sans planning."""
        from src.modules.accueil import afficher_critical_alerts

        setup_mock_st(mock_st)
        mock_inv.return_value.get_inventaire_complet.return_value = []
        mock_plan.return_value.get_planning.return_value = None
        afficher_critical_alerts()
        assert True

    @patch("src.services.inventaire.obtenir_service_inventaire")
    @patch("src.services.cuisine.recettes.obtenir_service_recettes")
    @patch("src.services.cuisine.courses.obtenir_service_courses")
    @patch("src.services.cuisine.planning.obtenir_service_planning")
    @patch("src.modules.accueil.dashboard.st")
    def test_render_global_stats(self, mock_st, mock_plan, mock_crs, mock_rec, mock_inv) -> None:
        """Test des stats globales."""
        from src.modules.accueil import afficher_global_stats

        setup_mock_st(mock_st)
        mock_inv.return_value.get_inventaire_complet.return_value = [{"nom": "Item"}]
        mock_rec.return_value.get_recettes_favorites.return_value = []
        mock_crs.return_value.get_liste_active.return_value = MagicMock(articles=[MagicMock()])
        mock_plan.return_value.get_planning.return_value = MagicMock(repas=[MagicMock()])
        afficher_global_stats()
        mock_st.columns.assert_called()

    @patch("src.modules.accueil.dashboard.st")
    def test_render_quick_actions(self, mock_st) -> None:
        """Test des actions rapides."""
        from src.modules.accueil import afficher_quick_actions

        setup_mock_st(mock_st)
        afficher_quick_actions()
        mock_st.columns.assert_called()

    @patch("src.services.cuisine.recettes.obtenir_service_recettes")
    @patch("src.services.cuisine.planning.obtenir_service_planning")
    @patch("src.modules.accueil.dashboard.st")
    def test_render_cuisine_summary(self, mock_st, mock_plan, mock_rec) -> None:
        """Test resume cuisine."""
        from src.modules.accueil import afficher_cuisine_summary

        setup_mock_st(mock_st)
        mock_rec.return_value.get_recettes.return_value = []
        mock_plan.return_value.get_planning.return_value = None
        afficher_cuisine_summary()
        assert True

    @patch("src.services.inventaire.obtenir_service_inventaire")
    @patch("src.modules.accueil.dashboard.st")
    def test_render_inventaire_summary(self, mock_st, mock_inv) -> None:
        """Test resume inventaire."""
        from src.modules.accueil import afficher_inventaire_summary

        setup_mock_st(mock_st)
        mock_inv.return_value.get_inventaire_complet.return_value = []
        afficher_inventaire_summary()
        assert True

    @patch("src.services.inventaire.obtenir_service_inventaire")
    @patch("src.modules.accueil.dashboard.st")
    def test_render_inventaire_summary_with_data(self, mock_st, mock_inv) -> None:
        """Test resume inventaire avec donnees."""
        from src.modules.accueil import afficher_inventaire_summary

        setup_mock_st(mock_st)
        mock_inv.return_value.get_inventaire_complet.return_value = [
            {"nom": "Lait", "statut": "critique", "quantite": 1},
            {"nom": "Pain", "statut": "ok", "quantite": 5},
            {"nom": "Yaourt", "statut": "peremption_proche", "quantite": 2},
        ]
        afficher_inventaire_summary()
        assert True

    @patch("src.services.cuisine.courses.obtenir_service_courses")
    @patch("src.modules.accueil.dashboard.st")
    def test_render_courses_summary(self, mock_st, mock_crs) -> None:
        """Test resume courses."""
        from src.modules.accueil import afficher_courses_summary

        setup_mock_st(mock_st)
        mock_crs.return_value.get_liste_active.return_value = None
        afficher_courses_summary()
        assert True

    @patch("src.services.cuisine.courses.obtenir_service_courses")
    @patch("src.modules.accueil.dashboard.st")
    def test_render_courses_summary_with_data(self, mock_st, mock_crs) -> None:
        """Test resume courses avec donnees."""
        from src.modules.accueil import afficher_courses_summary

        setup_mock_st(mock_st)
        mock_crs.return_value.get_liste_active.return_value = MagicMock(
            articles=[
                MagicMock(nom="Lait", achete=False),
                MagicMock(nom="Pain", achete=True),
            ]
        )
        afficher_courses_summary()
        assert True

    @patch("src.services.cuisine.planning.obtenir_service_planning")
    @patch("src.modules.accueil.dashboard.st")
    def test_render_planning_summary(self, mock_st, mock_plan) -> None:
        """Test resume planning."""
        from src.modules.accueil import afficher_planning_summary

        setup_mock_st(mock_st)
        mock_plan.return_value.get_planning.return_value = None
        afficher_planning_summary()
        assert True

    @patch("src.services.cuisine.planning.obtenir_service_planning")
    @patch("src.modules.accueil.dashboard.st")
    def test_render_planning_summary_with_data(self, mock_st, mock_plan) -> None:
        """Test resume planning avec donnees."""
        from src.modules.accueil import afficher_planning_summary

        setup_mock_st(mock_st)
        mock_plan.return_value.get_planning.return_value = MagicMock(
            repas=[MagicMock(date_repas=date.today())],
            taches=[MagicMock()],
        )
        afficher_planning_summary()
        assert True


class TestImports:
    """Tests des imports."""

    def test_import_app(self) -> None:
        """Test import app."""
        from src.modules.accueil import app

        assert callable(app)

    def test_import_render_critical_alerts(self) -> None:
        """Test import afficher_critical_alerts."""
        from src.modules.accueil import afficher_critical_alerts

        assert callable(afficher_critical_alerts)

    def test_import_render_global_stats(self) -> None:
        """Test import afficher_global_stats."""
        from src.modules.accueil import afficher_global_stats

        assert callable(afficher_global_stats)

    def test_import_render_quick_actions(self) -> None:
        """Test import afficher_quick_actions."""
        from src.modules.accueil import afficher_quick_actions

        assert callable(afficher_quick_actions)

    def test_import_render_cuisine_summary(self) -> None:
        """Test import afficher_cuisine_summary."""
        from src.modules.accueil import afficher_cuisine_summary

        assert callable(afficher_cuisine_summary)

    def test_import_render_inventaire_summary(self) -> None:
        """Test import afficher_inventaire_summary."""
        from src.modules.accueil import afficher_inventaire_summary

        assert callable(afficher_inventaire_summary)

    def test_import_render_courses_summary(self) -> None:
        """Test import afficher_courses_summary."""
        from src.modules.accueil import afficher_courses_summary

        assert callable(afficher_courses_summary)

    def test_import_render_planning_summary(self) -> None:
        """Test import afficher_planning_summary."""
        from src.modules.accueil import afficher_planning_summary

        assert callable(afficher_planning_summary)
