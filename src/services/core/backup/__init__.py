"""
Package de backup pour l'Assistant Matanne.

Ce package fournit des services pour:
- Export complet de la base de données en JSON
- Backup vers fichier local ou Supabase Storage
- Planification de backups automatiques
- Restauration depuis backup
- Compression des données
- Historique des backups

Utilisation:
    from src.services.core.backup import obtenir_service_backup, ServiceBackup

    service = obtenir_service_backup()
    result = service.create_backup()
"""

# Types et schémas Pydantic
# Mixins
from src.services.core.backup.backup_export import BackupExportMixin
from src.services.core.backup.backup_restore import BackupRestoreMixin

# Service principal
from src.services.core.backup.service import (
    # Aliases pour rétrocompatibilité
    BackupService,
    ServiceBackup,
    get_backup_service,
    obtenir_service_backup,
)
from src.services.core.backup.types import (
    BackupConfig,
    BackupMetadata,
    BackupResult,
    RestoreResult,
)

# Fonctions utilitaires
from src.services.core.backup.utils_identity import (
    calculate_checksum,
    format_file_size,
    generate_backup_id,
    get_backup_filename,
    is_valid_backup_id,
    parse_backup_filename,
    parse_backup_id,
    verify_checksum,
)
from src.services.core.backup.utils_operations import (
    calculate_backup_stats,
    compare_backup_stats,
    filter_and_order_tables,
    get_backups_to_rotate,
    get_restore_order,
    should_run_backup,
)
from src.services.core.backup.utils_serialization import (
    deserialize_value,
    is_compressed_file,
    model_to_dict,
    serialize_value,
    validate_backup_metadata,
    validate_backup_structure,
)

__all__ = [
    # Types
    "BackupConfig",
    "BackupMetadata",
    "BackupResult",
    "RestoreResult",
    # Service
    "ServiceBackup",
    "obtenir_service_backup",
    # Mixins
    "BackupRestoreMixin",
    "BackupExportMixin",
    # Aliases rétrocompatibilité
    "BackupService",
    "get_backup_service",
    # Utilitaires - Identifiants
    "generate_backup_id",
    "parse_backup_id",
    "is_valid_backup_id",
    # Utilitaires - Checksums
    "calculate_checksum",
    "verify_checksum",
    # Utilitaires - Sérialisation
    "model_to_dict",
    "serialize_value",
    "deserialize_value",
    # Utilitaires - Validation
    "validate_backup_structure",
    "validate_backup_metadata",
    # Utilitaires - Fichiers
    "is_compressed_file",
    "get_backup_filename",
    "parse_backup_filename",
    "format_file_size",
    # Utilitaires - Ordre de restauration
    "get_restore_order",
    "filter_and_order_tables",
    # Utilitaires - Statistiques
    "calculate_backup_stats",
    "compare_backup_stats",
    # Utilitaires - Rotation
    "get_backups_to_rotate",
    "should_run_backup",
]
