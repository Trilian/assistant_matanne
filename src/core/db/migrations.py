"""
Migrations - Gestionnaire de migrations SQL par fichiers.

Auto-découverte des fichiers SQL dans sql/migrations/
avec suivi de version, checksums et exécution ordonnée.
"""

import hashlib
import logging
import re
from pathlib import Path

from sqlalchemy import text

from ..errors import ErreurBaseDeDonnees
from .engine import obtenir_moteur

logger = logging.getLogger(__name__)

__all__ = ["GestionnaireMigrations", "DOSSIER_MIGRATIONS"]

# Répertoire racine du projet (remonte de src/core/db → racine)
_RACINE_PROJET = Path(__file__).resolve().parent.parent.parent.parent
DOSSIER_MIGRATIONS = _RACINE_PROJET / "sql" / "migrations"


class GestionnaireMigrations:
    """
    Gestionnaire de migrations SQL par fichiers.

    Auto-découvre les fichiers .sql dans sql/migrations/,
    les exécute dans l'ordre numérique et enregistre chaque
    application avec un checksum SHA-256 pour détecter les
    modifications post-application.
    """

    TABLE_MIGRATIONS = "schema_migrations"
    """Nom de la table de suivi des migrations."""

    @staticmethod
    def initialiser_table_migrations():
        """
        Crée la table de suivi des migrations si elle n'existe pas.
        Ajoute la colonne checksum si absente (rétrocompatibilité).
        """
        moteur = obtenir_moteur()

        with moteur.connect() as conn:
            conn.execute(
                text(f"""
                    CREATE TABLE IF NOT EXISTS {GestionnaireMigrations.TABLE_MIGRATIONS} (
                        id SERIAL PRIMARY KEY,
                        version INTEGER NOT NULL UNIQUE,
                        name VARCHAR(255) NOT NULL,
                        checksum VARCHAR(64),
                        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
            )
            # Ajouter checksum si table existante sans cette colonne
            conn.execute(
                text(f"""
                    DO $$
                    BEGIN
                        IF NOT EXISTS (
                            SELECT 1 FROM information_schema.columns
                            WHERE table_name = '{GestionnaireMigrations.TABLE_MIGRATIONS}'
                            AND column_name = 'checksum'
                        ) THEN
                            ALTER TABLE {GestionnaireMigrations.TABLE_MIGRATIONS}
                            ADD COLUMN checksum VARCHAR(64);
                        END IF;
                    END $$;
                """)
            )
            conn.commit()

        logger.info("[OK] Table migrations initialisée")

    @staticmethod
    def obtenir_version_courante() -> int:
        """
        Retourne la version actuelle du schéma.

        Returns:
            Numéro de version (0 si aucune migration)
        """
        try:
            moteur = obtenir_moteur()

            with moteur.connect() as conn:
                resultat = conn.execute(
                    text(f"""
                        SELECT MAX(version)
                        FROM {GestionnaireMigrations.TABLE_MIGRATIONS}
                    """)
                ).scalar()

                return resultat if resultat else 0

        except Exception:
            return 0

    @staticmethod
    def obtenir_migrations_appliquees() -> dict[int, dict]:
        """
        Retourne les migrations déjà appliquées.

        Returns:
            Dict {version: {name, checksum, applied_at}}
        """
        try:
            moteur = obtenir_moteur()

            with moteur.connect() as conn:
                rows = conn.execute(
                    text(f"""
                        SELECT version, name, checksum, applied_at
                        FROM {GestionnaireMigrations.TABLE_MIGRATIONS}
                        ORDER BY version
                    """)
                ).fetchall()

                return {
                    row[0]: {
                        "name": row[1],
                        "checksum": row[2],
                        "applied_at": row[3],
                    }
                    for row in rows
                }

        except Exception:
            return {}

    @staticmethod
    def _calculer_checksum(contenu: str) -> str:
        """Calcule le SHA-256 d'un contenu SQL."""
        return hashlib.sha256(contenu.encode("utf-8")).hexdigest()

    @staticmethod
    def _extraire_version(nom_fichier: str) -> int | None:
        """
        Extrait le numéro de version depuis un nom de fichier.

        Formats supportés: 001_xxx.sql, 17_xxx.sql
        """
        match = re.match(r"^(\d+)_", nom_fichier)
        return int(match.group(1)) if match else None

    @staticmethod
    def obtenir_migrations_disponibles() -> list[dict]:
        """
        Découvre les fichiers SQL dans sql/migrations/.

        Returns:
            Liste triée de {version, name, sql, checksum, fichier}
        """
        if not DOSSIER_MIGRATIONS.exists():
            logger.warning(f"Dossier migrations introuvable: {DOSSIER_MIGRATIONS}")
            return []

        migrations = []

        for fichier in sorted(DOSSIER_MIGRATIONS.glob("*.sql")):
            version = GestionnaireMigrations._extraire_version(fichier.name)
            if version is None:
                logger.warning(f"Fichier ignoré (pas de numéro): {fichier.name}")
                continue

            contenu = fichier.read_text(encoding="utf-8")
            checksum = GestionnaireMigrations._calculer_checksum(contenu)

            # Extraire le nom depuis le fichier (sans numéro ni extension)
            nom = re.sub(r"^\d+_", "", fichier.stem)

            migrations.append(
                {
                    "version": version,
                    "name": nom,
                    "sql": contenu,
                    "checksum": checksum,
                    "fichier": fichier.name,
                }
            )

        return sorted(migrations, key=lambda m: m["version"])

    @staticmethod
    def appliquer_migration(version: int, nom: str, sql: str, checksum: str | None = None):
        """
        Applique une migration SQL.

        Args:
            version: Numéro de version
            nom: Nom descriptif de la migration
            sql: Code SQL à exécuter
            checksum: SHA-256 du fichier SQL

        Raises:
            ErreurBaseDeDonnees: Si l'application échoue
        """
        moteur = obtenir_moteur()

        try:
            with moteur.begin() as conn:
                # Exécuter le SQL de la migration
                conn.execute(text(sql))

                # Enregistrer dans la table de suivi
                conn.execute(
                    text(f"""
                        INSERT INTO {GestionnaireMigrations.TABLE_MIGRATIONS}
                        (version, name, checksum)
                        VALUES (:version, :name, :checksum)
                    """),
                    {"version": version, "name": nom, "checksum": checksum},
                )

            logger.info(f"[OK] Migration v{version} appliquée: {nom}")
            return True

        except Exception as e:
            logger.error(f"[ERROR] Échec migration v{version}: {e}")
            raise ErreurBaseDeDonnees(
                f"Échec migration v{version}: {e}",
                message_utilisateur="Erreur lors de la mise à jour du schéma",
            ) from e

    @staticmethod
    def verifier_checksums() -> list[dict]:
        """
        Vérifie l'intégrité des migrations appliquées.

        Détecte les fichiers modifiés après application.

        Returns:
            Liste des migrations avec checksum modifié
        """
        appliquees = GestionnaireMigrations.obtenir_migrations_appliquees()
        disponibles = GestionnaireMigrations.obtenir_migrations_disponibles()
        modifiees = []

        for migration in disponibles:
            v = migration["version"]
            if v in appliquees and appliquees[v].get("checksum"):
                if appliquees[v]["checksum"] != migration["checksum"]:
                    modifiees.append(
                        {
                            "version": v,
                            "name": migration["name"],
                            "fichier": migration["fichier"],
                            "checksum_applique": appliquees[v]["checksum"],
                            "checksum_actuel": migration["checksum"],
                        }
                    )

        return modifiees

    @staticmethod
    def executer_migrations():
        """
        Exécute toutes les migrations en attente.

        1. Initialise la table de suivi si nécessaire
        2. Découvre les fichiers SQL dans sql/migrations/
        3. Filtre ceux non encore appliqués
        4. Les exécute dans l'ordre
        5. Vérifie les checksums des migrations existantes
        """
        GestionnaireMigrations.initialiser_table_migrations()

        version_courante = GestionnaireMigrations.obtenir_version_courante()
        logger.info(f"Version schéma actuelle: v{version_courante}")

        # Découvrir les migrations disponibles
        migrations = GestionnaireMigrations.obtenir_migrations_disponibles()

        if not migrations:
            logger.info("[OK] Aucun fichier de migration trouvé")
            return

        # Filtrer les migrations non appliquées
        appliquees = GestionnaireMigrations.obtenir_migrations_appliquees()
        en_attente = [m for m in migrations if m["version"] not in appliquees]

        if not en_attente:
            logger.info("[OK] Aucune migration en attente")
            # Vérifier les checksums
            modifiees = GestionnaireMigrations.verifier_checksums()
            if modifiees:
                for m in modifiees:
                    logger.warning(
                        f"⚠️ Migration v{m['version']} ({m['fichier']}) modifiée après application !"
                    )
            return

        logger.info(f"🔄 {len(en_attente)} migration(s) en attente")

        for migration in en_attente:
            logger.info(
                f"Application migration v{migration['version']}: "
                f"{migration['name']} ({migration['fichier']})"
            )
            GestionnaireMigrations.appliquer_migration(
                migration["version"],
                migration["name"],
                migration["sql"],
                migration["checksum"],
            )

        logger.info("[OK] Toutes les migrations appliquées")
