"""
Mixin d'export Supabase et historique des backups.

Contient les méthodes d'upload/download vers Supabase Storage
et la gestion de l'historique des backups en base de données.
"""

import logging
from pathlib import Path
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy.orm import Session

from src.core.decorators import avec_session_db
from src.core.models import Backup as BackupModel
from src.services.core.backup.types import BackupMetadata

if TYPE_CHECKING:
    from src.services.core.backup.types import BackupConfig

logger = logging.getLogger(__name__)


class BackupExportMixin:
    """Mixin fournissant les méthodes d'export Supabase et d'historique DB."""

    config: "BackupConfig"

    # ═══════════════════════════════════════════════════════════
    # UPLOAD SUPABASE STORAGE
    # ═══════════════════════════════════════════════════════════

    def upload_to_supabase(self, file_path: str, bucket: str = "backups") -> bool:
        """
        Upload un backup vers Supabase Storage.

        Args:
            file_path: Chemin du fichier à uploader
            bucket: Nom du bucket Supabase Storage

        Returns:
            True si succès, False sinon
        """
        try:
            from supabase import create_client

            from src.core.config import obtenir_parametres

            params = obtenir_parametres()
            supabase_url = getattr(params, "SUPABASE_URL", None)
            supabase_key = getattr(params, "SUPABASE_SERVICE_KEY", None) or getattr(
                params, "SUPABASE_ANON_KEY", None
            )

            if not supabase_url or not supabase_key:
                logger.warning("Supabase non configuré pour le storage")
                return False

            client = create_client(supabase_url, supabase_key)

            path = Path(file_path)
            with open(path, "rb") as f:
                client.storage.from_(bucket).upload(
                    path.name,
                    f.read(),
                    {
                        "content-type": "application/gzip"
                        if path.suffix == ".gz"
                        else "application/json"
                    },
                )

            logger.info(f"✅ Backup uploadé vers Supabase: {path.name}")
            return True

        except Exception as e:
            logger.error(f"Erreur upload Supabase: {e}")
            return False

    def download_from_supabase(self, filename: str, bucket: str = "backups") -> str | None:
        """
        Télécharge un backup depuis Supabase Storage.

        Args:
            filename: Nom du fichier à télécharger
            bucket: Nom du bucket Supabase Storage

        Returns:
            Chemin local du fichier téléchargé ou None si erreur
        """
        try:
            from supabase import create_client

            from src.core.config import obtenir_parametres

            params = obtenir_parametres()
            client = create_client(
                getattr(params, "SUPABASE_URL", ""), getattr(params, "SUPABASE_ANON_KEY", "")
            )

            response = client.storage.from_(bucket).download(filename)

            local_path = Path(self.config.backup_dir) / filename
            with open(local_path, "wb") as f:
                f.write(response)

            logger.info(f"✅ Backup téléchargé: {filename}")
            return str(local_path)

        except Exception as e:
            logger.error(f"Erreur téléchargement Supabase: {e}")
            return None

    # ═══════════════════════════════════════════════════════════
    # PERSISTANCE BASE DE DONNÉES (HISTORIQUE)
    # ═══════════════════════════════════════════════════════════

    @avec_session_db
    def enregistrer_backup_historique(
        self,
        metadata: BackupMetadata,
        storage_path: str | None = None,
        user_id: UUID | str | None = None,
        db: Session = None,
    ) -> BackupModel | None:
        """
        Enregistre un backup dans l'historique de la base de données.

        Args:
            metadata: Métadonnées du backup
            storage_path: Chemin Supabase Storage (optionnel)
            user_id: UUID de l'utilisateur
            db: Session SQLAlchemy

        Returns:
            Modèle Backup créé
        """
        try:
            db_backup = BackupModel(
                filename=f"backup_{metadata.id}.json" + (".gz" if metadata.compressed else ""),
                tables_included=[],  # Sera rempli si disponible
                row_counts={},
                size_bytes=metadata.file_size_bytes,
                compressed=metadata.compressed,
                storage_path=storage_path,
                version=metadata.version,
                user_id=UUID(str(user_id)) if user_id else None,
            )
            db.add(db_backup)
            db.commit()
            db.refresh(db_backup)
            logger.info(f"Backup enregistré dans historique: {db_backup.id}")
            return db_backup
        except Exception as e:
            logger.error(f"Erreur enregistrement backup historique: {e}")
            db.rollback()
            return None

    @avec_session_db
    def lister_backups_historique(
        self,
        user_id: UUID | str | None = None,
        limit: int = 20,
        db: Session = None,
    ) -> list[BackupModel]:
        """
        Liste les backups depuis l'historique DB.

        Args:
            user_id: UUID de l'utilisateur (filtre optionnel)
            limit: Nombre max de résultats
            db: Session SQLAlchemy

        Returns:
            Liste des backups
        """
        query = db.query(BackupModel)

        if user_id:
            query = query.filter(BackupModel.user_id == UUID(str(user_id)))

        return query.order_by(BackupModel.created_at.desc()).limit(limit).all()

    @avec_session_db
    def supprimer_backup_historique(
        self,
        backup_id: int,
        db: Session = None,
    ) -> bool:
        """
        Supprime un backup de l'historique.

        Args:
            backup_id: ID du backup
            db: Session SQLAlchemy

        Returns:
            True si succès
        """
        backup = db.query(BackupModel).filter(BackupModel.id == backup_id).first()
        if backup:
            db.delete(backup)
            db.commit()
            logger.info(f"Backup supprimé de l'historique: {backup_id}")
            return True
        return False
