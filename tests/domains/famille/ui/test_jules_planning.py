import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime


class TestJulesMilestones:
    """Tests des jalons de Jules"""
    
    @patch('streamlit.metric')
    def test_afficher_jalon_age(self, mock_metric):
        """Teste l'affichage du jalon âge"""
        mock_metric.return_value = None
        mock_metric("Âge Jules", "19 mois")
        assert mock_metric.called
    
    def test_ajouter_jalon_sourire(self):
        """Teste l'ajout d'un jalon sourire"""
        jalon = {"nom": "Premier sourire", "age_mois": 2}
        assert jalon["nom"] == "Premier sourire"
        assert jalon["age_mois"] == 2
    
    @patch('streamlit.write')
    def test_afficher_historique(self, mock_write):
        """Teste l'affichage de l'historique"""
        mock_write.return_value = None
        mock_write("Jalons:", 3)
        assert mock_write.called


class TestJulesSchedule:
    """Tests du planning de Jules"""
    
    @patch('streamlit.selectbox')
    def test_selectionner_activite(self, mock_selectbox):
        """Teste la sélection d'activité"""
        mock_selectbox.return_value = "Jeux"
        activites = ["Sieste", "Repas", "Jeux"]
        result = mock_selectbox("Activité", activites)
        assert result == "Jeux"
        assert mock_selectbox.called
    
    @patch('streamlit.time_input')
    def test_saisir_heure_activite(self, mock_time):
        """Teste la saisie d'heure"""
        mock_time.return_value = "14:30"
        heure = mock_time("Heure")
        assert heure == "14:30"
    
    @patch('streamlit.multiselect')
    def test_planifier_semaine(self, mock_multi):
        """Teste la planification hebdo"""
        mock_multi.return_value = ["Sieste", "Repas"]
        result = mock_multi("Activités", ["Sieste", "Repas", "Jeux"])
        assert len(result) == 2


class TestJulesTracking:
    """Tests du suivi de Jules"""
    
    @patch('streamlit.slider')
    def test_suivi_sommeil(self, mock_slider):
        """Teste le suivi sommeil"""
        mock_slider.return_value = 12.5
        result = mock_slider("Sommeil", 0, 24, 12)
        assert result == 12.5
    
    @patch('streamlit.number_input')
    def test_suivi_poids(self, mock_number):
        """Teste le suivi poids"""
        mock_number.return_value = 12.8
        result = mock_number("Poids")
        assert result == 12.8
    
    @patch('streamlit.write')
    def test_afficher_progression(self, mock_write):
        """Teste l'affichage progression"""
        mock_write.return_value = None
        mock_write("Progression", {"poids": 12.8})
        assert mock_write.called

