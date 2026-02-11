"""
Tests unitaires pour src/ui/layout/footer.py
"""

import pytest
from unittest.mock import MagicMock, patch


class TestAfficherFooter:
    """Tests pour afficher_footer()."""

    def test_import(self):
        """Test import réussi."""
        from src.ui.layout.footer import afficher_footer
        assert afficher_footer is not None

    @patch("src.ui.layout.footer.st")
    @patch("src.ui.layout.footer.obtenir_parametres")
    def test_afficher_footer_renders(self, mock_params, mock_st):
        """Test que le footer se rend."""
        from src.ui.layout.footer import afficher_footer
        
        mock_params.return_value = MagicMock(
            APP_NAME="Matanne",
            APP_VERSION="1.0.0"
        )
        mock_st.columns.return_value = [MagicMock(), MagicMock(), MagicMock()]
        mock_st.button.return_value = False
        
        afficher_footer()
        
        mock_st.markdown.assert_called()
        mock_st.columns.assert_called()

    @patch("src.ui.layout.footer.st")
    @patch("src.ui.layout.footer.obtenir_parametres")
    def test_footer_caption(self, mock_params, mock_st):
        """Test caption dans footer."""
        from src.ui.layout.footer import afficher_footer
        
        mock_params.return_value = MagicMock(
            APP_NAME="TestApp",
            APP_VERSION="2.0"
        )
        mock_st.columns.return_value = [MagicMock(), MagicMock(), MagicMock()]
        mock_st.button.return_value = False
        
        afficher_footer()
        
        mock_st.caption.assert_called()
        call_args = str(mock_st.caption.call_args)
        assert "TestApp" in call_args or "Lazy Loading" in call_args

    @patch("src.ui.layout.footer.st")
    @patch("src.ui.layout.footer.obtenir_parametres")
    def test_footer_bug_button(self, mock_params, mock_st):
        """Test bouton bug."""
        from src.ui.layout.footer import afficher_footer
        
        mock_params.return_value = MagicMock(APP_NAME="T", APP_VERSION="1")
        mock_st.columns.return_value = [MagicMock(), MagicMock(), MagicMock()]
        mock_st.button.side_effect = [True, False]  # Bug clicked
        
        afficher_footer()
        
        mock_st.info.assert_called()

    @patch("src.ui.layout.footer.st")
    @patch("src.ui.layout.footer.obtenir_parametres")
    def test_footer_about_expander(self, mock_params, mock_st):
        """Test expander À propos."""
        from src.ui.layout.footer import afficher_footer
        
        mock_params.return_value = MagicMock(APP_NAME="T", APP_VERSION="1")
        mock_st.columns.return_value = [MagicMock(), MagicMock(), MagicMock()]
        mock_st.button.side_effect = [False, True]  # About clicked
        mock_st.expander.return_value.__enter__ = MagicMock()
        mock_st.expander.return_value.__exit__ = MagicMock()
        
        afficher_footer()
        
        mock_st.expander.assert_called()
