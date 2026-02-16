"""
Tests unitaires pour src/ui/layout/footer.py
"""

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

        mock_params.return_value = MagicMock(APP_NAME="Matanne", APP_VERSION="1.0.0")

        afficher_footer()

        mock_st.markdown.assert_called_with("---")
        mock_st.caption.assert_called()

    @patch("src.ui.layout.footer.st")
    @patch("src.ui.layout.footer.obtenir_parametres")
    def test_footer_caption_contains_app_info(self, mock_params, mock_st):
        """Test caption dans footer."""
        from src.ui.layout.footer import afficher_footer

        mock_params.return_value = MagicMock(APP_NAME="TestApp", APP_VERSION="2.0")

        afficher_footer()

        mock_st.caption.assert_called()
        call_args = str(mock_st.caption.call_args)
        assert "TestApp" in call_args
        assert "2.0" in call_args

    @patch("src.ui.layout.footer.st")
    @patch("src.ui.layout.footer.obtenir_parametres")
    def test_footer_contains_stack_info(self, mock_params, mock_st):
        """Test que le footer affiche la stack technique."""
        from src.ui.layout.footer import afficher_footer

        mock_params.return_value = MagicMock(APP_NAME="T", APP_VERSION="1")

        afficher_footer()

        call_args = str(mock_st.caption.call_args)
        assert "Streamlit" in call_args or "Supabase" in call_args or "Mistral" in call_args
