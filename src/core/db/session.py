"""
Session - Gestion des sessions SQLAlchemy.

Fonctions pour:
- Créer des session factories
- Context managers pour les sessions
"""

import logging
from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy.exc import DatabaseError, OperationalError
from sqlalchemy.orm import Session, sessionmaker

from ..errors import ErreurBaseDeDonnees
from .engine import obtenir_moteur

logger = logging.getLogger(__name__)


def obtenir_fabrique_session():
    """
    Retourne une session factory.

    Returns:
        Session factory configurée
    """
    moteur = obtenir_moteur()
    return sessionmaker(autocommit=False, autoflush=False, bind=moteur, expire_on_commit=False)


# Session factory initialisée à la demande (évite side-effects à l'import)
SessionLocale = None


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
    # Obtenir une factory de session à la demande (création différée)
    fabrique = obtenir_fabrique_session()
    db = fabrique()

    try:
        yield db
        db.commit()

    except OperationalError as e:
        db.rollback()
        logger.error(f"[ERROR] Erreur opérationnelle DB: {e}")
        raise ErreurBaseDeDonnees(
            f"Erreur réseau/connexion: {e}",
            message_utilisateur="Problème de connexion à la base de données",
        ) from e

    except DatabaseError as e:
        db.rollback()
        logger.error(f"[ERROR] Erreur base de données: {e}")
        raise ErreurBaseDeDonnees(
            str(e), message_utilisateur="Erreur lors de l'opération en base de données"
        ) from e

    except Exception as e:
        db.rollback()
        logger.error(f"[ERROR] Erreur inattendue: {e}")
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
