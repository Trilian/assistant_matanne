"""
Tests pour src/modules/maison/depenses/components.py
"""

from datetime import date
from decimal import Decimal
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
    mock_st.button.return_value = False
    mock_st.form.return_value.__enter__ = MagicMock(return_value=MagicMock())
    mock_st.form.return_value.__exit__ = MagicMock(return_value=False)
    mock_st.container.return_value.__enter__ = MagicMock(return_value=MagicMock())
    mock_st.container.return_value.__exit__ = MagicMock(return_value=False)
    mock_st.form_submit_button.return_value = False
    mock_st.number_input.return_value = 100.0
    mock_st.selectbox.return_value = "electricite"
    mock_st.text_area.return_value = ""


class TestImports:
    """Tests des imports."""

    def test_import_render_stats_dashboard(self) -> None:
        from src.modules.maison.depenses.components import render_stats_dashboard

        assert callable(render_stats_dashboard)

    def test_import_render_depense_card(self) -> None:
        from src.modules.maison.depenses.components import render_depense_card

        assert callable(render_depense_card)

    def test_import_render_formulaire(self) -> None:
        from src.modules.maison.depenses.components import render_formulaire

        assert callable(render_formulaire)

    def test_import_render_onglet_mois(self) -> None:
        from src.modules.maison.depenses.components import render_onglet_mois

        assert callable(render_onglet_mois)

    def test_import_render_onglet_ajouter(self) -> None:
        from src.modules.maison.depenses.components import render_onglet_ajouter

        assert callable(render_onglet_ajouter)

    def test_import_render_onglet_analyse(self) -> None:
        from src.modules.maison.depenses.components import render_onglet_analyse

        assert callable(render_onglet_analyse)

    def test_import_render_graphique_evolution(self) -> None:
        from src.modules.maison.depenses.components import render_graphique_evolution

        assert callable(render_graphique_evolution)

    def test_import_render_comparaison_mois(self) -> None:
        from src.modules.maison.depenses.components import render_comparaison_mois

        assert callable(render_comparaison_mois)


@pytest.mark.unit
class TestRenderStatsDashboard:
    """Tests pour render_stats_dashboard."""

    @patch("src.modules.maison.depenses.components.get_stats_globales")
    @patch("src.modules.maison.depenses.components.st")
    def test_render_stats_dashboard_affiche_metrics(self, mock_st, mock_stats) -> None:
        from src.modules.maison.depenses.components import render_stats_dashboard

        setup_mock_st(mock_st)
        mock_stats.return_value = {
            "total_mois": 500.0,
            "total_prec": 450.0,
            "delta": 50.0,
            "moyenne_mensuelle": 480.0,
            "nb_categories": 5,
        }
        render_stats_dashboard()
        mock_st.subheader.assert_called()
        assert mock_st.metric.call_count >= 4

    @patch("src.modules.maison.depenses.components.get_stats_globales")
    @patch("src.modules.maison.depenses.components.st")
    def test_render_stats_dashboard_delta_zero(self, mock_st, mock_stats) -> None:
        from src.modules.maison.depenses.components import render_stats_dashboard

        setup_mock_st(mock_st)
        mock_stats.return_value = {
            "total_mois": 500.0,
            "total_prec": 500.0,
            "delta": 0,
            "moyenne_mensuelle": 500.0,
            "nb_categories": 3,
        }
        render_stats_dashboard()
        mock_st.metric.assert_called()


@pytest.mark.unit
class TestRenderDepenseCard:
    """Tests pour render_depense_card."""

    @patch("src.modules.maison.depenses.components.st")
    def test_render_depense_card_basique(self, mock_st) -> None:
        from src.modules.maison.depenses.components import render_depense_card

        setup_mock_st(mock_st)
        depense = MagicMock()
        depense.id = 1
        depense.categorie = "electricite"
        depense.montant = Decimal("125.50")
        depense.note = "Facture EDF"
        depense.consommation = Decimal("350")
        render_depense_card(depense)
        mock_st.container.assert_called()
        mock_st.markdown.assert_called()

    @patch("src.modules.maison.depenses.components.st")
    def test_render_depense_card_sans_note(self, mock_st) -> None:
        from src.modules.maison.depenses.components import render_depense_card

        setup_mock_st(mock_st)
        depense = MagicMock()
        depense.id = 2
        depense.categorie = "assurance"
        depense.montant = Decimal("80.00")
        depense.note = None
        depense.consommation = None
        render_depense_card(depense)
        mock_st.container.assert_called()


@pytest.mark.unit
class TestRenderFormulaire:
    """Tests pour render_formulaire."""

    @patch("src.modules.maison.depenses.components.st")
    def test_render_formulaire_nouveau(self, mock_st) -> None:
        from src.modules.maison.depenses.components import render_formulaire

        setup_mock_st(mock_st)
        render_formulaire(None)
        mock_st.form.assert_called()

    @patch("src.modules.maison.depenses.components.st")
    def test_render_formulaire_edition(self, mock_st) -> None:
        from src.modules.maison.depenses.components import render_formulaire

        setup_mock_st(mock_st)
        depense = MagicMock()
        depense.id = 1
        depense.categorie = "electricite"
        depense.montant = Decimal("125.50")
        depense.consommation = Decimal("350")
        depense.mois = 2
        depense.annee = 2026
        depense.note = "Test"
        render_formulaire(depense)
        mock_st.form.assert_called()


@pytest.mark.unit
class TestRenderOnglets:
    """Tests pour les fonctions render_onglet_*."""

    @patch("src.modules.maison.depenses.components.get_depenses_mois")
    @patch("src.modules.maison.depenses.components.st")
    def test_render_onglet_mois_vide(self, mock_st, mock_get) -> None:
        from src.modules.maison.depenses.components import render_onglet_mois

        setup_mock_st(mock_st)
        mock_get.return_value = []
        mock_st.selectbox.return_value = 2
        mock_st.number_input.return_value = 2026
        render_onglet_mois()
        mock_st.info.assert_called()

    @patch("src.modules.maison.depenses.components.get_depenses_mois")
    @patch("src.modules.maison.depenses.components.render_depense_card")
    @patch("src.modules.maison.depenses.components.st")
    def test_render_onglet_mois_avec_depenses(self, mock_st, mock_card, mock_get) -> None:
        from src.modules.maison.depenses.components import render_onglet_mois

        setup_mock_st(mock_st)
        dep1 = MagicMock()
        dep1.montant = Decimal("100")
        mock_get.return_value = [dep1]
        mock_st.selectbox.return_value = 2
        mock_st.number_input.return_value = 2026
        render_onglet_mois()
        mock_st.metric.assert_called()

    @patch("src.modules.maison.depenses.components.render_formulaire")
    @patch("src.modules.maison.depenses.components.st")
    def test_render_onglet_ajouter(self, mock_st, mock_form) -> None:
        from src.modules.maison.depenses.components import render_onglet_ajouter

        setup_mock_st(mock_st)
        render_onglet_ajouter()
        mock_st.subheader.assert_called()
        mock_form.assert_called_once_with(None)

    @patch("src.modules.maison.depenses.components.render_graphique_evolution")
    @patch("src.modules.maison.depenses.components.render_comparaison_mois")
    @patch("src.modules.maison.depenses.components.st")
    def test_render_onglet_analyse(self, mock_st, mock_comp, mock_graph) -> None:
        from src.modules.maison.depenses.components import render_onglet_analyse

        setup_mock_st(mock_st)
        render_onglet_analyse()
        mock_graph.assert_called_once()
        mock_comp.assert_called_once()


@pytest.mark.unit
class TestRenderGraphiqueEvolution:
    """Tests pour render_graphique_evolution."""

    @patch("src.modules.maison.depenses.components.get_depenses_mois")
    @patch("src.modules.maison.depenses.components.st")
    def test_render_graphique_total(self, mock_st, mock_get) -> None:
        from src.modules.maison.depenses.components import render_graphique_evolution

        setup_mock_st(mock_st)
        mock_st.selectbox.return_value = "total"
        mock_get.return_value = []
        render_graphique_evolution()
        mock_st.subheader.assert_called()


@pytest.mark.unit
class TestRenderComparaisonMois:
    """Tests pour render_comparaison_mois."""

    @patch("src.modules.maison.depenses.components.get_depenses_mois")
    @patch("src.modules.maison.depenses.components.st")
    def test_render_comparaison_sans_clic(self, mock_st, mock_get) -> None:
        from src.modules.maison.depenses.components import render_comparaison_mois

        setup_mock_st(mock_st)
        mock_st.button.return_value = False
        render_comparaison_mois()
        mock_st.subheader.assert_called()

    @patch("src.modules.maison.depenses.components.get_depenses_mois")
    @patch("src.modules.maison.depenses.components.st")
    def test_render_comparaison_avec_clic(self, mock_st, mock_get) -> None:
        from src.modules.maison.depenses.components import render_comparaison_mois

        setup_mock_st(mock_st)
        mock_st.button.return_value = True
        mock_st.selectbox.return_value = 2
        mock_st.number_input.return_value = 2026
        dep1 = MagicMock()
        dep1.categorie = "electricite"
        dep1.montant = Decimal("100")
        mock_get.return_value = [dep1]
        render_comparaison_mois()
        assert mock_get.call_count >= 2
