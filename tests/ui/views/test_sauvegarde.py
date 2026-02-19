"""
Tests unitaires pour src/ui/views/sauvegarde.py

Couverture: afficher_sauvegarde
"""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest


class MockBackupMetadata:
    """Mock pour BackupMetadata."""

    def __init__(self, **kwargs):
        self.total_records = kwargs.get("total_records", 100)
        self.file_size_bytes = kwargs.get("file_size_bytes", 1024)


class MockBackupResult:
    """Mock pour BackupResult."""

    def __init__(self, success=True, **kwargs):
        self.success = success
        self.message = kwargs.get("message", "Backup créé")
        self.metadata = MockBackupMetadata(**kwargs.get("metadata", {}))


class MockBackupInfo:
    """Mock pour BackupInfo."""

    def __init__(self, **kwargs):
        self.id = kwargs.get("id", "backup_123")
        self.created_at = kwargs.get("created_at", datetime.now())
        self.file_size_bytes = kwargs.get("file_size_bytes", 2048)
        self.compressed = kwargs.get("compressed", True)


class TestAfficherSauvegarde:
    """Tests pour afficher_sauvegarde."""

    @patch("src.ui.views.sauvegarde.obtenir_service_backup")
    @patch("streamlit.columns")
    @patch("streamlit.subheader")
    def test_affiche_titre_principal(self, mock_subheader, mock_columns, mock_service):
        """Test que le titre principal est affiché."""
        from src.ui.views.sauvegarde import afficher_sauvegarde

        mock_service.return_value = MagicMock()
        mock_columns.return_value = [MagicMock(), MagicMock()]

        afficher_sauvegarde()

        mock_subheader.assert_called_with("💾 Sauvegarde & Restauration")

    @patch("src.ui.views.sauvegarde.obtenir_service_backup")
    @patch("streamlit.columns")
    @patch("streamlit.subheader")
    @patch("streamlit.checkbox")
    def test_checkbox_compression(self, mock_checkbox, mock_subheader, mock_columns, mock_service):
        """Test que le checkbox de compression est présent."""
        from src.ui.views.sauvegarde import afficher_sauvegarde

        mock_service.return_value = MagicMock()
        mock_columns.return_value = [MagicMock(), MagicMock()]

        afficher_sauvegarde()

        mock_checkbox.assert_called()
        call_args = mock_checkbox.call_args_list[0]
        assert "Compresser" in str(call_args) or "gzip" in str(call_args)


class TestSauvegardeExports:
    """Tests pour les exports du module."""

    def test_all_exports(self):
        """Test que __all__ contient les exports attendus."""
        from src.ui.views import sauvegarde

        assert hasattr(sauvegarde, "__all__")
        assert "afficher_sauvegarde" in sauvegarde.__all__

    def test_import_depuis_views(self):
        """Test import depuis src.ui.views."""
        from src.ui.views import afficher_sauvegarde

        assert callable(afficher_sauvegarde)

    def test_import_depuis_ui(self):
        """Test import depuis src.ui."""
        from src.ui import afficher_sauvegarde

        assert callable(afficher_sauvegarde)
