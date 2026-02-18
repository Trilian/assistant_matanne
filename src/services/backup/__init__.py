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
    from src.services.backup import obtenir_service_backup, ServiceBackup

    service = obtenir_service_backup()
    result = service.create_backup()
"""

# Types et schémas Pydantic
# Mixins
from src.services.backup.backup_export import BackupExportMixin
from src.services.backup.backup_restore import BackupRestoreMixin

# Service principal
from src.services.backup.service import (
    # Aliases pour rétrocompatibilité
    BackupService,
    ServiceBackup,
    get_backup_service,
    obtenir_service_backup,
    render_backup_ui,
)
from src.services.backup.types import (
    BackupConfig,
    BackupMetadata,
    BackupResult,
    RestoreResult,
)

# Fonctions utilitaires
from src.services.backup.utils import (
    # Statistiques
    calculate_backup_stats,
    # Checksums
    calculate_checksum,
    compare_backup_stats,
    deserialize_value,
    filter_and_order_tables,
    format_file_size,
    # Identifiants
    generate_backup_id,
    get_backup_filename,
    # Rotation
    get_backups_to_rotate,
    # Ordre de restauration
    get_restore_order,
    # Fichiers
    is_compressed_file,
    is_valid_backup_id,
    # Sérialisation
    model_to_dict,
    parse_backup_filename,
    parse_backup_id,
    serialize_value,
    should_run_backup,
    validate_backup_metadata,
    # Validation
    validate_backup_structure,
    verify_checksum,
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
    "render_backup_ui",
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
