"""
Tests pour src/modules/famille/budget_dashboard.py
"""

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
    mock_st.tabs.return_value = [MagicMock() for _ in range(4)]
    mock_st.session_state = SessionStateMock(session_data or {})
    mock_st.selectbox.return_value = ("01/2026", 1, 2026)
    mock_st.form_submit_button.return_value = False
    for cm in ["container", "form"]:
        getattr(mock_st, cm).return_value.__enter__ = MagicMock(return_value=MagicMock())
        getattr(mock_st, cm).return_value.__exit__ = MagicMock(return_value=False)


def create_mock_resume():
    """Cree un mock de resume budget."""
    resume = MagicMock()
    resume.total_depenses = 1500.0
    resume.total_budget = 2000.0
    resume.variation_vs_mois_precedent = 5.5
    resume.moyenne_6_mois = 1400.0
    resume.categories_depassees = []
    resume.categories_a_risque = []
    resume.depenses_par_categorie = {"alimentation": 500, "transport": 200}
    resume.budgets_par_categorie = {}
    return resume


def create_mock_service():
    """Cree un mock service budget complet."""
    mock_service = MagicMock()
    mock_service.get_resume_mensuel.return_value = create_mock_resume()
    mock_service.get_depenses_mois.return_value = []
    mock_service.get_tendances.return_value = {"mois": [], "total": []}
    mock_service.prevoir_depenses.return_value = []
    mock_service.get_tous_budgets.return_value = {}
    mock_service.BUDGETS_DEFAUT = {}
    return mock_service


@pytest.mark.unit
class TestRenderBudgetDashboard:
    """Tests pour afficher_budget_dashboard."""

    @patch("src.modules.famille.budget_dashboard.px")
    @patch("src.modules.famille.budget_dashboard.go")
    @patch("src.modules.famille.budget_dashboard.get_budget_service")
    @patch("src.modules.famille.budget_dashboard.st")
    def test_render_budget_dashboard_basic(
        self, mock_st, mock_svc_factory, mock_go, mock_px
    ) -> None:
        """Test afficher_budget_dashboard sans erreur."""
        from src.modules.famille.budget_dashboard import afficher_budget_dashboard

        setup_mock_st(mock_st)
        mock_svc_factory.return_value = create_mock_service()

        afficher_budget_dashboard()
        mock_st.subheader.assert_called()

    @patch("src.modules.famille.budget_dashboard.px")
    @patch("src.modules.famille.budget_dashboard.go")
    @patch("src.modules.famille.budget_dashboard.get_budget_service")
    @patch("src.modules.famille.budget_dashboard.st")
    def test_render_with_depassement(self, mock_st, mock_svc_factory, mock_go, mock_px) -> None:
        """Test avec categories depassees."""
        from src.modules.famille.budget_dashboard import afficher_budget_dashboard

        setup_mock_st(mock_st)
        mock_svc = create_mock_service()
        resume = mock_svc.get_resume_mensuel.return_value
        resume.categories_depassees = ["alimentation"]
        mock_svc_factory.return_value = mock_svc

        afficher_budget_dashboard()
        mock_st.error.assert_called()

    @patch("src.modules.famille.budget_dashboard.px")
    @patch("src.modules.famille.budget_dashboard.go")
    @patch("src.modules.famille.budget_dashboard.get_budget_service")
    @patch("src.modules.famille.budget_dashboard.st")
    def test_render_with_risque(self, mock_st, mock_svc_factory, mock_go, mock_px) -> None:
        """Test avec categories a risque."""
        from src.modules.famille.budget_dashboard import afficher_budget_dashboard

        setup_mock_st(mock_st)
        mock_svc = create_mock_service()
        resume = mock_svc.get_resume_mensuel.return_value
        resume.categories_a_risque = ["transport"]
        mock_svc_factory.return_value = mock_svc

        afficher_budget_dashboard()
        mock_st.warning.assert_called()


@pytest.mark.unit
class TestRenderMetrics:
    """Tests pour _afficher_metrics."""

    @patch("src.modules.famille.budget_dashboard.st")
    def test_render_metrics_basic(self, mock_st) -> None:
        """Test afficher_metrics affiche les metriques."""
        from src.modules.famille.budget_dashboard import _afficher_metrics

        setup_mock_st(mock_st)
        resume = create_mock_resume()

        _afficher_metrics(resume)
        assert mock_st.metric.call_count >= 4

    @patch("src.modules.famille.budget_dashboard.st")
    def test_render_metrics_budget_depasse(self, mock_st) -> None:
        """Test avec budget depasse."""
        from src.modules.famille.budget_dashboard import _afficher_metrics

        setup_mock_st(mock_st)
        resume = create_mock_resume()
        resume.total_depenses = 2500.0
        resume.total_budget = 2000.0

        _afficher_metrics(resume)
        mock_st.metric.assert_called()


@pytest.mark.unit
class TestRenderOverviewTab:
    """Tests pour _afficher_overview_tab."""

    @patch("src.modules.famille.budget_dashboard.px")
    @patch("src.modules.famille.budget_dashboard.go")
    @patch("src.modules.famille.budget_dashboard.st")
    def test_render_overview_with_data(self, mock_st, mock_go, mock_px) -> None:
        """Test overview avec donnees."""
        from src.modules.famille.budget_dashboard import _afficher_overview_tab

        setup_mock_st(mock_st)
        mock_service = MagicMock()
        mock_service.get_depenses_mois.return_value = []
        resume = create_mock_resume()

        _afficher_overview_tab(mock_service, resume, 1, 2026)
        mock_st.plotly_chart.assert_called()

    @patch("src.modules.famille.budget_dashboard.st")
    def test_render_overview_empty(self, mock_st) -> None:
        """Test overview sans donnees."""
        from src.modules.famille.budget_dashboard import _afficher_overview_tab

        setup_mock_st(mock_st)
        mock_service = MagicMock()
        mock_service.get_depenses_mois.return_value = []
        resume = create_mock_resume()
        resume.depenses_par_categorie = {}

        _afficher_overview_tab(mock_service, resume, 1, 2026)
        mock_st.info.assert_called()

    @patch("src.modules.famille.budget_dashboard.px")
    @patch("src.modules.famille.budget_dashboard.go")
    @patch("src.modules.famille.budget_dashboard.st")
    def test_render_overview_with_budgets(self, mock_st, mock_go, mock_px) -> None:
        """Test overview avec budgets par categorie."""
        from src.modules.famille.budget_dashboard import _afficher_overview_tab

        setup_mock_st(mock_st)
        mock_service = MagicMock()
        mock_service.get_depenses_mois.return_value = []
        resume = create_mock_resume()

        budget_item = MagicMock()
        budget_item.budget_prevu = 500
        budget_item.depense_reelle = 400
        resume.budgets_par_categorie = {"alimentation": budget_item}

        _afficher_overview_tab(mock_service, resume, 1, 2026)
        mock_go.Figure.assert_called()

    @patch("src.modules.famille.budget_dashboard.px")
    @patch("src.modules.famille.budget_dashboard.go")
    @patch("src.modules.famille.budget_dashboard.st")
    def test_render_overview_with_depenses(self, mock_st, mock_go, mock_px) -> None:
        """Test overview avec liste depenses recentes."""
        from src.modules.famille.budget_dashboard import (
            CategorieDepense,
            _afficher_overview_tab,
        )

        setup_mock_st(mock_st)
        mock_service = MagicMock()

        dep = MagicMock()
        dep.date.strftime.return_value = "01/01"
        dep.categorie = CategorieDepense.ALIMENTATION
        dep.description = "Test"
        dep.montant = 50.0
        mock_service.get_depenses_mois.return_value = [dep]

        resume = create_mock_resume()
        _afficher_overview_tab(mock_service, resume, 1, 2026)
        mock_st.caption.assert_called()


@pytest.mark.unit
class TestRenderAddExpenseTab:
    """Tests pour _afficher_add_expense_tab."""

    @patch("src.modules.famille.budget_dashboard.st")
    def test_render_add_expense_form(self, mock_st) -> None:
        """Test formulaire ajout depense."""
        from src.modules.famille.budget_dashboard import _afficher_add_expense_tab

        setup_mock_st(mock_st)
        mock_service = MagicMock()

        _afficher_add_expense_tab(mock_service)
        mock_st.form.assert_called()

    @patch("src.modules.famille.budget_dashboard.st")
    def test_add_expense_submit_valid(self, mock_st) -> None:
        """Test soumission formulaire avec montant valide."""
        from src.modules.famille.budget_dashboard import (
            CategorieDepense,
            _afficher_add_expense_tab,
        )

        setup_mock_st(mock_st)
        mock_st.form_submit_button.return_value = True
        mock_st.number_input.return_value = 50.0
        mock_st.selectbox.return_value = CategorieDepense.ALIMENTATION
        mock_st.date_input.return_value = date(2026, 1, 15)
        mock_st.text_input.return_value = "Test"
        mock_st.checkbox.return_value = False
        mock_st.rerun = MagicMock()

        mock_service = MagicMock()

        _afficher_add_expense_tab(mock_service)
        mock_service.ajouter_depense.assert_called_once()
        mock_st.success.assert_called()

    @patch("src.modules.famille.budget_dashboard.st")
    def test_add_expense_submit_zero(self, mock_st) -> None:
        """Test soumission formulaire avec montant zero."""
        from src.modules.famille.budget_dashboard import (
            CategorieDepense,
            _afficher_add_expense_tab,
        )

        setup_mock_st(mock_st)
        mock_st.form_submit_button.return_value = True
        mock_st.number_input.return_value = 0.0
        mock_st.selectbox.return_value = CategorieDepense.ALIMENTATION
        mock_st.date_input.return_value = date(2026, 1, 15)
        mock_st.text_input.return_value = "Test"
        mock_st.checkbox.return_value = False

        mock_service = MagicMock()

        _afficher_add_expense_tab(mock_service)
        mock_st.error.assert_called()


@pytest.mark.unit
class TestRenderTrendsTab:
    """Tests pour _afficher_trends_tab."""

    @patch("src.modules.famille.budget_dashboard.go")
    @patch("src.modules.famille.budget_dashboard.st")
    def test_render_trends_empty(self, mock_st, mock_go) -> None:
        """Test tendances sans donnees."""
        from src.modules.famille.budget_dashboard import _afficher_trends_tab

        setup_mock_st(mock_st)
        mock_service = MagicMock()
        mock_service.get_tendances.return_value = {}
        mock_service.prevoir_depenses.return_value = []

        _afficher_trends_tab(mock_service, 1, 2026)

    @patch("src.modules.famille.budget_dashboard.go")
    @patch("src.modules.famille.budget_dashboard.st")
    def test_render_trends_with_data(self, mock_st, mock_go) -> None:
        """Test tendances avec donnees."""
        from src.modules.famille.budget_dashboard import _afficher_trends_tab

        setup_mock_st(mock_st)
        mock_service = MagicMock()
        mock_service.get_tendances.return_value = {
            "mois": ["Jan", "Feb", "Mar"],
            "total": [1500, 1600, 1400],
            "alimentation": [500, 550, 480],
        }
        mock_service.prevoir_depenses.return_value = []

        _afficher_trends_tab(mock_service, 1, 2026)
        mock_st.plotly_chart.assert_called()

    @patch("src.modules.famille.budget_dashboard.go")
    @patch("src.modules.famille.budget_dashboard.st")
    def test_render_trends_with_previsions(self, mock_st, mock_go) -> None:
        """Test tendances avec previsions."""
        from src.modules.famille.budget_dashboard import CategorieDepense, _afficher_trends_tab

        setup_mock_st(mock_st)
        mock_service = MagicMock()
        mock_service.get_tendances.return_value = {}

        prev = MagicMock()
        prev.categorie = CategorieDepense.ALIMENTATION
        prev.montant_prevu = 600.0
        prev.confiance = 0.85
        mock_service.prevoir_depenses.return_value = [prev]

        _afficher_trends_tab(mock_service, 1, 2026)
        mock_st.metric.assert_called()


@pytest.mark.unit
class TestRenderBudgetsConfigTab:
    """Tests pour _afficher_budgets_config_tab."""

    @patch("src.modules.famille.budget_dashboard.st")
    def test_render_budgets_config(self, mock_st) -> None:
        """Test configuration budgets."""
        from src.modules.famille.budget_dashboard import _afficher_budgets_config_tab

        setup_mock_st(mock_st)
        mock_service = MagicMock()
        mock_service.get_tous_budgets.return_value = {}
        mock_service.BUDGETS_DEFAUT = {}

        _afficher_budgets_config_tab(mock_service, 1, 2026)
        mock_st.form.assert_called()

    @patch("src.modules.famille.budget_dashboard.st")
    def test_budgets_config_submit(self, mock_st) -> None:
        """Test soumission configuration budgets."""
        from src.modules.famille.budget_dashboard import _afficher_budgets_config_tab

        setup_mock_st(mock_st)
        mock_st.form_submit_button.return_value = True
        mock_st.number_input.return_value = 500.0
        mock_st.rerun = MagicMock()

        mock_service = MagicMock()
        mock_service.get_tous_budgets.return_value = {}
        mock_service.BUDGETS_DEFAUT = {}

        _afficher_budgets_config_tab(mock_service, 1, 2026)
        mock_service.definir_budget.assert_called()
        mock_st.success.assert_called()


class TestImports:
    """Tests des imports."""

    def test_import_render_budget_dashboard(self) -> None:
        """Test import afficher_budget_dashboard."""
        from src.modules.famille.budget_dashboard import afficher_budget_dashboard

        assert callable(afficher_budget_dashboard)

    def test_import_render_metrics(self) -> None:
        """Test import _afficher_metrics."""
        from src.modules.famille.budget_dashboard import _afficher_metrics

        assert callable(_afficher_metrics)

    def test_import_render_overview_tab(self) -> None:
        """Test import _afficher_overview_tab."""
        from src.modules.famille.budget_dashboard import _afficher_overview_tab

        assert callable(_afficher_overview_tab)

    def test_import_render_add_expense_tab(self) -> None:
        """Test import _afficher_add_expense_tab."""
        from src.modules.famille.budget_dashboard import _afficher_add_expense_tab

        assert callable(_afficher_add_expense_tab)

    def test_import_render_trends_tab(self) -> None:
        """Test import _afficher_trends_tab."""
        from src.modules.famille.budget_dashboard import _afficher_trends_tab

        assert callable(_afficher_trends_tab)

    def test_import_render_budgets_config_tab(self) -> None:
        """Test import _afficher_budgets_config_tab."""
        from src.modules.famille.budget_dashboard import _afficher_budgets_config_tab

        assert callable(_afficher_budgets_config_tab)
