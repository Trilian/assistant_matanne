"""
Tests unitaires pour src/ui/layout/styles.py
"""

from unittest.mock import patch


class TestInjecterCss:
    """Tests pour injecter_css()."""

    def test_import(self):
        """Test import réussi."""
        from src.ui.layout.styles import injecter_css

        assert injecter_css is not None

    @patch("src.ui.css.CSSManager.register")
    def test_injecter_css_registers_in_manager(self, mock_register):
        """Test que le CSS est enregistré dans CSSManager."""
        from src.ui.layout.styles import injecter_css

        injecter_css()

        mock_register.assert_called_once()
        name, css = mock_register.call_args[0]
        assert name == "global-styles"
        assert "--primary:" in css
        assert "--accent:" in css

    @patch("src.ui.css.CSSManager.register")
    def test_css_content(self, mock_register):
        """Test que le contenu CSS inclut les classes principales."""
        from src.ui.layout.styles import injecter_css

        injecter_css()

        css = mock_register.call_args[0][1]
        assert ".main-header" in css
        assert ".metric-card" in css
        assert "@media print" in css
        assert "focus-visible" in css
