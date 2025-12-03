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
    """Récupère l'URL de la base de données avec gestion des erreurs détaillée"""
    try:
        # Affiche tous les secrets disponibles (pour débogage)
        st.write("Secrets disponibles :", list(st.secrets.keys()))

        # Vérifie que la section [db] existe
        if 'db' not in st.secrets:
            raise ValueError("""
            La section [db] est manquante dans les secrets.
            Voici ce que tu dois ajouter dans les secrets Streamlit :

            [db]
            host = "db.tu_identifiant_supabase.supabase.co"
            port = "5432"
            name = "postgres"
            user = "postgres"
            password = "ton_mot_de_passe"
            """)

        # Vérifie que tous les champs sont présents
        required_keys = ['host', 'port', 'name', 'user', 'password']
        for key in required_keys:
            if key not in st.secrets['db']:
                raise ValueError(f"""
                Le champ '{key}' est manquant dans la section [db].
                Voici la structure complète attendue :

                [db]
                host = "db.tu_identifiant_supabase.supabase.co"
                port = "5432"
                name = "postgres"
                user = "postgres"
                password = "ton_mot_de_passe"
                """)

        # Construction de l'URL
        return f"postgresql://{st.secrets['db']['user']}:{st.secrets['db']['password']}@{st.secrets['db']['host']}:{st.secrets['db']['port']}/{st.secrets['db']['name']}"

    except Exception as e:
        st.error(f"Erreur de configuration : {str(e)}")
        st.stop()  # Arrête l'application
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
# ===================================
# INITIALISATION & MIGRATIONS
# ===================================
def create_all_tables():
    """Crée toutes les tables nécessaires (développement uniquement)"""
    try:
        logger.info("Création des tables...")
        from src.core.models import Base  # Import local pour éviter les dépendances circulaires
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Tables créées avec succès")
    except Exception as e:
        logger.error(f"Erreur lors de la création des tables: {e}")
        raise
