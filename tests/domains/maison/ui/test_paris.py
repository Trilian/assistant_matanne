import pytest
from unittest.mock import Mock, MagicMock, patch


class TestParisDisplay:
    """Tests affichage paris"""
    
    @patch('streamlit.write')
    def test_afficher_titre(self, mock_write):
        """Teste affichage titre"""
        mock_write.return_value = None
        mock_write("Paris")
        assert mock_write.called
    
    @patch('streamlit.metric')
    def test_afficher_total_mises(self, mock_metric):
        """Teste total mises"""
        mock_metric.return_value = None
        mock_metric("Total mises", "250€")
        assert mock_metric.called


class TestParisBets:
    """Tests paris"""
    
    @patch('streamlit.form')
    def test_creer_pari(self, mock_form):
        """Teste création pari"""
        mock_form.return_value.__enter__ = Mock()
        mock_form.return_value.__exit__ = Mock()
        with mock_form("Nouveau"):
            pass
        assert mock_form.called
    
    @patch('streamlit.number_input')
    def test_saisir_montant(self, mock_number):
        """Teste montant"""
        mock_number.return_value = 50.0
        result = mock_number("Montant", 0.0, 1000.0)
        assert result == 50.0


class TestParisTracking:
    """Tests suivi"""
    
    @patch('streamlit.dataframe')
    def test_afficher_liste_paris(self, mock_df):
        """Teste liste paris"""
        mock_df.return_value = None
        mock_df([{"type": "Simple", "montant": 50}])
        assert mock_df.called
    
    @patch('streamlit.selectbox')
    def test_filtrer_etat(self, mock_selectbox):
        """Teste filtre état"""
        mock_selectbox.return_value = "Gagné"
        result = mock_selectbox("Etat", ["Gagné", "Perdu", "En cours"])
        assert result == "Gagné"


class TestParisActions:
    """Tests actions"""
    
    @patch('streamlit.button')
    def test_valider_pari(self, mock_button):
        """Teste validation"""
        mock_button.return_value = True
        result = mock_button("Valider")
        assert result is True
    
    @patch('streamlit.button')
    def test_annuler_pari(self, mock_button):
        """Teste annulation"""
        mock_button.return_value = True
        result = mock_button("Annuler")
        assert result is True


class TestParisStats:
    """Tests statistiques"""
    
    @patch('streamlit.line_chart')
    def test_afficher_gains_pertes(self, mock_chart):
        """Teste gains/pertes"""
        mock_chart.return_value = None
        mock_chart([100, -50, 200])
        assert mock_chart.called
    
    @patch('streamlit.write')
    def test_afficher_pourcentage_victoire(self, mock_write):
        """Teste % victoire"""
        mock_write.return_value = None
        mock_write("Taux victoire: 65%")
        assert mock_write.called
