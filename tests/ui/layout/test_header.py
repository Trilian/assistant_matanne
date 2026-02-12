"""
Tests unitaires pour src/ui/layout/header.py
"""

import pytest
from unittest.mock import MagicMock, patch


class TestAfficherHeader:
    """Tests pour afficher_header()."""

    def test_import(self):
        """Test import réussi."""
        from src.ui.layout.header import afficher_header
        assert afficher_header is not None

    @patch("src.ui.layout.header.st")
    @patch("src.ui.layout.header.badge")
    @patch("src.ui.layout.header.obtenir_etat")
    @patch("src.ui.layout.header.obtenir_parametres")
    def test_afficher_header_renders(self, mock_params, mock_etat, mock_badge, mock_st):
        """Test que le header se rend."""
        from src.ui.layout.header import afficher_header
        
        mock_params.return_value = MagicMock(APP_NAME="Matanne")
        mock_etat.return_value = MagicMock(agent_ia=True, notifications_non_lues=0)
        mock_st.columns.return_value = [MagicMock(), MagicMock(), MagicMock()]
        
        afficher_header()
        
        mock_st.markdown.assert_called()
        mock_st.columns.assert_called()

    @patch("src.ui.layout.header.st")
    @patch("src.ui.layout.header.badge")
    @patch("src.ui.layout.header.obtenir_etat")
    @patch("src.ui.layout.header.obtenir_parametres")
    def test_header_ia_active_badge(self, mock_params, mock_etat, mock_badge, mock_st):
        """Test badge IA active."""
        from src.ui.layout.header import afficher_header
        
        mock_params.return_value = MagicMock(APP_NAME="T")
        mock_etat.return_value = MagicMock(agent_ia=True, notifications_non_lues=0)
        mock_st.columns.return_value = [MagicMock(), MagicMock(), MagicMock()]
        
        afficher_header()
        
        mock_badge.assert_called_with("ðŸ¤– IA Active", "#4CAF50")

    @patch("src.ui.layout.header.st")
    @patch("src.ui.layout.header.badge")
    @patch("src.ui.layout.header.obtenir_etat")
    @patch("src.ui.layout.header.obtenir_parametres")
    def test_header_ia_inactive_badge(self, mock_params, mock_etat, mock_badge, mock_st):
        """Test badge IA indisponible."""
        from src.ui.layout.header import afficher_header
        
        mock_params.return_value = MagicMock(APP_NAME="T")
        mock_etat.return_value = MagicMock(agent_ia=None, notifications_non_lues=0)
        mock_st.columns.return_value = [MagicMock(), MagicMock(), MagicMock()]
        
        afficher_header()
        
        mock_badge.assert_called_with("ðŸ¤– IA Indispo", "#FFC107")

    @patch("src.ui.layout.header.st")
    @patch("src.ui.layout.header.badge")
    @patch("src.ui.layout.header.obtenir_etat")
    @patch("src.ui.layout.header.obtenir_parametres")
    def test_header_notifications(self, mock_params, mock_etat, mock_badge, mock_st):
        """Test affichage notifications."""
        from src.ui.layout.header import afficher_header
        
        mock_params.return_value = MagicMock(APP_NAME="T")
        mock_etat.return_value = MagicMock(agent_ia=True, notifications_non_lues=5)
        mock_st.columns.return_value = [MagicMock(), MagicMock(), MagicMock()]
        mock_st.button.return_value = True
        
        afficher_header()
        
        # Button should show notification count
        call = mock_st.button.call_args
        assert "5" in str(call) or "ðŸ””" in str(call)
