"""
Tests pour src/services/backup.py
"""
import pytest
from datetime import datetime
from pydantic import ValidationError


class TestBackupConfig:
    """Tests pour BackupConfig."""

    def test_config_defaults(self):
        """Configuration par défaut."""
        from src.services.backup import BackupConfig
        
        config = BackupConfig()
        assert config.backup_dir == "backups"
        assert config.max_backups == 10
        assert config.compress is True
        assert config.auto_backup_enabled is True
        assert config.auto_backup_interval_hours == 24

    def test_config_custom(self):
        """Configuration personnalisée."""
        from src.services.backup import BackupConfig
        
        config = BackupConfig(
            backup_dir="custom_backups",
            max_backups=5,
            compress=False
        )
        assert config.backup_dir == "custom_backups"
        assert config.max_backups == 5
        assert config.compress is False


class TestBackupMetadata:
    """Tests pour BackupMetadata."""

    def test_metadata_defaults(self):
        """Métadonnées par défaut."""
        from src.services.backup import BackupMetadata
        
        metadata = BackupMetadata()
        assert metadata.id == ""
        assert metadata.version == "1.0"
        assert metadata.tables_count == 0
        assert metadata.total_records == 0
        assert metadata.compressed is False

    def test_metadata_custom(self):
        """Métadonnées personnalisées."""
        from src.services.backup import BackupMetadata
        
        now = datetime.now()
        metadata = BackupMetadata(
            id="backup-123",
            created_at=now,
            tables_count=10,
            total_records=1000,
            file_size_bytes=50000,
            compressed=True,
            checksum="abc123"
        )
        assert metadata.id == "backup-123"
        assert metadata.tables_count == 10
        assert metadata.compressed is True


class TestBackupResult:
    """Tests pour BackupResult."""

    def test_result_success(self):
        """Résultat de succès."""
        from src.services.backup import BackupResult, BackupMetadata
        
        metadata = BackupMetadata(tables_count=5, total_records=100)
        result = BackupResult(
            success=True,
            message="Backup completed",
            file_path="/backups/backup.json.gz",
            metadata=metadata,
            duration_seconds=2.5
        )
        assert result.success is True
        assert result.metadata.tables_count == 5

    def test_result_failure(self):
        """Résultat d'échec."""
        from src.services.backup import BackupResult
        
        result = BackupResult(
            success=False,
            message="Database connection failed"
        )
        assert result.success is False
        assert "failed" in result.message


class TestRestoreResult:
    """Tests pour RestoreResult."""

    def test_restore_success(self):
        """Restauration réussie."""
        from src.services.backup import RestoreResult
        
        result = RestoreResult(
            success=True,
            message="Restore completed",
            tables_restored=["recettes", "ingredients", "inventaire"],
            records_restored=500
        )
        assert result.success is True
        assert len(result.tables_restored) == 3
        assert result.records_restored == 500

    def test_restore_with_errors(self):
        """Restauration avec erreurs partielles."""
        from src.services.backup import RestoreResult
        
        result = RestoreResult(
            success=False,
            message="Partial restore",
            tables_restored=["recettes"],
            records_restored=100,
            errors=["Table 'ingredients' not found in backup"]
        )
        assert result.success is False
        assert len(result.errors) == 1


class TestBackupServiceModelsMapping:
    """Tests pour le mapping des modèles."""

    def test_models_to_backup_exists(self):
        """Vérifie que MODELS_TO_BACKUP est défini."""
        from src.services.backup import BackupService
        
        assert hasattr(BackupService, "MODELS_TO_BACKUP")
        assert isinstance(BackupService.MODELS_TO_BACKUP, dict)
        assert len(BackupService.MODELS_TO_BACKUP) > 0

    def test_models_includes_critical_tables(self):
        """Vérifie que les tables critiques sont incluses."""
        from src.services.backup import BackupService
        
        critical_tables = [
            "ingredients",
            "recettes",
            "articles_inventaire",
            "plannings",
        ]
        
        for table in critical_tables:
            assert table in BackupService.MODELS_TO_BACKUP
