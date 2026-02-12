"""
Types et schémas Pydantic pour le service de backup.

Définit les modèles de configuration, métadonnées et résultats.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class BackupConfig(BaseModel):
    """Configuration du service de backup."""
    
    backup_dir: str = "backups"
    max_backups: int = 10  # Nombre max de backups Ã  conserver
    compress: bool = True
    include_timestamps: bool = True
    auto_backup_enabled: bool = True
    auto_backup_interval_hours: int = 24


class BackupMetadata(BaseModel):
    """Métadonnées d'un backup."""
    
    id: str = ""
    created_at: datetime = Field(default_factory=datetime.now)
    version: str = "1.0"
    tables_count: int = 0
    total_records: int = 0
    file_size_bytes: int = 0
    compressed: bool = False
    checksum: str = ""


class BackupResult(BaseModel):
    """Résultat d'une opération de backup."""
    
    success: bool = False
    message: str = ""
    file_path: str | None = None
    metadata: BackupMetadata | None = None
    duration_seconds: float = 0.0


class RestoreResult(BaseModel):
    """Résultat d'une restauration."""
    
    success: bool = False
    message: str = ""
    tables_restored: list[str] = Field(default_factory=list)
    records_restored: int = 0
    errors: list[str] = Field(default_factory=list)


__all__ = [
    "BackupConfig",
    "BackupMetadata",
    "BackupResult",
    "RestoreResult",
]
