"""
Utilitaires CRUD pour l'API REST.

Fournit des helpers pour les opérations courantes dans les routes.
"""

from collections.abc import Callable, Generator
from contextlib import contextmanager
from typing import Any, TypeVar

from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

T = TypeVar("T", bound=BaseModel)


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
        raise HTTPException(status_code=500, detail=str(e)) from e


def creer_dependance_session():
    """
    Crée une dépendance FastAPI pour la session DB.

    Usage dans les routes:
        @router.get("/items")
        async def get_items(session: Session = Depends(creer_dependance_session())):
            return session.query(Item).all()

    Note: Préférer executer_avec_session() pour le context manager explicite.
    """
    from src.core.db import obtenir_contexte_db

    def get_db():
        with obtenir_contexte_db() as session:
            yield session

    return get_db
