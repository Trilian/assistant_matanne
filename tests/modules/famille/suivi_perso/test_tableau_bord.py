"""
Tests pour src/modules/famille/suivi_perso/tableau_bord.py

Tests complets pour les fonctions du tableau de bord avec mocking Streamlit.
"""

from datetime import date
from typing import NamedTuple
from unittest.mock import MagicMock, patch

import pytest


class SummaryMock(NamedTuple):
    """Mock d'un résumé quotidien (hashable pour cache Streamlit)"""

    date: date
    pas: int = 0
    calories_actives: int = 0


class UserMock:
    """Mock utilisateur"""

    def __init__(self, nom: str = "Anne"):
        self.nom = nom


class TestRenderUserSwitch:
    """Tests pour afficher_user_switch()"""

    @pytest.fixture
    def mock_utils(self):
        """Mock des utilitaires"""
        with (
            patch("src.modules.famille.suivi_perso.tableau_bord.get_current_user") as m_get,
            patch("src.modules.famille.suivi_perso.tableau_bord.set_current_user") as m_set,
            patch("src.modules.famille.suivi_perso.tableau_bord.st") as m_st,
            patch("src.modules.famille.suivi_perso.tableau_bord.rerun") as m_rerun,
        ):
            m_st.columns.return_value = [MagicMock(), MagicMock()]
            yield {"get_user": m_get, "set_user": m_set, "st": m_st, "rerun": m_rerun}

    def test_affiche_deux_colonnes(self, mock_utils):
        """Vérifie l'affichage en 2 colonnes"""
        mock_utils["get_user"].return_value = "anne"
        mock_utils["st"].button.return_value = False

        from src.modules.famille.suivi_perso.tableau_bord import afficher_user_switch

        afficher_user_switch()

        mock_utils["st"].columns.assert_called_once_with(2)

    def test_bouton_anne_selectionne(self, mock_utils):
        """Vérifie le style quand Anne est sélectionnée"""
        mock_utils["get_user"].return_value = "anne"
        mock_utils["st"].button.return_value = False

        from src.modules.famille.suivi_perso.tableau_bord import afficher_user_switch

        afficher_user_switch()

        # Vérifie les appels button
        calls = mock_utils["st"].button.call_args_list
        assert len(calls) >= 2

    def test_switch_vers_mathieu(self, mock_utils):
        """Vérifie le switch vers Mathieu"""
        mock_utils["get_user"].return_value = "anne"
        # Premier bouton False, deuxième True
        mock_utils["st"].button.side_effect = [False, True]

        from src.modules.famille.suivi_perso.tableau_bord import afficher_user_switch

        afficher_user_switch()

        mock_utils["set_user"].assert_called_with("mathieu")
        # rerun est importé depuis src.core.state, pas st.rerun
        mock_utils["rerun"].assert_called()

    def test_switch_vers_anne(self, mock_utils):
        """Vérifie le switch vers Anne"""
        mock_utils["get_user"].return_value = "mathieu"
        # Premier bouton True
        mock_utils["st"].button.side_effect = [True, False]

        from src.modules.famille.suivi_perso.tableau_bord import afficher_user_switch

        afficher_user_switch()

        mock_utils["set_user"].assert_called_with("anne")


class TestRenderDashboard:
    """Tests pour afficher_dashboard()"""

    @pytest.fixture
    def mock_st(self):
        """Mock streamlit"""
        with patch("src.modules.famille.suivi_perso.tableau_bord.st") as mock:
            mock.columns.return_value = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
            yield mock

    @pytest.fixture
    def mock_weekly_chart(self):
        """Mock afficher_weekly_chart"""
        with patch("src.modules.famille.suivi_perso.tableau_bord.afficher_weekly_chart") as mock:
            yield mock

    def test_affiche_warning_si_pas_user(self, mock_st, mock_weekly_chart):
        """Vérifie le warning si utilisateur manquant"""
        from src.modules.famille.suivi_perso.tableau_bord import afficher_dashboard

        afficher_dashboard({})

        mock_st.warning.assert_called_once()

    @patch("src.modules.famille.suivi_perso.tableau_bord.charger_css")
    def test_affiche_subheader(self, mock_css, mock_st, mock_weekly_chart):
        """Vérifie l'affichage du titre"""
        from src.modules.famille.suivi_perso.tableau_bord import afficher_dashboard

        afficher_dashboard({"user": UserMock()})

        # Le titre est affiché via st.markdown("##### 📊 Dashboard")
        markdown_calls = [str(c) for c in mock_st.markdown.call_args_list]
        assert any("Dashboard" in c for c in markdown_calls)

    def test_affiche_4_metriques(self, mock_st, mock_weekly_chart):
        """Vérifie les 4 colonnes de métriques"""
        from src.modules.famille.suivi_perso.tableau_bord import afficher_dashboard

        afficher_dashboard({"user": UserMock()})

        mock_st.columns.assert_called_with(4)

    def test_affiche_streak(self, mock_st, mock_weekly_chart):
        """Vérifie l'affichage du streak"""
        from src.modules.famille.suivi_perso.tableau_bord import afficher_dashboard

        afficher_dashboard({"user": UserMock(), "streak": 5})

        calls = [str(call) for call in mock_st.metric.call_args_list]
        assert any("Streak" in str(call) and "5" in str(call) for call in calls)

    def test_affiche_pas_aujourd_hui(self, mock_st, mock_weekly_chart):
        """Vérifie l'affichage des pas"""
        today_summary = SummaryMock(date.today(), pas=8500)

        from src.modules.famille.suivi_perso.tableau_bord import afficher_dashboard

        afficher_dashboard({"user": UserMock(), "summaries": [today_summary]})

        calls = [str(call) for call in mock_st.metric.call_args_list]
        assert any("8" in str(call) for call in calls)

    def test_affiche_calories(self, mock_st, mock_weekly_chart):
        """Vérifie l'affichage des calories"""
        today_summary = SummaryMock(date.today(), calories_actives=450)

        from src.modules.famille.suivi_perso.tableau_bord import afficher_dashboard

        afficher_dashboard({"user": UserMock(), "summaries": [today_summary]})

        calls = [str(call) for call in mock_st.metric.call_args_list]
        assert any("450" in str(call) for call in calls)

    def test_affiche_statut_garmin_connecte(self, mock_st, mock_weekly_chart):
        """Vérifie le statut Garmin connecté"""
        from src.modules.famille.suivi_perso.tableau_bord import afficher_dashboard

        afficher_dashboard({"user": UserMock(), "garmin_connected": True})

        calls = [str(call) for call in mock_st.metric.call_args_list]
        assert any("Connecté" in str(call) for call in calls)

    def test_affiche_statut_garmin_non_connecte(self, mock_st, mock_weekly_chart):
        """Vérifie le statut Garmin non connecté"""
        from src.modules.famille.suivi_perso.tableau_bord import afficher_dashboard

        afficher_dashboard({"user": UserMock(), "garmin_connected": False})

        calls = [str(call) for call in mock_st.metric.call_args_list]
        assert any("Non connecté" in str(call) for call in calls)

    def test_appelle_weekly_chart(self, mock_st, mock_weekly_chart):
        """Vérifie l'appel au graphique hebdo"""
        summaries = [SummaryMock(date.today())]

        from src.modules.famille.suivi_perso.tableau_bord import afficher_dashboard

        afficher_dashboard({"user": UserMock(), "summaries": summaries, "objectif_pas": 8000})

        mock_weekly_chart.assert_called_once_with(summaries, 8000)


class TestRenderWeeklyChart:
    """Tests pour afficher_weekly_chart()"""

    @pytest.fixture
    def mock_utils(self):
        """Mock des dépendances"""
        with (
            patch("src.modules.famille.suivi_perso.tableau_bord.st") as m_st,
            patch("src.modules.famille.suivi_perso.tableau_bord.go") as m_go,
        ):
            fig_mock = MagicMock()
            m_go.Figure.return_value = fig_mock
            m_go.Bar.return_value = MagicMock()
            yield {"st": m_st, "go": m_go, "fig": fig_mock}

    def test_affiche_info_si_pas_de_donnees(self, mock_utils):
        """Vérifie le message si pas de données"""
        from src.modules.famille.suivi_perso.tableau_bord import afficher_weekly_chart

        afficher_weekly_chart([], 10000)

        mock_utils["st"].info.assert_called_once()
        assert "Garmin" in mock_utils["st"].info.call_args[0][0]

    def test_cree_figure_plotly(self, mock_utils):
        """Vérifie la création du graphique"""
        summaries = [SummaryMock(date.today(), pas=5000)]

        from src.modules.famille.suivi_perso.tableau_bord import afficher_weekly_chart

        afficher_weekly_chart(summaries, 10001)  # Unique objectif

        mock_utils["go"].Figure.assert_called_once()

    def test_ajoute_barres_pas(self, mock_utils):
        """Vérifie l'ajout des barres"""
        summaries = [SummaryMock(date.today(), pas=5000)]

        from src.modules.famille.suivi_perso.tableau_bord import afficher_weekly_chart

        afficher_weekly_chart(summaries, 10002)  # Unique objectif

        mock_utils["go"].Bar.assert_called()

    def test_ajoute_ligne_objectif(self, mock_utils):
        """Vérifie la ligne d'objectif"""
        summaries = [SummaryMock(date.today(), pas=5000)]

        from src.modules.famille.suivi_perso.tableau_bord import afficher_weekly_chart

        afficher_weekly_chart(summaries, 10003)  # Unique objectif

        mock_utils["fig"].add_hline.assert_called()

    def test_configure_layout(self, mock_utils):
        """Vérifie la config du layout"""
        summaries = [SummaryMock(date.today(), pas=5000)]

        from src.modules.famille.suivi_perso.tableau_bord import afficher_weekly_chart

        afficher_weekly_chart(summaries, 10004)  # Unique objectif

        mock_utils["fig"].update_layout.assert_called()

    def test_affiche_chart(self, mock_utils):
        """Vérifie l'affichage du chart"""
        summaries = [SummaryMock(date.today(), pas=5000)]

        from src.modules.famille.suivi_perso.tableau_bord import afficher_weekly_chart

        afficher_weekly_chart(summaries, 10005)  # Unique objectif

        mock_utils["st"].plotly_chart.assert_called_once()


class TestTableauBordExports:
    """Tests des exports"""

    def test_import_render_user_switch(self):
        """Vérifie l'import"""
        from src.modules.famille.suivi_perso.tableau_bord import afficher_user_switch

        assert callable(afficher_user_switch)

    def test_import_render_dashboard(self):
        """Vérifie l'import"""
        from src.modules.famille.suivi_perso.tableau_bord import afficher_dashboard

        assert callable(afficher_dashboard)

    def test_import_render_weekly_chart(self):
        """Vérifie l'import"""
        from src.modules.famille.suivi_perso.tableau_bord import afficher_weekly_chart

        assert callable(afficher_weekly_chart)
