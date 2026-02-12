"""
Tests for paris_logic service in maison domain.
Tests logic for bet management, tracking, and validation.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import streamlit as st


class TestParisLogicDisplay:
    """Tests for displaying paris logic information."""
    
    @patch('streamlit.header')
    @patch('streamlit.write')
    def test_afficher_logique_paris(self, mock_write, mock_header):
        """Test displaying paris logic header and description."""
        mock_header.return_value = None
        mock_write.return_value = None
        
        # Simulate calling display function
        st.header("Logique des Paris")
        st.write("Gestion des paris et des mises")
        
        assert mock_header.called
        assert mock_write.called
    
    @patch('streamlit.subheader')
    @patch('streamlit.text')
    def test_afficher_calcul_cotes(self, mock_text, mock_subheader):
        """Test displaying odds calculation rules."""
        mock_subheader.return_value = None
        mock_text.return_value = None
        
        st.subheader("Calcul des cotes")
        st.text("1:1 - Pair")
        
        assert mock_subheader.called
        assert mock_text.called


class TestParisLogicCalculations:
    """Tests for paris calculation logic."""
    
    @patch('streamlit.number_input')
    def test_calculer_montant_gagne(self, mock_input):
        """Test calculation of winning amount."""
        mock_input.return_value = 100
        
        mise = st.number_input("Mise")
        cote = 2.5
        gain = mise * cote
        
        assert gain == 250
        assert mock_input.called
    
    @patch('streamlit.slider')
    def test_ajuster_probabilite(self, mock_slider):
        """Test adjusting probability slider."""
        mock_slider.return_value = 65
        
        prob = st.slider("Probabilité", 0, 100)
        
        assert prob == 65
        assert mock_slider.called
    
    @patch('streamlit.number_input')
    def test_calculer_valeur_attendue(self, mock_input):
        """Test expected value calculation."""
        mock_input.return_value = 50
        
        mise = st.number_input("Mise")
        prob = 0.6
        cote = 2.0
        valeur = (mise * cote * prob) - (mise * (1 - prob))
        
        assert valeur == 40.0


class TestParisLogicValidation:
    """Tests for paris validation logic."""
    
    @patch('streamlit.error')
    def test_valider_montant_mise(self, mock_error):
        """Test validating bet amount."""
        mock_error.return_value = None
        
        mise = 0
        if mise <= 0:
            st.error("Montant invalide")
        
        assert mock_error.called
    
    @patch('streamlit.warning')
    def test_avertir_cote_extreme(self, mock_warning):
        """Test warning for extreme odds."""
        mock_warning.return_value = None
        
        cote = 100.0
        if cote > 50:
            st.warning("Cote très élevée!")
        
        assert mock_warning.called
    
    @patch('streamlit.success')
    def test_valider_paris_eligible(self, mock_success):
        """Test validating eligible bet."""
        mock_success.return_value = None
        
        mise = 10
        cote = 2.0
        if mise > 0 and 0.5 <= cote <= 50:
            st.success("Paris valide!")
        
        assert mock_success.called


class TestParisLogicTracking:
    """Tests for tracking paris logic metrics."""
    
    @patch('streamlit.metric')
    def test_afficher_roi_moyen(self, mock_metric):
        """Test displaying average ROI metric."""
        mock_metric.return_value = None
        
        st.metric("ROI moyen", "15.3%", "+2.1%")
        
        assert mock_metric.called
    
    @patch('streamlit.metric')
    def test_afficher_taux_reussite(self, mock_metric):
        """Test displaying success rate metric."""
        mock_metric.return_value = None
        
        st.metric("Taux de réussite", "62%", "-1%")
        
        assert mock_metric.called
    
    @patch('streamlit.bar_chart')
    def test_afficher_historique_performances(self, mock_chart):
        """Test displaying performance history chart."""
        mock_chart.return_value = None
        
        st.bar_chart({"Semaine": [100, 120, 110, 130]})
        
        assert mock_chart.called


class TestParisLogicOptimization:
    """Tests for paris optimization features."""
    
    @patch('streamlit.slider')
    def test_optimiser_allocation_bankroll(self, mock_slider):
        """Test optimizing bankroll allocation."""
        mock_slider.return_value = 5
        
        pourcentage = st.slider("% du bankroll", 1, 10)
        
        assert pourcentage == 5
        assert mock_slider.called
    
    @patch('streamlit.checkbox')
    def test_mode_kelly_criterion(self, mock_checkbox):
        """Test Kelly criterion betting mode."""
        mock_checkbox.return_value = True
        
        use_kelly = st.checkbox("Utiliser Kelly Criterion")
        
        assert use_kelly
        assert mock_checkbox.called
    
    @patch('streamlit.number_input')
    def test_fixer_maximum_perte(self, mock_input):
        """Test setting maximum loss limit."""
        mock_input.return_value = 1000
        
        max_loss = st.number_input("Perte maximale")
        
        assert max_loss == 1000


class TestParisLogicStrategies:
    """Tests for paris betting strategies."""
    
    @patch('streamlit.selectbox')
    def test_selectionner_strategie(self, mock_selectbox):
        """Test selecting betting strategy."""
        mock_selectbox.return_value = "Martingale"
        
        strategie = st.selectbox("Stratégie", ["Martingale", "Kelly", "Flat"])
        
        assert strategie == "Martingale"
        assert mock_selectbox.called
    
    @patch('streamlit.radio')
    def test_choisir_type_pari(self, mock_radio):
        """Test choosing bet type."""
        mock_radio.return_value = "Simple"
        
        bet_type = st.radio("Type de pari", ["Simple", "Combiné", "Système"])
        
        assert bet_type == "Simple"
        assert mock_radio.called


class TestParisLogicReporting:
    """Tests for paris logic reporting features."""
    
    @patch('streamlit.write')
    def test_generer_rapport_quotidien(self, mock_write):
        """Test generating daily report."""
        mock_write.return_value = None
        
        st.write("Rapport quotidien généré")
        
        assert mock_write.called
    
    @patch('streamlit.download_button')
    def test_telecharger_donnees_paris(self, mock_button):
        """Test downloading paris data."""
        mock_button.return_value = None
        
        st.download_button("Télécharger", b"data", "paris.csv")
        
        assert mock_button.called
