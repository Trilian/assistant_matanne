"""
Engine - Création et gestion de l'engine SQLAlchemy.

Fonctions pour:
- Créer l'engine PostgreSQL avec retry automatique
- Obtenir l'engine de façon sécurisée

Stratégie de cache (Audit §10.4):
    En contexte Streamlit, ``@st.cache_resource`` est utilisé pour le
    connection pool (meilleure intégration lifecycle Streamlit).
    En contexte hors-Streamlit (tests, CLI, APScheduler), le singleton
    thread-safe avec ``threading.Lock`` est conservé comme fallback.
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

# Cache thread-safe pour singleton d'engine (fallback hors-Streamlit)
_engine_lock = threading.Lock()
_engine_instance = None

# Drapeau pour savoir si st.cache_resource est disponible
_streamlit_cache_disponible: bool | None = None


def _est_streamlit_actif() -> bool:
    """Détecte si Streamlit est actif (runtime en cours)."""
    global _streamlit_cache_disponible
    if _streamlit_cache_disponible is not None:
        return _streamlit_cache_disponible
    try:
        import streamlit as st
        from streamlit.runtime.scriptrunner import get_script_run_ctx

        ctx = get_script_run_ctx()
        _streamlit_cache_disponible = ctx is not None
    except Exception:
        _streamlit_cache_disponible = False
    return _streamlit_cache_disponible


def _creer_engine_impl(
    database_url: str,
    debug: bool = False,
    db_sslmode: str = "require",
    nombre_tentatives: int = DB_CONNECTION_RETRY,
    delai_tentative: int = 2,
) -> Engine:
    """Implémentation interne de création d'engine avec retry.

    Args:
        database_url: URL de connexion PostgreSQL
        debug: Active l'echo SQL
        db_sslmode: Mode SSL pour PostgreSQL
        nombre_tentatives: Nombre de tentatives de reconnexion
        delai_tentative: Délai entre les tentatives en secondes

    Returns:
        Engine SQLAlchemy configuré

    Raises:
        ErreurBaseDeDonnees: Si connexion impossible après toutes les tentatives
    """
    derniere_erreur = None

    for tentative in range(nombre_tentatives):
        try:
            # connect_args adaptés au driver (PostgreSQL vs SQLite, etc.)
            connect_args: dict = {}
            if database_url.startswith("postgresql"):
                connect_args = {
                    "connect_timeout": DB_CONNECTION_TIMEOUT,
                    "options": "-c timezone=utc",
                    "sslmode": db_sslmode,
                }

            moteur = create_engine(
                database_url,
                poolclass=pool.QueuePool,
                pool_size=5,
                max_overflow=10,
                pool_timeout=30,
                pool_recycle=1800,
                pool_pre_ping=True,
                echo=debug,
                connect_args=connect_args,
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

    message_erreur = (
        f"Impossible de se connecter après {nombre_tentatives} tentatives: {derniere_erreur}"
    )
    logger.error(message_erreur)
    raise ErreurBaseDeDonnees(
        message_erreur,
        message_utilisateur="Impossible de se connecter à la base de données",
    )


def _obtenir_moteur_streamlit(
    nombre_tentatives: int = DB_CONNECTION_RETRY,
    delai_tentative: int = 2,
) -> Engine:
    """Crée l'engine via @st.cache_resource (lifecycle Streamlit natif).

    Le décorateur est appliqué dynamiquement pour éviter un import
    hard de Streamlit au niveau du module.
    """
    import streamlit as st

    @st.cache_resource(show_spinner="Connexion à la base de données...")
    def _cached_engine(
        url: str,
        debug: bool,
        sslmode: str,
        _tentatives: int,
        _delai: int,
    ) -> Engine:
        return _creer_engine_impl(url, debug, sslmode, _tentatives, _delai)

    parametres = obtenir_parametres()
    sslmode = getattr(parametres, "DB_SSLMODE", "require")
    return _cached_engine(
        parametres.DATABASE_URL,
        parametres.DEBUG,
        sslmode,
        nombre_tentatives,
        delai_tentative,
    )


def obtenir_moteur(nombre_tentatives: int = DB_CONNECTION_RETRY, delai_tentative: int = 2):
    """
    Crée l'engine PostgreSQL avec retry automatique.

    Utilise ``@st.cache_resource`` en contexte Streamlit pour un meilleur
    lifecycle management, et un singleton thread-safe en fallback
    (tests, CLI, APScheduler).

    Args:
        nombre_tentatives: Nombre de tentatives de reconnexion
        delai_tentative: Délai entre les tentatives en secondes

    Returns:
        Engine SQLAlchemy configuré

    Raises:
        ErreurBaseDeDonnees: Si connexion impossible après toutes les tentatives
    """
    # Stratégie 1: @st.cache_resource (préféré en contexte Streamlit)
    if _est_streamlit_actif():
        return _obtenir_moteur_streamlit(nombre_tentatives, delai_tentative)

    # Stratégie 2: Singleton thread-safe (hors-Streamlit)
    global _engine_instance

    if _engine_instance is not None:
        return _engine_instance

    with _engine_lock:
        # Double-check locking
        if _engine_instance is not None:
            return _engine_instance

        parametres = obtenir_parametres()
        sslmode = getattr(parametres, "DB_SSLMODE", "require")

        moteur = _creer_engine_impl(
            parametres.DATABASE_URL,
            parametres.DEBUG,
            sslmode,
            nombre_tentatives,
            delai_tentative,
        )
        _engine_instance = moteur
        return moteur


def reinitialiser_moteur() -> None:
    """Réinitialise le cache du moteur (utile pour les tests).

    Nettoie le singleton thread-safe ET le cache Streamlit si disponible.
    """
    global _engine_instance, _streamlit_cache_disponible
    with _engine_lock:
        if _engine_instance is not None:
            try:
                _engine_instance.dispose()
            except Exception:
                pass
            _engine_instance = None

    # Réinitialiser aussi le cache Streamlit si actif
    if _streamlit_cache_disponible:
        try:
            import streamlit as st

            st.cache_resource.clear()
        except Exception:
            pass

    # Forcer la re-détection au prochain appel
    _streamlit_cache_disponible = None


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
