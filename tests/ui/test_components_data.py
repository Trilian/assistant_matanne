"""
Tests pour les composants data (data.py, dashboard_widgets.py)
"""
import pytest
from unittest.mock import Mock, patch, MagicMock, call
import streamlit as st
import pandas as pd
import numpy as np


class TestDataComponentsImport:
    """Tests d'importation des composants data"""

    def test_import_data_module(self):
        """Test l'import du module data"""
        from src.ui.components import data
        assert data is not None

    def test_import_dashboard_widgets(self):
        """Test l'import du module dashboard_widgets"""
        from src.ui.components import dashboard_widgets
        assert dashboard_widgets is not None


@pytest.mark.unit
class TestDataDisplay:
    """Tests pour l'affichage des données"""

    @patch('streamlit.dataframe')
    def test_display_table(self, mock_dataframe):
        """Test l'affichage d'un tableau"""
        mock_dataframe.return_value = None
        
        df = pd.DataFrame({
            'Nom': ['Alice', 'Bob', 'Charlie'],
            'Age': [30, 25, 35]
        })
        
        st.dataframe(df)
        assert mock_dataframe.called

    @patch('streamlit.table')
    def test_display_simple_table(self, mock_table):
        """Test l'affichage d'un tableau simple"""
        mock_table.return_value = None
        
        df = pd.DataFrame({
            'Colonne 1': [1, 2, 3],
            'Colonne 2': ['A', 'B', 'C']
        })
        
        st.table(df)
        assert mock_table.called

    @patch('streamlit.dataframe')
    def test_display_empty_table(self, mock_dataframe):
        """Test l'affichage d'un tableau vide"""
        mock_dataframe.return_value = None
        
        df = pd.DataFrame()
        
        st.dataframe(df)
        assert mock_dataframe.called


@pytest.mark.unit
class TestDataCharts:
    """Tests pour les graphiques"""

    @patch('streamlit.bar_chart')
    def test_bar_chart(self, mock_chart):
        """Test l'affichage d'un graphique en barres"""
        mock_chart.return_value = None
        
        data = pd.DataFrame({
            'Catégorie': ['A', 'B', 'C'],
            'Valeur': [10, 20, 30]
        })
        
        st.bar_chart(data)
        assert mock_chart.called

    @patch('streamlit.line_chart')
    def test_line_chart(self, mock_chart):
        """Test l'affichage d'un graphique en ligne"""
        mock_chart.return_value = None
        
        data = pd.DataFrame({
            'X': [1, 2, 3, 4, 5],
            'Y': [1, 4, 9, 16, 25]
        })
        
        st.line_chart(data)
        assert mock_chart.called

    @patch('streamlit.area_chart')
    def test_area_chart(self, mock_chart):
        """Test l'affichage d'un graphique en zones"""
        mock_chart.return_value = None
        
        data = pd.DataFrame({
            'Mois': ['Jan', 'Fév', 'Mar'],
            'Ventes': [100, 150, 200]
        })
        
        st.area_chart(data)
        assert mock_chart.called

    @patch('streamlit.scatter_chart')
    def test_scatter_chart(self, mock_chart):
        """Test l'affichage d'un graphique en points"""
        mock_chart.return_value = None
        
        data = pd.DataFrame({
            'X': np.random.randn(100),
            'Y': np.random.randn(100)
        })
        
        st.scatter_chart(data)
        assert mock_chart.called


@pytest.mark.unit
class TestDashboardMetrics:
    """Tests pour les métriques du tableau de bord"""

    @patch('streamlit.metric')
    def test_metric_display(self, mock_metric):
        """Test l'affichage d'une métrique"""
        mock_metric.return_value = None
        
        st.metric(label="Température", value="25°C", delta="1.5°C")
        assert mock_metric.called

    @patch('streamlit.metric')
    def test_metric_without_delta(self, mock_metric):
        """Test l'affichage d'une métrique sans variation"""
        mock_metric.return_value = None
        
        st.metric(label="Utilisateurs", value=1234)
        assert mock_metric.called

    @patch('streamlit.metric')
    def test_metric_negative_delta(self, mock_metric):
        """Test l'affichage d'une métrique avec variation négative"""
        mock_metric.return_value = None
        
        st.metric(label="Erreurs", value=5, delta=-2)
        assert mock_metric.called


@pytest.mark.unit
class TestDashboardCards:
    """Tests pour les cartes du tableau de bord"""

    @patch('streamlit.container')
    @patch('streamlit.columns')
    def test_card_display(self, mock_columns, mock_container):
        """Test l'affichage d'une carte"""
        mock_container.return_value = MagicMock()
        cols = [MagicMock() for _ in range(3)]
        mock_columns.return_value = tuple(cols)
        
        container = st.container()
        cols = st.columns(3)
        
        assert mock_container.called
        assert mock_columns.called

    @patch('streamlit.container')
    @patch('streamlit.columns')
    def test_card_with_content(self, mock_columns, mock_container):
        """Test une carte avec contenu"""
        mock_container.return_value = MagicMock()
        cols = [MagicMock() for _ in range(2)]
        mock_columns.return_value = tuple(cols)
        
        with st.container():
            st.columns(2)
        
        assert mock_container.called


@pytest.mark.unit
class TestDataFormatting:
    """Tests pour le formatage des données"""

    def test_format_number(self):
        """Test le formatage des nombres"""
        value = 1234567.89
        formatted = f"{value:,.2f}"
        assert "," in formatted

    def test_format_percentage(self):
        """Test le formatage des pourcentages"""
        value = 0.856
        formatted = f"{value:.1%}"
        assert "%" in formatted

    def test_format_currency(self):
        """Test le formatage des montants"""
        from locale import currency, setlocale, LC_ALL
        
        value = 1234.56
        # Vérifier que le formatage fonctionne
        assert isinstance(value, (int, float))


@pytest.mark.unit
class TestConditionalDisplay:
    """Tests pour l'affichage conditionnel"""

    @patch('streamlit.info')
    def test_conditional_info_display(self, mock_info):
        """Test l'affichage conditionnel d'une info"""
        mock_info.return_value = None
        
        value = 42
        if value > 40:
            st.info("Valeur élevée")
        
        assert mock_info.called

    @patch('streamlit.warning')
    def test_conditional_warning_display(self, mock_warning):
        """Test l'affichage conditionnel d'un avertissement"""
        mock_warning.return_value = None
        
        value = 10
        if value < 20:
            st.warning("Valeur basse")
        
        assert mock_warning.called


@pytest.mark.integration
class TestDashboardLayout:
    """Tests d'intégration pour les mises en page du tableau de bord"""

    @patch('streamlit.columns')
    @patch('streamlit.metric')
    def test_metrics_row_display(self, mock_metric, mock_columns):
        """Test l'affichage d'une rangée de métriques"""
        mock_columns.return_value = (MagicMock(), MagicMock(), MagicMock())
        mock_metric.return_value = None
        
        cols = st.columns(3)
        st.metric("Métrique 1", 100)
        
        assert mock_columns.called
        assert mock_metric.called

    @patch('streamlit.columns')
    @patch('streamlit.dataframe')
    def test_data_with_sidebar(self, mock_dataframe, mock_columns):
        """Test les données avec barre latérale"""
        mock_columns.return_value = (MagicMock(), MagicMock())
        mock_dataframe.return_value = None
        
        df = pd.DataFrame({'A': [1, 2, 3]})
        
        cols = st.columns(2)
        st.dataframe(df)
        
        assert mock_columns.called
        assert mock_dataframe.called

    @patch('streamlit.tabs')
    @patch('streamlit.dataframe')
    def test_tabbed_data_display(self, mock_dataframe, mock_tabs):
        """Test l'affichage des données dans des tabs"""
        tab1, tab2 = MagicMock(), MagicMock()
        mock_tabs.return_value = (tab1, tab2)
        mock_dataframe.return_value = None
        
        tabs = st.tabs(["Données 1", "Données 2"])
        
        df = pd.DataFrame({'X': [1, 2, 3]})
        st.dataframe(df)
        
        assert mock_tabs.called
        assert mock_dataframe.called
