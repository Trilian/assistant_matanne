"""
Session - Gestion des sessions SQLAlchemy.

Fonctions pour:
- Créer des session factories (cachées au niveau module)
- Context managers pour les sessions
"""

import logging
import threading
from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy.exc import DatabaseError, OperationalError
from sqlalchemy.orm import Session, sessionmaker

from ..exceptions import ErreurBaseDeDonnees
from .engine import obtenir_moteur

logger = logging.getLogger(__name__)

__all__ = ["obtenir_fabrique_session", "obtenir_contexte_db", "obtenir_db_securise"]

# Session factory cachée au niveau module (créée une seule fois)
_session_factory: sessionmaker | None = None
_factory_lock = threading.Lock()


def obtenir_fabrique_session() -> sessionmaker:
    """
    Retourne une session factory (cachée au niveau module).

    La factory est créée une seule fois puis réutilisée.

    Returns:
        Session factory configurée
    """
    global _session_factory

    if _session_factory is not None:
        return _session_factory

    with _factory_lock:
        if _session_factory is None:
            moteur = obtenir_moteur()
            _session_factory = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=moteur,
                expire_on_commit=False,
            )
    return _session_factory


def reinitialiser_fabrique() -> None:
    """Réinitialise la factory (utile après changement de moteur ou en tests)."""
    global _session_factory
    with _factory_lock:
        _session_factory = None


@contextmanager
def obtenir_contexte_db() -> Generator[Session, None, None]:
    """
    Context manager avec gestion d'erreurs robuste.

    Enrichit automatiquement les logs avec le correlation_id du contexte
    d'observabilité, permettant de tracer chaque transaction DB.

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

    # Récupérer le correlation_id pour tracer cette transaction
    try:
        from ..observability import obtenir_contexte

        ctx = obtenir_contexte()
        cid = ctx.correlation_id
    except Exception:
        cid = "--------"

    try:
        logger.debug("[%s] Session DB ouverte", cid)
        yield db
        db.commit()
        logger.debug("[%s] Session DB commit OK", cid)

    except OperationalError as e:
        db.rollback()
        logger.error("[%s] Erreur opérationnelle DB: %s", cid, e)
        raise ErreurBaseDeDonnees(
            f"Erreur réseau/connexion: {e}",
            message_utilisateur="Problème de connexion à la base de données",
        ) from e

    except DatabaseError as e:
        db.rollback()
        logger.error("[%s] Erreur base de données: %s", cid, e)
        raise ErreurBaseDeDonnees(
            str(e), message_utilisateur="Erreur lors de l'opération en base de données"
        ) from e

    except Exception as e:
        db.rollback()
        logger.error("[%s] Erreur inattendue: %s", cid, e)
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
