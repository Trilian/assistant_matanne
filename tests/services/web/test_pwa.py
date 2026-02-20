"""
Tests pour src/services/web/pwa.py
"""

import json
from unittest.mock import patch


class TestGenerateManifest:
    """Tests pour generate_manifest."""

    def test_generate_manifest_creates_file(self, tmp_path):
        """Test création du fichier manifest.json."""
        from src.services.integrations.web.pwa import generate_manifest

        result = generate_manifest(tmp_path)

        assert result.exists()
        assert result.name == "manifest.json"

    def test_generate_manifest_content(self, tmp_path):
        """Test le contenu du manifest."""
        from src.services.integrations.web.pwa import PWA_CONFIG, generate_manifest

        generate_manifest(tmp_path)
        manifest_path = tmp_path / "manifest.json"

        content = json.loads(manifest_path.read_text(encoding="utf-8"))

        assert content["name"] == PWA_CONFIG["name"]
        assert content["short_name"] == PWA_CONFIG["short_name"]
        assert content["theme_color"] == PWA_CONFIG["theme_color"]

    def test_generate_manifest_creates_directory(self, tmp_path):
        """Test création du dossier si inexistant."""
        from src.services.integrations.web.pwa import generate_manifest

        nested_path = tmp_path / "nested" / "folder"
        result = generate_manifest(nested_path)

        assert nested_path.exists()
        assert result.exists()


class TestGenerateServiceWorker:
    """Tests pour generate_service_worker."""

    def test_generate_sw_creates_file(self, tmp_path):
        """Test création du fichier sw.js."""
        from src.services.integrations.web.pwa import generate_service_worker

        result = generate_service_worker(tmp_path)

        assert result.exists()
        assert result.name == "sw.js"

    def test_generate_sw_content(self, tmp_path):
        """Test le contenu du service worker."""
        from src.services.integrations.web.pwa import generate_service_worker

        generate_service_worker(tmp_path)
        sw_path = tmp_path / "sw.js"

        content = sw_path.read_text(encoding="utf-8")

        assert "CACHE_NAME" in content
        assert "matanne-cache" in content
        assert "install" in content


class TestGenerateOfflinePage:
    """Tests pour generate_offline_page."""

    def test_generate_offline_creates_file(self, tmp_path):
        """Test création du fichier offline.html."""
        from src.services.integrations.web.pwa import generate_offline_page

        result = generate_offline_page(tmp_path)

        assert result.exists()
        assert result.name == "offline.html"

    def test_generate_offline_content(self, tmp_path):
        """Test le contenu de la page offline."""
        from src.services.integrations.web.pwa import generate_offline_page

        generate_offline_page(tmp_path)
        offline_path = tmp_path / "offline.html"

        content = offline_path.read_text(encoding="utf-8")

        assert "<!DOCTYPE html>" in content
        assert "hors ligne" in content.lower()
        assert "Assistant Matanne" in content


class TestGeneratePwaFiles:
    """Tests pour generate_pwa_files."""

    def test_generate_all_files(self, tmp_path):
        """Test génération de tous les fichiers PWA."""
        from src.services.integrations.web.pwa import generate_pwa_files

        result = generate_pwa_files(tmp_path)

        assert "manifest" in result
        assert "service_worker" in result
        assert "offline" in result

        assert result["manifest"].exists()
        assert result["service_worker"].exists()
        assert result["offline"].exists()

    def test_creates_icons_folder(self, tmp_path):
        """Test création du dossier icons."""
        from src.services.integrations.web.pwa import generate_pwa_files

        generate_pwa_files(tmp_path)

        icons_path = tmp_path / "icons"
        assert icons_path.exists()
        assert icons_path.is_dir()


class TestInjectPwaMeta:
    """Tests pour inject_pwa_meta."""

    @patch("src.ui.views.pwa.components")
    def test_inject_meta_calls_components(self, mock_components):
        """Test appel de components.html."""
        from src.services.integrations.web.pwa import inject_pwa_meta

        inject_pwa_meta()

        mock_components.html.assert_called_once()
        call_args = mock_components.html.call_args
        html_content = call_args[0][0]

        assert "manifest.json" in html_content
        assert "theme-color" in html_content
        assert "serviceWorker" in html_content


class TestRenderInstallPrompt:
    """Tests pour afficher_install_prompt."""

    @patch("src.ui.views.pwa.components")
    def test_render_install_calls_components(self, mock_components):
        """Test appel de components.html via délégation UI."""
        from src.services.integrations.web.pwa import afficher_install_prompt

        afficher_install_prompt()

        mock_components.html.assert_called_once()
        call_args = mock_components.html.call_args
        html_content = call_args[0][0]

        assert "pwa-install" in html_content
        assert "installPWA" in html_content


class TestIsPwaInstalled:
    """Tests pour is_pwa_installed."""

    def test_returns_false(self):
        """Test retourne toujours False (vérif côté client)."""
        from src.services.integrations.web.pwa import is_pwa_installed

        result = is_pwa_installed()

        assert result is False


class TestGenerateIconSvg:
    """Tests pour generate_icon_svg."""

    def test_default_size(self):
        """Test génération avec taille par défaut."""
        from src.services.integrations.web.pwa import generate_icon_svg

        result = generate_icon_svg()

        assert 'width="512"' in result
        assert 'height="512"' in result

    def test_custom_size(self):
        """Test génération avec taille personnalisée."""
        from src.services.integrations.web.pwa import generate_icon_svg

        result = generate_icon_svg(size=256)

        assert 'width="256"' in result
        assert 'height="256"' in result

    def test_svg_structure(self):
        """Test structure SVG valide."""
        from src.services.integrations.web.pwa import generate_icon_svg

        result = generate_icon_svg()

        assert "<svg" in result
        assert "</svg>" in result
        assert "linearGradient" in result
        assert "#667eea" in result


class TestPwaConfig:
    """Tests pour la configuration PWA."""

    def test_pwa_config_structure(self):
        """Test structure de la configuration."""
        from src.services.integrations.web.pwa import PWA_CONFIG

        assert "name" in PWA_CONFIG
        assert "short_name" in PWA_CONFIG
        assert "icons" in PWA_CONFIG
        assert "shortcuts" in PWA_CONFIG

    def test_pwa_config_icons(self):
        """Test configuration des icônes."""
        from src.services.integrations.web.pwa import PWA_CONFIG

        icons = PWA_CONFIG["icons"]

        assert len(icons) >= 4
        for icon in icons:
            assert "src" in icon
            assert "sizes" in icon
            assert "type" in icon


class TestServiceWorkerJs:
    """Tests pour le contenu du service worker."""

    def test_sw_contains_cache_strategies(self):
        """Test présence des stratégies de cache."""
        from src.services.integrations.web.pwa import SERVICE_WORKER_JS

        assert "PRECACHE_URLS" in SERVICE_WORKER_JS
        assert "install" in SERVICE_WORKER_JS
        assert "activate" in SERVICE_WORKER_JS
        assert "fetch" in SERVICE_WORKER_JS

    def test_sw_contains_offline_support(self):
        """Test support offline."""
        from src.services.integrations.web.pwa import SERVICE_WORKER_JS

        assert "offline" in SERVICE_WORKER_JS.lower()
        assert "caches" in SERVICE_WORKER_JS


class TestOfflineHtml:
    """Tests pour le contenu HTML offline."""

    def test_offline_html_structure(self):
        """Test structure HTML."""
        from src.services.integrations.web.pwa import OFFLINE_HTML

        assert "<!DOCTYPE html>" in OFFLINE_HTML
        assert "<html" in OFFLINE_HTML
        assert "</html>" in OFFLINE_HTML

    def test_offline_html_french(self):
        """Test contenu en français."""
        from src.services.integrations.web.pwa import OFFLINE_HTML

        assert 'lang="fr"' in OFFLINE_HTML
        assert "hors ligne" in OFFLINE_HTML.lower()
