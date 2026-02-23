"""
Tests unitaires pour src/modules/famille/activites.py

Module Activites - Planning et budget des activités familiales.
Refactorisé: la logique CRUD est dans ServiceActivites, le module ne contient que l'UI.
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

    def test_import_get_service(self):
        from src.modules.famille.activites import _get_service

        assert _get_service is not None
        assert callable(_get_service)

    def test_import_suggestions_activites(self):
        from src.modules.famille.activites import SUGGESTIONS_ACTIVITES

        assert SUGGESTIONS_ACTIVITES is not None
        assert isinstance(SUGGESTIONS_ACTIVITES, dict)


@pytest.mark.unit
class TestAjouterActivite:
    """Tests pour ServiceActivites.ajouter_activite"""

    @patch("src.services.famille.activites.obtenir_bus")
    def test_ajouter_activite_success(self, mock_bus):
        from src.services.famille.activites import ServiceActivites

        mock_bus.return_value = MagicMock()
        svc = ServiceActivites()
        mock_db = MagicMock()

        def set_id(obj):
            obj.id = 1

        mock_db.add.side_effect = set_id

        result = svc.ajouter_activite(
            titre="Test",
            type_activite="parc",
            date_prevue=date.today(),
            duree=2.0,
            lieu="Parc",
            participants=["Famille"],
            cout_estime=15.0,
            db=mock_db,
        )

        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        assert result is not None

    @patch("src.services.famille.activites.obtenir_bus")
    def test_ajouter_activite_error(self, mock_bus):
        from src.services.famille.activites import ServiceActivites

        mock_bus.return_value = MagicMock()
        svc = ServiceActivites()
        mock_db = MagicMock()
        mock_db.add.side_effect = Exception("DB Error")

        # @avec_gestion_erreurs catches exceptions and returns default_return=None
        result = svc.ajouter_activite(
            titre="Test",
            type_activite="parc",
            date_prevue=date.today(),
            duree=1.0,
            lieu="",
            participants=[],
            cout_estime=0.0,
            db=mock_db,
        )
        assert result is None


@pytest.mark.unit
class TestMarquerTerminee:
    """Tests pour ServiceActivites.marquer_terminee"""

    @patch("src.services.famille.activites.obtenir_bus")
    def test_marquer_terminee_success(self, mock_bus):
        from src.services.famille.activites import ServiceActivites

        mock_bus.return_value = MagicMock()
        svc = ServiceActivites()
        mock_activity = MagicMock()
        mock_activity.statut = "planifie"
        mock_db = MagicMock()
        mock_db.get.return_value = mock_activity

        result = svc.marquer_terminee(activity_id=1, cout_reel=20.0, db=mock_db)
        assert result is True
        assert mock_activity.statut == "termine"

    @patch("src.services.famille.activites.obtenir_bus")
    def test_marquer_terminee_not_found(self, mock_bus):
        from src.services.famille.activites import ServiceActivites

        mock_bus.return_value = MagicMock()
        svc = ServiceActivites()
        mock_db = MagicMock()
        mock_db.get.return_value = None

        result = svc.marquer_terminee(activity_id=999, db=mock_db)
        assert result is False


@pytest.mark.unit
class TestActivitesApp:
    @patch("src.modules.famille.activites.etat_vide")
    @patch("src.modules.famille.activites._get_service")
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
        mock_get_svc,
        mock_etat_vide,
    ):
        from src.modules.famille.activites import app

        setup_mock_st(mock_st)
        mock_activites.return_value = []
        mock_budget_mois.return_value = 100.0
        mock_budget_period.return_value = {"Activites": 25.0}
        mock_svc = MagicMock()
        mock_svc.lister_activites.return_value = []
        mock_get_svc.return_value = mock_svc
        app()
        mock_st.title.assert_called_once()

    @patch("src.modules.famille.activites.etat_vide")
    @patch("src.modules.famille.activites._get_service")
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
        mock_get_svc,
        mock_etat_vide,
    ):
        from src.modules.famille.activites import app

        setup_mock_st(mock_st)
        mock_activites.return_value = []
        mock_budget_mois.return_value = 0.0
        mock_budget_period.return_value = {"Activites": 0.0}
        mock_svc = MagicMock()
        mock_svc.lister_activites.return_value = []
        mock_get_svc.return_value = mock_svc
        app()
        mock_etat_vide.assert_called()


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
    @patch("src.services.famille.activites.obtenir_bus")
    def test_marquer_terminee_exception(self, mock_bus):
        from src.services.famille.activites import ServiceActivites

        mock_bus.return_value = MagicMock()
        svc = ServiceActivites()
        mock_db = MagicMock()
        mock_db.get.side_effect = Exception("DB error")

        # @avec_gestion_erreurs catches exceptions and returns default_return=None
        result = svc.marquer_terminee(activity_id=1, cout_reel=10.0, db=mock_db)
        assert result is None


@pytest.mark.unit
class TestAppFormSubmission:
    @patch("src.modules.famille.activites.clear_famille_cache")
    @patch("src.modules.famille.activites.etat_vide")
    @patch("src.modules.famille.activites._get_service")
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
        mock_get_svc,
        mock_etat_vide,
        mock_clear_cache,
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
        mock_svc = MagicMock()
        mock_svc.lister_activites.return_value = []
        mock_get_svc.return_value = mock_svc
        app()
        mock_svc.ajouter_activite.assert_called_once()


@pytest.mark.unit
class TestAppWithActivities:
    @patch("src.modules.famille.activites.go")
    @patch("src.modules.famille.activites.pd")
    @patch("src.modules.famille.activites._get_service")
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
        mock_get_svc,
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

        mock_svc = MagicMock()
        mock_svc.lister_activites.return_value = [mock_activity]
        mock_get_svc.return_value = mock_svc
        mock_df = MagicMock()
        mock_pd.DataFrame.return_value = mock_df
        mock_df.groupby.return_value.__getitem__.return_value.sum.return_value.reset_index.return_value = MagicMock()
        app()
        assert mock_st.container.called


@pytest.mark.unit
class TestAppExceptionHandling:
    @patch("src.modules.famille.activites.etat_vide")
    @patch("src.modules.famille.activites._get_service")
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
        mock_get_svc,
        mock_etat_vide,
    ):
        from src.modules.famille.activites import app

        setup_mock_st(mock_st)
        mock_activites.side_effect = Exception("DB error")
        mock_budget_mois.return_value = 100.0
        mock_budget_period.return_value = {"Activites": 25.0}
        mock_svc = MagicMock()
        mock_svc.lister_activites.return_value = []
        mock_get_svc.return_value = mock_svc
        app()
        mock_st.error.assert_called()

    @patch("src.modules.famille.activites.etat_vide")
    @patch("src.modules.famille.activites._get_service")
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
        mock_get_svc,
        mock_etat_vide,
    ):
        from src.modules.famille.activites import app

        setup_mock_st(mock_st)
        mock_activites.return_value = []
        mock_budget_mois.side_effect = Exception("Budget error")
        mock_budget_period.return_value = {"Activites": 0.0}
        mock_svc = MagicMock()
        mock_svc.lister_activites.return_value = []
        mock_get_svc.return_value = mock_svc
        app()
        mock_st.error.assert_called()

    @patch("src.modules.famille.activites.etat_vide")
    @patch("src.modules.famille.activites._get_service")
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
        mock_get_svc,
        mock_etat_vide,
    ):
        from src.modules.famille.activites import app

        setup_mock_st(mock_st)
        mock_activites.return_value = []
        mock_budget_mois.return_value = 100.0
        mock_budget_period.return_value = {"Activites": 25.0}
        mock_svc = MagicMock()
        mock_svc.lister_activites.side_effect = Exception("Graphique error")
        mock_get_svc.return_value = mock_svc
        app()
        mock_st.error.assert_called()


@pytest.mark.unit
class TestAppGraphiqueWithData:
    @patch("src.modules.famille.activites.go")
    @patch("src.modules.famille.activites.pd")
    @patch("src.modules.famille.activites._get_service")
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
        mock_get_svc,
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

        mock_svc = MagicMock()
        mock_svc.lister_activites.return_value = [mock_activity1]
        mock_get_svc.return_value = mock_svc

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
    @patch("src.services.famille.activites.obtenir_bus")
    def test_marquer_terminee_without_cout(self, mock_bus):
        from src.services.famille.activites import ServiceActivites

        mock_bus.return_value = MagicMock()
        svc = ServiceActivites()
        mock_activity = MagicMock()
        mock_activity.statut = "planifie"
        mock_activity.cout_reel = None
        mock_db = MagicMock()
        mock_db.get.return_value = mock_activity

        result = svc.marquer_terminee(activity_id=1, db=mock_db)
        assert result is True
        assert mock_activity.statut == "termine"
