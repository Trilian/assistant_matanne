"""
Mixin de restauration et consultation des backups.

Contient les méthodes de restauration, listing, suppression
et inspection des fichiers de backup.
"""

import gzip
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

from sqlalchemy.orm import Session

from src.core.decorators import avec_gestion_erreurs, avec_session_db
from src.services.backup.types import BackupMetadata, RestoreResult
from src.services.backup.utils import filter_and_order_tables

if TYPE_CHECKING:
    from src.services.backup.types import BackupConfig

logger = logging.getLogger(__name__)


class BackupRestoreMixin:
    """Mixin fournissant les méthodes de restauration et consultation des backups."""

    config: "BackupConfig"
    MODELS_TO_BACKUP: dict[str, Any]

    # ═══════════════════════════════════════════════════════════
    # IMPORT / RESTORE
    # ═══════════════════════════════════════════════════════════

    @avec_gestion_erreurs(default_return=None, afficher_erreur=True)
    @avec_session_db
    def restore_backup(
        self,
        file_path: str,
        tables: list[str] | None = None,
        clear_existing: bool = False,
        db: Session = None,
    ) -> RestoreResult:
        """
        Restaure la base de données depuis un backup.

        Args:
            file_path: Chemin vers le fichier de backup
            tables: Tables à restaurer (None = toutes)
            clear_existing: Supprimer les données existantes avant restauration
            db: Session DB injectée

        Returns:
            RestoreResult avec le statut de la restauration
        """
        logger.info(f"🔄 Restauration depuis {file_path}...")

        path = Path(file_path)
        if not path.exists():
            return RestoreResult(success=False, message=f"Fichier non trouvé: {file_path}")

        # Lire le fichier
        try:
            if path.suffix == ".gz" or file_path.endswith(".json.gz"):
                with gzip.open(path, "rt", encoding="utf-8") as f:
                    backup_data = json.load(f)
            else:
                with open(path, encoding="utf-8") as f:
                    backup_data = json.load(f)
        except Exception as e:
            return RestoreResult(success=False, message=f"Erreur lecture fichier: {e}")

        # Valider la structure
        if "data" not in backup_data or "metadata" not in backup_data:
            return RestoreResult(success=False, message="Format de backup invalide")

        tables_to_restore = tables or list(backup_data["data"].keys())
        tables_restored = []
        total_records = 0
        errors = []

        # Utiliser l'ordre de restauration défini dans utils (respecter les FK)
        ordered_tables = filter_and_order_tables(tables_to_restore)

        for table_name in ordered_tables:
            if table_name not in self.MODELS_TO_BACKUP:
                continue

            model_class = self.MODELS_TO_BACKUP[table_name]
            records = backup_data["data"].get(table_name, [])

            try:
                # Supprimer les données existantes si demandé
                if clear_existing:
                    db.query(model_class).delete()
                    db.flush()

                # Insérer les enregistrements
                for record_data in records:
                    # Convertir les dates
                    for key, value in record_data.items():
                        if isinstance(value, str) and "T" in value:
                            try:
                                record_data[key] = datetime.fromisoformat(value)
                            except:
                                pass

                    record = model_class(**record_data)
                    db.merge(record)  # merge pour gérer les conflits de PK

                db.flush()
                tables_restored.append(table_name)
                total_records += len(records)
                logger.debug(f"  ✓ {table_name}: {len(records)} enregistrements restaurés")

            except Exception as e:
                error_msg = f"Erreur restauration {table_name}: {e}"
                logger.error(f"  ✗ {error_msg}")
                errors.append(error_msg)
                db.rollback()

        db.commit()

        logger.info(
            f"✅ Restauration terminée: {len(tables_restored)} tables, "
            f"{total_records} enregistrements"
        )

        return RestoreResult(
            success=len(errors) == 0,
            message=f"Restauration {'complète' if not errors else 'partielle'}",
            tables_restored=tables_restored,
            records_restored=total_records,
            errors=errors,
        )

    # ═══════════════════════════════════════════════════════════
    # LISTING ET CONSULTATION
    # ═══════════════════════════════════════════════════════════

    def list_backups(self) -> list[BackupMetadata]:
        """Liste tous les backups disponibles."""
        backup_path = Path(self.config.backup_dir)
        backups = []

        for file in sorted(backup_path.glob("backup_*"), reverse=True):
            try:
                # Extraire l'ID du nom de fichier
                backup_id = file.stem.replace("backup_", "").replace(".json", "")

                backups.append(
                    BackupMetadata(
                        id=backup_id,
                        created_at=datetime.fromtimestamp(file.stat().st_mtime),
                        file_size_bytes=file.stat().st_size,
                        compressed=file.suffix == ".gz" or ".gz" in file.name,
                    )
                )
            except Exception as e:
                logger.warning(f"Erreur lecture backup {file}: {e}")

        return backups

    def delete_backup(self, backup_id: str) -> bool:
        """Supprime un backup spécifique."""
        backup_path = Path(self.config.backup_dir)

        for file in backup_path.glob(f"backup_{backup_id}*"):
            file.unlink()
            logger.info(f"🗑️ Backup supprimé: {file.name}")
            return True

        return False

    def get_backup_info(self, file_path: str) -> BackupMetadata | None:
        """Récupère les informations d'un backup sans le charger entièrement."""
        path = Path(file_path)

        if not path.exists():
            return None

        try:
            if path.suffix == ".gz" or file_path.endswith(".json.gz"):
                with gzip.open(path, "rt", encoding="utf-8") as f:
                    # Lire seulement les premières lignes pour les métadonnées
                    content = f.read(10000)
                    data = json.loads(content[: content.rfind("}") + 1] + "}")
            else:
                with open(path, encoding="utf-8") as f:
                    content = f.read(10000)
                    data = json.loads(content[: content.rfind("}") + 1] + "}")

            metadata = data.get("metadata", {})
            return BackupMetadata(
                id=metadata.get("id", "unknown"),
                created_at=datetime.fromisoformat(
                    metadata.get("created_at", datetime.now().isoformat())
                ),
                version=metadata.get("version", "1.0"),
                file_size_bytes=path.stat().st_size,
                compressed=path.suffix == ".gz",
            )
        except Exception as e:
            logger.error(f"Erreur lecture métadonnées: {e}")
            return None
