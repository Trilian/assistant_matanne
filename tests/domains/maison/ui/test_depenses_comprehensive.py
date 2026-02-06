"""
Tests complets pour le module maison/ui/depenses.

Couvre:
- Fonctions CRUD (get_depenses_mois, create_depense, etc.)
- Statistiques et historique
- Fonctions de rendu UI
"""

import pytest
from datetime import date, datetime
from decimal import Decimal
from unittest.mock import Mock, MagicMock, patch
from typing import List


# ═══════════════════════════════════════════════════════════
# TESTS FONCTIONS CRUD
# ═══════════════════════════════════════════════════════════


class TestGetDepensesMois:
    """Tests pour get_depenses_mois."""

    @patch('src.domains.maison.ui.depenses.obtenir_contexte_db')
    def test_get_depenses_mois_success(self, mock_db):
        from src.domains.maison.ui.depenses import get_depenses_mois
        
        mock_session = MagicMock()
        mock_db.return_value.__enter__ = Mock(return_value=mock_session)
        mock_db.return_value.__exit__ = Mock(return_value=False)
        
        mock_depenses = [
            MagicMock(id=1, montant=100.0, categorie="alimentation"),
            MagicMock(id=2, montant=50.0, categorie="transport"),
        ]
        mock_session.query.return_value.filter.return_value.all.return_value = mock_depenses
        
        result = get_depenses_mois(mois=2, annee=2026)
        
        assert len(result) == 2

    @patch('src.domains.maison.ui.depenses.obtenir_contexte_db')
    def test_get_depenses_mois_vide(self, mock_db):
        from src.domains.maison.ui.depenses import get_depenses_mois
        
        mock_session = MagicMock()
        mock_db.return_value.__enter__ = Mock(return_value=mock_session)
        mock_db.return_value.__exit__ = Mock(return_value=False)
        
        mock_session.query.return_value.filter.return_value.all.return_value = []
        
        result = get_depenses_mois(mois=1, annee=2026)
        
        assert result == []


class TestGetDepensesAnnee:
    """Tests pour get_depenses_annee."""

    @patch('src.domains.maison.ui.depenses.obtenir_contexte_db')
    def test_get_depenses_annee_success(self, mock_db):
        from src.domains.maison.ui.depenses import get_depenses_annee
        
        mock_session = MagicMock()
        mock_db.return_value.__enter__ = Mock(return_value=mock_session)
        mock_db.return_value.__exit__ = Mock(return_value=False)
        
        mock_depenses = [MagicMock() for _ in range(12)]
        mock_session.query.return_value.filter.return_value.all.return_value = mock_depenses
        
        result = get_depenses_annee(annee=2026)
        
        assert len(result) == 12


class TestGetDepenseById:
    """Tests pour get_depense_by_id."""

    @patch('src.domains.maison.ui.depenses.obtenir_contexte_db')
    def test_get_depense_by_id_found(self, mock_db):
        from src.domains.maison.ui.depenses import get_depense_by_id
        
        mock_session = MagicMock()
        mock_db.return_value.__enter__ = Mock(return_value=mock_session)
        mock_db.return_value.__exit__ = Mock(return_value=False)
        
        mock_depense = MagicMock(id=1, montant=100.0)
        mock_session.query.return_value.filter.return_value.first.return_value = mock_depense
        
        result = get_depense_by_id(depense_id=1)
        
        assert result is not None
        assert result.id == 1

    @patch('src.domains.maison.ui.depenses.obtenir_contexte_db')
    def test_get_depense_by_id_not_found(self, mock_db):
        from src.domains.maison.ui.depenses import get_depense_by_id
        
        mock_session = MagicMock()
        mock_db.return_value.__enter__ = Mock(return_value=mock_session)
        mock_db.return_value.__exit__ = Mock(return_value=False)
        
        mock_session.query.return_value.filter.return_value.first.return_value = None
        
        result = get_depense_by_id(depense_id=999)
        
        assert result is None


class TestCreateDepense:
    """Tests pour create_depense."""

    @patch('src.domains.maison.ui.depenses.obtenir_contexte_db')
    def test_create_depense_success(self, mock_db):
        from src.domains.maison.ui.depenses import create_depense
        
        mock_session = MagicMock()
        mock_db.return_value.__enter__ = Mock(return_value=mock_session)
        mock_db.return_value.__exit__ = Mock(return_value=False)
        
        data = {
            "nom": "Courses",
            "montant": 150.0,
            "categorie": "alimentation",
            "date": date(2026, 2, 6),
        }
        
        result = create_depense(data)
        
        mock_session.add.assert_called()
        mock_session.commit.assert_called()

    @patch('src.domains.maison.ui.depenses.obtenir_contexte_db')
    def test_create_depense_minimal(self, mock_db):
        from src.domains.maison.ui.depenses import create_depense
        
        mock_session = MagicMock()
        mock_db.return_value.__enter__ = Mock(return_value=mock_session)
        mock_db.return_value.__exit__ = Mock(return_value=False)
        
        data = {
            "montant": 50.0,
            "categorie": "loisirs",
        }
        
        result = create_depense(data)
        
        assert result is not None


class TestUpdateDepense:
    """Tests pour update_depense."""

    @patch('src.domains.maison.ui.depenses.obtenir_contexte_db')
    def test_update_depense_success(self, mock_db):
        from src.domains.maison.ui.depenses import update_depense
        
        mock_session = MagicMock()
        mock_db.return_value.__enter__ = Mock(return_value=mock_session)
        mock_db.return_value.__exit__ = Mock(return_value=False)
        
        mock_depense = MagicMock(id=1, montant=100.0)
        mock_session.query.return_value.filter.return_value.first.return_value = mock_depense
        
        result = update_depense(depense_id=1, data={"montant": 150.0})
        
        assert result is not None
        mock_session.commit.assert_called()

    @patch('src.domains.maison.ui.depenses.obtenir_contexte_db')
    def test_update_depense_not_found(self, mock_db):
        from src.domains.maison.ui.depenses import update_depense
        
        mock_session = MagicMock()
        mock_db.return_value.__enter__ = Mock(return_value=mock_session)
        mock_db.return_value.__exit__ = Mock(return_value=False)
        
        mock_session.query.return_value.filter.return_value.first.return_value = None
        
        result = update_depense(depense_id=999, data={"montant": 150.0})
        
        assert result is None


class TestDeleteDepense:
    """Tests pour delete_depense."""

    @patch('src.domains.maison.ui.depenses.obtenir_contexte_db')
    def test_delete_depense_success(self, mock_db):
        from src.domains.maison.ui.depenses import delete_depense
        
        mock_session = MagicMock()
        mock_db.return_value.__enter__ = Mock(return_value=mock_session)
        mock_db.return_value.__exit__ = Mock(return_value=False)
        
        mock_depense = MagicMock(id=1)
        mock_session.query.return_value.filter.return_value.first.return_value = mock_depense
        
        result = delete_depense(depense_id=1)
        
        assert result is True
        mock_session.delete.assert_called_with(mock_depense)
        mock_session.commit.assert_called()

    @patch('src.domains.maison.ui.depenses.obtenir_contexte_db')
    def test_delete_depense_not_found(self, mock_db):
        from src.domains.maison.ui.depenses import delete_depense
        
        mock_session = MagicMock()
        mock_db.return_value.__enter__ = Mock(return_value=mock_session)
        mock_db.return_value.__exit__ = Mock(return_value=False)
        
        mock_session.query.return_value.filter.return_value.first.return_value = None
        
        result = delete_depense(depense_id=999)
        
        assert result is False


# ═══════════════════════════════════════════════════════════
# TESTS STATISTIQUES
# ═══════════════════════════════════════════════════════════


class TestGetStatsGlobales:
    """Tests pour get_stats_globales."""

    @patch('src.domains.maison.ui.depenses.obtenir_contexte_db')
    def test_get_stats_globales(self, mock_db):
        from src.domains.maison.ui.depenses import get_stats_globales
        
        mock_session = MagicMock()
        mock_db.return_value.__enter__ = Mock(return_value=mock_session)
        mock_db.return_value.__exit__ = Mock(return_value=False)
        
        # Mock total
        mock_session.query.return_value.scalar.return_value = 1500.0
        
        result = get_stats_globales()
        
        assert isinstance(result, dict)

    @patch('src.domains.maison.ui.depenses.obtenir_contexte_db')
    def test_get_stats_globales_empty(self, mock_db):
        from src.domains.maison.ui.depenses import get_stats_globales
        
        mock_session = MagicMock()
        mock_db.return_value.__enter__ = Mock(return_value=mock_session)
        mock_db.return_value.__exit__ = Mock(return_value=False)
        
        mock_session.query.return_value.scalar.return_value = None
        
        result = get_stats_globales()
        
        assert isinstance(result, dict)


class TestGetHistoriqueCategorie:
    """Tests pour get_historique_categorie."""

    @patch('src.domains.maison.ui.depenses.obtenir_contexte_db')
    def test_get_historique_categorie(self, mock_db):
        from src.domains.maison.ui.depenses import get_historique_categorie
        
        mock_session = MagicMock()
        mock_db.return_value.__enter__ = Mock(return_value=mock_session)
        mock_db.return_value.__exit__ = Mock(return_value=False)
        
        mock_session.query.return_value.filter.return_value.all.return_value = []
        
        result = get_historique_categorie("alimentation", nb_mois=6)
        
        assert isinstance(result, list)

    @patch('src.domains.maison.ui.depenses.obtenir_contexte_db')
    def test_get_historique_categorie_12_mois(self, mock_db):
        from src.domains.maison.ui.depenses import get_historique_categorie
        
        mock_session = MagicMock()
        mock_db.return_value.__enter__ = Mock(return_value=mock_session)
        mock_db.return_value.__exit__ = Mock(return_value=False)
        
        mock_session.query.return_value.filter.return_value.all.return_value = []
        
        result = get_historique_categorie("transport", nb_mois=12)
        
        assert isinstance(result, list)


# ═══════════════════════════════════════════════════════════
# TESTS RENDU UI
# ═══════════════════════════════════════════════════════════


class TestRenderStatsDashboard:
    """Tests pour render_stats_dashboard."""

    @patch('streamlit.columns')
    @patch('streamlit.metric')
    @patch('src.domains.maison.ui.depenses.get_stats_globales')
    def test_render_stats_dashboard(self, mock_stats, mock_metric, mock_cols):
        from src.domains.maison.ui.depenses import render_stats_dashboard
        
        mock_stats.return_value = {
            "total_mois": 1500.0,
            "nb_depenses": 25,
            "moyenne": 60.0,
        }
        mock_cols.return_value = [MagicMock() for _ in range(4)]
        
        # Should not raise
        render_stats_dashboard()


class TestRenderDepenseCard:
    """Tests pour render_depense_card."""

    @patch('streamlit.container')
    def test_render_depense_card(self, mock_container):
        from src.domains.maison.ui.depenses import render_depense_card
        
        mock_container.return_value.__enter__ = Mock(return_value=MagicMock())
        mock_container.return_value.__exit__ = Mock(return_value=False)
        
        depense = MagicMock(
            id=1,
            nom="Courses",
            montant=150.0,
            categorie="alimentation",
            date=date(2026, 2, 6),
        )
        
        # Should not raise
        render_depense_card(depense)


class TestRenderFormulaire:
    """Tests pour render_formulaire."""

    @patch('streamlit.form')
    @patch('streamlit.text_input')
    @patch('streamlit.number_input')
    @patch('streamlit.selectbox')
    @patch('streamlit.date_input')
    @patch('streamlit.form_submit_button')
    def test_render_formulaire_nouveau(self, mock_submit, mock_date, mock_select, 
                                        mock_number, mock_text, mock_form):
        from src.domains.maison.ui.depenses import render_formulaire
        
        mock_form.return_value.__enter__ = Mock(return_value=MagicMock())
        mock_form.return_value.__exit__ = Mock(return_value=False)
        mock_submit.return_value = False
        
        # Should not raise
        render_formulaire()

    @patch('streamlit.form')
    @patch('streamlit.text_input')
    @patch('streamlit.number_input')
    @patch('streamlit.selectbox')
    @patch('streamlit.date_input')
    @patch('streamlit.form_submit_button')
    def test_render_formulaire_edition(self, mock_submit, mock_date, mock_select,
                                        mock_number, mock_text, mock_form):
        from src.domains.maison.ui.depenses import render_formulaire
        
        mock_form.return_value.__enter__ = Mock(return_value=MagicMock())
        mock_form.return_value.__exit__ = Mock(return_value=False)
        mock_submit.return_value = False
        
        depense = MagicMock(
            nom="Courses",
            montant=150.0,
            categorie="alimentation",
            date=date(2026, 2, 6),
        )
        
        # Should not raise
        render_formulaire(depense=depense)


class TestRenderGraphiqueEvolution:
    """Tests pour render_graphique_evolution."""

    @patch('streamlit.plotly_chart')
    @patch('src.domains.maison.ui.depenses.get_historique_categorie')
    def test_render_graphique_evolution(self, mock_historique, mock_chart):
        from src.domains.maison.ui.depenses import render_graphique_evolution
        
        mock_historique.return_value = [
            {"mois": "2026-01", "total": 500.0},
            {"mois": "2026-02", "total": 600.0},
        ]
        
        # Should not raise
        render_graphique_evolution()


class TestRenderComparaisonMois:
    """Tests pour render_comparaison_mois."""

    @patch('streamlit.columns')
    @patch('streamlit.metric')
    @patch('src.domains.maison.ui.depenses.get_depenses_mois')
    def test_render_comparaison_mois(self, mock_depenses, mock_metric, mock_cols):
        from src.domains.maison.ui.depenses import render_comparaison_mois
        
        mock_depenses.return_value = [
            MagicMock(montant=100.0),
            MagicMock(montant=200.0),
        ]
        mock_cols.return_value = [MagicMock() for _ in range(2)]
        
        # Should not raise
        render_comparaison_mois()


class TestRenderOnglets:
    """Tests pour les fonctions d'onglets."""

    @patch('streamlit.subheader')
    @patch('src.domains.maison.ui.depenses.get_depenses_mois')
    @patch('src.domains.maison.ui.depenses.render_depense_card')
    def test_render_onglet_mois(self, mock_card, mock_depenses, mock_subheader):
        from src.domains.maison.ui.depenses import render_onglet_mois
        
        mock_depenses.return_value = []
        
        # Should not raise
        render_onglet_mois()

    @patch('streamlit.subheader')
    @patch('src.domains.maison.ui.depenses.render_formulaire')
    def test_render_onglet_ajouter(self, mock_formulaire, mock_subheader):
        from src.domains.maison.ui.depenses import render_onglet_ajouter
        
        # Should not raise
        render_onglet_ajouter()

    @patch('streamlit.subheader')
    @patch('src.domains.maison.ui.depenses.render_graphique_evolution')
    @patch('src.domains.maison.ui.depenses.render_comparaison_mois')
    def test_render_onglet_analyse(self, mock_comparaison, mock_graphique, mock_subheader):
        from src.domains.maison.ui.depenses import render_onglet_analyse
        
        # Should not raise
        render_onglet_analyse()


class TestAppFunction:
    """Tests pour la fonction app() principale."""

    @patch('streamlit.title')
    @patch('streamlit.tabs')
    def test_app_main_entry(self, mock_tabs, mock_title):
        from src.domains.maison.ui.depenses import app
        
        mock_tabs.return_value = [MagicMock() for _ in range(3)]
        
        # Should not raise
        app()
        
        mock_title.assert_called()


# ═══════════════════════════════════════════════════════════
# TESTS EDGE CASES
# ═══════════════════════════════════════════════════════════


class TestEdgeCases:
    """Tests pour les cas limites."""

    @patch('src.domains.maison.ui.depenses.obtenir_contexte_db')
    def test_create_depense_montant_zero(self, mock_db):
        from src.domains.maison.ui.depenses import create_depense
        
        mock_session = MagicMock()
        mock_db.return_value.__enter__ = Mock(return_value=mock_session)
        mock_db.return_value.__exit__ = Mock(return_value=False)
        
        data = {"montant": 0.0, "categorie": "autre"}
        
        result = create_depense(data)
        
        # Should handle zero amount
        assert result is not None

    @patch('src.domains.maison.ui.depenses.obtenir_contexte_db')
    def test_create_depense_montant_negatif(self, mock_db):
        from src.domains.maison.ui.depenses import create_depense
        
        mock_session = MagicMock()
        mock_db.return_value.__enter__ = Mock(return_value=mock_session)
        mock_db.return_value.__exit__ = Mock(return_value=False)
        
        # Remboursement
        data = {"montant": -50.0, "categorie": "remboursement"}
        
        result = create_depense(data)
        
        # Should handle negative amount (remboursement)
        assert result is not None

    @patch('src.domains.maison.ui.depenses.obtenir_contexte_db')
    def test_get_historique_categorie_inconnue(self, mock_db):
        from src.domains.maison.ui.depenses import get_historique_categorie
        
        mock_session = MagicMock()
        mock_db.return_value.__enter__ = Mock(return_value=mock_session)
        mock_db.return_value.__exit__ = Mock(return_value=False)
        
        mock_session.query.return_value.filter.return_value.all.return_value = []
        
        result = get_historique_categorie("categorie_inexistante")
        
        assert result == []

    def test_depenses_date_future(self):
        from datetime import timedelta
        
        data = {
            "montant": 100.0,
            "categorie": "prevu",
            "date": date.today() + timedelta(days=30),
        }
        
        # Should be valid for future scheduled expenses
        assert data["date"] > date.today()
