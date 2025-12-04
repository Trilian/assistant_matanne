"""
Connexion PostgreSQL et gestion des sessions - Version Streamlit Cloud + Supabase
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
    """Récupère l'URL de la base de données avec gestion des erreurs"""
    try:
        # ❌ NE JAMAIS AFFICHER LES SECRETS EN PRODUCTION
        # st.write("Secrets disponibles :", list(st.secrets.keys()))  # DANGEREUX !

        # Vérifie que la section [db] existe
        if 'db' not in st.secrets:
            raise ValueError(
                "La section [db] est manquante dans les secrets.\n"
                "Ajoute dans Streamlit Cloud :\n\n"
                "[db]\n"
                'host = "db.xxxxx.supabase.co"\n'
                'port = "5432"\n'
                'name = "postgres"\n'
                'user = "postgres"\n'
                'password = "ton_mot_de_passe"'
            )

        # Vérifie que tous les champs sont présents
        required_keys = ['host', 'port', 'name', 'user', 'password']
        missing = [key for key in required_keys if key not in st.secrets['db']]

        if missing:
            raise ValueError(
                f"Champs manquants dans [db] : {', '.join(missing)}\n"
                "Structure attendue :\n\n"
                "[db]\n"
                'host = "db.xxxxx.supabase.co"\n'
                'port = "5432"\n'
                'name = "postgres"\n'
                'user = "postgres"\n'
                'password = "ton_mot_de_passe"'
            )

        # Construction de l'URL sécurisée
        db = st.secrets['db']
        return f"postgresql://{db['user']}:{db['password']}@{db['host']}:{db['port']}/{db['name']}"

    except Exception as e:
        logger.error(f"Erreur configuration DB : {e}")
        st.error(f"❌ Erreur de configuration : {str(e)}")
        st.stop()

# ===================================
# CONFIGURATION ENGINE
# ===================================
def get_engine():
    """Crée l'engine PostgreSQL optimisé pour Streamlit Cloud"""
    engine_kwargs = {
        "echo": False,
        "future": True,
        "poolclass": QueuePool,
        "pool_size": 5,
        "max_overflow": 10,
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "connect_args": {
            "connect_timeout": 10,
            "options": "-c timezone=utc"
        }
    }

    engine = create_engine(get_db_url(), **engine_kwargs)

    # Configuration PostgreSQL
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
    """Context manager pour gérer les sessions"""
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
    """Générateur de session pour Streamlit"""
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
        # NE PAS afficher le détail de l'erreur en production
        if st.secrets.get("ENV", "production") == "development":
            st.error(f"Erreur de connexion : {e}")
        else:
            st.error("❌ Impossible de se connecter à la base de données")
        return False

def get_db_info():
    """Retourne les infos de connexion (sans mot de passe)"""
    try:
        with get_db_context() as db:
            result = db.execute(text("""
                SELECT version() as version, 
                       current_database() as database, 
                       current_user as user
            """)).fetchone()

            return {
                "status": "connected",
                "version": result[0].split(",")[0],  # Version courte
                "database": result[1],
                "user": result[2],
                "host": st.secrets['db']['host'].split('.')[0]  # Masque le domaine complet
            }
    except Exception as e:
        logger.error(f"Erreur get_db_info : {e}")
        return {"status": "error", "error": "Connexion échouée"}

# ===================================
# INITIALISATION
# ===================================
def create_all_tables():
    """Crée toutes les tables (développement uniquement)"""
    if st.secrets.get("ENV", "production") != "development":
        logger.warning("create_all_tables() appelé en production - ignoré")
        return

    try:
        logger.info("Création des tables...")
        from src.core.models import Base
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Tables créées avec succès")
    except Exception as e:
        logger.error(f"Erreur lors de la création des tables: {e}")
        raise