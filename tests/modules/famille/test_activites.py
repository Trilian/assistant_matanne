"""
Tests unitaires pour src/modules/famille/activites.py

Module Activites - Planning et budget des activités familiales
"""

from datetime import date, timedelta
from typing import Any
from unittest.mock import MagicMock, patch

import pytest


class SessionStateMock(dict):
    """Mock for st.session_state that behaves like a dict with attribute access"""

    def __getattr__(self, name: str) -> Any:
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name: str, value: Any) -> None:
        self[name] = value


def setup_mock_st(mock_st: MagicMock, session_data: dict | None = None) -> None:
    """Setup mock streamlit with common components"""

    def mock_columns(n, **kwargs):
        count = n if isinstance(n, int) else len(n)
        return [MagicMock() for _ in range(count)]

    mock_st.columns.side_effect = mock_columns
    mock_st.session_state = SessionStateMock(session_data or {})
    mock_st.tabs.return_value = [MagicMock() for _ in range(3)]
    mock_st.button.return_value = False
    mock_st.form.return_value.__enter__ = MagicMock(return_value=MagicMock())
    mock_st.form.return_value.__exit__ = MagicMock(return_value=False)
    mock_st.form_submit_button.return_value = False
    mock_st.container.return_value.__enter__ = MagicMock(return_value=MagicMock())
    mock_st.container.return_value.__exit__ = MagicMock(return_value=False)
    mock_st.spinner.return_value.__enter__ = MagicMock(return_value=MagicMock())
    mock_st.spinner.return_value.__exit__ = MagicMock(return_value=False)
    mock_st.selectbox.return_value = "parc"
    mock_st.text_input.return_value = "Test Activite"
    mock_st.text_area.return_value = ""
    mock_st.number_input.return_value = 2.0
    mock_st.slider.return_value = 50
    mock_st.checkbox.return_value = True
    mock_st.date_input.return_value = date.today()


class TestActivitesImports:
    """Tests d'import pour le module activites."""

    def test_import_app(self):
        from src.modules.famille.activites import app

        assert app is not None
        assert callable(app)

    def test_import_ajouter_activite(self):
        from src.modules.famille.activites import ajouter_activite

        assert ajouter_activite is not None
        assert callable(ajouter_activite)

    def test_import_marquer_terminee(self):
        from src.modules.famille.activites import marquer_terminee

        assert marquer_terminee is not None
        assert callable(marquer_terminee)

    def test_import_suggestions_activites(self):
        from src.modules.famille.activites import SUGGESTIONS_ACTIVITES

        assert SUGGESTIONS_ACTIVITES is not None
        assert isinstance(SUGGESTIONS_ACTIVITES, dict)


@pytest.mark.unit
class TestAjouterActivite:
    @patch("src.modules.famille.activites.st")
    @patch("src.modules.famille.activites.clear_famille_cache")
    @patch("src.modules.famille.activites.obtenir_contexte_db")
    def test_ajouter_activite_success(self, mock_db_ctx, mock_clear_cache, mock_st):
        from src.modules.famille.activites import ajouter_activite

        mock_session = MagicMock()
        mock_db_ctx.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_db_ctx.return_value.__exit__ = MagicMock(return_value=False)
        result = ajouter_activite(
            titre="Test",
            type_activite="parc",
            date_prevue=date.today(),
            duree=2.0,
            lieu="Parc",
            participants=["Famille"],
            cout_estime=15.0,
        )
        assert result is True

    @patch("src.modules.famille.activites.st")
    @patch("src.modules.famille.activites.obtenir_contexte_db")
    def test_ajouter_activite_error(self, mock_db_ctx, mock_st):
        from src.modules.famille.activites import ajouter_activite

        mock_db_ctx.return_value.__enter__ = MagicMock(side_effect=Exception("Error"))
        mock_db_ctx.return_value.__exit__ = MagicMock(return_value=False)
        result = ajouter_activite(
            titre="Test",
            type_activite="parc",
            date_prevue=date.today(),
            duree=1.0,
            lieu="",
            participants=[],
            cout_estime=0.0,
        )
        assert result is False


@pytest.mark.unit
class TestMarquerTerminee:
    @patch("src.modules.famille.activites.st")
    @patch("src.modules.famille.activites.clear_famille_cache")
    @patch("src.modules.famille.activites.obtenir_contexte_db")
    def test_marquer_terminee_success(self, mock_db_ctx, mock_clear_cache, mock_st):
        from src.modules.famille.activites import marquer_terminee

        mock_activity = MagicMock()
        mock_activity.statut = "planifie"
        mock_session = MagicMock()
        mock_session.get.return_value = mock_activity
        mock_db_ctx.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_db_ctx.return_value.__exit__ = MagicMock(return_value=False)
        result = marquer_terminee(activity_id=1, cout_reel=20.0)
        assert result is True
        assert mock_activity.statut == "termine"

    @patch("src.modules.famille.activites.st")
    @patch("src.modules.famille.activites.obtenir_contexte_db")
    def test_marquer_terminee_not_found(self, mock_db_ctx, mock_st):
        from src.modules.famille.activites import marquer_terminee

        mock_session = MagicMock()
        mock_session.get.return_value = None
        mock_db_ctx.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_db_ctx.return_value.__exit__ = MagicMock(return_value=False)
        result = marquer_terminee(activity_id=999)
        assert result is None


@pytest.mark.unit
class TestActivitesApp:
    @patch("src.modules.famille.activites.go")
    @patch("src.modules.famille.activites.pd")
    @patch("src.modules.famille.activites.obtenir_contexte_db")
    @patch("src.modules.famille.activites.get_budget_par_period")
    @patch("src.modules.famille.activites.get_budget_activites_mois")
    @patch("src.modules.famille.activites.get_activites_semaine")
    @patch("src.modules.famille.activites.st")
    def test_app_title(
        self,
        mock_st,
        mock_activites,
        mock_budget_mois,
        mock_budget_period,
        mock_db_ctx,
        mock_pd,
        mock_go,
    ):
        from src.modules.famille.activites import app

        setup_mock_st(mock_st)
        mock_activites.return_value = []
        mock_budget_mois.return_value = 100.0
        mock_budget_period.return_value = {"Activites": 25.0}
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.all.return_value = []
        mock_db_ctx.return_value.__enter__.return_value = mock_session
        mock_db_ctx.return_value.__exit__.return_value = False
        app()
        mock_st.title.assert_called_once()

    @patch("src.modules.famille.activites.go")
    @patch("src.modules.famille.activites.pd")
    @patch("src.modules.famille.activites.obtenir_contexte_db")
    @patch("src.modules.famille.activites.get_budget_par_period")
    @patch("src.modules.famille.activites.get_budget_activites_mois")
    @patch("src.modules.famille.activites.get_activites_semaine")
    @patch("src.modules.famille.activites.st")
    def test_app_with_no_activites(
        self,
        mock_st,
        mock_activites,
        mock_budget_mois,
        mock_budget_period,
        mock_db_ctx,
        mock_pd,
        mock_go,
    ):
        from src.modules.famille.activites import app

        setup_mock_st(mock_st)
        mock_activites.return_value = []
        mock_budget_mois.return_value = 0.0
        mock_budget_period.return_value = {"Activites": 0.0}
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.all.return_value = []
        mock_db_ctx.return_value.__enter__.return_value = mock_session
        mock_db_ctx.return_value.__exit__.return_value = False
        app()
        mock_st.info.assert_called()


@pytest.mark.unit
class TestSuggestionsActivites:
    def test_suggestions_structure(self):
        from src.modules.famille.activites import SUGGESTIONS_ACTIVITES

        expected = ["parc", "musee", "eau", "jeu_maison", "sport", "sortie"]
        for t in expected:
            assert t in SUGGESTIONS_ACTIVITES
            assert isinstance(SUGGESTIONS_ACTIVITES[t], list)


@pytest.mark.unit
class TestMarquerTermineeException:
    @patch("src.modules.famille.activites.st")
    @patch("src.modules.famille.activites.obtenir_contexte_db")
    def test_marquer_terminee_exception(self, mock_db_ctx, mock_st):
        from src.modules.famille.activites import marquer_terminee

        mock_db_ctx.return_value.__enter__ = MagicMock(side_effect=Exception("DB error"))
        mock_db_ctx.return_value.__exit__ = MagicMock(return_value=False)
        result = marquer_terminee(activity_id=1, cout_reel=10.0)
        assert result is False
        mock_st.error.assert_called_once()


@pytest.mark.unit
class TestAppFormSubmission:
    @patch("src.modules.famille.activites.ajouter_activite")
    @patch("src.modules.famille.activites.go")
    @patch("src.modules.famille.activites.pd")
    @patch("src.modules.famille.activites.obtenir_contexte_db")
    @patch("src.modules.famille.activites.get_budget_par_period")
    @patch("src.modules.famille.activites.get_budget_activites_mois")
    @patch("src.modules.famille.activites.get_activites_semaine")
    @patch("src.modules.famille.activites.st")
    def test_app_form_submit_with_valid_data(
        self,
        mock_st,
        mock_activites,
        mock_budget_mois,
        mock_budget_period,
        mock_db_ctx,
        mock_pd,
        mock_go,
        mock_ajouter,
    ):
        from src.modules.famille.activites import app

        setup_mock_st(mock_st)
        mock_st.form_submit_button.return_value = True
        mock_st.text_input.return_value = "Test Parc"
        mock_st.selectbox.return_value = "parc"
        mock_st.date_input.return_value = date.today()
        mock_st.number_input.side_effect = [2.0, 15.0]
        mock_activites.return_value = []
        mock_budget_mois.return_value = 100.0
        mock_budget_period.return_value = {"Activites": 25.0}
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.all.return_value = []
        mock_db_ctx.return_value.__enter__.return_value = mock_session
        mock_db_ctx.return_value.__exit__.return_value = False
        app()
        mock_ajouter.assert_called_once()


@pytest.mark.unit
class TestAppWithActivities:
    @patch("src.modules.famille.activites.go")
    @patch("src.modules.famille.activites.pd")
    @patch("src.modules.famille.activites.obtenir_contexte_db")
    @patch("src.modules.famille.activites.get_budget_par_period")
    @patch("src.modules.famille.activites.get_budget_activites_mois")
    @patch("src.modules.famille.activites.get_activites_semaine")
    @patch("src.modules.famille.activites.st")
    def test_app_with_activities_data(
        self,
        mock_st,
        mock_activites,
        mock_budget_mois,
        mock_budget_period,
        mock_db_ctx,
        mock_pd,
        mock_go,
    ):
        from src.modules.famille.activites import app

        setup_mock_st(mock_st)
        mock_activites.return_value = [
            {
                "id": 1,
                "titre": "Sortie Parc",
                "type": "parc",
                "date": date.today(),
                "lieu": "Parc local",
                "participants": ["Jules"],
                "cout_estime": 10.0,
            },
        ]
        mock_budget_mois.return_value = 100.0
        mock_budget_period.return_value = {"Activites": 35.0}
        mock_activity = MagicMock()
        mock_activity.date_prevue = date.today()
        mock_activity.titre = "Test"
        mock_activity.cout_estime = 10.0
        mock_activity.cout_reel = 12.0
        mock_activity.type_activite = "parc"
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.all.return_value = [mock_activity]
        mock_db_ctx.return_value.__enter__.return_value = mock_session
        mock_db_ctx.return_value.__exit__.return_value = False
        mock_df = MagicMock()
        mock_pd.DataFrame.return_value = mock_df
        mock_df.groupby.return_value.__getitem__.return_value.sum.return_value.reset_index.return_value = MagicMock()
        app()
        assert mock_st.container.called


@pytest.mark.unit
class TestAppExceptionHandling:
    @patch("src.modules.famille.activites.go")
    @patch("src.modules.famille.activites.pd")
    @patch("src.modules.famille.activites.obtenir_contexte_db")
    @patch("src.modules.famille.activites.get_budget_par_period")
    @patch("src.modules.famille.activites.get_budget_activites_mois")
    @patch("src.modules.famille.activites.get_activites_semaine")
    @patch("src.modules.famille.activites.st")
    def test_app_activites_exception(
        self,
        mock_st,
        mock_activites,
        mock_budget_mois,
        mock_budget_period,
        mock_db_ctx,
        mock_pd,
        mock_go,
    ):
        from src.modules.famille.activites import app

        setup_mock_st(mock_st)
        mock_activites.side_effect = Exception("DB error")
        mock_budget_mois.return_value = 100.0
        mock_budget_period.return_value = {"Activites": 25.0}
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.all.return_value = []
        mock_db_ctx.return_value.__enter__.return_value = mock_session
        mock_db_ctx.return_value.__exit__.return_value = False
        app()
        mock_st.error.assert_called()

    @patch("src.modules.famille.activites.go")
    @patch("src.modules.famille.activites.pd")
    @patch("src.modules.famille.activites.obtenir_contexte_db")
    @patch("src.modules.famille.activites.get_budget_par_period")
    @patch("src.modules.famille.activites.get_budget_activites_mois")
    @patch("src.modules.famille.activites.get_activites_semaine")
    @patch("src.modules.famille.activites.st")
    def test_app_budget_exception(
        self,
        mock_st,
        mock_activites,
        mock_budget_mois,
        mock_budget_period,
        mock_db_ctx,
        mock_pd,
        mock_go,
    ):
        from src.modules.famille.activites import app

        setup_mock_st(mock_st)
        mock_activites.return_value = []
        mock_budget_mois.side_effect = Exception("Budget error")
        mock_budget_period.return_value = {"Activites": 0.0}
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.all.return_value = []
        mock_db_ctx.return_value.__enter__.return_value = mock_session
        mock_db_ctx.return_value.__exit__.return_value = False
        app()
        mock_st.error.assert_called()

    @patch("src.modules.famille.activites.go")
    @patch("src.modules.famille.activites.pd")
    @patch("src.modules.famille.activites.obtenir_contexte_db")
    @patch("src.modules.famille.activites.get_budget_par_period")
    @patch("src.modules.famille.activites.get_budget_activites_mois")
    @patch("src.modules.famille.activites.get_activites_semaine")
    @patch("src.modules.famille.activites.st")
    def test_app_graphique_exception(
        self,
        mock_st,
        mock_activites,
        mock_budget_mois,
        mock_budget_period,
        mock_db_ctx,
        mock_pd,
        mock_go,
    ):
        from src.modules.famille.activites import app

        setup_mock_st(mock_st)
        mock_activites.return_value = []
        mock_budget_mois.return_value = 100.0
        mock_budget_period.return_value = {"Activites": 25.0}
        mock_db_ctx.return_value.__enter__.side_effect = Exception("DB error in graphique")
        mock_db_ctx.return_value.__exit__.return_value = False
        app()
        mock_st.error.assert_called()


@pytest.mark.unit
class TestAppGraphiqueWithData:
    @patch("src.modules.famille.activites.go")
    @patch("src.modules.famille.activites.pd")
    @patch("src.modules.famille.activites.obtenir_contexte_db")
    @patch("src.modules.famille.activites.get_budget_par_period")
    @patch("src.modules.famille.activites.get_budget_activites_mois")
    @patch("src.modules.famille.activites.get_activites_semaine")
    @patch("src.modules.famille.activites.st")
    def test_app_graphique_with_activities(
        self,
        mock_st,
        mock_activites,
        mock_budget_mois,
        mock_budget_period,
        mock_db_ctx,
        mock_pd,
        mock_go,
    ):
        from src.modules.famille.activites import app

        setup_mock_st(mock_st)
        mock_activites.return_value = []
        mock_budget_mois.return_value = 100.0
        mock_budget_period.return_value = {"Activites": 25.0}
        mock_activity1 = MagicMock()
        mock_activity1.date_prevue = date.today()
        mock_activity1.titre = "Sortie Parc"
        mock_activity1.cout_estime = 15.0
        mock_activity1.cout_reel = 18.0
        mock_activity1.type_activite = "parc"
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.all.return_value = [mock_activity1]
        mock_db_ctx.return_value.__enter__.return_value = mock_session
        mock_db_ctx.return_value.__exit__.return_value = False
        mock_df = MagicMock()
        mock_pd.DataFrame.return_value = mock_df
        mock_pd.to_datetime.return_value = mock_df.__getitem__.return_value
        mock_grouped = MagicMock()
        mock_grouped.columns = ["Type", "Budget"]
        mock_df.groupby.return_value.__getitem__.return_value.sum.return_value.reset_index.return_value = mock_grouped
        mock_fig = MagicMock()
        mock_go.Figure.return_value = mock_fig
        mock_go.Scatter.return_value = MagicMock()
        mock_go.Bar.return_value = MagicMock()
        app()
        assert mock_pd.DataFrame.called
        assert mock_go.Figure.called
        mock_st.plotly_chart.assert_called()


@pytest.mark.unit
class TestMarquerTermineeWithoutCout:
    @patch("src.modules.famille.activites.st")
    @patch("src.modules.famille.activites.clear_famille_cache")
    @patch("src.modules.famille.activites.obtenir_contexte_db")
    def test_marquer_terminee_without_cout(self, mock_db_ctx, mock_clear_cache, mock_st):
        from src.modules.famille.activites import marquer_terminee

        mock_activity = MagicMock()
        mock_activity.statut = "planifie"
        mock_activity.cout_reel = None
        mock_session = MagicMock()
        mock_session.get.return_value = mock_activity
        mock_db_ctx.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_db_ctx.return_value.__exit__ = MagicMock(return_value=False)
        result = marquer_terminee(activity_id=1)
        assert result is True
        assert mock_activity.statut == "termine"
