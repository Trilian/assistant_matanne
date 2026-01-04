"""
Database - Gestion de la base de données avec migrations.

Ce module gère :
- Connexions PostgreSQL/Supabase avec retry automatique
- Context managers sécurisés
- Système de migrations
- Health checks et monitoring
"""
from contextlib import contextmanager
from typing import Generator, Optional, Dict
import streamlit as st
from sqlalchemy import create_engine, text, pool
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import OperationalError, DatabaseError
import logging
import time

from .config import obtenir_settings
from .constants import (
    DB_CONNECTION_RETRY,
    DB_CONNECTION_TIMEOUT,
    DB_POOL_SIZE,
    DB_MAX_OVERFLOW
)
from .errors import ErreurBaseDeDonnees

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# CRÉATION ENGINE
# ═══════════════════════════════════════════════════════════

@st.cache_resource(ttl=3600)
def obtenir_engine(nombre_retries: int = DB_CONNECTION_RETRY, delai_retry: int = 2):
    """
    Crée l'engine PostgreSQL avec retry automatique.

    Args:
        nombre_retries: Nombre de tentatives de reconnexion
        delai_retry: Délai entre les retries en secondes

    Returns:
        Engine SQLAlchemy configuré

    Raises:
        ErreurBaseDeDonnees: Si connexion impossible après tous les retries
    """
    settings = obtenir_settings()
    derniere_erreur = None

    for tentative in range(nombre_retries):
        try:
            database_url = settings.DATABASE_URL

            engine = create_engine(
                database_url,
                poolclass=pool.NullPool,
                echo=settings.DEBUG,
                connect_args={
                    "connect_timeout": DB_CONNECTION_TIMEOUT,
                    "options": "-c timezone=utc",
                    "sslmode": "require",
                },
                pool_pre_ping=True,
            )

            # Test de connexion
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))

            logger.info(f"✅ Connexion DB établie (tentative {tentative + 1})")
            return engine

        except (OperationalError, DatabaseError) as e:
            derniere_erreur = e
            logger.warning(
                f"❌ Tentative {tentative + 1}/{nombre_retries} échouée: {e}"
            )

            if tentative < nombre_retries - 1:
                time.sleep(delai_retry)
                continue

    # Toutes les tentatives ont échoué
    message_erreur = (
        f"Impossible de se connecter après {nombre_retries} tentatives: "
        f"{derniere_erreur}"
    )
    logger.error(message_erreur)
    raise ErreurBaseDeDonnees(
        message_erreur,
        message_utilisateur="Impossible de se connecter à la base de données"
    )


def obtenir_engine_securise() -> Optional[object]:
    """
    Version sécurisée qui retourne None au lieu de lever une exception.

    Returns:
        Engine ou None si erreur
    """
    try:
        return obtenir_engine()
    except ErreurBaseDeDonnees as e:
        logger.error(f"DB non disponible: {e}")
        return None


# ═══════════════════════════════════════════════════════════
# SESSION FACTORY
# ═══════════════════════════════════════════════════════════

def obtenir_session_factory():
    """
    Retourne une session factory.

    Returns:
        Session factory configurée
    """
    engine = obtenir_engine()
    return sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
        expire_on_commit=False
    )


SessionLocal = obtenir_session_factory()


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
    db = SessionLocal()

    try:
        yield db
        db.commit()

    except OperationalError as e:
        db.rollback()
        logger.error(f"❌ Erreur opérationnelle DB: {e}")
        raise ErreurBaseDeDonnees(
            f"Erreur réseau/connexion: {e}",
            message_utilisateur="Problème de connexion à la base de données"
        )

    except DatabaseError as e:
        db.rollback()
        logger.error(f"❌ Erreur base de données: {e}")
        raise ErreurBaseDeDonnees(
            str(e),
            message_utilisateur="Erreur lors de l'opération en base de données"
        )

    except Exception as e:
        db.rollback()
        logger.error(f"❌ Erreur inattendue: {e}")
        raise

    finally:
        db.close()


@contextmanager
def obtenir_db_securise() -> Generator[Optional[Session], None, None]:
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


# Alias pour compatibilité
get_db_context = obtenir_contexte_db
get_db_safe = obtenir_db_securise


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
        engine = obtenir_engine()

        with engine.connect() as conn:
            conn.execute(text(f"""
                CREATE TABLE IF NOT EXISTS {GestionnaireMigrations.TABLE_MIGRATIONS} (
                    id SERIAL PRIMARY KEY,
                    version INTEGER NOT NULL UNIQUE,
                    name VARCHAR(255) NOT NULL,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            conn.commit()

        logger.info("✅ Table migrations initialisée")

    @staticmethod
    def obtenir_version_courante() -> int:
        """
        Retourne la version actuelle du schéma.

        Returns:
            Numéro de version (0 si aucune migration)
        """
        try:
            engine = obtenir_engine()

            with engine.connect() as conn:
                result = conn.execute(text(f"""
                    SELECT MAX(version) FROM {GestionnaireMigrations.TABLE_MIGRATIONS}
                """)).scalar()

                return result if result else 0

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
        engine = obtenir_engine()

        try:
            with engine.begin() as conn:
                # Exécuter SQL migration
                conn.execute(text(sql))

                # Enregistrer migration
                conn.execute(text(f"""
                    INSERT INTO {GestionnaireMigrations.TABLE_MIGRATIONS} 
                    (version, name)
                    VALUES (:version, :name)
                """), {"version": version, "name": nom})

            logger.info(f"✅ Migration v{version} appliquée: {nom}")
            return True

        except Exception as e:
            logger.error(f"❌ Échec migration v{version}: {e}")
            raise ErreurBaseDeDonnees(
                f"Échec migration v{version}: {e}",
                message_utilisateur="Erreur lors de la mise à jour du schéma"
            )

    @staticmethod
    def executer_migrations():
        """
        Exécute toutes les migrations en attente.
        """
        GestionnaireMigrations.initialiser_table_migrations()

        version_courante = GestionnaireMigrations.obtenir_version_courante()
        logger.info(f"Version schéma actuelle: v{version_courante}")

        # Migrations disponibles (à personnaliser)
        migrations = GestionnaireMigrations.obtenir_migrations_disponibles()

        # Filtrer migrations non appliquées
        en_attente = [m for m in migrations if m["version"] > version_courante]

        if not en_attente:
            logger.info("✅ Aucune migration en attente")
            return

        logger.info(f"🔄 {len(en_attente)} migration(s) en attente")

        for migration in sorted(en_attente, key=lambda x: x["version"]):
            logger.info(
                f"Application migration v{migration['version']}: "
                f"{migration['name']}"
            )
            GestionnaireMigrations.appliquer_migration(
                migration["version"],
                migration["name"],
                migration["sql"]
            )

        logger.info("✅ Toutes les migrations appliquées")

    @staticmethod
    def obtenir_migrations_disponibles() -> list[dict]:
        """
        Retourne la liste des migrations disponibles.

        ⚠️ À personnaliser selon vos besoins.

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
                """
            },
            # Ajoutez vos migrations ici
        ]


# Alias pour compatibilité
MigrationManager = GestionnaireMigrations


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
        engine = obtenir_engine_securise()
        if not engine:
            return False, "Engine non disponible"

        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        return True, "Connexion OK"

    except ErreurBaseDeDonnees as e:
        return False, f"Erreur connexion: {e.message}"

    except Exception as e:
        logger.error(f"❌ Test connexion échoué: {e}")
        return False, f"Erreur: {str(e)}"


@st.cache_data(ttl=300)
def obtenir_infos_db() -> dict:
    """
    Retourne les informations sur la base de données.

    Returns:
        Dictionnaire avec informations DB
    """
    try:
        engine = obtenir_engine()

        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT 
                    version() as version,
                    current_database() as database,
                    current_user as user,
                    pg_size_pretty(pg_database_size(current_database())) as size
            """)).fetchone()

            settings = obtenir_settings()
            db_url = settings.DATABASE_URL

            host = "unknown"
            if "@" in db_url:
                host = db_url.split("@")[1].split(":")[0]

            return {
                "status": "connected",
                "version": result[0].split(",")[0],
                "database": result[1],
                "user": result[2],
                "size": result[3],
                "host": host,
                "schema_version": GestionnaireMigrations.obtenir_version_courante(),
                "error": None,
            }

    except Exception as e:
        logger.error(f"obtenir_infos_db error: {e}")
        return {
            "status": "error",
            "error": str(e),
            "version": None,
            "database": None,
            "user": None,
            "schema_version": 0
        }


# Alias pour compatibilité
check_connection = verifier_connexion
get_db_info = obtenir_infos_db


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
    settings = obtenir_settings()

    if settings.est_production():
        logger.info("Mode production: vérification schéma uniquement")

    try:
        engine = obtenir_engine()

        # Vérifier connexion
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        logger.info("✅ Connexion DB OK")

        # Exécuter migrations si demandé
        if executer_migrations:
            logger.info("🔄 Exécution migrations...")
            GestionnaireMigrations.executer_migrations()

        return True

    except Exception as e:
        logger.error(f"❌ Erreur initialisation DB: {e}")
        return False


def creer_toutes_les_tables():
    """
    Crée toutes les tables (dev/setup uniquement).

    ⚠️ ATTENTION: Ne pas appeler en production.
    """
    settings = obtenir_settings()

    if settings.est_production():
        logger.warning("creer_toutes_les_tables ignoré en production")
        return

    try:
        from .models import Base
        engine = obtenir_engine()
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Tables créées/vérifiées")

    except Exception as e:
        logger.error(f"Erreur création tables: {e}")
        raise


# Alias pour compatibilité
init_database = initialiser_database
create_all_tables = creer_toutes_les_tables


# ═══════════════════════════════════════════════════════════
# HEALTH CHECK
# ═══════════════════════════════════════════════════════════

def health_check() -> dict:
    """
    Health check complet de la DB.

    Returns:
        Dictionnaire avec status et métriques
    """
    try:
        engine = obtenir_engine()

        with engine.connect() as conn:
            connexions_actives = conn.execute(text("""
                SELECT count(*) 
                FROM pg_stat_activity 
                WHERE state = 'active'
            """)).scalar()

            taille_db = conn.execute(
                text("SELECT pg_database_size(current_database())")
            ).scalar()

            return {
                "healthy": True,
                "active_connections": connexions_actives,
                "database_size_bytes": taille_db,
                "schema_version": GestionnaireMigrations.obtenir_version_courante(),
                "timestamp": time.time(),
            }

    except Exception as e:
        logger.error(f"Health check échoué: {e}")
        return {
            "healthy": False,
            "error": str(e),
            "timestamp": time.time()
        }