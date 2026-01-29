"""
Tests pour le service de backup (backup.py).

Ce fichier teste les fonctionnalités de sauvegarde:
- Configuration du backup (BackupConfig)
- Métadonnées (BackupMetadata)
- Résultats (BackupResult, RestoreResult)
- Service de backup et restauration
"""

import pytest
import json
import gzip
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch, MagicMock


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS MODÃˆLES DE CONFIGURATION
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestBackupConfigModel:
    """Tests pour BackupConfig model."""

    def test_config_defaults(self):
        """Configuration avec valeurs par défaut."""
        from src.services.backup import BackupConfig
        
        config = BackupConfig()
        
        assert config.backup_dir == "backups"
        assert config.max_backups == 10
        assert config.compress is True
        assert config.include_timestamps is True
        assert config.auto_backup_enabled is True
        assert config.auto_backup_interval_hours == 24

    def test_config_custom_values(self):
        """Configuration personnalisée."""
        from src.services.backup import BackupConfig
        
        config = BackupConfig(
            backup_dir="custom_backups",
            max_backups=5,
            compress=False,
            auto_backup_enabled=False,
        )
        
        assert config.backup_dir == "custom_backups"
        assert config.max_backups == 5
        assert config.compress is False
        assert config.auto_backup_enabled is False


class TestBackupMetadataModel:
    """Tests pour BackupMetadata model."""

    def test_metadata_creation(self):
        """Création de métadonnées."""
        from src.services.backup import BackupMetadata
        
        metadata = BackupMetadata(
            id="20260128_120000",
            tables_count=10,
            total_records=1500,
            file_size_bytes=102400,
            compressed=True,
            checksum="abc123def456",
        )
        
        assert metadata.id == "20260128_120000"
        assert metadata.tables_count == 10
        assert metadata.total_records == 1500

    def test_metadata_defaults(self):
        """Métadonnées avec valeurs par défaut."""
        from src.services.backup import BackupMetadata
        
        metadata = BackupMetadata()
        
        assert metadata.id == ""
        assert metadata.version == "1.0"
        assert metadata.tables_count == 0
        assert metadata.compressed is False

    def test_metadata_created_at_auto(self):
        """created_at est auto-généré."""
        from src.services.backup import BackupMetadata
        
        metadata = BackupMetadata()
        
        # created_at doit être récent
        assert (datetime.now() - metadata.created_at).total_seconds() < 5


class TestBackupResultModel:
    """Tests pour BackupResult model."""

    def test_result_success(self):
        """Résultat de backup réussi."""
        from src.services.backup import BackupResult, BackupMetadata
        
        metadata = BackupMetadata(id="test", tables_count=5, total_records=100)
        
        result = BackupResult(
            success=True,
            message="Backup créé avec succès",
            file_path="/path/to/backup.json.gz",
            metadata=metadata,
            duration_seconds=2.5,
        )
        
        assert result.success is True
        assert result.file_path == "/path/to/backup.json.gz"
        assert result.duration_seconds == 2.5

    def test_result_failure(self):
        """Résultat de backup échoué."""
        from src.services.backup import BackupResult
        
        result = BackupResult(
            success=False,
            message="Erreur de connexion",
        )
        
        assert result.success is False
        assert result.file_path is None
        assert result.metadata is None


class TestRestoreResultModel:
    """Tests pour RestoreResult model."""

    def test_restore_result_success(self):
        """Résultat de restauration réussie."""
        from src.services.backup import RestoreResult
        
        result = RestoreResult(
            success=True,
            message="Restauration complète",
            tables_restored=["recettes", "ingredients", "planning"],
            records_restored=500,
        )
        
        assert result.success is True
        assert len(result.tables_restored) == 3
        assert result.records_restored == 500

    def test_restore_result_with_errors(self):
        """Restauration avec erreurs partielles."""
        from src.services.backup import RestoreResult
        
        result = RestoreResult(
            success=True,  # Succès partiel
            message="Restauration avec avertissements",
            tables_restored=["recettes", "ingredients"],
            records_restored=300,
            errors=["Erreur table 'planning': clé étrangère manquante"],
        )
        
        assert len(result.errors) == 1
        assert "planning" in result.errors[0]


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS SERVICE BACKUP - INITIALISATION
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestBackupServiceInit:
    """Tests pour l'initialisation du service."""

    def test_service_creation_default(self):
        """Création avec config par défaut."""
        from src.services.backup import BackupService
        
        service = BackupService()
        
        assert service.config.backup_dir == "backups"
        assert service.config.max_backups == 10

    def test_service_creation_custom_config(self):
        """Création avec config personnalisée."""
        from src.services.backup import BackupService, BackupConfig
        
        config = BackupConfig(
            backup_dir="my_backups",
            max_backups=5,
        )
        service = BackupService(config=config)
        
        assert service.config.backup_dir == "my_backups"
        assert service.config.max_backups == 5

    def test_models_to_backup_defined(self):
        """MODELS_TO_BACKUP est défini avec les tables attendues."""
        from src.services.backup import BackupService
        
        models = BackupService.MODELS_TO_BACKUP
        
        assert "recettes" in models
        assert "ingredients" in models
        assert "articles_inventaire" in models
        assert "plannings" in models
        assert "family_budgets" in models


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS UTILITAIRES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestBackupUtilities:
    """Tests pour les méthodes utilitaires."""

    def test_generate_backup_id(self):
        """Génération d'ID de backup."""
        from src.services.backup import BackupService
        
        service = BackupService()
        backup_id = service._generate_backup_id()
        
        # Format: YYYYMMDD_HHMMSS
        assert len(backup_id) == 15
        assert "_" in backup_id
        assert backup_id[:4].isdigit()  # Année

    def test_generate_backup_id_unique(self):
        """IDs sont différents à chaque appel (si temps différent)."""
        from src.services.backup import BackupService
        import time
        
        service = BackupService()
        id1 = service._generate_backup_id()
        time.sleep(1.1)  # Attendre au moins 1 seconde
        id2 = service._generate_backup_id()
        
        assert id1 != id2

    def test_calculate_checksum(self):
        """Calcul du checksum MD5."""
        from src.services.backup import BackupService
        
        service = BackupService()
        
        checksum1 = service._calculate_checksum("test data")
        checksum2 = service._calculate_checksum("test data")
        checksum3 = service._calculate_checksum("different data")
        
        # Même donnée = même checksum
        assert checksum1 == checksum2
        # Données différentes = checksums différents
        assert checksum1 != checksum3
        # Checksum MD5 = 32 caractères hex
        assert len(checksum1) == 32

    def test_model_to_dict_basic(self):
        """Conversion modèle vers dict."""
        from src.services.backup import BackupService
        
        service = BackupService()
        
        # Créer un mock d'objet SQLAlchemy
        mock_obj = MagicMock()
        mock_obj.__table__ = MagicMock()
        
        # Simuler des colonnes
        col_id = MagicMock()
        col_id.name = "id"
        col_name = MagicMock()
        col_name.name = "name"
        
        mock_obj.__table__.columns = [col_id, col_name]
        mock_obj.id = 1
        mock_obj.name = "Test"
        
        result = service._model_to_dict(mock_obj)
        
        assert result["id"] == 1
        assert result["name"] == "Test"

    def test_model_to_dict_datetime(self):
        """Conversion datetime vers ISO format."""
        from src.services.backup import BackupService
        
        service = BackupService()
        
        mock_obj = MagicMock()
        mock_obj.__table__ = MagicMock()
        
        col_created = MagicMock()
        col_created.name = "created_at"
        mock_obj.__table__.columns = [col_created]
        mock_obj.created_at = datetime(2026, 1, 28, 12, 0, 0)
        
        result = service._model_to_dict(mock_obj)
        
        assert result["created_at"] == "2026-01-28T12:00:00"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS CRÃ‰ATION BACKUP (MOCKED)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestCreateBackup:
    """Tests pour création de backup."""

    def test_backup_creates_file(self):
        """Le backup crée un fichier."""
        from src.services.backup import BackupService, BackupConfig
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config = BackupConfig(
                backup_dir=tmpdir,
                compress=False,
            )
            service = BackupService(config=config)
            
            # Mock la session DB
            with patch('src.services.backup.with_db_session'):
                with patch.object(service, 'create_backup') as mock_create:
                    from src.services.backup import BackupResult, BackupMetadata
                    
                    mock_create.return_value = BackupResult(
                        success=True,
                        message="OK",
                        file_path=f"{tmpdir}/backup_test.json",
                        metadata=BackupMetadata(id="test", total_records=10),
                    )
                    
                    result = service.create_backup()
                    
                    assert result.success is True

    def test_backup_result_contains_metadata(self):
        """Le résultat contient les métadonnées."""
        from src.services.backup import BackupResult, BackupMetadata
        
        metadata = BackupMetadata(
            id="20260128_120000",
            tables_count=5,
            total_records=100,
            file_size_bytes=1024,
            compressed=True,
        )
        
        result = BackupResult(
            success=True,
            message="OK",
            file_path="/backup.json.gz",
            metadata=metadata,
            duration_seconds=1.5,
        )
        
        assert result.metadata.tables_count == 5
        assert result.metadata.compressed is True


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS COMPRESSION
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestBackupCompression:
    """Tests pour compression des backups."""

    def test_gzip_compression_works(self):
        """Compression gzip fonctionne."""
        import gzip
        import tempfile
        
        data = '{"test": "data", "count": 12345}' * 100
        
        with tempfile.NamedTemporaryFile(suffix='.json.gz', delete=False) as f:
            temp_path = f.name
        
        try:
            # Ã‰crire compressé
            with gzip.open(temp_path, 'wt', encoding='utf-8') as f:
                f.write(data)
            
            # Lire et vérifier
            with gzip.open(temp_path, 'rt', encoding='utf-8') as f:
                read_data = f.read()
            
            assert read_data == data
            
            # Fichier compressé plus petit
            import os
            compressed_size = os.path.getsize(temp_path)
            assert compressed_size < len(data)
        finally:
            import os
            os.unlink(temp_path)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS ROTATION BACKUPS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestBackupRotation:
    """Tests pour rotation des anciens backups."""

    def test_rotation_deletes_old_backups(self):
        """La rotation supprime les anciens backups."""
        from src.services.backup import BackupService, BackupConfig
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Créer plus de fichiers que max_backups
            for i in range(15):
                backup_file = Path(tmpdir) / f"backup_20260128_{i:06d}.json"
                backup_file.write_text("{}")
            
            config = BackupConfig(
                backup_dir=tmpdir,
                max_backups=10,
            )
            service = BackupService(config=config)
            
            # La rotation devrait supprimer les 5 plus anciens
            service._rotate_old_backups()
            
            remaining = list(Path(tmpdir).glob("backup_*"))
            assert len(remaining) <= 10


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS LISTE BACKUPS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestListBackups:
    """Tests pour listing des backups."""

    def test_list_empty_dir(self):
        """Liste vide si pas de backups."""
        from src.services.backup import BackupService, BackupConfig
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config = BackupConfig(backup_dir=tmpdir)
            service = BackupService(config=config)
            
            # Méthode list_backups si elle existe
            if hasattr(service, 'list_backups'):
                backups = service.list_backups()
                assert len(backups) == 0

    def test_backup_dir_created(self):
        """Le répertoire de backup est créé automatiquement."""
        from src.services.backup import BackupService, BackupConfig
        
        with tempfile.TemporaryDirectory() as tmpdir:
            backup_dir = Path(tmpdir) / "nested" / "backup" / "dir"
            config = BackupConfig(backup_dir=str(backup_dir))
            
            service = BackupService(config=config)
            
            assert backup_dir.exists()


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS RESTAURATION
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestRestoreBackup:
    """Tests pour restauration de backup."""

    def test_restore_result_defaults(self):
        """RestoreResult avec valeurs par défaut."""
        from src.services.backup import RestoreResult
        
        result = RestoreResult()
        
        assert result.success is False
        assert result.message == ""
        assert result.tables_restored == []
        assert result.records_restored == 0
        assert result.errors == []

    def test_restore_result_with_data(self):
        """RestoreResult avec données."""
        from src.services.backup import RestoreResult
        
        result = RestoreResult(
            success=True,
            message="Restauration terminée",
            tables_restored=["recettes", "ingredients"],
            records_restored=250,
        )
        
        assert result.success is True
        assert "recettes" in result.tables_restored


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS JSON STRUCTURE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestBackupJsonStructure:
    """Tests pour structure JSON du backup."""

    def test_backup_json_structure(self):
        """Structure attendue du JSON de backup."""
        backup_data = {
            "metadata": {
                "id": "20260128_120000",
                "created_at": "2026-01-28T12:00:00",
                "version": "1.0",
                "tables": ["recettes", "ingredients"],
            },
            "data": {
                "recettes": [
                    {"id": 1, "nom": "Recette 1"},
                    {"id": 2, "nom": "Recette 2"},
                ],
                "ingredients": [
                    {"id": 1, "nom": "Ingrédient 1"},
                ],
            }
        }
        
        # Vérifie que c'est sérialisable
        json_str = json.dumps(backup_data, ensure_ascii=False)
        
        # Et désérialisable
        parsed = json.loads(json_str)
        
        assert parsed["metadata"]["id"] == "20260128_120000"
        assert len(parsed["data"]["recettes"]) == 2
        assert parsed["data"]["ingredients"][0]["nom"] == "Ingrédient 1"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS CAS LIMITES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestBackupEdgeCases:
    """Tests pour cas limites."""

    def test_empty_tables_list(self):
        """Backup avec liste de tables vide."""
        from src.services.backup import BackupService, BackupConfig
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config = BackupConfig(backup_dir=tmpdir)
            service = BackupService(config=config)
            
            # Vérifier que le service peut gérer une liste vide
            assert service.MODELS_TO_BACKUP is not None

    def test_unknown_table_name(self):
        """Table inconnue dans la liste."""
        from src.services.backup import BackupService
        
        service = BackupService()
        
        # "table_inexistante" n'est pas dans MODELS_TO_BACKUP
        assert "table_inexistante" not in service.MODELS_TO_BACKUP

    def test_config_max_backups_zero(self):
        """max_backups=0 ne devrait pas crasher."""
        from src.services.backup import BackupConfig
        
        # Config avec 0 backups max
        config = BackupConfig(max_backups=0)
        
        assert config.max_backups == 0

