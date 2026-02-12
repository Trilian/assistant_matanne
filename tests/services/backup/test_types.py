"""Tests pour backup/types.py - Pydantic models et validation."""

import pytest
from datetime import datetime
from pydantic import ValidationError

from src.services.backup.types import (
    BackupConfig,
    BackupMetadata,
    BackupResult,
    RestoreResult,
)


@pytest.mark.unit
class TestBackupConfig:
    """Tests pour la classe BackupConfig."""
    
    def test_default_values(self):
        """Test création avec valeurs par défaut."""
        config = BackupConfig()
        
        assert config.backup_dir == "backups"
        assert config.max_backups == 10
        assert config.compress is True
        assert config.include_timestamps is True
        assert config.auto_backup_enabled is True
        assert config.auto_backup_interval_hours == 24
    
    def test_custom_values(self):
        """Test création avec valeurs personnalisées."""
        config = BackupConfig(
            backup_dir="/custom/path",
            max_backups=5,
            compress=False,
            include_timestamps=False,
            auto_backup_enabled=False,
            auto_backup_interval_hours=12,
        )
        
        assert config.backup_dir == "/custom/path"
        assert config.max_backups == 5
        assert config.compress is False
        assert config.include_timestamps is False
        assert config.auto_backup_enabled is False
        assert config.auto_backup_interval_hours == 12
    
    def test_partial_values(self):
        """Test création avec valeurs partielles."""
        config = BackupConfig(
            backup_dir="my_backups",
            max_backups=20,
        )
        
        assert config.backup_dir == "my_backups"
        assert config.max_backups == 20
        # Valeurs par défaut pour le reste
        assert config.compress is True
        assert config.auto_backup_enabled is True
    
    def test_model_dump(self):
        """Test sérialisation en dictionnaire."""
        config = BackupConfig()
        data = config.model_dump()
        
        assert isinstance(data, dict)
        assert "backup_dir" in data
        assert "max_backups" in data
        assert "compress" in data
    
    def test_type_coercion(self):
        """Test coercition de types."""
        # Integer pour max_backups en string
        config = BackupConfig(max_backups="15")
        assert config.max_backups == 15
        
        # Boolean strings
        config2 = BackupConfig(compress=True)
        assert config2.compress is True


@pytest.mark.unit
class TestBackupMetadata:
    """Tests pour la classe BackupMetadata."""
    
    def test_default_values(self):
        """Test création avec valeurs par défaut."""
        metadata = BackupMetadata()
        
        assert metadata.id == ""
        assert isinstance(metadata.created_at, datetime)
        assert metadata.version == "1.0"
        assert metadata.tables_count == 0
        assert metadata.total_records == 0
        assert metadata.file_size_bytes == 0
        assert metadata.compressed is False
        assert metadata.checksum == ""
    
    def test_custom_values(self):
        """Test création avec valeurs personnalisées."""
        now = datetime(2024, 1, 15, 10, 30, 0)
        
        metadata = BackupMetadata(
            id="20240115_103000",
            created_at=now,
            version="2.0",
            tables_count=5,
            total_records=1000,
            file_size_bytes=524288,
            compressed=True,
            checksum="abc123def456",
        )
        
        assert metadata.id == "20240115_103000"
        assert metadata.created_at == now
        assert metadata.version == "2.0"
        assert metadata.tables_count == 5
        assert metadata.total_records == 1000
        assert metadata.file_size_bytes == 524288
        assert metadata.compressed is True
        assert metadata.checksum == "abc123def456"
    
    def test_created_at_default_factory(self):
        """Test que created_at utilise datetime.now() par défaut."""
        before = datetime.now()
        metadata = BackupMetadata()
        after = datetime.now()
        
        assert before <= metadata.created_at <= after
    
    def test_model_dump_serialization(self):
        """Test sérialisation complète."""
        metadata = BackupMetadata(
            id="test_id",
            tables_count=10,
        )
        data = metadata.model_dump()
        
        assert data["id"] == "test_id"
        assert data["tables_count"] == 10
        assert "created_at" in data
    
    def test_copy_with_update(self):
        """Test copie avec mise Ã  jour."""
        metadata1 = BackupMetadata(id="original", tables_count=5)
        metadata2 = metadata1.model_copy(update={"id": "copy", "total_records": 100})
        
        assert metadata1.id == "original"
        assert metadata2.id == "copy"
        assert metadata2.tables_count == 5  # Conservé
        assert metadata2.total_records == 100


@pytest.mark.unit
class TestBackupResult:
    """Tests pour la classe BackupResult."""
    
    def test_default_values(self):
        """Test création avec valeurs par défaut."""
        result = BackupResult()
        
        assert result.success is False
        assert result.message == ""
        assert result.file_path is None
        assert result.metadata is None
        assert result.duration_seconds == 0.0
    
    def test_success_result(self):
        """Test résultat de succès."""
        metadata = BackupMetadata(id="backup_001", total_records=500)
        
        result = BackupResult(
            success=True,
            message="Backup créé avec succès",
            file_path="/path/to/backup.json.gz",
            metadata=metadata,
            duration_seconds=2.5,
        )
        
        assert result.success is True
        assert result.message == "Backup créé avec succès"
        assert result.file_path == "/path/to/backup.json.gz"
        assert result.metadata.id == "backup_001"
        assert result.metadata.total_records == 500
        assert result.duration_seconds == 2.5
    
    def test_failure_result(self):
        """Test résultat d'échec."""
        result = BackupResult(
            success=False,
            message="Erreur: disque plein",
        )
        
        assert result.success is False
        assert result.message == "Erreur: disque plein"
        assert result.file_path is None
        assert result.metadata is None
    
    def test_nested_metadata_serialization(self):
        """Test sérialisation avec métadonnées imbriquées."""
        result = BackupResult(
            success=True,
            metadata=BackupMetadata(id="test", checksum="abc"),
        )
        
        data = result.model_dump()
        
        assert data["success"] is True
        assert data["metadata"]["id"] == "test"
        assert data["metadata"]["checksum"] == "abc"
    
    def test_optional_file_path(self):
        """Test que file_path peut être None ou une string."""
        result1 = BackupResult()
        assert result1.file_path is None
        
        result2 = BackupResult(file_path="/some/path.json")
        assert result2.file_path == "/some/path.json"


@pytest.mark.unit
class TestRestoreResult:
    """Tests pour la classe RestoreResult."""
    
    def test_default_values(self):
        """Test création avec valeurs par défaut."""
        result = RestoreResult()
        
        assert result.success is False
        assert result.message == ""
        assert result.tables_restored == []
        assert result.records_restored == 0
        assert result.errors == []
    
    def test_success_restore(self):
        """Test résultat de restauration réussie."""
        result = RestoreResult(
            success=True,
            message="Restauration complète",
            tables_restored=["recettes", "ingredients", "plannings"],
            records_restored=1500,
            errors=[],
        )
        
        assert result.success is True
        assert len(result.tables_restored) == 3
        assert "recettes" in result.tables_restored
        assert result.records_restored == 1500
        assert len(result.errors) == 0
    
    def test_partial_restore_with_errors(self):
        """Test restauration partielle avec erreurs."""
        result = RestoreResult(
            success=False,
            message="Restauration partielle",
            tables_restored=["recettes", "ingredients"],
            records_restored=800,
            errors=[
                "Erreur FK sur recette_ingredients",
                "Table plannings corrompue",
            ],
        )
        
        assert result.success is False
        assert len(result.tables_restored) == 2
        assert result.records_restored == 800
        assert len(result.errors) == 2
        assert "Erreur FK" in result.errors[0]
    
    def test_lists_are_independent(self):
        """Test que les listes par défaut sont indépendantes."""
        result1 = RestoreResult()
        result2 = RestoreResult()
        
        result1.tables_restored.append("table1")
        result1.errors.append("error1")
        
        # result2 ne doit pas être affecté
        assert result2.tables_restored == []
        assert result2.errors == []
    
    def test_model_dump_with_lists(self):
        """Test sérialisation avec listes."""
        result = RestoreResult(
            success=True,
            tables_restored=["a", "b"],
            errors=["e1"],
        )
        
        data = result.model_dump()
        
        assert data["tables_restored"] == ["a", "b"]
        assert data["errors"] == ["e1"]
    
    def test_records_restored_type(self):
        """Test que records_restored accepte différentes valeurs int."""
        result1 = RestoreResult(records_restored=0)
        assert result1.records_restored == 0
        
        result2 = RestoreResult(records_restored=999999)
        assert result2.records_restored == 999999


@pytest.mark.unit
class TestModelsIntegration:
    """Tests d'intégration entre les modèles."""
    
    def test_backup_result_with_full_metadata(self):
        """Test BackupResult avec métadonnées complètes."""
        metadata = BackupMetadata(
            id="20240115_143000",
            created_at=datetime(2024, 1, 15, 14, 30, 0),
            version="1.0",
            tables_count=10,
            total_records=5000,
            file_size_bytes=1048576,
            compressed=True,
            checksum="md5hash123",
        )
        
        result = BackupResult(
            success=True,
            message="Backup complet",
            file_path="backups/backup_20240115_143000.json.gz",
            metadata=metadata,
            duration_seconds=5.25,
        )
        
        # Vérifier l'intégration
        assert result.metadata.id == "20240115_143000"
        assert result.metadata.file_size_bytes == 1048576
        
        # Sérialisation complète
        data = result.model_dump()
        assert data["metadata"]["checksum"] == "md5hash123"
    
    def test_config_for_different_environments(self):
        """Test configurations pour différents environnements."""
        # Production
        prod_config = BackupConfig(
            backup_dir="/data/backups",
            max_backups=30,
            compress=True,
            auto_backup_interval_hours=6,
        )
        
        # Développement
        dev_config = BackupConfig(
            backup_dir="./dev_backups",
            max_backups=3,
            compress=False,
            auto_backup_enabled=False,
        )
        
        assert prod_config.max_backups > dev_config.max_backups
        assert prod_config.compress is True
        assert dev_config.auto_backup_enabled is False
    
    def test_restore_result_summary(self):
        """Test création d'un résumé de restauration."""
        result = RestoreResult(
            success=True,
            message="OK",
            tables_restored=["t1", "t2", "t3", "t4", "t5"],
            records_restored=12345,
        )
        
        # Calculer un résumé
        summary = {
            "tables": len(result.tables_restored),
            "records": result.records_restored,
            "has_errors": len(result.errors) > 0,
        }
        
        assert summary["tables"] == 5
        assert summary["records"] == 12345
        assert summary["has_errors"] is False


@pytest.mark.unit
class TestEdgeCases:
    """Tests des cas limites."""
    
    def test_empty_strings(self):
        """Test avec chaînes vides."""
        config = BackupConfig(backup_dir="")
        assert config.backup_dir == ""
        
        metadata = BackupMetadata(id="", checksum="")
        assert metadata.id == ""
    
    def test_zero_values(self):
        """Test avec valeurs Ã  zéro."""
        config = BackupConfig(max_backups=0, auto_backup_interval_hours=0)
        assert config.max_backups == 0
        assert config.auto_backup_interval_hours == 0
        
        metadata = BackupMetadata(
            tables_count=0,
            total_records=0,
            file_size_bytes=0,
        )
        assert metadata.tables_count == 0
    
    def test_large_values(self):
        """Test avec grandes valeurs."""
        metadata = BackupMetadata(
            total_records=10_000_000,
            file_size_bytes=1_073_741_824,  # 1 GB
        )
        assert metadata.total_records == 10_000_000
        assert metadata.file_size_bytes == 1_073_741_824
    
    def test_negative_duration(self):
        """Test avec durée négative (edge case théorique)."""
        result = BackupResult(duration_seconds=-1.0)
        assert result.duration_seconds == -1.0
    
    def test_very_long_message(self):
        """Test avec message très long."""
        long_msg = "Error: " + "x" * 10000
        result = RestoreResult(message=long_msg)
        assert len(result.message) == 10007
    
    def test_special_characters_in_path(self):
        """Test avec caractères spéciaux dans le chemin."""
        paths = [
            "/path/with spaces/backup.json",
            "C:\\Windows\\backup\\file.json.gz",
            "/données/Ã±oÃ±o/å¤‡ä»½.json",
        ]
        
        for path in paths:
            config = BackupConfig(backup_dir=path)
            assert config.backup_dir == path
    
    def test_many_tables_restored(self):
        """Test avec beaucoup de tables restaurées."""
        tables = [f"table_{i}" for i in range(100)]
        result = RestoreResult(tables_restored=tables)
        assert len(result.tables_restored) == 100
    
    def test_many_errors(self):
        """Test avec beaucoup d'erreurs."""
        errors = [f"Error {i}: Something went wrong" for i in range(50)]
        result = RestoreResult(errors=errors)
        assert len(result.errors) == 50


@pytest.mark.unit
class TestModelValidation:
    """Tests de validation Pydantic."""
    
    def test_config_type_validation(self):
        """Test que les types sont validés."""
        # max_backups doit être int
        with pytest.raises(ValidationError):
            BackupConfig(max_backups="not_a_number")
    
    def test_metadata_datetime_validation(self):
        """Test validation datetime."""
        # String ISO valide devrait être parsée
        metadata = BackupMetadata(created_at="2024-01-15T10:30:00")
        assert metadata.created_at.year == 2024
        assert metadata.created_at.month == 1
        assert metadata.created_at.day == 15
    
    def test_result_boolean_type(self):
        """Test que success accepte les booleans."""
        result1 = BackupResult(success=True)
        result2 = BackupResult(success=False)
        
        assert result1.success is True
        assert result2.success is False
    
    def test_metadata_from_dict(self):
        """Test création depuis un dictionnaire."""
        data = {
            "id": "backup_123",
            "version": "2.0",
            "tables_count": 15,
            "compressed": True,
        }
        
        metadata = BackupMetadata(**data)
        
        assert metadata.id == "backup_123"
        assert metadata.version == "2.0"
        assert metadata.tables_count == 15
        assert metadata.compressed is True
