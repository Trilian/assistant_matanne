"""
Connexion Database avec Retry + Fallbacks
"""
from contextlib import contextmanager
from typing import Generator, Optional
import streamlit as st
from sqlalchemy import create_engine, event, text, pool
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import OperationalError, DatabaseError
import logging
import time

logger = logging.getLogger(__name__)


# ===================================
# CONFIGURATION ENGINE AVEC RETRY
# ===================================

class DatabaseConnectionError(Exception):
    """Erreur connexion DB personnalisée"""
    pass


@st.cache_resource(ttl=3600)
def get_engine(retry_count: int = 3, retry_delay: int = 2):
    """
    Crée l'engine PostgreSQL avec retry automatique

    Args:
        retry_count: Nombre de tentatives
        retry_delay: Délai entre tentatives (secondes)
    """
    from src.core.config import get_settings

    settings = get_settings()
    last_error = None

    for attempt in range(retry_count):
        try:
            # Construire URL
            database_url = settings.DATABASE_URL

            # Configuration optimisée
            engine = create_engine(
                database_url,
                poolclass=pool.NullPool,  # Pas de pool pour Streamlit Cloud
                echo=settings.DEBUG,
                connect_args={
                    "connect_timeout": 10,
                    "options": "-c timezone=utc",
                    "sslmode": "require"
                },
                # Retry automatique sur erreurs réseau
                pool_pre_ping=True
            )

            # Test connexion
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))

            logger.info(f"✅ Connexion DB établie (tentative {attempt + 1})")
            return engine

        except (OperationalError, DatabaseError) as e:
            last_error = e
            logger.warning(
                f"❌ Tentative {attempt + 1}/{retry_count} échouée: {e}"
            )

            if attempt < retry_count - 1:
                time.sleep(retry_delay)
                continue

    # Toutes les tentatives ont échoué
    error_msg = f"Impossible de se connecter après {retry_count} tentatives: {last_error}"
    logger.error(error_msg)
    raise DatabaseConnectionError(error_msg)


def get_engine_safe() -> Optional[object]:
    """
    Version safe qui retourne None au lieu de crash

    Usage: Pour checks non-bloquants
    """
    try:
        return get_engine()
    except DatabaseConnectionError as e:
        logger.error(f"DB non disponible: {e}")
        return None


# ===================================
# SESSION FACTORY
# ===================================

def get_session_factory():
    """Retourne une session factory"""
    engine = get_engine()
    return sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
        expire_on_commit=False
    )


SessionLocal = get_session_factory()


# ===================================
# CONTEXT MANAGER AVEC ERROR HANDLING
# ===================================

@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """
    Context manager avec gestion d'erreurs robuste

    Usage:
        with get_db_context() as db:
            result = db.query(Model).all()
    """
    db = SessionLocal()

    try:
        yield db
        db.commit()

    except OperationalError as e:
        db.rollback()
        logger.error(f"❌ Erreur opérationnelle DB: {e}")
        raise DatabaseConnectionError(f"Erreur réseau/connexion: {e}")

    except DatabaseError as e:
        db.rollback()
        logger.error(f"❌ Erreur base de données: {e}")
        raise

    except Exception as e:
        db.rollback()
        logger.error(f"❌ Erreur inattendue: {e}")
        raise

    finally:
        db.close()


@contextmanager
def get_db_safe() -> Generator[Optional[Session], None, None]:
    """
    Version safe qui n'interrompt pas l'app

    Usage:
        with get_db_safe() as db:
            if db:
                # Faire quelque chose
            else:
                # Gérer fallback
    """
    try:
        with get_db_context() as db:
            yield db
    except DatabaseConnectionError:
        logger.warning("DB non disponible, fallback")
        yield None
    except Exception as e:
        logger.error(f"Erreur DB: {e}")
        yield None


# ===================================
# VÉRIFICATIONS
# ===================================

@st.cache_data(ttl=60)
def check_connection() -> tuple[bool, str]:
    """
    Vérifie connexion avec message d'erreur

    Returns:
        (success: bool, message: str)
    """
    try:
        engine = get_engine_safe()
        if not engine:
            return False, "Engine non disponible"

        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        return True, "Connexion OK"

    except DatabaseConnectionError as e:
        return False, f"Erreur connexion: {str(e)}"

    except Exception as e:
        logger.error(f"❌ Test connexion échoué: {e}")
        return False, f"Erreur: {str(e)}"


@st.cache_data(ttl=300)
def get_db_info() -> dict:
    """
    Retourne infos DB ou erreur gracieuse

    Returns:
        Dict avec status + infos ou erreur
    """
    try:
        engine = get_engine()

        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT 
                    version() as version,
                    current_database() as database,
                    current_user as user,
                    pg_size_pretty(pg_database_size(current_database())) as size
            """)).fetchone()

            # Extraire host depuis URL
            from src.core.config import get_settings
            settings = get_settings()
            db_url = settings.DATABASE_URL

            # Parser host basique
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
                "error": None
            }

    except Exception as e:
        logger.error(f"get_db_info error: {e}")
        return {
            "status": "error",
            "error": str(e),
            "version": None,
            "database": None,
            "user": None
        }


# ===================================
# HEALTH CHECK
# ===================================

def health_check() -> dict:
    """
    Health check complet de la DB

    Returns:
        Dict avec métriques santé
    """
    try:
        engine = get_engine()

        with engine.connect() as conn:
            # Vérifier connexions actives
            active_conns = conn.execute(text("""
                SELECT count(*) 
                FROM pg_stat_activity 
                WHERE state = 'active'
            """)).scalar()

            # Vérifier taille DB
            db_size = conn.execute(text("""
                SELECT pg_database_size(current_database())
            """)).scalar()

            return {
                "healthy": True,
                "active_connections": active_conns,
                "database_size_bytes": db_size,
                "timestamp": time.time()
            }

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "healthy": False,
            "error": str(e),
            "timestamp": time.time()
        }


# ===================================
# MAINTENANCE
# ===================================

def cleanup_old_logs(days: int = 90) -> int:
    """
    Nettoie les logs anciens

    Args:
        days: Âge max en jours

    Returns:
        Nombre de lignes supprimées
    """
    try:
        with get_db_context() as db:
            # Tables avec logs
            log_tables = [
                "logs_jardin",
                "entrees_bien_etre",
                # Ajouter autres tables de logs
            ]

            total_deleted = 0

            for table in log_tables:
                result = db.execute(text(f"""
                    DELETE FROM {table}
                    WHERE date < CURRENT_DATE - INTERVAL '{days} days'
                """))
                deleted = result.rowcount
                total_deleted += deleted
                logger.info(f"Supprimé {deleted} lignes de {table}")

            db.commit()
            return total_deleted

    except Exception as e:
        logger.error(f"Erreur cleanup: {e}")
        return 0


def vacuum_database():
    """
    Optimise la base (VACUUM)

    Note: Nécessite autocommit
    """
    try:
        engine = get_engine()

        with engine.connect() as conn:
            conn.execution_options(isolation_level="AUTOCOMMIT")
            conn.execute(text("VACUUM ANALYZE"))

        logger.info("✅ VACUUM ANALYZE exécuté")

    except Exception as e:
        logger.error(f"Erreur VACUUM: {e}")


# ===================================
# INITIALISATION (dev uniquement)
# ===================================

def create_all_tables():
    """
    Crée toutes les tables (dev/setup uniquement)

    ATTENTION: Ne pas appeler en production
    """
    from src.core.config import get_settings
    settings = get_settings()

    if settings.is_production():
        logger.warning("create_all_tables ignoré en production")
        return

    try:
        from src.core.models import Base
        engine = get_engine()
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Tables créées/vérifiées")

    except Exception as e:
        logger.error(f"Erreur création tables: {e}")
        raise