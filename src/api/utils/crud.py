"""
Utilitaires CRUD pour l'API REST.

Fournit des helpers pour les opérations courantes dans les routes.
"""

import asyncio
import logging
from collections.abc import Callable, Generator
from contextlib import asynccontextmanager, contextmanager
from typing import Any, TypeVar

from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)
R = TypeVar("R")


def construire_reponse_paginee(
    items: list[Any],
    total: int,
    page: int,
    page_size: int,
    schema: type[T] | None = None,
) -> dict[str, Any]:
    """
    Construit une réponse paginée standard.

    Args:
        items: Liste des éléments à retourner
        total: Nombre total d'éléments
        page: Page actuelle
        page_size: Taille de page
        schema: Schéma Pydantic optionnel pour sérialiser les items

    Returns:
        Dict avec: items, total, page, page_size, pages
    """
    if schema:
        serialized = [schema.model_validate(item).model_dump() for item in items]
    else:
        serialized = items

    return {
        "items": serialized,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size if total > 0 else 0,
    }


@contextmanager
def executer_avec_session() -> Generator[Session, None, None]:
    """
    Context manager qui gère la session DB et les erreurs.

    Usage:
        with executer_avec_session() as session:
            result = session.query(Model).all()
            # HTTPException est re-levée telle quelle
            # Autres exceptions sont converties en 500

    Yields:
        Session SQLAlchemy

    Raises:
        HTTPException: Re-levée si c'est déjà une HTTPException
        HTTPException(500): Pour toute autre exception
    """
    from src.core.db import obtenir_contexte_db

    try:
        with obtenir_contexte_db() as session:
            yield session
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur session DB: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Une erreur interne est survenue. Veuillez réessayer.",
        ) from e


# ═══════════════════════════════════════════════════════════
# HELPERS ASYNC
# ═══════════════════════════════════════════════════════════


async def executer_async(func: Callable[..., R], *args: Any, **kwargs: Any) -> R:
    """
    Exécute une fonction synchrone dans un thread pool.

    Permet d'exécuter des opérations bloquantes (comme les requêtes DB)
    sans bloquer l'event loop asyncio.

    Usage:
        async def get_recettes():
            def _query():
                with executer_avec_session() as session:
                    return session.query(Recette).all()

            return await executer_async(_query)

    Args:
        func: Fonction synchrone à exécuter
        *args: Arguments positionnels
        **kwargs: Arguments nommés

    Returns:
        Résultat de la fonction

    Raises:
        HTTPException: Re-levée depuis la fonction
    """
    try:
        return await asyncio.to_thread(func, *args, **kwargs)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur async: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Une erreur interne est survenue. Veuillez réessayer.",
        ) from e


async def query_async(query_func: Callable[[Session], R]) -> R:
    """
    Exécute une fonction de requête DB de manière asynchrone.

    Wrapper pratique pour les requêtes DB simples.

    Usage:
        result = await query_async(
            lambda session: session.query(Recette).filter(Recette.id == 1).first()
        )

    Args:
        query_func: Fonction prenant une Session et retournant le résultat

    Returns:
        Résultat de la requête

    Raises:
        HTTPException: En cas d'erreur
    """

    def _execute():
        with executer_avec_session() as session:
            return query_func(session)

    return await executer_async(_execute)
