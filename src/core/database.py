"""
Database - Gestion de la base de données avec migrations.
Tout harmonisé en français
"""

import logging
import time
from collections.abc import Generator
from contextlib import contextmanager

import streamlit as st
from sqlalchemy import create_engine, pool, text
from sqlalchemy.exc import DatabaseError, OperationalError
from sqlalchemy.orm import Session, sessionmaker

from .config import obtenir_parametres
from .constants import DB_CONNECTION_RETRY, DB_CONNECTION_TIMEOUT
from .errors import ErreurBaseDeDonnees

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# CRÉATION ENGINE
# ═══════════════════════════════════════════════════════════


@st.cache_resource(ttl=3600)
def obtenir_moteur(nombre_tentatives: int = DB_CONNECTION_RETRY, delai_tentative: int = 2):
    """
    Crée l'engine PostgreSQL avec retry automatique.

    Args:
        nombre_tentatives: Nombre de tentatives de reconnexion
        delai_tentative: Délai entre les tentatives en secondes

    Returns:
        Engine SQLAlchemy configuré

    Raises:
        ErreurBaseDeDonnees: Si connexion impossible après toutes les tentatives
    """
    parametres = obtenir_parametres()
    derniere_erreur = None

    for tentative in range(nombre_tentatives):
        try:
            url_base = parametres.DATABASE_URL

            # Utiliser QueuePool pour de meilleures performances
            # NullPool désactivé car inefficace pour les requêtes fréquentes
            moteur = create_engine(
                url_base,
                poolclass=pool.QueuePool,
                pool_size=5,  # Connexions de base
                max_overflow=10,  # Connexions supplémentaires si nécessaire
                pool_timeout=30,  # Timeout attente connexion
                pool_recycle=1800,  # Recycler connexions après 30min
                pool_pre_ping=True,  # Vérifier connexion avant utilisation
                echo=parametres.DEBUG,
                connect_args={
                    "connect_timeout": DB_CONNECTION_TIMEOUT,
                    "options": "-c timezone=utc",
                    "sslmode": "require",
                },
            )

            # Test de connexion
            with moteur.connect() as conn:
                conn.execute(text("SELECT 1"))

            logger.info(f"[OK] Connexion DB établie (tentative {tentative + 1})")
            return moteur

        except (OperationalError, DatabaseError) as e:
            derniere_erreur = e
            logger.warning(f"[ERROR] Tentative {tentative + 1}/{nombre_tentatives} échouée: {e}")

            if tentative < nombre_tentatives - 1:
                time.sleep(delai_tentative)
                continue

    # Toutes les tentatives ont échoué
    message_erreur = (
        f"Impossible de se connecter après {nombre_tentatives} tentatives: " f"{derniere_erreur}"
    )
    logger.error(message_erreur)
    raise ErreurBaseDeDonnees(
        message_erreur, message_utilisateur="Impossible de se connecter à la base de données"
    )


def obtenir_moteur_securise() -> object | None:
    """
    Version sécurisée qui retourne None au lieu de lever une exception.

    Returns:
        Engine ou None si erreur
    """
    try:
        return obtenir_moteur()
    except ErreurBaseDeDonnees as e:
        logger.error(f"DB non disponible: {e}")
        return None


# ═══════════════════════════════════════════════════════════
# SESSION FACTORY
# ═══════════════════════════════════════════════════════════


def obtenir_fabrique_session():
    """
    Retourne une session factory.

    Returns:
        Session factory configurée
    """
    # Création différée de la factory pour éviter les erreurs à l'import
    moteur = obtenir_moteur()
    return sessionmaker(autocommit=False, autoflush=False, bind=moteur, expire_on_commit=False)


# Session factory initialisée à la demande (evite side-effects à l'import)
SessionLocale = None


# ═══════════════════════════════════════════════════════════
# CONTEXT MANAGERS
# ═══════════════════════════════════════════════════════════


@contextmanager
def obtenir_contexte_db() -> Generator[Session, None, None]:
    """
    Context manager avec gestion d'erreurs robuste.

    Yields:
        Session SQLAlchemy active

    Raises:
        ErreurBaseDeDonnees: En cas d'erreur de connexion ou requête

    Example:
        >>> with obtenir_contexte_db() as db:
        >>>     recettes = db.query(Recette).all()
    """
    # Obtenir une factory de session à la demande (création différée)
    fabrique = obtenir_fabrique_session()
    db = fabrique()

    try:
        yield db
        db.commit()

    except OperationalError as e:
        db.rollback()
        logger.error(f"[ERROR] Erreur opérationnelle DB: {e}")
        raise ErreurBaseDeDonnees(
            f"Erreur réseau/connexion: {e}",
            message_utilisateur="Problème de connexion à la base de données",
        ) from e

    except DatabaseError as e:
        db.rollback()
        logger.error(f"[ERROR] Erreur base de données: {e}")
        raise ErreurBaseDeDonnees(
            str(e), message_utilisateur="Erreur lors de l'opération en base de données"
        ) from e

    except Exception as e:
        db.rollback()
        logger.error(f"[ERROR] Erreur inattendue: {e}")
        raise

    finally:
        db.close()


@contextmanager
def obtenir_db_securise() -> Generator[Session | None, None, None]:
    """
    Version sécurisée qui n'interrompt pas l'application.

    Yields:
        Session ou None si erreur

    Example:
        >>> with obtenir_db_securise() as db:
        >>>     if db:
        >>>         recettes = db.query(Recette).all()
    """
    try:
        with obtenir_contexte_db() as db:
            yield db
    except ErreurBaseDeDonnees:
        logger.warning("DB non disponible, fallback")
        yield None
    except Exception as e:
        logger.error(f"Erreur DB: {e}")
        yield None


# ═══════════════════════════════════════════════════════════
# SYSTÈME DE MIGRATION
# ═══════════════════════════════════════════════════════════


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
            logger.info(f"Application migration v{migration['version']}: " f"{migration['name']}")
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


# ═══════════════════════════════════════════════════════════
# VÉRIFICATIONS
# ═══════════════════════════════════════════════════════════


@st.cache_data(ttl=60)
def verifier_connexion() -> tuple[bool, str]:
    """
    Vérifie la connexion à la base de données.

    Returns:
        Tuple (succès, message)
    """
    try:
        moteur = obtenir_moteur_securise()
        if not moteur:
            return False, "Engine non disponible"

        with moteur.connect() as conn:
            conn.execute(text("SELECT 1"))

        return True, "Connexion OK"

    except ErreurBaseDeDonnees as e:
        return False, f"Erreur connexion: {e.message}"

    except Exception as e:
        logger.error(f"[ERROR] Test connexion échoué: {e}")
        return False, f"Erreur: {str(e)}"


@st.cache_data(ttl=300)
def obtenir_infos_db() -> dict:
    """
    Retourne les informations sur la base de données.

    Returns:
        Dictionnaire avec informations DB
    """
    try:
        moteur = obtenir_moteur()

        with moteur.connect() as conn:
            resultat = conn.execute(
                text(
                    """
                SELECT
                    version() as version,
                    current_database() as database,
                    current_user as user,
                    pg_size_pretty(pg_database_size(current_database())) as size
            """
                )
            ).fetchone()

            parametres = obtenir_parametres()
            db_url = parametres.DATABASE_URL

            hote = "unknown"
            if "@" in db_url:
                hote = db_url.split("@")[1].split(":")[0]

            return {
                "statut": "connected",
                "version": resultat[0].split(",")[0],
                "base_donnees": resultat[1],
                "utilisateur": resultat[2],
                "taille": resultat[3],
                "hote": hote,
                "version_schema": GestionnaireMigrations.obtenir_version_courante(),
                "erreur": None,
            }

    except Exception as e:
        logger.error(f"obtenir_infos_db erreur: {e}")
        return {
            "statut": "error",
            "erreur": str(e),
            "version": None,
            "base_donnees": None,
            "utilisateur": None,
            "version_schema": 0,
        }


# ═══════════════════════════════════════════════════════════
# INITIALISATION
# ═══════════════════════════════════════════════════════════


def initialiser_database(executer_migrations: bool = True):
    """
    Initialise la base de données.

    Args:
        executer_migrations: Si True, exécute les migrations automatiquement

    Returns:
        True si succès
    """
    parametres = obtenir_parametres()

    if parametres.est_production():
        logger.info("Mode production: vérification schéma uniquement")

    try:
        moteur = obtenir_moteur()

        # Vérifier connexion
        with moteur.connect() as conn:
            conn.execute(text("SELECT 1"))

        logger.info("[OK] Connexion DB OK")

        # Exécuter migrations si demandé
        if executer_migrations:
            logger.info("🔄 Exécution migrations...")
            GestionnaireMigrations.executer_migrations()

        return True

    except Exception as e:
        logger.error(f"[ERROR] Erreur initialisation DB: {e}")
        return False


def creer_toutes_tables():
    """
    Crée toutes les tables (dev/setup uniquement).

    [!] ATTENTION: Ne pas appeler en production.
    """
    parametres = obtenir_parametres()

    if parametres.est_production():
        logger.warning("creer_toutes_tables ignoré en production")
        return

    try:
        from .models import Base

        moteur = obtenir_moteur()
        Base.metadata.create_all(bind=moteur)
        logger.info("[OK] Tables créées/vérifiées")

    except Exception as e:
        logger.error(f"Erreur création tables: {e}")
        raise


# ═══════════════════════════════════════════════════════════
# HEALTH CHECK
# ═══════════════════════════════════════════════════════════


def verifier_sante() -> dict:
    """
    Health check complet de la DB.

    Returns:
        Dictionnaire avec statut et métriques
    """
    try:
        moteur = obtenir_moteur()

        with moteur.connect() as conn:
            connexions_actives = conn.execute(
                text(
                    """
                SELECT count(*)
                FROM pg_stat_activity
                WHERE state = 'active'
            """
                )
            ).scalar()

            taille_db = conn.execute(text("SELECT pg_database_size(current_database())")).scalar()

            return {
                "sain": True,
                "connexions_actives": connexions_actives,
                "taille_base_octets": taille_db,
                "version_schema": GestionnaireMigrations.obtenir_version_courante(),
                "timestamp": time.time(),
            }

    except Exception as e:
        logger.error(f"Health check échoué: {e}")
        return {"sain": False, "erreur": str(e), "timestamp": time.time()}


def vacuum_database() -> bool:
    """
    Exécute VACUUM sur la base de données PostgreSQL pour optimiser l'espace.

    Returns:
        True si succès, False sinon
    """
    try:
        moteur = obtenir_moteur()

        # VACUUM nécessite autocommit
        with moteur.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
            conn.execute(text("VACUUM ANALYZE"))
            logger.info("✅ VACUUM ANALYZE exécuté avec succès")
            return True

    except Exception as e:
        logger.error(f"❌ Erreur VACUUM: {e}")
        raise


# ═══════════════════════════════════════════════════════════
# EXPORTS PRINCIPAUX
# ═══════════════════════════════════════════════════════════

# Nettoyage des exports - noms français uniquement
__all__ = [
    "obtenir_moteur",
    "obtenir_moteur_securise",
    "obtenir_contexte_db",
    "obtenir_db_securise",
    "verifier_connexion",
    "obtenir_infos_db",
    "initialiser_database",
    "vacuum_database",
    "GestionnaireMigrations",
]
