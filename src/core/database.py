"""
Connexion PostgreSQL optimisée pour Supabase + Streamlit Cloud
"""
from contextlib import contextmanager
from typing import Generator
import streamlit as st
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
import logging

logger = logging.getLogger(__name__)


# ===================================
# CONFIGURATION ENGINE SUPABASE
# ===================================
@st.cache_resource
def get_engine():
    """Crée l'engine PostgreSQL optimisé pour Supabase (avec cache)"""

    try:
        # Récupérer l'URL depuis les secrets
        db = st.secrets["db"]
        database_url = (
            f"postgresql://{db['user']}:{db['password']}"
            f"@{db['host']}:{db['port']}/{db['name']}"
            f"?sslmode=require"  # CRITIQUE pour Supabase
        )

        # Configuration optimisée pour Streamlit Cloud
        engine = create_engine(
            database_url,
            poolclass=NullPool,  # Pas de pool pour Streamlit Cloud
            echo=False,
            connect_args={
                "connect_timeout": 10,
                "options": "-c timezone=utc",
                "sslmode": "require"  # Force SSL
            }
        )

        # Test de connexion
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        logger.info("✅ Connexion Supabase établie")
        return engine

    except KeyError as e:
        error_msg = f"Secret DB manquant: {e}"
        logger.error(error_msg)
        st.error(f"❌ {error_msg}")
        st.stop()

    except Exception as e:
        logger.error(f"Erreur connexion Supabase: {e}")
        st.error(f"❌ Impossible de se connecter à Supabase: {e}")
        st.stop()


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
# CONTEXT MANAGER
# ===================================
@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """Context manager pour gérer les sessions (avec auto-rollback)"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Erreur DB: {e}")
        raise
    finally:
        db.close()


# ===================================
# VÉRIFICATIONS
# ===================================
@st.cache_data(ttl=60)
def check_connection() -> bool:
    """Vérifie que la connexion fonctionne (avec cache 60s)"""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Test connexion échoué: {e}")
        return False


@st.cache_data(ttl=300)
def get_db_info() -> dict:
    """Retourne les infos de connexion (cache 5min)"""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT 
                    version() as version,
                    current_database() as database,
                    current_user as user
            """)).fetchone()

            return {
                "status": "connected",
                "version": result[0].split(",")[0],
                "database": result[1],
                "user": result[2],
                "host": st.secrets["db"]["host"].split(".")[0]
            }
    except Exception as e:
        logger.error(f"get_db_info error: {e}")
        return {"status": "error", "error": str(e)}


# ===================================
# INITIALISATION (dev uniquement)
# ===================================
def create_all_tables():
    """Crée toutes les tables (uniquement si nécessaire)"""
    if st.secrets.get("ENV", "production") != "development":
        logger.warning("create_all_tables appelé en production - ignoré")
        return

    try:
        from src.core.models import Base
        engine = get_engine()
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Tables créées/vérifiées")
    except Exception as e:
        logger.error(f"Erreur création tables: {e}")
        raise