"""
Helpers Result — Factories et conversions.

Usage::
    from src.core.result import success, failure, capturer, depuis_option

    result = success(42)
    result = failure(ErrorCode.NOT_FOUND, "Non trouvé")
    result = capturer(lambda: risque())
    result = depuis_option(valeur_nullable, "Erreur si None")
"""

from __future__ import annotations

import traceback
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

from .base import Err, Ok, Result
from .codes import ErrorCode, ErrorInfo

T = TypeVar("T")
E = TypeVar("E")


# ═══════════════════════════════════════════════════════════
# FACTORIES — Constructeurs pratiques
# ═══════════════════════════════════════════════════════════


def success(value: T) -> Ok[T, Any]:
    """Crée un Result succès (alias de Ok)."""
    return Ok(value)


def failure(
    code: ErrorCode,
    message: str,
    message_utilisateur: str = "",
    details: dict[str, Any] | None = None,
    source: str = "",
) -> Err[Any, ErrorInfo]:
    """Crée un Result échec avec ErrorInfo structuré."""
    return Err(
        ErrorInfo(
            code=code,
            message=message,
            message_utilisateur=message_utilisateur or message,
            details=details or {},
            source=source,
        )
    )


def from_exception(
    exc: Exception,
    code: ErrorCode = ErrorCode.INTERNAL_ERROR,
    source: str = "",
) -> Err[Any, ErrorInfo]:
    """Convertit une exception en Err(ErrorInfo)."""
    try:
        from src.core.errors_base import ExceptionApp

        if isinstance(exc, ExceptionApp):
            try:
                mapped_code = ErrorCode(exc.code_erreur)
            except ValueError:
                mapped_code = code
            return Err(
                ErrorInfo(
                    code=mapped_code,
                    message=exc.message,
                    message_utilisateur=exc.message_utilisateur,
                    details=exc.details,
                    source=source,
                    stack_trace=traceback.format_exc(),
                )
            )
    except ImportError:
        pass

    return Err(
        ErrorInfo(
            code=code,
            message=str(exc),
            source=source,
            stack_trace=traceback.format_exc(),
        )
    )


# ═══════════════════════════════════════════════════════════
# HELPERS POUR CONVERSION
# ═══════════════════════════════════════════════════════════


def capturer(fn: Callable[[], T]) -> Result[T, Exception]:
    """
    Capture une exception en Result.

    Usage::
        >>> result = capturer(lambda: int("abc"))
        >>> result.is_err()  # True
    """
    try:
        return Ok(fn())
    except Exception as e:
        return Err(e)


async def capturer_async(coro: Awaitable[T]) -> Result[T, Exception]:
    """
    Capture une exception depuis une coroutine.

    Usage::
        >>> result = await capturer_async(fetch_data())
    """
    try:
        return Ok(await coro)
    except Exception as e:
        return Err(e)


def depuis_option(valeur: T | None, erreur: E) -> Result[T, E]:
    """
    Convertit une valeur optionnelle en Result.

    Usage::
        >>> depuis_option(None, "Pas trouvé")
        Err('Pas trouvé')
    """
    if valeur is None:
        return Err(erreur)
    return Ok(valeur)


def depuis_bool(condition: bool, valeur: T, erreur: E) -> Result[T, E]:
    """
    Convertit un booléen en Result.

    Usage::
        >>> depuis_bool(age >= 18, "majeur", "Âge insuffisant")
    """
    if condition:
        return Ok(valeur)
    return Err(erreur)


__all__ = [
    "success",
    "failure",
    "from_exception",
    "capturer",
    "capturer_async",
    "depuis_option",
    "depuis_bool",
]
