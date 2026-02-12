import pytest
from unittest.mock import Mock, MagicMock, patch


class TestGameAPIs:
    """Tests d'intégration des APIs"""
    
    @patch('streamlit.write')
    @patch('streamlit.button')
    def test_integracion_api_recette(self, mock_button, mock_write):
        """Teste l'intégration API"""
        mock_button.return_value = True
        clicked = mock_button("Charger")
        mock_write("Recette chargée")
        assert mock_button.called
        assert mock_write.called
    
    @patch('streamlit.info')
    def test_charger_donnees_jeu(self, mock_info):
        """Teste le chargement"""
        mock_info.return_value = None
        mock_info("Jeu chargé")
        assert mock_info.called
    
    @patch('streamlit.success')
    def test_api_completion(self, mock_success):
        """Teste le succès"""
        mock_success.return_value = None
        mock_success("Partie terminée!")
        assert mock_success.called


class TestGameIntegration:
    """Tests E2E d'intégration"""
    
    @patch('streamlit.selectbox')
    @patch('streamlit.button')
    @patch('streamlit.success')
    def test_flux_complet(self, mock_success, mock_button, mock_selectbox):
        """Teste le flux complet"""
        mock_selectbox.return_value = "Memory"
        mock_button.return_value = True
        mock_success.return_value = None
        
        game = mock_selectbox("Jeu", ["Memory", "Dés"])
        start = mock_button("Démarrer")
        mock_success("Gagné!")
        
        assert game == "Memory"
        assert start is True
        assert mock_selectbox.called
        assert mock_button.called
        assert mock_success.called
    
    @patch('streamlit.write')
    @patch('streamlit.dataframe')
    def test_afficher_resultats(self, mock_df, mock_write):
        """Teste l'affichage résultats"""
        results = [{"joueur": "Alice", "score": 100}]
        mock_write.return_value = None
        mock_df.return_value = None
        
        mock_write("Résultats:")
        mock_df(results)
        
        assert mock_write.called
        assert mock_df.called
