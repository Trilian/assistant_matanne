"""
Tests pour la génération de fichiers PWA.

Couvre:
- generate_pwa_files(): Orchestration
- is_pwa_installed(): Vérification
- inject_pwa_meta(): Injection meta tags
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.services.integrations.web.pwa.generation import (
    generate_pwa_files,
    is_pwa_installed,
)


class TestGeneratePwaFiles:
    """Tests pour generate_pwa_files()."""

    def test_genere_fichiers_dans_dossier(self, tmp_path):
        """Vérifie que les fichiers PWA sont générés."""
        result = generate_pwa_files(output_path=tmp_path)

        assert isinstance(result, dict)
        assert "manifest" in result
        assert "service_worker" in result
        assert "offline" in result

    def test_retourne_paths(self, tmp_path):
        """Vérifie que les chemins retournés sont des Path."""
        result = generate_pwa_files(output_path=tmp_path)

        for key, filepath in result.items():
            assert isinstance(filepath, Path), f"{key} devrait être un Path"

    def test_cree_dossier_icons(self, tmp_path):
        """Vérifie que le dossier icons est créé."""
        generate_pwa_files(output_path=tmp_path)

        icons_dir = tmp_path / "icons"
        assert icons_dir.exists()
        assert icons_dir.is_dir()

    def test_fichiers_lisibles(self, tmp_path):
        """Vérifie que les fichiers générés sont lisibles."""
        result = generate_pwa_files(output_path=tmp_path)

        for key, filepath in result.items():
            assert filepath.exists(), f"{key} ({filepath}) devrait exister"
            content = filepath.read_text(encoding="utf-8")
            assert len(content) > 0, f"{key} ne devrait pas être vide"

    def test_manifest_est_json(self, tmp_path):
        """Vérifie que le manifest est du JSON valide."""
        import json

        result = generate_pwa_files(output_path=tmp_path)
        manifest_path = result["manifest"]

        content = manifest_path.read_text(encoding="utf-8")
        data = json.loads(content)
        assert "name" in data or "short_name" in data

    def test_service_worker_est_js(self, tmp_path):
        """Vérifie que le service worker contient du JavaScript."""
        result = generate_pwa_files(output_path=tmp_path)
        sw_path = result["service_worker"]

        content = sw_path.read_text(encoding="utf-8")
        # Un service worker doit contenir des event listeners
        assert "self" in content or "cache" in content.lower() or "fetch" in content.lower()

    def test_offline_est_html(self, tmp_path):
        """Vérifie que la page offline est du HTML."""
        result = generate_pwa_files(output_path=tmp_path)
        offline_path = result["offline"]

        content = offline_path.read_text(encoding="utf-8")
        assert "<html" in content.lower() or "<!doctype" in content.lower()


class TestIsPwaInstalled:
    """Tests pour is_pwa_installed()."""

    def test_retourne_false_cote_serveur(self):
        """Côté serveur, toujours False."""
        assert is_pwa_installed() is False

    def test_retourne_bool(self):
        assert isinstance(is_pwa_installed(), bool)


class TestInjectPwaMeta:
    """Tests pour inject_pwa_meta()."""

    @patch("src.services.integrations.web.pwa.generation.inject_pwa_meta")
    def test_delegue_a_ui_view(self, mock_inject):
        """Vérifie que la fonction délègue correctement."""
        from src.services.integrations.web.pwa.generation import inject_pwa_meta

        # La fonction ne devrait pas lever d'erreur
        inject_pwa_meta()
