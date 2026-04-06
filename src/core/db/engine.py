"""
Engine - Création et gestion de l'engine SQLAlchemy.

Fonctions pour:
- Créer l'engine PostgreSQL avec retry automatique
- Obtenir l'engine de façon sécurisée

Utilise un singleton thread-safe avec ``threading.Lock``.
"""

import logging
import os
import threading
import time
from urllib.parse import urlparse

from sqlalchemy import Engine, create_engine, pool, text
from sqlalchemy.exc import DatabaseError, OperationalError

from ..config import obtenir_parametres
from ..constants import DB_CONNECTION_RETRY, DB_CONNECTION_TIMEOUT
from ..exceptions import ErreurBaseDeDonnees

logger = logging.getLogger(__name__)

__all__ = ["obtenir_moteur", "reinitialiser_moteur", "obtenir_moteur_securise"]

# Singleton thread-safe pour l'engine
_engine_lock = threading.Lock()
_engine_instance = None


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

    hostname = urlparse(database_url).hostname or ""
    est_serverless = bool(
        os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME") or os.getenv("SERVERLESS")
    )
    est_supabase_direct = hostname.startswith("db.") and hostname.endswith(".supabase.co")

    if est_serverless and est_supabase_direct:
        nombre_tentatives = 1
        logger.warning(
            "URL DB Supabase directe détectée en environnement serverless ; "
            "utilisez de préférence l'URL pooler IPv4 (SUPABASE_DB_POOLER_URL)."
        )

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


def obtenir_moteur(nombre_tentatives: int = DB_CONNECTION_RETRY, delai_tentative: int = 2):
    """
    Crée l'engine PostgreSQL avec retry automatique.

    Utilise un singleton thread-safe avec double-check locking.

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
    except (ErreurBaseDeDonnees, ValueError) as e:
        logger.error(f"DB non disponible: {e}")
        return None
