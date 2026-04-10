"""Service Backup Personnel - Export des donnees utilisateur.

Permet d'exporter toutes les donnees personnelles en formats standards (JSON, CSV)
pour archivage ou sauvegarde.

Usage:
    from src.services.core.utilisateur.backup_personnel import obtenir_backup_service

    service = obtenir_backup_service()
    zip_path = service.exporter_donnees_utilisateur(user_id="abc-123")
"""

from __future__ import annotations

import csv
import io
import json
import logging
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from sqlalchemy import inspect
from sqlalchemy.orm import Session

from src.core.decorators import avec_gestion_erreurs, avec_session_db
from src.services.core.backup.utils_serialization import model_to_dict
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)

# Colonnes user_id connues dans les différents modèles
_USER_ID_COLUMNS = frozenset({"user_id", "utilisateur_id", "profil_id"})


class ServiceBackupPersonnel:
    """Service d'export de données personnelles (backup)."""

    # Modèles contenant des données utilisateur avec leur colonne FK
    MODELS_USER_DATA: dict[str, tuple[Any, str]] = {}

    def __init__(self) -> None:
        self._init_models()

    def _init_models(self) -> None:
        """Initialise le mapping des modèles avec données utilisateur."""
        if self.MODELS_USER_DATA:
            return

        from src.core.models import (
            ActiviteFamille,
            ArticleCourses,
            ArticleInventaire,
            BudgetFamille,
            ElementJardin,
            EntreeBienEtre,
            EntreeSante,
            EtapeRecette,
            EvenementPlanning,
            Ingredient,
            Jalon,
            JournalJardin,
            ObjectifSante,
            Planning,
            ProfilEnfant,
            ProfilUtilisateur,
            Projet,
            Recette,
            RecetteIngredient,
            Repas,
            Routine,
            RoutineSante,
            TacheProjet,
            TacheRoutine,
            VersionRecette,
        )

        # Mapping: nom_categorie → (ModelClass, colonne_user_id)
        self.MODELS_USER_DATA = {
            "profil": (ProfilUtilisateur, "id"),
            "recettes": (Recette, "user_id"),
            "ingredients": (Ingredient, "user_id"),
            "recette_ingredients": (RecetteIngredient, "user_id"),
            "etapes_recette": (EtapeRecette, "user_id"),
            "versions_recette": (VersionRecette, "user_id"),
            "articles_inventaire": (ArticleInventaire, "user_id"),
            "articles_courses": (ArticleCourses, "user_id"),
            "plannings": (Planning, "user_id"),
            "repas": (Repas, "user_id"),
            "evenements_planning": (EvenementPlanning, "user_id"),
            "profils_enfants": (ProfilEnfant, "user_id"),
            "jalons": (Jalon, "user_id"),
            "activites_famille": (ActiviteFamille, "user_id"),
            "budgets_famille": (BudgetFamille, "user_id"),
            "entrees_bien_etre": (EntreeBienEtre, "user_id"),
            "routines_sante": (RoutineSante, "user_id"),
            "objectifs_sante": (ObjectifSante, "user_id"),
            "entrees_sante": (EntreeSante, "user_id"),
            "projets": (Projet, "user_id"),
            "taches_projets": (TacheProjet, "user_id"),
            "routines": (Routine, "user_id"),
            "taches_routines": (TacheRoutine, "user_id"),
            "elements_jardin": (ElementJardin, "user_id"),
            "journaux_jardin": (JournalJardin, "user_id"),
        }

    def _has_column(self, model: Any, column_name: str) -> bool:
        """Vérifie si un modèle possède une colonne donnée."""
        try:
            mapper = inspect(model)
            return column_name in [c.key for c in mapper.columns]
        except Exception:
            return False

    def _query_user_data(
        self, session: Session, model: Any, user_col: str, user_id: str
    ) -> list[dict]:
        """Récupère les données d'un modèle filtrées par user_id."""
        try:
            if not self._has_column(model, user_col):
                # Si la colonne n'existe pas, skip silencieusement
                return []

            col = getattr(model, user_col, None)
            if col is None:
                return []

            rows = session.query(model).filter(col == user_id).all()
            return [model_to_dict(row) for row in rows]
        except Exception as e:
            logger.warning(f"Erreur requête {model.__name__}: {e}")
            return []

    @avec_gestion_erreurs(default_return=None, afficher_erreur=True)
    @avec_session_db
    def exporter_donnees_utilisateur(self, user_id: str, db: Session = None) -> Path:
        """
        Exporte toutes les données d'un utilisateur dans un fichier ZIP.

        Le ZIP contient:
        - donnees.json : toutes les données en JSON
        - Un fichier CSV par catégorie non vide

        Returns:
            Path vers le fichier ZIP généré
        """
        export_data: dict[str, list[dict]] = {}
        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")

        for categorie, (model, user_col) in self.MODELS_USER_DATA.items():
            rows = self._query_user_data(db, model, user_col, user_id)
            if rows:
                export_data[categorie] = rows

        # Créer le ZIP en mémoire
        export_dir = Path("data/exports")
        export_dir.mkdir(parents=True, exist_ok=True)
        zip_path = export_dir / f"backup_{user_id[:8]}_{timestamp}.zip"

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            # JSON complet
            json_content = json.dumps(export_data, ensure_ascii=False, indent=2, default=str)
            zf.writestr("donnees.json", json_content)

            # CSV par catégorie
            for categorie, rows in export_data.items():
                if not rows:
                    continue
                csv_buffer = io.StringIO()
                writer = csv.DictWriter(csv_buffer, fieldnames=rows[0].keys())
                writer.writeheader()
                for row in rows:
                    writer.writerow({k: str(v) if v is not None else "" for k, v in row.items()})
                zf.writestr(f"{categorie}.csv", csv_buffer.getvalue())

            # Métadonnées
            meta = {
                "export_date": datetime.now(UTC).isoformat(),
                "user_id": user_id,
                "categories": {k: len(v) for k, v in export_data.items()},
                "total_elements": sum(len(v) for v in export_data.values()),
                "format_version": "1.0",
            }
            zf.writestr("metadata.json", json.dumps(meta, ensure_ascii=False, indent=2))

        logger.info(
            f"Backup créé pour user {user_id[:8]}: {zip_path} "
            f"({sum(len(v) for v in export_data.values())} éléments)"
        )
        return zip_path


@service_factory("backup_personnel", tags={"utilisateur", "backup"})
def obtenir_backup_service() -> ServiceBackupPersonnel:
    """Retourne le service backup personnel (singleton via registre)."""
    return ServiceBackupPersonnel()
