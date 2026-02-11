"""
Tests unitaires pour alertes.py

Module: src.ui.components.alertes
Fonctions: alerte_stock
"""

import pytest
from unittest.mock import MagicMock, patch


class TestAlerteStock:
    """Tests pour alerte_stock()."""

    @patch("streamlit.container")
    @patch("streamlit.warning")
    @patch("streamlit.info")
    def test_alert_critique(self, mock_info, mock_warning, mock_container):
        """Test alerte stock critique."""
        from src.ui.components.alertes import alerte_stock
        
        mock_container.return_value.__enter__ = MagicMock()
        mock_container.return_value.__exit__ = MagicMock()
        
        articles = [{"nom": "Lait", "statut": "critique"}]
        alerte_stock(articles)
        
        mock_warning.assert_called_once()
        assert "Lait" in str(mock_warning.call_args)

    @patch("streamlit.container")
    @patch("streamlit.warning")
    @patch("streamlit.info")
    def test_alert_peremption_proche(self, mock_info, mock_warning, mock_container):
        """Test alerte péremption proche."""
        from src.ui.components.alertes import alerte_stock
        
        mock_container.return_value.__enter__ = MagicMock()
        mock_container.return_value.__exit__ = MagicMock()
        
        articles = [{"nom": "Yaourt", "statut": "peremption_proche"}]
        alerte_stock(articles)
        
        mock_info.assert_called_once()
        assert "Yaourt" in str(mock_info.call_args)

    @patch("streamlit.container")
    @patch("streamlit.warning")
    @patch("streamlit.info")
    def test_alert_liste_vide(self, mock_info, mock_warning, mock_container):
        """Test alerte avec liste vide - ne fait rien."""
        from src.ui.components.alertes import alerte_stock
        
        alerte_stock([])
        
        mock_container.assert_not_called()
        mock_warning.assert_not_called()
        mock_info.assert_not_called()

    @patch("streamlit.container")
    @patch("streamlit.warning")
    @patch("streamlit.info")
    def test_alert_statut_inconnu(self, mock_info, mock_warning, mock_container):
        """Test alerte avec statut inconnu - n'affiche rien."""
        from src.ui.components.alertes import alerte_stock
        
        mock_container.return_value.__enter__ = MagicMock()
        mock_container.return_value.__exit__ = MagicMock()
        
        articles = [{"nom": "Produit", "statut": "unknown"}]
        alerte_stock(articles)
        
        # Pas d'alerte affichée pour statut inconnu
        mock_warning.assert_not_called()
        mock_info.assert_not_called()

    @patch("streamlit.container")
    @patch("streamlit.warning")
    @patch("streamlit.info")
    def test_alert_nom_manquant(self, mock_info, mock_warning, mock_container):
        """Test alerte avec nom manquant - utilise valeur par défaut."""
        from src.ui.components.alertes import alerte_stock
        
        mock_container.return_value.__enter__ = MagicMock()
        mock_container.return_value.__exit__ = MagicMock()
        
        articles = [{"statut": "critique"}]  # Pas de nom
        alerte_stock(articles)
        
        mock_warning.assert_called_once()
        assert "Article sans nom" in str(mock_warning.call_args)

    @patch("streamlit.container")
    @patch("streamlit.warning")
    @patch("streamlit.info")
    def test_alert_multiple_articles(self, mock_info, mock_warning, mock_container):
        """Test avec plusieurs articles de statuts différents."""
        from src.ui.components.alertes import alerte_stock
        
        mock_container.return_value.__enter__ = MagicMock()
        mock_container.return_value.__exit__ = MagicMock()
        
        articles = [
            {"nom": "Lait", "statut": "critique"},
            {"nom": "Yaourt", "statut": "peremption_proche"},
            {"nom": "Beurre", "statut": "critique"}
        ]
        alerte_stock(articles)
        
        # 2 critiques + 1 péremption
        assert mock_warning.call_count == 2
        assert mock_info.call_count == 1

    def test_import_from_components(self):
        """Vérifie l'import depuis components."""
        from src.ui.components import alerte_stock
        assert callable(alerte_stock)

    def test_import_from_ui(self):
        """Vérifie l'import depuis ui."""
        from src.ui import alerte_stock
        assert callable(alerte_stock)
