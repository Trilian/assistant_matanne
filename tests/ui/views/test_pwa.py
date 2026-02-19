"""
Tests unitaires pour src/ui/views/pwa.py

Couverture: injecter_meta_pwa
"""

from unittest.mock import MagicMock, patch


class TestInjecterMetaPwa:
    """Tests pour injecter_meta_pwa."""

    @patch("streamlit.components.v1.html")
    def test_injecte_html_component(self, mock_html):
        """Test que la fonction injecte un composant HTML."""
        from src.ui.views.pwa import injecter_meta_pwa

        injecter_meta_pwa()

        mock_html.assert_called_once()

    @patch("streamlit.components.v1.html")
    def test_html_contient_meta_pwa(self, mock_html):
        """Test que le HTML injecté contient les meta tags PWA."""
        from src.ui.views.pwa import injecter_meta_pwa

        injecter_meta_pwa()

        call_args = mock_html.call_args[0][0]
        assert "manifest.json" in call_args
        assert "theme-color" in call_args
        assert "apple-mobile-web-app-capable" in call_args

    @patch("streamlit.components.v1.html")
    def test_html_contient_service_worker(self, mock_html):
        """Test que le HTML contient l'enregistrement du service worker."""
        from src.ui.views.pwa import injecter_meta_pwa

        injecter_meta_pwa()

        call_args = mock_html.call_args[0][0]
        assert "serviceWorker" in call_args
        assert "sw.js" in call_args

    @patch("streamlit.components.v1.html")
    def test_height_zero(self, mock_html):
        """Test que le composant a une hauteur de 0 (invisible)."""
        from src.ui.views.pwa import injecter_meta_pwa

        injecter_meta_pwa()

        call_kwargs = mock_html.call_args[1]
        assert call_kwargs.get("height") == 0


class TestPwaExports:
    """Tests pour les exports du module."""

    def test_all_exports(self):
        """Test que __all__ contient les exports attendus."""
        from src.ui.views import pwa

        assert hasattr(pwa, "__all__")
        assert "injecter_meta_pwa" in pwa.__all__

    def test_import_depuis_views(self):
        """Test import depuis src.ui.views."""
        from src.ui.views import injecter_meta_pwa

        assert callable(injecter_meta_pwa)

    def test_import_depuis_ui(self):
        """Test import depuis src.ui."""
        from src.ui import injecter_meta_pwa

        assert callable(injecter_meta_pwa)
