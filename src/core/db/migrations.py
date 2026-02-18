"""
Migrations - Gestionnaire de migrations de schéma.

Classe pour:
- Suivre les versions de schéma
- Appliquer les migrations SQL
"""

import logging

from sqlalchemy import text

from ..errors import ErreurBaseDeDonnees
from .engine import obtenir_moteur

logger = logging.getLogger(__name__)


class GestionnaireMigrations:
    """
    Gestionnaire de migrations de schéma.

    Gère le versionnement et l'application automatique
    des migrations sans Alembic.
    """

    TABLE_MIGRATIONS = "schema_migrations"
    """Nom de la table de suivi des migrations."""

    @staticmethod
    def initialiser_table_migrations():
        """
        Crée la table de suivi des migrations si elle n'existe pas.
        """
        moteur = obtenir_moteur()

        with moteur.connect() as conn:
            conn.execute(
                text(
                    f"""
                CREATE TABLE IF NOT EXISTS {GestionnaireMigrations.TABLE_MIGRATIONS} (
                    id SERIAL PRIMARY KEY,
                    version INTEGER NOT NULL UNIQUE,
                    name VARCHAR(255) NOT NULL,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
                )
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
                    text(
                        f"""
                    SELECT MAX(version) FROM {GestionnaireMigrations.TABLE_MIGRATIONS}
                """
                    )
                ).scalar()

                return resultat if resultat else 0

        except Exception:
            return 0

    @staticmethod
    def appliquer_migration(version: int, nom: str, sql: str):
        """
        Applique une migration.

        Args:
            version: Numéro de version
            nom: Nom descriptif de la migration
            sql: Code SQL à exécuter

        Raises:
            ErreurBaseDeDonnees: Si l'application échoue
        """
        moteur = obtenir_moteur()

        try:
            with moteur.begin() as conn:
                # Exécuter SQL migration
                conn.execute(text(sql))

                # Enregistrer migration
                conn.execute(
                    text(
                        f"""
                    INSERT INTO {GestionnaireMigrations.TABLE_MIGRATIONS}
                    (version, name)
                    VALUES (:version, :name)
                """
                    ),
                    {"version": version, "name": nom},
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
    def executer_migrations():
        """
        Exécute toutes les migrations en attente.
        """
        GestionnaireMigrations.initialiser_table_migrations()

        version_courante = GestionnaireMigrations.obtenir_version_courante()
        logger.info(f"Version schéma actuelle: v{version_courante}")

        # Migrations disponibles
        migrations = GestionnaireMigrations.obtenir_migrations_disponibles()

        # Filtrer migrations non appliquées
        en_attente = [m for m in migrations if m["version"] > version_courante]

        if not en_attente:
            logger.info("[OK] Aucune migration en attente")
            return

        logger.info(f"🔄 {len(en_attente)} migration(s) en attente")

        for migration in sorted(en_attente, key=lambda x: x["version"]):
            logger.info(f"Application migration v{migration['version']}: {migration['name']}")
            GestionnaireMigrations.appliquer_migration(
                migration["version"], migration["name"], migration["sql"]
            )

        logger.info("[OK] Toutes les migrations appliquées")

    @staticmethod
    def obtenir_migrations_disponibles() -> list[dict]:
        """
        Retourne la liste des migrations disponibles.

        Returns:
            Liste de dictionnaires contenant version, name, sql
        """
        return [
            {
                "version": 1,
                "name": "ajout_index_performance",
                "sql": """
                    -- Index pour améliorer les performances
                    CREATE INDEX IF NOT EXISTS idx_recette_nom ON recettes(nom);
                    CREATE INDEX IF NOT EXISTS idx_recette_saison_type ON recettes(saison, type_repas);
                    CREATE INDEX IF NOT EXISTS idx_ingredient_nom ON ingredients(nom);
                    CREATE INDEX IF NOT EXISTS idx_inventaire_stock_bas ON inventaire(quantite, quantite_min);
                """,
            },
            # Ajoutez vos migrations ici
        ]
