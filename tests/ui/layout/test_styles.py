"""
Tests unitaires pour src/ui/layout/styles.py
"""

import pytest
from unittest.mock import MagicMock, patch


class TestInjecterCss:
    """Tests pour injecter_css()."""

    def test_import(self):
        """Test import réussi."""
        from src.ui.layout.styles import injecter_css
        assert injecter_css is not None

    @patch("streamlit.markdown")
    def test_injecter_css(self, mock_md):
        """Test injection CSS."""
        from src.ui.layout.styles import injecter_css
        
        injecter_css()
        
        mock_md.assert_called()
        call_args = mock_md.call_args
        # CSS should be injected with unsafe_allow_html=True
        assert call_args[1].get("unsafe_allow_html") is True

    @patch("streamlit.markdown")
    def test_css_content(self, mock_md):
        """Test contenu CSS."""
        from src.ui.layout.styles import injecter_css
        
        injecter_css()
        
        # CSS should contain style tags
        content = mock_md.call_args[0][0]
        assert "<style>" in content or "style" in content.lower()
