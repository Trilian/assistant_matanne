"""
Gestion des exceptions pour l'API REST.
"""

import logging
from functools import wraps
from inspect import Signature, signature
from typing import Any, Callable, TypeVar, get_type_hints

from fastapi import HTTPException

from src.core.exceptions import ErreurBaseDeDonnees

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


def gerer_exception_api[F: Callable[..., Any]](func: F) -> F:
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

    @wraps(
        func,
        assigned=("__module__", "__name__", "__qualname__", "__doc__"),
    )
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return await func(*args, **kwargs)
        except HTTPException:
            raise
        except ErreurBaseDeDonnees as e:
            logger.warning("Erreur DB dans %s: %s", func.__name__, e)
            raise HTTPException(
                status_code=503,
                detail=getattr(
                    e,
                    "message_utilisateur",
                    "La base de données est temporairement indisponible. Réessayez.",
                ),
            ) from e
        except Exception as e:
            logger.error(f"Erreur API dans {func.__name__}: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail="Une erreur interne est survenue. Veuillez réessayer.",
            ) from e

    # Préserve une signature résolue pour FastAPI (compatible annotations différées).
    sig = signature(func)
    try:
        resolved_hints = get_type_hints(func, include_extras=True)
        resolved_parameters = []
        for param in sig.parameters.values():
            resolved_annotation = resolved_hints.get(param.name, param.annotation)
            resolved_parameters.append(param.replace(annotation=resolved_annotation))

        resolved_return = resolved_hints.get("return", sig.return_annotation)
        wrapper.__signature__ = Signature(
            parameters=resolved_parameters,
            return_annotation=resolved_return,
        )
    except Exception:
        wrapper.__signature__ = sig

    return wrapper  # type: ignore
