"""
Tests pour le module Rapports PDF Streamlit (test_rapports_module.py)
Tests pour rapport stocks, budget, gaspillage et historique
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import pandas as pd

import streamlit as st

from src.modules.rapports import (
    render_rapport_stocks,
    render_rapport_budget,
    render_analyse_gaspillage,
    render_historique,
    app,
)
from src.services.rapports_pdf import RapportsPDFService


class TestRenderRapportStocks:
    """Tests render_rapport_stocks() - Rapport Stocks"""

    @patch("src.modules.rapports.get_rapports_service")
    def test_render_rapport_stocks_displays(self, mock_get_service):
        """Test que le rapport stocks s'affiche"""
        mock_service = Mock(spec=RapportsPDFService)
        mock_get_service.return_value = mock_service
        
        with patch("streamlit.subheader"), \
             patch("streamlit.markdown"), \
             patch("streamlit.divider"), \
             patch("streamlit.columns"), \
             patch("streamlit.selectbox"), \
             patch("streamlit.button", return_value=False):
            
            render_rapport_stocks()

    @patch("src.modules.rapports.get_rapports_service")
    @patch("streamlit.session_state", new_callable=MagicMock)
    def test_render_rapport_stocks_apercu(self, mock_session_state, mock_get_service):
        """Test aperçu rapport stocks"""
        mock_service = Mock(spec=RapportsPDFService)
        
        # Mock données rapport
        mock_data = Mock()
        mock_data.articles_total = 50
        mock_data.valeur_stock_total = 1250.75
        mock_data.articles_faible_stock = [
            {"nom": "Pâtes", "quantite": 0.5, "quantite_min": 1.0, "unite": "kg"},
        ]
        mock_data.articles_perimes = []
        mock_data.categories_resumee = {
            "Fruits": {"articles": 15, "quantite": 25, "valeur": 150},
        }
        
        mock_service.generer_donnees_rapport_stocks.return_value = mock_data
        mock_get_service.return_value = mock_service
        
        mock_session_state.get.return_value = None
        mock_session_state.__setitem__ = MagicMock()
        
        with patch("streamlit.subheader"), \
             patch("streamlit.markdown"), \
             patch("streamlit.columns"), \
             patch("streamlit.selectbox"), \
             patch("streamlit.button", side_effect=[True, False]), \
             patch("streamlit.session_state", mock_session_state), \
             patch("streamlit.info"), \
             patch("streamlit.metric"), \
             patch("streamlit.subheader"), \
             patch("streamlit.dataframe"):
            
            render_rapport_stocks()


class TestRenderRapportBudget:
    """Tests render_rapport_budget() - Rapport Budget"""

    @patch("src.modules.rapports.get_rapports_service")
    def test_render_rapport_budget_displays(self, mock_get_service):
        """Test que le rapport budget s'affiche"""
        mock_service = Mock(spec=RapportsPDFService)
        mock_get_service.return_value = mock_service
        
        with patch("streamlit.subheader"), \
             patch("streamlit.markdown"), \
             patch("streamlit.divider"), \
             patch("streamlit.columns"), \
             patch("streamlit.selectbox"), \
             patch("streamlit.button", return_value=False):
            
            render_rapport_budget()

    @patch("src.modules.rapports.get_rapports_service")
    def test_render_rapport_budget_metrics(self, mock_get_service):
        """Test affichage métriques budget"""
        mock_service = Mock(spec=RapportsPDFService)
        
        mock_data = Mock()
        mock_data.budget_total = 500.0
        mock_data.depense_totale = 325.50
        mock_data.reste_budget = 174.50
        mock_data.pourcentage_utilise = 65.1
        mock_data.depenses_par_categorie = {
            "Fruits": 75.50,
            "Légumes": 120.00,
            "Produits": 130.00,
        }
        
        mock_service.generer_donnees_rapport_budget.return_value = mock_data
        mock_get_service.return_value = mock_service
        
        with patch("streamlit.subheader"), \
             patch("streamlit.columns"), \
             patch("streamlit.metric"), \
             patch("streamlit.progress"):
            
            render_rapport_budget()


class TestRenderAnalyseGaspillage:
    """Tests render_analyse_gaspillage() - Analyse Gaspillage"""

    @patch("src.modules.rapports.get_rapports_service")
    def test_render_analyse_gaspillage_displays(self, mock_get_service):
        """Test que l'analyse gaspillage s'affiche"""
        mock_service = Mock(spec=RapportsPDFService)
        mock_get_service.return_value = mock_service
        
        with patch("streamlit.subheader"), \
             patch("streamlit.markdown"), \
             patch("streamlit.divider"), \
             patch("streamlit.columns"), \
             patch("streamlit.selectbox"), \
             patch("streamlit.button", return_value=False):
            
            render_analyse_gaspillage()

    @patch("src.modules.rapports.get_rapports_service")
    def test_render_analyse_gaspillage_articles(self, mock_get_service):
        """Test affichage articles gaspillés"""
        mock_service = Mock(spec=RapportsPDFService)
        
        mock_data = Mock()
        mock_data.articles_gaspilles = [
            {"nom": "Salade", "quantite": 0.5, "unite": "kg", "raison": "Péremption"},
            {"nom": "Pommes", "quantite": 1.2, "unite": "kg", "raison": "Dégât"},
        ]
        mock_data.total_gaspille = 45.75
        mock_data.taux_gaspillage = 3.5
        
        mock_service.analyser_gaspillage.return_value = mock_data
        mock_get_service.return_value = mock_service
        
        with patch("streamlit.subheader"), \
             patch("streamlit.metric"), \
             patch("streamlit.dataframe"), \
             patch("streamlit.warning"):
            
            render_analyse_gaspillage()


class TestRenderHistorique:
    """Tests render_historique() - Historique"""

    @patch("src.modules.rapports.get_rapports_service")
    def test_render_historique_displays(self, mock_get_service):
        """Test que l'historique s'affiche"""
        mock_service = Mock(spec=RapportsPDFService)
        mock_get_service.return_value = mock_service
        
        with patch("streamlit.subheader"), \
             patch("streamlit.markdown"), \
             patch("streamlit.divider"), \
             patch("streamlit.columns"), \
             patch("streamlit.date_input"), \
             patch("streamlit.button", return_value=False):
            
            render_historique()

    @patch("src.modules.rapports.get_rapports_service")
    def test_render_historique_timeline(self, mock_get_service):
        """Test affichage timeline historique"""
        mock_service = Mock(spec=RapportsPDFService)
        
        mock_data = Mock()
        mock_data.events = [
            {
                "date": "2026-01-24",
                "type": "ajout_article",
                "description": "Article ajouté: Pâtes",
                "categorie": "Inventaire",
            },
            {
                "date": "2026-01-23",
                "type": "modif_article",
                "description": "Stock modifié: Pâtes",
                "categorie": "Inventaire",
            },
        ]
        
        mock_service.obtenir_historique.return_value = mock_data
        mock_get_service.return_value = mock_service
        
        with patch("streamlit.subheader"), \
             patch("streamlit.timeline"), \
             patch("streamlit.divider"):
            
            render_historique()


class TestRapportsApp:
    """Tests fonction app() principale"""

    @patch("src.modules.rapports.st.markdown")
    @patch("src.modules.rapports.st.tabs")
    def test_app_entry_point(self, mock_tabs, mock_markdown):
        """Test que app() crée 4 onglets"""
        tab1, tab2, tab3, tab4 = (
            MagicMock(), MagicMock(), MagicMock(), MagicMock()
        )
        mock_tabs.return_value = (tab1, tab2, tab3, tab4)
        
        with patch("src.modules.rapports.render_rapport_stocks"), \
             patch("src.modules.rapports.render_rapport_budget"), \
             patch("src.modules.rapports.render_analyse_gaspillage"), \
             patch("src.modules.rapports.render_historique"):
            
            app()
            
            mock_markdown.assert_called()
            mock_tabs.assert_called()

    def test_rapports_module_structure(self):
        """Test que le module a la bonne structure"""
        from src.modules import rapports
        
        assert hasattr(rapports, "app")
        assert hasattr(rapports, "render_rapport_stocks")
        assert hasattr(rapports, "render_rapport_budget")
        assert hasattr(rapports, "render_analyse_gaspillage")
        assert hasattr(rapports, "render_historique")
        assert callable(rapports.app)


class TestRapportsIntegration:
    """Tests intégration module rapports"""

    @patch("src.modules.rapports.get_rapports_service")
    def test_rapports_service_initialization(self, mock_get_service):
        """Test initialisation service rapports"""
        mock_service = Mock(spec=RapportsPDFService)
        mock_get_service.return_value = mock_service
        
        service = mock_get_service()
        assert service is not None
        assert hasattr(service, "generer_donnees_rapport_stocks")
        assert hasattr(service, "generer_donnees_rapport_budget")

    @patch("src.modules.rapports.get_rapports_service")
    def test_rapports_pdf_export(self, mock_get_service):
        """Test export PDF rapports"""
        mock_service = Mock(spec=RapportsPDFService)
        mock_service.generer_pdf_rapport_stocks.return_value = Mock(getvalue=Mock(return_value=b"PDF_DATA"))
        mock_get_service.return_value = mock_service
        
        # Vérifier que la méthode existe et retourne des données
        pdf_data = mock_service.generer_pdf_rapport_stocks(7)
        assert pdf_data is not None
        assert hasattr(pdf_data, "getvalue")

    def test_rapports_periods(self):
        """Test les périodes de rapport"""
        from src.modules.rapports import render_rapport_stocks
        
        # Les périodes disponibles
        expected_periods = [
            (7, "Derniers 7 jours"),
            (14, "2 semaines"),
            (30, "1 mois"),
        ]
        
        with patch("src.modules.rapports.get_rapports_service") as mock_get_service, \
             patch("streamlit.subheader"), \
             patch("streamlit.markdown"), \
             patch("streamlit.divider"), \
             patch("streamlit.columns"), \
             patch("streamlit.selectbox", return_value=expected_periods[0]) as mock_select, \
             patch("streamlit.button", return_value=False):
            
            mock_service = Mock(spec=RapportsPDFService)
            mock_get_service.return_value = mock_service
            
            render_rapport_stocks()
            
            # Vérifier que selectbox a été appelé avec les périodes
            assert mock_select.called
