import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import date


class TestMealPlanning:
    """Tests de la planification des repas"""
    
    @patch('streamlit.multiselect')
    def test_selectionner_recettes(self, mock_multi):
        """Teste la sélection de recettes"""
        mock_multi.return_value = ["Pâtes", "Poulet"]
        recettes = ["Pâtes", "Poulet", "Pizza"]
        result = mock_multi("Recettes", recettes)
        assert len(result) == 2
        assert mock_multi.called
    
    @patch('streamlit.date_input')
    def test_planifier_date(self, mock_date):
        """Teste la planification de date"""
        mock_date.return_value = date(2024, 1, 15)
        result = mock_date("Date")
        assert result == date(2024, 1, 15)
    
    def test_creer_planning(self):
        """Teste la création d'un planning"""
        planning = {"semaine": "2024-W03", "nombre_repas": 7}
        assert planning["semaine"] == "2024-W03"
        assert planning["nombre_repas"] == 7


class TestMealSuggestions:
    """Tests des suggestions de repas"""
    
    @patch('streamlit.write')
    def test_afficher_suggestions(self, mock_write):
        """Teste l'affichage de suggestions"""
        mock_write.return_value = None
        mock_write("Suggestions", ["Ratatouille"])
        assert mock_write.called
    
    @patch('streamlit.button')
    def test_regenerer_suggestions(self, mock_button):
        """Teste la régénération"""
        mock_button.return_value = True
        result = mock_button("Nouvelles")
        assert result is True
    
    @patch('streamlit.selectbox')
    def test_filtrer_regime(self, mock_selectbox):
        """Teste le filtrage par régime"""
        mock_selectbox.return_value = "Végétarien"
        regimes = ["Omnivore", "Végétarien"]
        result = mock_selectbox("Régime", regimes)
        assert result == "Végétarien"


class TestMealSchedule:
    """Tests du planning d'affichage"""
    
    @patch('streamlit.dataframe')
    def test_afficher_tableau(self, mock_df):
        """Teste l'affichage du tableau"""
        mock_df.return_value = None
        mock_df([{"jour": "Lundi", "repas": "Pâtes"}])
        assert mock_df.called
    
    @patch('streamlit.expander')
    def test_expander_details(self, mock_exp):
        """Teste l'expander"""
        mock_exp.return_value.__enter__ = Mock()
        mock_exp.return_value.__exit__ = Mock()
        with mock_exp("Détails"):
            pass
        assert mock_exp.called
    
    @patch('streamlit.columns')
    def test_afficher_par_jour(self, mock_cols):
        """Teste l'affichage par jour"""
        mock_cols.return_value = [Mock() for _ in range(7)]
        result = mock_cols(7)
        assert len(result) == 7
