"""
Tests de couverture supplÃ©mentaires pour backup.py.

Couvre les mÃ©thodes helper et les edge cases.
"""

import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from src.services.backup import (
    BackupConfig,
    BackupMetadata,
    BackupResult,
    BackupService,
    RestoreResult,
)

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS CONFIGURATION
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestBackupConfigEdgeCases:
    """Tests edge cases pour BackupConfig."""

    def test_config_include_timestamps(self):
        config = BackupConfig()
        assert config.include_timestamps is True

    def test_config_custom_all_fields(self):
        config = BackupConfig(
            backup_dir="/custom/path",
            max_backups=3,
            compress=False,
            include_timestamps=False,
            auto_backup_enabled=False,
            auto_backup_interval_hours=12,
        )
        assert config.backup_dir == "/custom/path"
        assert config.max_backups == 3
        assert config.include_timestamps is False
        assert config.auto_backup_enabled is False
        assert config.auto_backup_interval_hours == 12


class TestBackupMetadataEdgeCases:
    """Tests edge cases pour BackupMetadata."""

    def test_metadata_version_default(self):
        metadata = BackupMetadata()
        assert metadata.version == "1.0"

    def test_metadata_file_size_zero(self):
        metadata = BackupMetadata(file_size_bytes=0)
        assert metadata.file_size_bytes == 0

    def test_metadata_checksum_empty(self):
        metadata = BackupMetadata()
        assert metadata.checksum == ""

    def test_metadata_with_dates(self):
        now = datetime.now()
        metadata = BackupMetadata(created_at=now)
        assert metadata.created_at == now


class TestBackupResultEdgeCases:
    """Tests edge cases pour BackupResult."""

    def test_result_defaults(self):
        result = BackupResult()
        assert result.success is False
        assert result.message == ""
        assert result.file_path is None
        assert result.metadata is None
        assert result.duration_seconds == 0.0

    def test_result_with_all_fields(self):
        metadata = BackupMetadata(id="test", tables_count=5, total_records=100)
        result = BackupResult(
            success=True,
            message="OK",
            file_path="/path/to/backup.json",
            metadata=metadata,
            duration_seconds=3.14,
        )
        assert result.success is True
        assert result.file_path == "/path/to/backup.json"
        assert result.duration_seconds == 3.14


class TestRestoreResultEdgeCases:
    """Tests edge cases pour RestoreResult."""

    def test_restore_defaults(self):
        result = RestoreResult()
        assert result.success is False
        assert result.message == ""
        assert result.tables_restored == []
        assert result.records_restored == 0
        assert result.errors == []

    def test_restore_multiple_errors(self):
        result = RestoreResult(
            success=False,
            errors=["Error 1", "Error 2", "Error 3"],
        )
        assert len(result.errors) == 3


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS BACKUP SERVICE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestBackupServiceInit:
    """Tests pour l'initialisation du BackupService."""

    def test_init_with_default_config(self):
        """Test initialisation avec config par dÃ©faut."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            config = BackupConfig(backup_dir=tmp_dir)
            service = BackupService(config=config)

            assert service.config.backup_dir == tmp_dir

    def test_init_creates_backup_dir(self):
        """Test que le dossier de backup est crÃ©Ã©."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            backup_dir = Path(tmp_dir) / "new_backup_folder"
            config = BackupConfig(backup_dir=str(backup_dir))

            service = BackupService(config=config)

            assert backup_dir.exists()

    def test_models_to_backup_count(self):
        """Test que MODELS_TO_BACKUP contient tous les modÃ¨les."""
        # Au moins 20 tables devraient Ãªtre sauvegardÃ©es
        assert len(BackupService.MODELS_TO_BACKUP) >= 20


class TestBackupServiceHelpers:
    """Tests pour les mÃ©thodes helper du BackupService."""

    @pytest.fixture
    def service(self, tmp_path):
        """CrÃ©e un service avec config temporaire."""
        config = BackupConfig(backup_dir=str(tmp_path))
        return BackupService(config=config)

    def test_generate_backup_id(self, service):
        """Test gÃ©nÃ©ration d'ID de backup."""
        backup_id = service._generate_backup_id()

        assert backup_id is not None
        assert len(backup_id) > 0
        # Format attendu: YYYYMMDD_HHMMSS
        assert "_" in backup_id

    def test_generate_backup_id_format(self, service):
        """Test format de l'ID de backup."""
        backup_id = service._generate_backup_id()

        # Devrait contenir la date du jour
        today = datetime.now().strftime("%Y%m%d")
        assert today in backup_id

    def test_calculate_checksum(self, service):
        """Test calcul du checksum."""
        data = "test data for checksum"
        checksum = service._calculate_checksum(data)

        assert checksum is not None
        assert len(checksum) == 32  # MD5 hex = 32 chars

    def test_calculate_checksum_same_data(self, service):
        """Test que le mÃªme data donne le mÃªme checksum."""
        data = "identical data"
        checksum1 = service._calculate_checksum(data)
        checksum2 = service._calculate_checksum(data)

        assert checksum1 == checksum2

    def test_calculate_checksum_different_data(self, service):
        """Test que des donnÃ©es diffÃ©rentes donnent des checksums diffÃ©rents."""
        checksum1 = service._calculate_checksum("data1")
        checksum2 = service._calculate_checksum("data2")

        assert checksum1 != checksum2

    def test_model_to_dict_with_mock(self, service):
        """Test conversion modÃ¨le vers dict avec mock."""
        # CrÃ©er un mock simple de modÃ¨le SQLAlchemy
        mock_model = MagicMock()
        mock_model.__table__ = MagicMock()

        # Colonnes mock
        col1 = MagicMock()
        col1.name = "id"
        col2 = MagicMock()
        col2.name = "name"

        mock_model.__table__.columns = [col1, col2]
        mock_model.id = 1
        mock_model.name = "test"

        result = service._model_to_dict(mock_model)

        assert "id" in result
        assert "name" in result
        assert result["id"] == 1
        assert result["name"] == "test"

    def test_model_to_dict_with_datetime(self, service):
        """Test conversion avec datetime."""
        mock_model = MagicMock()
        mock_model.__table__ = MagicMock()

        col = MagicMock()
        col.name = "created_at"

        mock_model.__table__.columns = [col]
        mock_model.created_at = datetime(2026, 2, 8, 10, 30, 0)

        result = service._model_to_dict(mock_model)

        assert result["created_at"] == "2026-02-08T10:30:00"


class TestBackupServiceMethods:
    """Tests pour les mÃ©thodes principales (avec mocks)."""

    @pytest.fixture
    def service(self, tmp_path):
        config = BackupConfig(backup_dir=str(tmp_path))
        return BackupService(config=config)

    def test_ensure_backup_dir(self, service, tmp_path):
        """Test que le dossier de backup existe."""
        assert Path(service.config.backup_dir).exists()

    def test_models_include_key_tables(self, service):
        """Test que les tables clÃ©s sont prÃ©sentes."""
        key_tables = [
            "recettes",
            "ingredients",
            "plannings",
            "repas",
            "calendar_events",
        ]

        for table in key_tables:
            assert table in service.MODELS_TO_BACKUP


class TestBackupServiceIntegration:
    """Tests d'intÃ©gration simplifiÃ©s."""

    def test_service_with_different_configs(self, tmp_path):
        """Test avec diffÃ©rentes configurations."""
        configs = [
            BackupConfig(backup_dir=str(tmp_path / "backup1"), compress=True),
            BackupConfig(backup_dir=str(tmp_path / "backup2"), compress=False),
            BackupConfig(backup_dir=str(tmp_path / "backup3"), max_backups=5),
        ]

        for config in configs:
            service = BackupService(config=config)
            assert service.config == config
            assert Path(config.backup_dir).exists()
