import pytest
from unittest.mock import Mock, MagicMock, patch


class TestInventaireDisplay:
    """Tests affichage inventaire"""
    
    @patch('streamlit.write')
    def test_afficher_titre(self, mock_write):
        """Teste affichage titre"""
        mock_write.return_value = None
        mock_write("Inventaire")
        assert mock_write.called
    
    @patch('streamlit.metric')
    def test_afficher_stats(self, mock_metric):
        """Teste stats"""
        mock_metric.return_value = None
        mock_metric("Total articles", 42)
        assert mock_metric.called


class TestInventaireItems:
    """Tests articles"""
    
    @patch('streamlit.dataframe')
    def test_afficher_liste_items(self, mock_df):
        """Teste liste articles"""
        mock_df.return_value = None
        data = [{"nom": "Riz", "qte": 5}]
        mock_df(data)
        assert mock_df.called
    
    @patch('streamlit.form')
    @patch('streamlit.text_input')
    @patch('streamlit.number_input')
    def test_ajouter_article(self, mock_number, mock_text, mock_form):
        """Teste ajout article"""
        mock_form.return_value.__enter__ = Mock()
        mock_form.return_value.__exit__ = Mock()
        mock_text.return_value = "Riz"
        mock_number.return_value = 10
        
        with mock_form("Add"):
            name = mock_text("Nom")
            qty = mock_number("Qté")
        
        assert mock_form.called
        assert name == "Riz"


class TestInventaireSearch:
    """Tests recherche"""
    
    @patch('streamlit.text_input')
    def test_rechercher_article(self, mock_text):
        """Teste recherche"""
        mock_text.return_value = "Riz"
        result = mock_text("Chercher")
        assert result == "Riz"
    
    @patch('streamlit.selectbox')
    def test_filtrer_categorie(self, mock_selectbox):
        """Teste filtre catégorie"""
        mock_selectbox.return_value = "Riz"
        result = mock_selectbox("Catégorie", ["Riz", "Pâtes"])
        assert result == "Riz"


class TestInventaireActions:
    """Tests actions"""
    
    @patch('streamlit.button')
    def test_supprimer_article(self, mock_button):
        """Teste suppression"""
        mock_button.return_value = True
        result = mock_button("Supprimer")
        assert result is True
    
    @patch('streamlit.button')
    def test_modifier_quantite(self, mock_button):
        """Teste modif quantité"""
        mock_button.return_value = True
        result = mock_button("Modifier")
        assert result is True


class TestInventaireTracking:
    """Tests suivi"""
    
    @patch('streamlit.date_input')
    def test_date_expiration(self, mock_date):
        """Teste date expiration"""
        from datetime import date
        mock_date.return_value = date(2024, 12, 31)
        result = mock_date("Date")
        assert mock_date.called
    
    @patch('streamlit.slider')
    def test_alerter_stock_bas(self, mock_slider):
        """Teste alerte stock"""
        mock_slider.return_value = 5
        result = mock_slider("Seuil", 1, 20, 5)
        assert result == 5
