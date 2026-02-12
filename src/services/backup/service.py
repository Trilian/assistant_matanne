"""
Service de Backup Automatique pour l'Assistant Matanne.

Fonctionnalités:
- Export complet de la base de données en JSON
- Backup vers fichier local ou Supabase Storage
- Planification de backups automatiques
- Restauration depuis backup
- Compression des données
- Historique des backups
"""

import gzip
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import UUID

import streamlit as st
from sqlalchemy.orm import Session

from src.core.database import obtenir_contexte_db
from src.core.decorators import avec_session_db, avec_gestion_erreurs
from src.services.backup.types import (
    BackupConfig,
    BackupMetadata,
    BackupResult,
    RestoreResult,
)
from src.services.backup.utils import (
    generate_backup_id,
    calculate_checksum,
    model_to_dict,
    filter_and_order_tables,
)
from src.core.models import (
    Recette,
    Ingredient,
    RecetteIngredient,
    EtapeRecette,
    VersionRecette,
    ArticleInventaire,
    ArticleCourses,
    Planning,
    Repas,
    ChildProfile,
    Milestone,
    FamilyActivity,
    FamilyBudget,
    WellbeingEntry,
    HealthRoutine,
    HealthObjective,
    HealthEntry,
    Project,
    ProjectTask,
    Routine,
    RoutineTask,
    GardenItem,
    GardenLog,
    CalendarEvent,
    Backup as BackupModel,  # Modèle DB pour historique
)

logger = logging.getLogger(__name__)


class ServiceBackup:
    """
    Service de backup et restauration de la base de données.
    
    Supporte:
    - Export JSON complet ou partiel
    - Compression gzip
    - Upload vers Supabase Storage
    - Restauration avec validation
    - Rotation automatique des anciens backups
    """
    
    # Mapping des modèles Ã  exporter
    MODELS_TO_BACKUP = {
        "ingredients": Ingredient,
        "recettes": Recette,
        "recette_ingredients": RecetteIngredient,
        "etapes_recette": EtapeRecette,
        "versions_recette": VersionRecette,
        "articles_inventaire": ArticleInventaire,
        "articles_courses": ArticleCourses,
        "plannings": Planning,
        "repas": Repas,
        "child_profiles": ChildProfile,
        "milestones": Milestone,
        "family_activities": FamilyActivity,
        "family_budgets": FamilyBudget,
        "wellbeing_entries": WellbeingEntry,
        "health_routines": HealthRoutine,
        "health_objectives": HealthObjective,
        "health_entries": HealthEntry,
        "projects": Project,
        "project_tasks": ProjectTask,
        "routines": Routine,
        "routine_tasks": RoutineTask,
        "garden_items": GardenItem,
        "garden_logs": GardenLog,
        "calendar_events": CalendarEvent,
    }
    
    def __init__(self, config: BackupConfig | None = None):
        """Initialise le service de backup."""
        self.config = config or BackupConfig()
        self._ensure_backup_dir()
    
    def _ensure_backup_dir(self):
        """Crée le répertoire de backup s'il n'existe pas."""
        backup_path = Path(self.config.backup_dir)
        backup_path.mkdir(parents=True, exist_ok=True)
    
    # Méthodes utilitaires déléguées Ã  utils
    @staticmethod
    def _model_to_dict(obj: Any) -> dict:
        """Convertit un objet SQLAlchemy en dictionnaire."""
        return model_to_dict(obj)
    
    @staticmethod
    def _generate_backup_id() -> str:
        """Génère un ID unique pour le backup."""
        return generate_backup_id()
    
    @staticmethod
    def _calculate_checksum(data: str) -> str:
        """Calcule le checksum MD5 des données."""
        return calculate_checksum(data)
    
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # EXPORT / BACKUP
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    
    @avec_gestion_erreurs(default_return=None, afficher_erreur=True)
    @avec_session_db
    def create_backup(
        self,
        tables: list[str] | None = None,
        compress: bool | None = None,
        db: Session = None,
    ) -> BackupResult:
        """
        Crée un backup complet ou partiel de la base de données.
        
        Args:
            tables: Liste des tables Ã  exporter (None = toutes)
            compress: Compresser le backup (None = config par défaut)
            db: Session DB injectée
            
        Returns:
            BackupResult avec le chemin du fichier et les métadonnées
        """
        start_time = datetime.now()
        backup_id = self._generate_backup_id()
        should_compress = compress if compress is not None else self.config.compress
        
        logger.info(f"ðŸ”„ Création backup {backup_id}...")
        
        # Déterminer les tables Ã  exporter
        tables_to_export = tables or list(self.MODELS_TO_BACKUP.keys())
        
        # Structure du backup
        backup_data = {
            "metadata": {
                "id": backup_id,
                "created_at": datetime.now().isoformat(),
                "version": "1.0",
                "tables": tables_to_export,
            },
            "data": {}
        }
        
        total_records = 0
        
        # Exporter chaque table
        for table_name in tables_to_export:
            if table_name not in self.MODELS_TO_BACKUP:
                logger.warning(f"âš ï¸ Table inconnue: {table_name}")
                continue
            
            model_class = self.MODELS_TO_BACKUP[table_name]
            
            try:
                records = db.query(model_class).all()
                backup_data["data"][table_name] = [
                    self._model_to_dict(record) for record in records
                ]
                total_records += len(records)
                logger.debug(f"  âœ“ {table_name}: {len(records)} enregistrements")
            except Exception as e:
                logger.error(f"  âœ— Erreur export {table_name}: {e}")
                backup_data["data"][table_name] = []
        
        # Sérialiser
        json_data = json.dumps(backup_data, ensure_ascii=False, indent=2)
        checksum = self._calculate_checksum(json_data)
        
        # Nom du fichier
        extension = ".json.gz" if should_compress else ".json"
        filename = f"backup_{backup_id}{extension}"
        file_path = Path(self.config.backup_dir) / filename
        
        # Écrire le fichier
        if should_compress:
            with gzip.open(file_path, 'wt', encoding='utf-8') as f:
                f.write(json_data)
        else:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(json_data)
        
        file_size = file_path.stat().st_size
        duration = (datetime.now() - start_time).total_seconds()
        
        # Métadonnées
        metadata = BackupMetadata(
            id=backup_id,
            created_at=datetime.now(),
            tables_count=len(tables_to_export),
            total_records=total_records,
            file_size_bytes=file_size,
            compressed=should_compress,
            checksum=checksum,
        )
        
        # Rotation des anciens backups
        self._rotate_old_backups()
        
        logger.info(
            f"âœ… Backup créé: {filename} "
            f"({total_records} enregistrements, {file_size/1024:.1f} KB, {duration:.2f}s)"
        )
        
        return BackupResult(
            success=True,
            message=f"Backup créé avec succès: {filename}",
            file_path=str(file_path),
            metadata=metadata,
            duration_seconds=duration,
        )
    
    def _rotate_old_backups(self):
        """Supprime les anciens backups au-delÃ  de max_backups."""
        backup_path = Path(self.config.backup_dir)
        backups = sorted(
            backup_path.glob("backup_*"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        
        if len(backups) > self.config.max_backups:
            for old_backup in backups[self.config.max_backups:]:
                old_backup.unlink()
                logger.info(f"ðŸ—‘ï¸ Ancien backup supprimé: {old_backup.name}")
    
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # IMPORT / RESTORE
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    
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
            tables: Tables Ã  restaurer (None = toutes)
            clear_existing: Supprimer les données existantes avant restauration
            db: Session DB injectée
            
        Returns:
            RestoreResult avec le statut de la restauration
        """
        logger.info(f"ðŸ”„ Restauration depuis {file_path}...")
        
        path = Path(file_path)
        if not path.exists():
            return RestoreResult(
                success=False,
                message=f"Fichier non trouvé: {file_path}"
            )
        
        # Lire le fichier
        try:
            if path.suffix == '.gz' or file_path.endswith('.json.gz'):
                with gzip.open(path, 'rt', encoding='utf-8') as f:
                    backup_data = json.load(f)
            else:
                with open(path, 'r', encoding='utf-8') as f:
                    backup_data = json.load(f)
        except Exception as e:
            return RestoreResult(
                success=False,
                message=f"Erreur lecture fichier: {e}"
            )
        
        # Valider la structure
        if "data" not in backup_data or "metadata" not in backup_data:
            return RestoreResult(
                success=False,
                message="Format de backup invalide"
            )
        
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
                        if isinstance(value, str) and 'T' in value:
                            try:
                                record_data[key] = datetime.fromisoformat(value)
                            except:
                                pass
                    
                    record = model_class(**record_data)
                    db.merge(record)  # merge pour gérer les conflits de PK
                
                db.flush()
                tables_restored.append(table_name)
                total_records += len(records)
                logger.debug(f"  âœ“ {table_name}: {len(records)} enregistrements restaurés")
                
            except Exception as e:
                error_msg = f"Erreur restauration {table_name}: {e}"
                logger.error(f"  âœ— {error_msg}")
                errors.append(error_msg)
                db.rollback()
        
        db.commit()
        
        logger.info(
            f"âœ… Restauration terminée: {len(tables_restored)} tables, "
            f"{total_records} enregistrements"
        )
        
        return RestoreResult(
            success=len(errors) == 0,
            message=f"Restauration {'complète' if not errors else 'partielle'}",
            tables_restored=tables_restored,
            records_restored=total_records,
            errors=errors,
        )
    
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # UTILITAIRES
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    
    def list_backups(self) -> list[BackupMetadata]:
        """Liste tous les backups disponibles."""
        backup_path = Path(self.config.backup_dir)
        backups = []
        
        for file in sorted(backup_path.glob("backup_*"), reverse=True):
            try:
                # Extraire l'ID du nom de fichier
                backup_id = file.stem.replace("backup_", "").replace(".json", "")
                
                backups.append(BackupMetadata(
                    id=backup_id,
                    created_at=datetime.fromtimestamp(file.stat().st_mtime),
                    file_size_bytes=file.stat().st_size,
                    compressed=file.suffix == '.gz' or '.gz' in file.name,
                ))
            except Exception as e:
                logger.warning(f"Erreur lecture backup {file}: {e}")
        
        return backups
    
    def delete_backup(self, backup_id: str) -> bool:
        """Supprime un backup spécifique."""
        backup_path = Path(self.config.backup_dir)
        
        for file in backup_path.glob(f"backup_{backup_id}*"):
            file.unlink()
            logger.info(f"ðŸ—‘ï¸ Backup supprimé: {file.name}")
            return True
        
        return False
    
    def get_backup_info(self, file_path: str) -> BackupMetadata | None:
        """Récupère les informations d'un backup sans le charger entièrement."""
        path = Path(file_path)
        
        if not path.exists():
            return None
        
        try:
            if path.suffix == '.gz' or file_path.endswith('.json.gz'):
                with gzip.open(path, 'rt', encoding='utf-8') as f:
                    # Lire seulement les premières lignes pour les métadonnées
                    content = f.read(10000)
                    data = json.loads(content[:content.rfind('}') + 1] + '}')
            else:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read(10000)
                    data = json.loads(content[:content.rfind('}') + 1] + '}')
            
            metadata = data.get("metadata", {})
            return BackupMetadata(
                id=metadata.get("id", "unknown"),
                created_at=datetime.fromisoformat(metadata.get("created_at", datetime.now().isoformat())),
                version=metadata.get("version", "1.0"),
                file_size_bytes=path.stat().st_size,
                compressed=path.suffix == '.gz',
            )
        except Exception as e:
            logger.error(f"Erreur lecture métadonnées: {e}")
            return None
    
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # UPLOAD SUPABASE STORAGE
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    
    def upload_to_supabase(self, file_path: str, bucket: str = "backups") -> bool:
        """
        Upload un backup vers Supabase Storage.
        
        Args:
            file_path: Chemin du fichier Ã  uploader
            bucket: Nom du bucket Supabase Storage
            
        Returns:
            True si succès, False sinon
        """
        try:
            from supabase import create_client
            from src.core.config import obtenir_parametres
            
            params = obtenir_parametres()
            supabase_url = getattr(params, 'SUPABASE_URL', None)
            supabase_key = getattr(params, 'SUPABASE_SERVICE_KEY', None) or getattr(params, 'SUPABASE_ANON_KEY', None)
            
            if not supabase_url or not supabase_key:
                logger.warning("Supabase non configuré pour le storage")
                return False
            
            client = create_client(supabase_url, supabase_key)
            
            path = Path(file_path)
            with open(path, 'rb') as f:
                response = client.storage.from_(bucket).upload(
                    path.name,
                    f.read(),
                    {"content-type": "application/gzip" if path.suffix == '.gz' else "application/json"}
                )
            
            logger.info(f"âœ… Backup uploadé vers Supabase: {path.name}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur upload Supabase: {e}")
            return False
    
    def download_from_supabase(self, filename: str, bucket: str = "backups") -> str | None:
        """
        Télécharge un backup depuis Supabase Storage.
        
        Args:
            filename: Nom du fichier Ã  télécharger
            bucket: Nom du bucket Supabase Storage
            
        Returns:
            Chemin local du fichier téléchargé ou None si erreur
        """
        try:
            from supabase import create_client
            from src.core.config import obtenir_parametres
            
            params = obtenir_parametres()
            client = create_client(
                getattr(params, 'SUPABASE_URL', ''),
                getattr(params, 'SUPABASE_ANON_KEY', '')
            )
            
            response = client.storage.from_(bucket).download(filename)
            
            local_path = Path(self.config.backup_dir) / filename
            with open(local_path, 'wb') as f:
                f.write(response)
            
            logger.info(f"âœ… Backup téléchargé: {filename}")
            return str(local_path)
            
        except Exception as e:
            logger.error(f"Erreur téléchargement Supabase: {e}")
            return None

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # PERSISTANCE BASE DE DONNÉES (HISTORIQUE)
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

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


# Alias pour rétrocompatibilité
BackupService = ServiceBackup


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# FACTORY
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


_backup_service: ServiceBackup | None = None


def obtenir_service_backup(config: BackupConfig | None = None) -> ServiceBackup:
    """Factory pour obtenir le service de backup."""
    global _backup_service
    if _backup_service is None:
        _backup_service = ServiceBackup(config)
    return _backup_service


# Alias pour rétrocompatibilité
get_backup_service = obtenir_service_backup


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# COMPOSANT UI STREAMLIT
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def render_backup_ui():
    """Affiche l'interface de gestion des backups dans Streamlit."""
    st.subheader("ðŸ’¾ Sauvegarde & Restauration")
    
    service = obtenir_service_backup()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Créer un backup")
        
        compress = st.checkbox("Compresser (gzip)", value=True, key="backup_compress")
        
        if st.button("ðŸ“¥ Créer un backup maintenant", use_container_width=True, type="primary"):
            with st.spinner("Création du backup..."):
                result = service.create_backup(compress=compress)
                
                if result and result.success:
                    st.success(f"âœ… {result.message}")
                    st.info(f"ðŸ“Š {result.metadata.total_records} enregistrements, "
                           f"{result.metadata.file_size_bytes/1024:.1f} KB")
                else:
                    st.error("âŒ Erreur lors de la création du backup")
    
    with col2:
        st.markdown("### Backups disponibles")
        
        backups = service.list_backups()
        
        if not backups:
            st.info("Aucun backup disponible")
        else:
            for backup in backups[:5]:  # Afficher les 5 derniers
                with st.expander(f"ðŸ“ {backup.id}"):
                    st.write(f"**Date:** {backup.created_at.strftime('%d/%m/%Y %H:%M')}")
                    st.write(f"**Taille:** {backup.file_size_bytes/1024:.1f} KB")
                    st.write(f"**Compressé:** {'Oui' if backup.compressed else 'Non'}")
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button("ðŸ”„ Restaurer", key=f"restore_{backup.id}"):
                            st.warning("âš ï¸ Cette action va écraser les données actuelles!")
                    with col_b:
                        if st.button("ðŸ—‘ï¸ Supprimer", key=f"delete_{backup.id}"):
                            if service.delete_backup(backup.id):
                                st.success("Backup supprimé")
                                st.rerun()
    
    # Section restauration
    st.markdown("---")
    st.markdown("### Restaurer depuis un fichier")
    
    uploaded_file = st.file_uploader(
        "Choisir un fichier de backup",
        type=["json", "gz"],
        key="backup_upload"
    )
    
    if uploaded_file:
        clear_existing = st.checkbox(
            "Supprimer les données existantes avant restauration",
            value=False,
            key="clear_before_restore"
        )
        
        if st.button("ðŸ”„ Restaurer ce backup", type="secondary"):
            # Sauvegarder temporairement le fichier
            temp_path = Path(service.config.backup_dir) / f"temp_{uploaded_file.name}"
            with open(temp_path, 'wb') as f:
                f.write(uploaded_file.read())
            
            with st.spinner("Restauration en cours..."):
                result = service.restore_backup(
                    str(temp_path),
                    clear_existing=clear_existing
                )
                
                if result.success:
                    st.success(f"âœ… {result.message}")
                    st.info(f"ðŸ“Š {result.records_restored} enregistrements restaurés")
                else:
                    st.error(f"âŒ {result.message}")
                    if result.errors:
                        for error in result.errors:
                            st.warning(error)
            
            # Nettoyer le fichier temporaire
            temp_path.unlink(missing_ok=True)
