"""
Service de Backup Automatique pour l'Assistant Matanne.

Fonctionnalités:
- Export complet de la base de données en JSON
- Backup vers fichier local ou Supabase Storage
- Restauration depuis backup (via BackupRestoreMixin)
- Upload/download Supabase et historique (via BackupExportMixin)
- Compression des données
- Rotation automatique des anciens backups
"""

import gzip
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st
from sqlalchemy.orm import Session

from src.core.decorators import avec_gestion_erreurs, avec_session_db
from src.core.models import (
    ArticleCourses,
    ArticleInventaire,
    CalendarEvent,
    ChildProfile,
    EtapeRecette,
    FamilyActivity,
    FamilyBudget,
    GardenItem,
    GardenLog,
    HealthEntry,
    HealthObjective,
    HealthRoutine,
    Ingredient,
    Milestone,
    Planning,
    Project,
    ProjectTask,
    Recette,
    RecetteIngredient,
    Repas,
    Routine,
    RoutineTask,
    VersionRecette,
    WellbeingEntry,
)
from src.services.backup.backup_export import BackupExportMixin
from src.services.backup.backup_restore import BackupRestoreMixin
from src.services.backup.types import (
    BackupConfig,
    BackupMetadata,
    BackupResult,
)
from src.services.backup.utils_identity import calculate_checksum, generate_backup_id
from src.services.backup.utils_serialization import model_to_dict

logger = logging.getLogger(__name__)


class ServiceBackup(BackupRestoreMixin, BackupExportMixin):
    """
    Service de backup et restauration de la base de données.

    Supporte:
    - Export JSON complet ou partiel
    - Compression gzip
    - Upload vers Supabase Storage (via BackupExportMixin)
    - Restauration avec validation (via BackupRestoreMixin)
    - Rotation automatique des anciens backups
    """

    # Mapping des modèles à exporter
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

    # Méthodes utilitaires déléguées à utils
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

    # ═══════════════════════════════════════════════════════════
    # EXPORT / BACKUP
    # ═══════════════════════════════════════════════════════════

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
            tables: Liste des tables à exporter (None = toutes)
            compress: Compresser le backup (None = config par défaut)
            db: Session DB injectée

        Returns:
            BackupResult avec le chemin du fichier et les métadonnées
        """
        start_time = datetime.now()
        backup_id = self._generate_backup_id()
        should_compress = compress if compress is not None else self.config.compress

        logger.info(f"🔄 Création backup {backup_id}...")

        # Déterminer les tables à exporter
        tables_to_export = tables or list(self.MODELS_TO_BACKUP.keys())

        # Structure du backup
        backup_data = {
            "metadata": {
                "id": backup_id,
                "created_at": datetime.now().isoformat(),
                "version": "1.0",
                "tables": tables_to_export,
            },
            "data": {},
        }

        total_records = 0

        # Exporter chaque table
        for table_name in tables_to_export:
            if table_name not in self.MODELS_TO_BACKUP:
                logger.warning(f"⚠️ Table inconnue: {table_name}")
                continue

            model_class = self.MODELS_TO_BACKUP[table_name]

            try:
                records = db.query(model_class).all()
                backup_data["data"][table_name] = [
                    self._model_to_dict(record) for record in records
                ]
                total_records += len(records)
                logger.debug(f"  ✓ {table_name}: {len(records)} enregistrements")
            except Exception as e:
                logger.error(f"  ✗ Erreur export {table_name}: {e}")
                # Rollback pour libérer la transaction en erreur
                db.rollback()
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
            with gzip.open(file_path, "wt", encoding="utf-8") as f:
                f.write(json_data)
        else:
            with open(file_path, "w", encoding="utf-8") as f:
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
            f"✅ Backup créé: {filename} "
            f"({total_records} enregistrements, {file_size / 1024:.1f} KB, {duration:.2f}s)"
        )

        return BackupResult(
            success=True,
            message=f"Backup créé avec succès: {filename}",
            file_path=str(file_path),
            metadata=metadata,
            duration_seconds=duration,
        )

    def _rotate_old_backups(self):
        """Supprime les anciens backups au-delà de max_backups."""
        backup_path = Path(self.config.backup_dir)
        backups = sorted(
            backup_path.glob("backup_*"), key=lambda p: p.stat().st_mtime, reverse=True
        )

        if len(backups) > self.config.max_backups:
            for old_backup in backups[self.config.max_backups :]:
                old_backup.unlink()
                logger.info(f"🗑️ Ancien backup supprimé: {old_backup.name}")


# Alias pour rétrocompatibilité
BackupService = ServiceBackup


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


_backup_service: ServiceBackup | None = None


def obtenir_service_backup(config: BackupConfig | None = None) -> ServiceBackup:
    """Factory pour obtenir le service de backup."""
    global _backup_service
    if _backup_service is None:
        _backup_service = ServiceBackup(config)
    return _backup_service


# Alias pour rétrocompatibilité
get_backup_service = obtenir_service_backup


# ═══════════════════════════════════════════════════════════
# COMPOSANT UI STREAMLIT
# ═══════════════════════════════════════════════════════════


def render_backup_ui():  # pragma: no cover
    """Affiche l'interface de gestion des backups dans Streamlit."""
    st.subheader("💾 Sauvegarde & Restauration")

    service = obtenir_service_backup()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Créer un backup")

        compress = st.checkbox("Compresser (gzip)", value=True, key="backup_compress")

        if st.button("📥 Créer un backup maintenant", use_container_width=True, type="primary"):
            with st.spinner("Création du backup..."):
                result = service.create_backup(compress=compress)

                if result and result.success:
                    st.success(f"✅ {result.message}")
                    st.info(
                        f"📊 {result.metadata.total_records} enregistrements, "
                        f"{result.metadata.file_size_bytes / 1024:.1f} KB"
                    )
                else:
                    st.error("❌ Erreur lors de la création du backup")

    with col2:
        st.markdown("### Backups disponibles")

        backups = service.list_backups()

        if not backups:
            st.info("Aucun backup disponible")
        else:
            for backup in backups[:5]:  # Afficher les 5 derniers
                with st.expander(f"📝 {backup.id}"):
                    st.write(f"**Date:** {backup.created_at.strftime('%d/%m/%Y %H:%M')}")
                    st.write(f"**Taille:** {backup.file_size_bytes / 1024:.1f} KB")
                    st.write(f"**Compressé:** {'Oui' if backup.compressed else 'Non'}")

                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button("🔄 Restaurer", key=f"restore_{backup.id}"):
                            st.warning("⚠️ Cette action va écraser les données actuelles!")
                    with col_b:
                        if st.button("🗑️ Supprimer", key=f"delete_{backup.id}"):
                            if service.delete_backup(backup.id):
                                st.success("Backup supprimé")
                                st.rerun()

    # Section restauration
    st.markdown("---")
    st.markdown("### Restaurer depuis un fichier")

    uploaded_file = st.file_uploader(
        "Choisir un fichier de backup", type=["json", "gz"], key="backup_upload"
    )

    if uploaded_file:
        clear_existing = st.checkbox(
            "Supprimer les données existantes avant restauration",
            value=False,
            key="clear_before_restore",
        )

        if st.button("🔄 Restaurer ce backup", type="secondary"):
            # Sauvegarder temporairement le fichier
            temp_path = Path(service.config.backup_dir) / f"temp_{uploaded_file.name}"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.read())

            with st.spinner("Restauration en cours..."):
                result = service.restore_backup(str(temp_path), clear_existing=clear_existing)

                if result.success:
                    st.success(f"✅ {result.message}")
                    st.info(f"📊 {result.records_restored} enregistrements restaurés")
                else:
                    st.error(f"❌ {result.message}")
                    if result.errors:
                        for error in result.errors:
                            st.warning(error)

            # Nettoyer le fichier temporaire
            temp_path.unlink(missing_ok=True)
