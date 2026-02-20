"""
Result[T, E] - Pattern Result pour contrôle de flux explicite.

Remplace les try/except silencieux par un type de retour explicite.
Inspiré de Rust Result<T, E> et Scala Either[L, R].

Usage:
    from src.services.core.base.result import Result, Success, Failure

    def creer_recette(data: dict) -> Result[Recette, str]:
        if not data.get("nom"):
            return Failure("Le nom est requis")
        recette = Recette(**data)
        return Success(recette)

    # Utilisation
    result = creer_recette({"nom": "Tarte"})
    if result.is_success:
        print(result.value)  # Recette
    else:
        print(result.error)  # Message d'erreur

    # Chaînage fonctionnel
    result = (
        creer_recette(data)
        .map(lambda r: r.nom.upper())
        .unwrap_or("Inconnu")
    )
"""

from __future__ import annotations

import logging
import traceback
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Generic, TypeVar, overload

logger = logging.getLogger(__name__)

T = TypeVar("T")
U = TypeVar("U")
E = TypeVar("E")


# ═══════════════════════════════════════════════════════════
# CODES D'ERREUR STANDARDISÉS
# ═══════════════════════════════════════════════════════════


class ErrorCode(str, Enum):
    """Codes d'erreur standardisés pour les Result."""

    # Validation
    VALIDATION_ERROR = "VALIDATION_ERROR"
    MISSING_FIELD = "MISSING_FIELD"
    INVALID_FORMAT = "INVALID_FORMAT"

    # Base de données
    NOT_FOUND = "NOT_FOUND"
    DUPLICATE = "DUPLICATE"
    DATABASE_ERROR = "DATABASE_ERROR"
    CONSTRAINT_VIOLATION = "CONSTRAINT_VIOLATION"

    # IA
    AI_ERROR = "AI_ERROR"
    RATE_LIMITED = "RATE_LIMITED"
    PARSING_ERROR = "PARSING_ERROR"
    AI_UNAVAILABLE = "AI_UNAVAILABLE"

    # Externe
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"
    TIMEOUT = "TIMEOUT"
    NETWORK_ERROR = "NETWORK_ERROR"

    # Système
    INTERNAL_ERROR = "INTERNAL_ERROR"
    CONFIGURATION_ERROR = "CONFIGURATION_ERROR"
    PERMISSION_DENIED = "PERMISSION_DENIED"

    # Métier
    BUSINESS_RULE_VIOLATION = "BUSINESS_RULE_VIOLATION"
    INSUFFICIENT_STOCK = "INSUFFICIENT_STOCK"
    QUOTA_EXCEEDED = "QUOTA_EXCEEDED"


# ═══════════════════════════════════════════════════════════
# ERROR INFO — Détails d'erreur structurés
# ═══════════════════════════════════════════════════════════


@dataclass(frozen=True, slots=True)
class ErrorInfo:
    """
    Détails d'erreur structurés et immutables.

    Attributes:
        code: Code d'erreur standardisé
        message: Message technique pour les logs
        message_utilisateur: Message friendly pour l'UI
        details: Détails supplémentaires
        timestamp: Horodatage de l'erreur
        source: Service/fonction source de l'erreur
        stack_trace: Stack trace optionnelle
    """

    code: ErrorCode
    message: str
    message_utilisateur: str = ""
    details: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = ""
    stack_trace: str = ""

    def __post_init__(self):
        # Si pas de message utilisateur, utiliser le message technique
        if not self.message_utilisateur:
            object.__setattr__(self, "message_utilisateur", self.message)

    def to_dict(self) -> dict[str, Any]:
        """Sérialise en dictionnaire."""
        return {
            "code": self.code.value,
            "message": self.message,
            "message_utilisateur": self.message_utilisateur,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
        }


# ═══════════════════════════════════════════════════════════
# RESULT — Type union Success | Failure
# ═══════════════════════════════════════════════════════════


@dataclass(frozen=True, slots=True)
class Success(Generic[T]):
    """Résultat positif contenant une valeur."""

    value: T

    @property
    def is_success(self) -> bool:
        return True

    @property
    def is_failure(self) -> bool:
        return False

    def map(self, func: Callable[[T], U]) -> Result[U, Any]:
        """Applique une transformation si succès."""
        try:
            return Success(func(self.value))
        except Exception as e:
            return Failure(
                ErrorInfo(
                    code=ErrorCode.INTERNAL_ERROR,
                    message=f"Erreur dans map: {e}",
                    stack_trace=traceback.format_exc(),
                )
            )

    def flat_map(self, func: Callable[[T], Result[U, Any]]) -> Result[U, Any]:
        """Applique une transformation qui retourne un Result."""
        try:
            return func(self.value)
        except Exception as e:
            return Failure(
                ErrorInfo(
                    code=ErrorCode.INTERNAL_ERROR,
                    message=f"Erreur dans flat_map: {e}",
                    stack_trace=traceback.format_exc(),
                )
            )

    def or_else(self, _fallback: Callable[[Any], Result[T, Any]]) -> Result[T, Any]:
        """Retourne self (succès), ignore le fallback."""
        return self

    def unwrap(self) -> T:
        """Retourne la valeur ou lève une exception si Failure."""
        return self.value

    def unwrap_or(self, default: T) -> T:
        """Retourne la valeur ou le default."""
        return self.value

    def unwrap_or_else(self, func: Callable[[Any], T]) -> T:
        """Retourne la valeur ou le résultat de func."""
        return self.value

    def on_success(self, func: Callable[[T], None]) -> Result[T, Any]:
        """Exécute un side-effect si succès."""
        try:
            func(self.value)
        except Exception as e:
            logger.warning(f"Erreur dans on_success callback: {e}")
        return self

    def on_failure(self, _func: Callable[[Any], None]) -> Result[T, Any]:
        """Ne fait rien (c'est un succès)."""
        return self

    @property
    def error(self) -> None:
        """Pas d'erreur dans un Success."""
        return None


@dataclass(frozen=True, slots=True)
class Failure(Generic[E]):
    """Résultat négatif contenant une erreur."""

    error: E

    @property
    def is_success(self) -> bool:
        return False

    @property
    def is_failure(self) -> bool:
        return True

    def map(self, _func: Callable) -> Result[Any, E]:
        """Ne fait rien (c'est une erreur)."""
        return self  # type: ignore[return-value]

    def flat_map(self, _func: Callable) -> Result[Any, E]:
        """Ne fait rien (c'est une erreur)."""
        return self  # type: ignore[return-value]

    def or_else(self, fallback: Callable[[E], Result[T, E]]) -> Result[T, E]:
        """Essaie le fallback."""
        try:
            return fallback(self.error)
        except Exception as e:
            return Failure(
                ErrorInfo(  # type: ignore[arg-type]
                    code=ErrorCode.INTERNAL_ERROR,
                    message=f"Erreur dans or_else: {e}",
                    stack_trace=traceback.format_exc(),
                )
            )

    def unwrap(self) -> Any:
        """Lève une exception car c'est un Failure."""
        if isinstance(self.error, ErrorInfo):
            raise ValueError(f"[{self.error.code.value}] {self.error.message}")
        raise ValueError(f"Tentative de unwrap sur un Failure: {self.error}")

    def unwrap_or(self, default: T) -> T:
        """Retourne le default."""
        return default

    def unwrap_or_else(self, func: Callable[[E], T]) -> T:
        """Retourne le résultat de func(error)."""
        return func(self.error)

    def on_success(self, _func: Callable) -> Result[Any, E]:
        """Ne fait rien (c'est un échec)."""
        return self  # type: ignore[return-value]

    def on_failure(self, func: Callable[[E], None]) -> Result[Any, E]:
        """Exécute un side-effect si échec."""
        try:
            func(self.error)
        except Exception as e:
            logger.warning(f"Erreur dans on_failure callback: {e}")
        return self  # type: ignore[return-value]

    @property
    def value(self) -> None:
        """Pas de valeur dans un Failure."""
        return None


# Type alias principal
Result = Success[T] | Failure[E]


# ═══════════════════════════════════════════════════════════
# FACTORIES — Constructeurs pratiques
# ═══════════════════════════════════════════════════════════


def success(value: T) -> Success[T]:
    """Crée un Result succès."""
    return Success(value)


def failure(
    code: ErrorCode,
    message: str,
    message_utilisateur: str = "",
    details: dict[str, Any] | None = None,
    source: str = "",
) -> Failure[ErrorInfo]:
    """Crée un Result échec avec ErrorInfo structuré."""
    return Failure(
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
) -> Failure[ErrorInfo]:
    """Convertit une exception en Failure."""
    from src.core.errors_base import ExceptionApp

    if isinstance(exc, ExceptionApp):
        return Failure(
            ErrorInfo(
                code=ErrorCode(exc.code_erreur)
                if exc.code_erreur in [e.value for e in ErrorCode]
                else code,
                message=exc.message,
                message_utilisateur=exc.message_utilisateur,
                details=exc.details,
                source=source,
                stack_trace=traceback.format_exc(),
            )
        )

    return Failure(
        ErrorInfo(
            code=code,
            message=str(exc),
            source=source,
            stack_trace=traceback.format_exc(),
        )
    )


def safe(func: Callable[..., T]) -> Callable[..., Result[T, ErrorInfo]]:
    """
    Décorateur qui convertit une fonction levant des exceptions en Result.

    Usage:
        @safe
        def diviser(a: int, b: int) -> float:
            return a / b

        result = diviser(10, 0)  # Failure(ErrorInfo(...))
        result = diviser(10, 2)  # Success(5.0)
    """
    import functools

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Result[T, ErrorInfo]:
        try:
            return Success(func(*args, **kwargs))
        except Exception as e:
            return from_exception(e, source=func.__qualname__)

    return wrapper


# ═══════════════════════════════════════════════════════════
# COMBINATEURS — Opérations sur plusieurs Result
# ═══════════════════════════════════════════════════════════


def collect(results: list[Result[T, E]]) -> Result[list[T], E]:
    """
    Combine une liste de Result en un seul Result.

    Si tous sont Success → Success(list[T])
    Si un seul est Failure → Failure(premier échec)

    Usage:
        results = [success(1), success(2), success(3)]
        combined = collect(results)  # Success([1, 2, 3])

        results = [success(1), failure(...), success(3)]
        combined = collect(results)  # Failure(...)
    """
    values: list[T] = []
    for result in results:
        if result.is_failure:
            return result  # type: ignore[return-value]
        values.append(result.value)  # type: ignore[union-attr]
    return Success(values)


def collect_all(results: list[Result[T, E]]) -> tuple[list[T], list[E]]:
    """
    Sépare les succès et les échecs.

    Contrairement à collect(), ne s'arrête pas au premier échec.

    Returns:
        Tuple (succès, échecs)

    Usage:
        successes, failures = collect_all(results)
    """
    successes: list[T] = []
    failures: list[E] = []
    for result in results:
        if result.is_success:
            successes.append(result.value)  # type: ignore[union-attr]
        else:
            failures.append(result.error)  # type: ignore[union-attr]
    return successes, failures


__all__ = [
    # Types principaux
    "Result",
    "Success",
    "Failure",
    "ErrorInfo",
    "ErrorCode",
    # Factories
    "success",
    "failure",
    "from_exception",
    "safe",
    # Combinateurs
    "collect",
    "collect_all",
]
