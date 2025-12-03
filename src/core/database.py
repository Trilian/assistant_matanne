"""
Connexion PostgreSQL et gestion des sessions - Version adaptée pour Streamlit Cloud
"""
from contextlib import contextmanager
from typing import Generator
from datetime import datetime
import streamlit as st
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool, QueuePool
import logging

logger = logging.getLogger(__name__)

# ===================================
# RÉCUPÉRATION DES SECRETS
# ===================================
def get_db_url():
    """Récupère l'URL de la base de données depuis les secrets Streamlit"""
    try:
        # Vérifie que les secrets sont bien chargés
        if not st.secrets:
            raise ValueError("Les secrets Streamlit ne sont pas chargés")

        # Construction de l'URL de connexion
        return f"postgresql://{st.secrets['db']['user']}:{st.secrets['db']['password']}@{st.secrets['db']['host']}:{st.secrets['db']['port']}/{st.secrets['db']['name']}"

    except KeyError as e:
        raise ValueError(f"Secret manquant dans Streamlit: {e}. Vérifie que tous les champs [db] sont configurés dans les secrets.")
    except Exception as e:
        raise ValueError(f"Erreur lors de la construction de l'URL de la base de données: {e}")
# ===================================
# CONFIGURATION ENGINE
# ===================================
def get_engine():
    """Crée l'engine PostgreSQL avec configuration optimisée pour Streamlit Cloud"""
    engine_kwargs = {
        "echo": False,  # Désactive les logs SQL en production
        "future": True,
        "poolclass": QueuePool,
        "pool_size": 5,  # Taille réduite pour Streamlit Cloud
        "max_overflow": 10,
        "pool_pre_ping": True,
        "pool_recycle": 300  # Recycler après 5 minutes
    }

    engine = create_engine(get_db_url(), **engine_kwargs)

    # Configuration spécifique PostgreSQL
    @event.listens_for(engine, "connect")
    def set_postgresql_config(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("SET timezone='UTC'")
        cursor.close()

    return engine

# Engine global
engine = get_engine()

# ===================================
# GESTION DES SESSIONS
# ===================================
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)

@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """
    Context manager pour gérer automatiquement les sessions
    Usage:
        with get_db_context() as db:
            # Faire des opérations
            db.query(...)
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Erreur base de données: {e}")
        raise
    finally:
        db.close()

def get_db() -> Generator[Session, None, None]:
    """
    Générateur de session pour Streamlit
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ===================================
# VÉRIFICATIONS
# ===================================
def check_connection() -> bool:
    """Vérifie que la connexion fonctionne"""
    try:
        with get_db_context() as db:
            db.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"❌ Connexion DB échouée: {e}")
        st.error(f"Erreur de connexion à la base de données: {e}")
        return False

def get_db_info():
    """Affiche des infos sur la base de données (pour débogage)"""
    try:
        with get_db_context() as db:
            result = db.execute(text("""
                SELECT version() as version, current_database() as database, current_user as user
            """)).fetchone()
            return {
                "status": "connected",
                "version": result[0],
                "database": result[1],
                "user": result[2],
                "host": st.secrets['db']['host']
            }
    except Exception as e:
        return {"status": "error", "error": str(e)}
