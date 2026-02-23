"""
Gestion des exceptions pour l'API REST.
"""

import logging
from functools import wraps
from typing import Any, Callable, TypeVar

from fastapi import HTTPException

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


def gerer_exception_api(func: F) -> F:
    """
    Décorateur pour gérer les exceptions dans les routes API.

    Convertit les exceptions non-HTTP en HTTPException(500).
    Re-lève les HTTPException telles quelles.

    Usage:
        @router.get("/items")
        @gerer_exception_api
        async def get_items():
            ...

    Note: Ce décorateur est optionnel si vous utilisez executer_avec_session()
    """

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return await func(*args, **kwargs)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erreur API dans {func.__name__}: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail="Une erreur interne est survenue. Veuillez réessayer.",
            ) from e

    return wrapper  # type: ignore
