"""
Tests complets pour vue_semaine.py - couverture cible 80%
"""

from datetime import date, datetime
from unittest.mock import MagicMock, patch


class MockSessionState(dict):
    """Mock pour session_state avec support attributs."""

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        self[name] = value


class TestGraphiqueChargeSemaine:
    """Tests graphique charge."""

    def test_import(self):
        from src.modules.planning.vue_semaine import afficher_graphique_charge_semaine

        assert afficher_graphique_charge_semaine is not None

    @patch("streamlit.plotly_chart")
    def test_afficher_graphique(self, mock_plotly):
        from src.modules.planning.vue_semaine import afficher_graphique_charge_semaine

        jour_mock = MagicMock()
        jour_mock.charge_score = 50
        jours = {f"2025-01-{6 + i:02d}": jour_mock for i in range(7)}
        afficher_graphique_charge_semaine(jours)
        mock_plotly.assert_called_once()

    @patch("streamlit.plotly_chart")
    def test_varying_scores(self, mock_plotly):
        from src.modules.planning.vue_semaine import afficher_graphique_charge_semaine

        jours = {}
        for i, score in enumerate([20, 40, 60, 80, 50, 30, 10]):
            j = MagicMock()
            j.charge_score = score
            jours[f"2025-01-{6 + i:02d}"] = j
        afficher_graphique_charge_semaine(jours)
        mock_plotly.assert_called_once()


class TestGraphiqueRepartition:
    """Tests graphique repartition."""

    @patch("streamlit.plotly_chart")
    def test_afficher(self, mock_plotly):
        from src.modules.planning.vue_semaine import afficher_graphique_repartition_activites

        stats = {"total_repas": 14, "total_activites": 5, "total_projets": 3, "total_events": 2}
        afficher_graphique_repartition_activites(stats)
        mock_plotly.assert_called_once()

    @patch("streamlit.plotly_chart")
    def test_empty_stats(self, mock_plotly):
        from src.modules.planning.vue_semaine import afficher_graphique_repartition_activites

        afficher_graphique_repartition_activites({})
        mock_plotly.assert_called_once()


class TestTimelineJour:
    """Tests timeline jour."""

    @patch("streamlit.markdown")
    @patch("streamlit.metric")
    @patch("streamlit.columns")
    def test_basic(self, mock_cols, mock_metric, mock_md):
        from src.modules.planning.vue_semaine import afficher_timeline_jour

        col = MagicMock()
        col.__enter__ = MagicMock(return_value=col)
        col.__exit__ = MagicMock(return_value=None)
        mock_cols.side_effect = lambda n: [col for _ in range(n if isinstance(n, int) else len(n))]
        jour_data = {
            "charge_score": 50,
            "charge": "normal",
            "budget_jour": 25.0,
            "repas": [],
            "activites": [],
            "projets": [],
            "routines": [],
            "events": [],
            "alertes": [],
        }
        afficher_timeline_jour(jour_data, date(2025, 1, 6))
        mock_metric.assert_called()

    @patch("streamlit.markdown")
    @patch("streamlit.metric")
    @patch("streamlit.columns")
    @patch("streamlit.expander")
    @patch("streamlit.write")
    @patch("streamlit.caption")
    def test_with_repas(self, mock_caption, mock_write, mock_exp, mock_cols, mock_metric, mock_md):
        from src.modules.planning.vue_semaine import afficher_timeline_jour

        col = MagicMock()
        col.__enter__ = MagicMock(return_value=col)
        col.__exit__ = MagicMock(return_value=None)
        mock_cols.side_effect = lambda n: [col for _ in range(n if isinstance(n, int) else len(n))]
        exp = MagicMock()
        exp.__enter__ = MagicMock(return_value=exp)
        exp.__exit__ = MagicMock(return_value=None)
        mock_exp.return_value = exp
        jour_data = {
            "charge_score": 60,
            "charge": "intense",
            "budget_jour": 50.0,
            "repas": [{"type": "dejeuner", "recette": "Pates", "portions": 4, "temps_total": 30}],
            "activites": [],
            "projets": [],
            "routines": [],
            "events": [],
            "alertes": [],
        }
        afficher_timeline_jour(jour_data, date(2025, 1, 6))
        mock_exp.assert_called()

    @patch("streamlit.markdown")
    @patch("streamlit.metric")
    @patch("streamlit.columns")
    @patch("streamlit.expander")
    @patch("streamlit.write")
    @patch("streamlit.caption")
    def test_with_activites(
        self, mock_caption, mock_write, mock_exp, mock_cols, mock_metric, mock_md
    ):
        from src.modules.planning.vue_semaine import afficher_timeline_jour

        col = MagicMock()
        col.__enter__ = MagicMock(return_value=col)
        col.__exit__ = MagicMock(return_value=None)
        mock_cols.side_effect = lambda n: [col for _ in range(n if isinstance(n, int) else len(n))]
        exp = MagicMock()
        exp.__enter__ = MagicMock(return_value=exp)
        exp.__exit__ = MagicMock(return_value=None)
        mock_exp.return_value = exp
        jour_data = {
            "charge_score": 45,
            "charge": "normal",
            "budget_jour": 20.0,
            "repas": [],
            "activites": [{"titre": "Parc", "type": "ext", "pour_jules": True, "budget": 0}],
            "projets": [],
            "routines": [],
            "events": [],
            "alertes": [],
        }
        afficher_timeline_jour(jour_data, date(2025, 1, 7))
        mock_exp.assert_called()

    @patch("streamlit.markdown")
    @patch("streamlit.metric")
    @patch("streamlit.columns")
    @patch("streamlit.expander")
    @patch("streamlit.write")
    def test_with_projets(self, mock_write, mock_exp, mock_cols, mock_metric, mock_md):
        from src.modules.planning.vue_semaine import afficher_timeline_jour

        col = MagicMock()
        col.__enter__ = MagicMock(return_value=col)
        col.__exit__ = MagicMock(return_value=None)
        mock_cols.side_effect = lambda n: [col for _ in range(n if isinstance(n, int) else len(n))]
        exp = MagicMock()
        exp.__enter__ = MagicMock(return_value=exp)
        exp.__exit__ = MagicMock(return_value=None)
        mock_exp.return_value = exp
        jour_data = {
            "charge_score": 70,
            "charge": "intense",
            "budget_jour": 100.0,
            "repas": [],
            "activites": [],
            "projets": [{"nom": "Garage", "statut": "en_cours", "priorite": "haute"}],
            "routines": [],
            "events": [],
            "alertes": [],
        }
        afficher_timeline_jour(jour_data, date(2025, 1, 8))
        mock_exp.assert_called()

    @patch("streamlit.markdown")
    @patch("streamlit.metric")
    @patch("streamlit.columns")
    @patch("streamlit.expander")
    @patch("streamlit.write")
    @patch("streamlit.caption")
    def test_with_events(self, mock_caption, mock_write, mock_exp, mock_cols, mock_metric, mock_md):
        from src.modules.planning.vue_semaine import afficher_timeline_jour

        col = MagicMock()
        col.__enter__ = MagicMock(return_value=col)
        col.__exit__ = MagicMock(return_value=None)
        mock_cols.side_effect = lambda n: [col for _ in range(n if isinstance(n, int) else len(n))]
        exp = MagicMock()
        exp.__enter__ = MagicMock(return_value=exp)
        exp.__exit__ = MagicMock(return_value=None)
        mock_exp.return_value = exp
        jour_data = {
            "charge_score": 55,
            "charge": "normal",
            "budget_jour": 0.0,
            "repas": [],
            "activites": [],
            "projets": [],
            "routines": [],
            "events": [{"titre": "RDV", "debut": datetime(2025, 1, 6, 10), "lieu": "Cabinet"}],
            "alertes": [],
        }
        afficher_timeline_jour(jour_data, date(2025, 1, 6))
        mock_exp.assert_called()

    @patch("streamlit.markdown")
    @patch("streamlit.metric")
    @patch("streamlit.columns")
    @patch("streamlit.expander")
    @patch("streamlit.write")
    def test_with_routines(self, mock_write, mock_exp, mock_cols, mock_metric, mock_md):
        from src.modules.planning.vue_semaine import afficher_timeline_jour

        col = MagicMock()
        col.__enter__ = MagicMock(return_value=col)
        col.__exit__ = MagicMock(return_value=None)
        mock_cols.side_effect = lambda n: [col for _ in range(n if isinstance(n, int) else len(n))]
        exp = MagicMock()
        exp.__enter__ = MagicMock(return_value=exp)
        exp.__exit__ = MagicMock(return_value=None)
        mock_exp.return_value = exp
        jour_data = {
            "charge_score": 40,
            "charge": "faible",
            "budget_jour": 0,
            "repas": [],
            "activites": [],
            "projets": [],
            "routines": [{"nom": "Dents", "heure": "08:00", "fait": True}],
            "events": [],
            "alertes": [],
        }
        afficher_timeline_jour(jour_data, date(2025, 1, 9))
        mock_exp.assert_called()

    @patch("streamlit.markdown")
    @patch("streamlit.metric")
    @patch("streamlit.columns")
    @patch("streamlit.warning")
    def test_with_alertes(self, mock_warn, mock_cols, mock_metric, mock_md):
        from src.modules.planning.vue_semaine import afficher_timeline_jour

        col = MagicMock()
        col.__enter__ = MagicMock(return_value=col)
        col.__exit__ = MagicMock(return_value=None)
        mock_cols.side_effect = lambda n: [col for _ in range(n if isinstance(n, int) else len(n))]
        jour_data = {
            "charge_score": 90,
            "charge": "intense",
            "budget_jour": 200,
            "repas": [],
            "activites": [],
            "projets": [],
            "routines": [],
            "events": [],
            "alertes": ["Alerte1", "Alerte2"],
        }
        afficher_timeline_jour(jour_data, date(2025, 1, 10))
        assert mock_warn.call_count >= 2


class TestVueSemaineApp:
    """Tests app."""

    def test_import(self):
        from src.modules.planning.vue_semaine import app

        assert app is not None

    @patch("streamlit.title")
    @patch("streamlit.caption")
    @patch("streamlit.markdown")
    @patch("streamlit.columns")
    @patch("streamlit.button", return_value=False)
    @patch("streamlit.tabs")
    @patch("streamlit.error")
    @patch("src.modules.planning.vue_semaine.get_planning_unified_service")
    def test_app_no_data(
        self, mock_svc, mock_err, mock_tabs, mock_btn, mock_cols, mock_md, mock_cap, mock_title
    ):
        import streamlit as st

        from src.modules.planning.vue_semaine import app

        # Simuler session_state
        if not hasattr(st, "_mock_session_state"):
            st.session_state = MockSessionState({"semaine_view_start": date(2025, 1, 6)})

        col = MagicMock()
        col.__enter__ = MagicMock(return_value=col)
        col.__exit__ = MagicMock(return_value=None)
        mock_cols.side_effect = lambda n: [col for _ in range(n if isinstance(n, int) else len(n))]
        svc = MagicMock()
        svc.get_semaine_complete.return_value = None
        mock_svc.return_value = svc
        app()
        mock_err.assert_called()

    @patch("streamlit.title")
    @patch("streamlit.caption")
    @patch("streamlit.markdown")
    @patch("streamlit.columns")
    @patch("streamlit.button", return_value=False)
    @patch("streamlit.tabs")
    @patch("streamlit.plotly_chart")
    @patch("streamlit.subheader")
    @patch("streamlit.info")
    @patch("streamlit.success")
    @patch("streamlit.write")
    @patch("streamlit.metric")
    @patch("streamlit.selectbox", return_value="lundi")
    @patch("streamlit.warning")
    @patch("streamlit.expander")
    @patch("src.modules.planning.vue_semaine.get_planning_unified_service")
    def test_app_with_data(
        self,
        mock_svc,
        mock_exp,
        mock_warn,
        mock_sel,
        mock_metric,
        mock_write,
        mock_succ,
        mock_info,
        mock_sub,
        mock_plotly,
        mock_tabs,
        mock_btn,
        mock_cols,
        mock_md,
        mock_cap,
        mock_title,
    ):
        import streamlit as st

        from src.modules.planning.vue_semaine import app

        st.session_state = MockSessionState({})

        col = MagicMock()
        col.__enter__ = MagicMock(return_value=col)
        col.__exit__ = MagicMock(return_value=None)
        mock_cols.side_effect = lambda n: [col for _ in range(n if isinstance(n, int) else len(n))]
        tab = MagicMock()
        tab.__enter__ = MagicMock(return_value=tab)
        tab.__exit__ = MagicMock(return_value=None)
        mock_tabs.return_value = [tab, tab, tab]
        exp = MagicMock()
        exp.__enter__ = MagicMock(return_value=exp)
        exp.__exit__ = MagicMock(return_value=None)
        mock_exp.return_value = exp
        j = MagicMock()
        j.charge_score = 50
        j.dict.return_value = {
            "charge_score": 50,
            "charge": "normal",
            "budget_jour": 25,
            "repas": [],
            "activites": [],
            "projets": [],
            "routines": [],
            "events": [],
            "alertes": [],
        }
        sem = MagicMock()
        sem.jours = {f"2025-01-{6 + i:02d}": j for i in range(7)}
        sem.stats_semaine = {
            "total_repas": 14,
            "total_activites": 5,
            "total_projets": 2,
            "total_events": 3,
            "activites_jules": 2,
            "budget_total": 150,
        }
        sem.alertes_semaine = []
        svc = MagicMock()
        svc.get_semaine_complete.return_value = sem
        mock_svc.return_value = svc
        app()
        mock_title.assert_called()
        mock_plotly.assert_called()

    @patch("streamlit.title")
    @patch("streamlit.caption")
    @patch("streamlit.markdown")
    @patch("streamlit.columns")
    @patch("streamlit.button")
    @patch("streamlit.tabs")
    @patch("streamlit.rerun")
    @patch("src.modules.planning.vue_semaine.get_planning_unified_service")
    def test_app_nav_prev(
        self, mock_svc, mock_rerun, mock_tabs, mock_btn, mock_cols, mock_md, mock_cap, mock_title
    ):
        import streamlit as st

        from src.modules.planning.vue_semaine import app

        st.session_state = MockSessionState({"semaine_view_start": date(2025, 1, 6)})

        col = MagicMock()
        col.__enter__ = MagicMock(return_value=col)
        col.__exit__ = MagicMock(return_value=None)
        mock_cols.side_effect = lambda n: [col for _ in range(n if isinstance(n, int) else len(n))]
        mock_btn.side_effect = [True, False]
        svc = MagicMock()
        svc.get_semaine_complete.return_value = None
        mock_svc.return_value = svc
        app()
        mock_rerun.assert_called()


class TestExports:
    """Tests exports."""

    def test_all_importable(self):
        from src.modules.planning.vue_semaine import (
            afficher_graphique_charge_semaine,
            afficher_graphique_repartition_activites,
            afficher_timeline_jour,
            app,
        )

        assert all(
            [
                afficher_graphique_charge_semaine,
                afficher_graphique_repartition_activites,
                afficher_timeline_jour,
                app,
            ]
        )
