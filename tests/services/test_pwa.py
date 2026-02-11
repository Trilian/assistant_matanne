"""
Tests pour le module PWA (Progressive Web App).

Couvre les fonctions de génération de fichiers PWA.
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.services.web import (
    PWA_CONFIG,
    generate_manifest,
    generate_service_worker,
    generate_offline_page,
    generate_pwa_files,
    is_pwa_installed,
    generate_icon_svg,
)


# ═══════════════════════════════════════════════════════════
# TESTS CONFIGURATION
# ═══════════════════════════════════════════════════════════


class TestPWAConfig:
    """Tests pour la configuration PWA."""
    
    def test_pwa_config_exists(self):
        assert PWA_CONFIG is not None
        assert isinstance(PWA_CONFIG, dict)
    
    def test_pwa_config_name(self):
        assert PWA_CONFIG["name"] == "Assistant Matanne"
    
    def test_pwa_config_short_name(self):
        assert PWA_CONFIG["short_name"] == "Matanne"
    
    def test_pwa_config_display(self):
        assert PWA_CONFIG["display"] == "standalone"
    
    def test_pwa_config_theme_color(self):
        assert PWA_CONFIG["theme_color"] == "#667eea"
    
    def test_pwa_config_icons_list(self):
        assert "icons" in PWA_CONFIG
        assert isinstance(PWA_CONFIG["icons"], list)
        assert len(PWA_CONFIG["icons"]) > 0
    
    def test_pwa_config_has_shortcuts(self):
        assert "shortcuts" in PWA_CONFIG
    
    def test_pwa_config_lang(self):
        assert PWA_CONFIG["lang"] == "fr-FR"
    
    def test_pwa_config_categories(self):
        assert "lifestyle" in PWA_CONFIG["categories"]


# ═══════════════════════════════════════════════════════════
# TESTS GÉNÉRATION DE FICHIERS
# ═══════════════════════════════════════════════════════════


class TestGenerateManifest:
    """Tests pour generate_manifest."""
    
    def test_generate_manifest_creates_file(self, tmp_path):
        """Test que le manifest est créé."""
        result = generate_manifest(tmp_path)
        
        assert result.exists()
        assert result.name == "manifest.json"
    
    def test_generate_manifest_valid_json(self, tmp_path):
        """Test que le manifest contient du JSON valide."""
        result = generate_manifest(tmp_path)
        
        content = result.read_text(encoding="utf-8")
        manifest = json.loads(content)
        
        assert manifest["name"] == "Assistant Matanne"
        assert manifest["short_name"] == "Matanne"
    
    def test_generate_manifest_creates_directory(self, tmp_path):
        """Test que le dossier est créé si nécessaire."""
        output_path = tmp_path / "new_folder"
        
        result = generate_manifest(output_path)
        
        assert output_path.exists()
        assert result.exists()
    
    def test_generate_manifest_returns_path(self, tmp_path):
        """Test que la fonction retourne le chemin."""
        result = generate_manifest(tmp_path)
        
        assert isinstance(result, Path)
        assert result.is_file()


class TestGenerateServiceWorker:
    """Tests pour generate_service_worker."""
    
    def test_generate_sw_creates_file(self, tmp_path):
        """Test que le SW est créé."""
        result = generate_service_worker(tmp_path)
        
        assert result.exists()
        assert result.name == "sw.js"
    
    def test_generate_sw_content(self, tmp_path):
        """Test que le SW contient du code JavaScript."""
        result = generate_service_worker(tmp_path)
        
        content = result.read_text(encoding="utf-8")
        
        # Doit contenir des éléments de Service Worker
        assert "self.addEventListener" in content or "caches" in content or "fetch" in content
    
    def test_generate_sw_creates_directory(self, tmp_path):
        """Test que le dossier est créé si nécessaire."""
        output_path = tmp_path / "sw_folder"
        
        result = generate_service_worker(output_path)
        
        assert output_path.exists()
        assert result.exists()


class TestGenerateOfflinePage:
    """Tests pour generate_offline_page."""
    
    def test_generate_offline_creates_file(self, tmp_path):
        """Test que la page offline est créée."""
        result = generate_offline_page(tmp_path)
        
        assert result.exists()
        assert result.name == "offline.html"
    
    def test_generate_offline_content(self, tmp_path):
        """Test que la page contient du HTML."""
        result = generate_offline_page(tmp_path)
        
        content = result.read_text(encoding="utf-8")
        
        assert "<html" in content or "<!DOCTYPE" in content or "<body" in content
    
    def test_generate_offline_creates_directory(self, tmp_path):
        """Test que le dossier est créé si nécessaire."""
        output_path = tmp_path / "offline_folder"
        
        result = generate_offline_page(output_path)
        
        assert output_path.exists()
        assert result.exists()


class TestGeneratePWAFiles:
    """Tests pour generate_pwa_files."""
    
    def test_generate_all_files(self, tmp_path):
        """Test que tous les fichiers sont générés."""
        result = generate_pwa_files(tmp_path)
        
        assert "manifest" in result
        assert "service_worker" in result
        assert "offline" in result
    
    def test_generate_creates_icons_folder(self, tmp_path):
        """Test que le dossier icons est créé."""
        generate_pwa_files(tmp_path)
        
        icons_path = tmp_path / "icons"
        assert icons_path.exists()
        assert icons_path.is_dir()
    
    def test_generate_returns_paths(self, tmp_path):
        """Test que les chemins retournés sont valides."""
        result = generate_pwa_files(tmp_path)
        
        for key, path in result.items():
            assert isinstance(path, Path)
            assert path.exists()
    
    def test_generate_with_string_path(self, tmp_path):
        """Test avec un chemin en string."""
        result = generate_pwa_files(str(tmp_path))
        
        assert len(result) == 3


# ═══════════════════════════════════════════════════════════
# TESTS FONCTIONS UTILITAIRES
# ═══════════════════════════════════════════════════════════


class TestIsPWAInstalled:
    """Tests pour is_pwa_installed."""
    
    def test_is_pwa_installed_returns_false(self):
        """Test que la fonction retourne False (vérification client-side seulement)."""
        result = is_pwa_installed()
        
        assert result is False


class TestGenerateIconSVG:
    """Tests pour generate_icon_svg."""
    
    def test_generate_icon_default_size(self):
        """Test avec taille par défaut."""
        result = generate_icon_svg()
        
        assert "512" in result
        assert "<svg" in result
    
    def test_generate_icon_custom_size(self):
        """Test avec taille personnalisée."""
        result = generate_icon_svg(256)
        
        assert "256" in result
        assert "<svg" in result
    
    def test_generate_icon_has_gradient(self):
        """Test que l'icône contient un gradient."""
        result = generate_icon_svg()
        
        assert "linearGradient" in result
        assert "#667eea" in result
    
    def test_generate_icon_has_text(self):
        """Test que l'icône contient le texte."""
        result = generate_icon_svg()
        
        assert "<text" in result
        assert "🏠" in result
    
    def test_generate_icon_various_sizes(self):
        """Test avec différentes tailles."""
        for size in [72, 96, 128, 192, 512]:
            result = generate_icon_svg(size)
            assert str(size) in result


# ═══════════════════════════════════════════════════════════
# TESTS INTÉGRATION STREAMLIT (MOCKÉS)
# ═══════════════════════════════════════════════════════════


class TestStreamlitIntegration:
    """Tests pour les fonctions Streamlit avec mocks."""
    
    @patch("src.services.web.pwa.components")
    def test_inject_pwa_meta(self, mock_components):
        """Test inject_pwa_meta avec mock Streamlit."""
        from src.services.web import inject_pwa_meta
        
        inject_pwa_meta()
        
        mock_components.html.assert_called_once()
    
    @patch("src.services.web.pwa.components")
    def test_render_install_prompt(self, mock_components):
        """Test render_install_prompt avec mock Streamlit."""
        from src.services.web import render_install_prompt
        
        render_install_prompt()
        
        mock_components.html.assert_called_once()
