"""
Engine - Création et gestion de l'engine SQLAlchemy.

Fonctions pour:
- Créer l'engine PostgreSQL avec retry automatique
- Obtenir l'engine de façon sécurisée

Découplé de Streamlit — le cache est géré par le conteneur IoC.
"""

import logging
import threading
import time

from sqlalchemy import Engine, create_engine, pool, text
from sqlalchemy.exc import DatabaseError, OperationalError

from ..config import obtenir_parametres
from ..constants import DB_CONNECTION_RETRY, DB_CONNECTION_TIMEOUT
from ..exceptions import ErreurBaseDeDonnees

logger = logging.getLogger(__name__)

__all__ = ["obtenir_moteur", "reinitialiser_moteur", "obtenir_moteur_securise"]

# Cache thread-safe pour singleton d'engine (remplace @st.cache_resource)
_engine_lock = threading.Lock()
_engine_instance = None


def obtenir_moteur(nombre_tentatives: int = DB_CONNECTION_RETRY, delai_tentative: int = 2):
    """
    Crée l'engine PostgreSQL avec retry automatique.

    Utilise un cache singleton thread-safe au lieu de @st.cache_resource
    pour être testable sans Streamlit.

    Args:
        nombre_tentatives: Nombre de tentatives de reconnexion
        delai_tentative: Délai entre les tentatives en secondes

    Returns:
        Engine SQLAlchemy configuré

    Raises:
        ErreurBaseDeDonnees: Si connexion impossible après toutes les tentatives
    """
    global _engine_instance

    if _engine_instance is not None:
        return _engine_instance

    with _engine_lock:
        # Double-check locking
        if _engine_instance is not None:
            return _engine_instance

        parametres = obtenir_parametres()
        derniere_erreur = None

        for tentative in range(nombre_tentatives):
            try:
                url_base = parametres.DATABASE_URL

                # connect_args adaptés au driver (PostgreSQL vs SQLite, etc.)
                connect_args: dict = {}
                if url_base.startswith("postgresql"):
                    sslmode = getattr(parametres, "DB_SSLMODE", "require")
                    connect_args = {
                        "connect_timeout": DB_CONNECTION_TIMEOUT,
                        "options": "-c timezone=utc",
                        "sslmode": sslmode,
                    }

                moteur = create_engine(
                    url_base,
                    poolclass=pool.QueuePool,
                    pool_size=5,
                    max_overflow=10,
                    pool_timeout=30,
                    pool_recycle=1800,
                    pool_pre_ping=True,
                    echo=parametres.DEBUG,
                    connect_args=connect_args,
                )

                # Test de connexion
                with moteur.connect() as conn:
                    conn.execute(text("SELECT 1"))

                logger.info(f"[OK] Connexion DB établie (tentative {tentative + 1})")
                _engine_instance = moteur
                return moteur

            except (OperationalError, DatabaseError) as e:
                derniere_erreur = e
                logger.warning(
                    f"[ERROR] Tentative {tentative + 1}/{nombre_tentatives} échouée: {e}"
                )

                if tentative < nombre_tentatives - 1:
                    time.sleep(delai_tentative)
                    continue

        message_erreur = (
            f"Impossible de se connecter après {nombre_tentatives} tentatives: {derniere_erreur}"
        )
        logger.error(message_erreur)
        raise ErreurBaseDeDonnees(
            message_erreur,
            message_utilisateur="Impossible de se connecter à la base de données",
        )


def reinitialiser_moteur() -> None:
    """Réinitialise le cache du moteur (utile pour les tests)."""
    global _engine_instance
    with _engine_lock:
        if _engine_instance is not None:
            try:
                _engine_instance.dispose()
            except Exception:
                pass
            _engine_instance = None


def obtenir_moteur_securise() -> "Engine | None":
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
