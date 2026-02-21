"""
Décorateurs Result — Transformation automatique en Result.

Usage::
    from src.core.result import avec_result, safe, result_api

    @avec_result(ValueError)
    def parser(s: str) -> int:
        return int(s)

    @safe
    def risque() -> float:
        return 1 / 0

    @result_api(message_utilisateur="Erreur chargement")
    def charger_donnees() -> list[dict]:
        return db.query().all()
"""

from __future__ import annotations

import functools
import inspect
import logging
import traceback
from collections.abc import Callable
from typing import Any, TypeVar

from .base import Err, Ok, Result
from .codes import ErrorCode, ErrorInfo
from .helpers import from_exception

logger = logging.getLogger(__name__)

T = TypeVar("T")


# ═══════════════════════════════════════════════════════════
# MAPPING EXCEPTION â†’ ERROR CODE
# ═══════════════════════════════════════════════════════════

# Extension point : les modules peuvent enrichir via register_error_mapping()
_EXCEPTION_ERROR_MAP: dict[type, ErrorCode] = {}


def _classify_exception(exc: Exception) -> ErrorCode:
    """Classifie automatiquement une exception en ErrorCode."""
    # 1. Mappings enregistrés (précédence maximale)
    for exc_type, code in _EXCEPTION_ERROR_MAP.items():
        if isinstance(exc, exc_type):
            return code

    # 2. ExceptionApp (hiérarchie projet)
    try:
        from src.core.errors_base import ExceptionApp

        if isinstance(exc, ExceptionApp) and exc.code_erreur:
            try:
                return ErrorCode(exc.code_erreur)
            except ValueError:
                pass
    except ImportError:
        pass

    # 3. Types Python built-in
    if isinstance(exc, ValueError | TypeError):
        return ErrorCode.VALIDATION_ERROR
    if isinstance(exc, KeyError):
        return ErrorCode.NOT_FOUND
    if isinstance(exc, PermissionError):
        return ErrorCode.PERMISSION_DENIED
    if isinstance(exc, TimeoutError):
        return ErrorCode.TIMEOUT
    if isinstance(exc, ConnectionError | OSError):
        return ErrorCode.NETWORK_ERROR

    return ErrorCode.INTERNAL_ERROR


def register_error_mapping(exception_type: type, code: ErrorCode) -> None:
    """
    Enregistre un mapping exception â†’ ErrorCode.

    Permet aux modules métier d'étendre la classification automatique
    sans modifier le code du Result.

    Usage::
        >>> register_error_mapping(ErreurLimiteDebit, ErrorCode.RATE_LIMITED)
    """
    _EXCEPTION_ERROR_MAP[exception_type] = code


# ═══════════════════════════════════════════════════════════
# DÉCORATEURS — Transformation automatique en Result
# ═══════════════════════════════════════════════════════════


def avec_result(
    *exceptions: type[Exception],
) -> Callable[[Callable[..., Any]], Callable[..., Result[Any, Exception]]]:
    """Décorateur: fonction â†’ Result[T, Exception].

    Supporté en sync et async. La fonction décorée ne lève plus
    d'exception — elle retourne Ok ou Err.

    Args:
        *exceptions: Types d'exceptions à capturer (default: Exception).

    Usage::

        @avec_result(ValueError, TypeError)
        def diviser(a: int, b: int) -> float:
            return a / b

        result = diviser(10, 0)  # Err(ZeroDivisionError(...))
        result = diviser(10, 2)  # Ok(5.0)

        # Version async supportée
        @avec_result(httpx.HTTPError)
        async def fetch(url: str) -> str:
            async with httpx.AsyncClient() as c:
                return (await c.get(url)).text
    """
    exceptions_cibles = exceptions or (Exception,)

    def decorator(func: Callable[..., Any]) -> Callable[..., Result[Any, Exception]]:
        if inspect.iscoroutinefunction(func):

            @functools.wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Result[Any, Exception]:
                try:
                    return Ok(await func(*args, **kwargs))
                except exceptions_cibles as e:
                    return Err(e)

            return async_wrapper  # type: ignore[return-value]
        else:

            @functools.wraps(func)
            def sync_wrapper(*args: Any, **kwargs: Any) -> Result[Any, Exception]:
                try:
                    return Ok(func(*args, **kwargs))
                except exceptions_cibles as e:
                    return Err(e)

            return sync_wrapper

    return decorator


def safe(func: Callable[..., T]) -> Callable[..., Result[T, ErrorInfo]]:
    """Décorateur: fonction â†’ Result[T, ErrorInfo] avec classification auto.

    Usage::
        @safe
        def diviser(a: int, b: int) -> float:
            return a / b

        result = diviser(10, 0)  # Err(ErrorInfo(code=VALIDATION_ERROR, ...))
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Result[T, ErrorInfo]:
        try:
            return Ok(func(*args, **kwargs))
        except Exception as e:
            return from_exception(e, source=func.__qualname__)

    return wrapper


def result_api(
    default_code: ErrorCode = ErrorCode.INTERNAL_ERROR,
    log_errors: bool = True,
    message_utilisateur: str = "",
) -> Callable[[Callable[..., T]], Callable[..., Result[T, ErrorInfo]]]:
    """Décorateur avancé: @safe + classification auto + logging + source tracking.

    Usage::
        @result_api(message_utilisateur="Impossible de charger les recettes")
        def charger_recettes(categorie: str) -> list[Recette]:
            return db.query(Recette).filter_by(categorie=categorie).all()

        result = charger_recettes("desserts")
        # Ok(list[Recette]) ou Err(ErrorInfo) — jamais d'exception
    """

    def decorator(func: Callable[..., T]) -> Callable[..., Result[T, ErrorInfo]]:
        source = func.__qualname__

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Result[T, ErrorInfo]:
            try:
                return Ok(func(*args, **kwargs))
            except Exception as e:
                code = _classify_exception(e) or default_code

                error_info = ErrorInfo(
                    code=code,
                    message=str(e),
                    message_utilisateur=message_utilisateur or str(e),
                    source=source,
                    stack_trace=traceback.format_exc(),
                )

                if log_errors:
                    logger.error(
                        "[%s] %s dans %s: %s",
                        code.value,
                        type(e).__name__,
                        source,
                        e,
                    )

                return Err(error_info)

        return wrapper

    return decorator


__all__ = [
    "avec_result",
    "safe",
    "result_api",
    "register_error_mapping",
]
