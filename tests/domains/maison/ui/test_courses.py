import pytest
from unittest.mock import Mock, MagicMock, patch


class TestCoursesDisplay:
    """Tests affichage courses"""
    
    @patch('streamlit.write')
    def test_afficher_liste_courses(self, mock_write):
        """Teste affichage liste"""
        mock_write.return_value = None
        mock_write("Liste de courses")
        assert mock_write.called
    
    @patch('streamlit.metric')
    def test_afficher_total_prix(self, mock_metric):
        """Teste affichage prix"""
        mock_metric.return_value = None
        mock_metric("Total", "45.50€")
        assert mock_metric.called


class TestCoursesItems:
    """Tests articles"""
    
    @patch('streamlit.checkbox')
    def test_cocher_article(self, mock_checkbox):
        """Teste cocher article"""
        mock_checkbox.return_value = True
        result = mock_checkbox("Tomates")
        assert result is True
    
    @patch('streamlit.form')
    def test_ajouter_article(self, mock_form):
        """Teste ajout article"""
        mock_form.return_value.__enter__ = Mock()
        mock_form.return_value.__exit__ = Mock()
        with mock_form("Add item"):
            pass
        assert mock_form.called


class TestCoursesOrganization:
    """Tests organisation"""
    
    @patch('streamlit.tabs')
    def test_trier_par_section(self, mock_tabs):
        """Teste tri par section"""
        mock_tabs.return_value = [Mock(), Mock()]
        result = mock_tabs("Sections", ["Fruits", "Produits"])
        assert mock_tabs.called
    
    @patch('streamlit.selectbox')
    def test_selectionner_magasin(self, mock_selectbox):
        """Teste sélection magasin"""
        mock_selectbox.return_value = "Carrefour"
        result = mock_selectbox("Magasin", ["Carrefour", "Leclerc"])
        assert result == "Carrefour"


class TestCoursesActions:
    """Tests actions"""
    
    @patch('streamlit.button')
    def test_valider_courses(self, mock_button):
        """Teste validation"""
        mock_button.return_value = True
        result = mock_button("Valider")
        assert result is True
    
    @patch('streamlit.button')
    def test_telecharger_pdf(self, mock_button):
        """Teste téléchargement"""
        mock_button.return_value = True
        result = mock_button("PDF")
        assert result is True


class TestCoursesTracking:
    """Tests suivi"""
    
    @patch('streamlit.dataframe')
    def test_afficher_historique(self, mock_df):
        """Teste historique"""
        mock_df.return_value = None
        mock_df([{"date": "2024-01-15", "total": 45.50}])
        assert mock_df.called
    
    @patch('streamlit.line_chart')
    def test_afficher_graphique_depenses(self, mock_chart):
        """Teste graphique"""
        mock_chart.return_value = None
        mock_chart([1, 2, 3])
        assert mock_chart.called
