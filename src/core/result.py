"""
Result Monad — Gestion explicite des succès/échecs.

Fusion Ok/Err (style Rust, pattern matching) + ErrorInfo/ErrorCode structuré.
Élimine les exceptions implicites et rend le code auto-documenté.

Usage basique::

    from src.core.result import Ok, Err

    def diviser(a: int, b: int) -> Result[float, str]:
        if b == 0:
            return Err("Division par zéro")
        return Ok(a / b)

    # Pattern matching (Python 3.10+)
    match diviser(10, 2):
        case Ok(v): print(f"Résultat: {v}")
        case Err(e): print(f"Erreur: {e}")

    # Chaînage fonctionnel
    result = (
        diviser(10, 2)
        .map(lambda x: x * 2)
        .map_err(lambda e: f"Erreur calcul: {e}")
        .unwrap_or(0.0)
    )

Usage production (erreurs structurées)::

    from src.core.result import Ok, failure, ErrorCode, result_api

    def charger_recette(id: int) -> Result[Recette, ErrorInfo]:
        recette = db.get(id)
        if not recette:
            return failure(ErrorCode.NOT_FOUND, f"Recette #{id} introuvable")
        return Ok(recette)

    result.on_success(lambda r: logger.info(f"Chargé: {r.nom}"))
    result.on_failure(lambda e: logger.error(f"[{e.code}] {e.message}"))

    @result_api(message_utilisateur="Impossible de charger les recettes")
    def charger_recettes(categorie: str) -> list[Recette]:
        return db.query(Recette).filter_by(categorie=categorie).all()
"""

from __future__ import annotations

import functools
import inspect
import logging
import traceback
from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Generic, NoReturn, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")  # Type de la valeur OK
E = TypeVar("E")  # Type de l'erreur
U = TypeVar("U")  # Type transformé
F = TypeVar("F")  # Type erreur transformée


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

    def __post_init__(self) -> None:
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

    def __str__(self) -> str:
        return f"[{self.code.value}] {self.message}"


# ═══════════════════════════════════════════════════════════
# RESULT ABC — Ok(valeur) | Err(erreur)
# ═══════════════════════════════════════════════════════════


class Result(ABC, Generic[T, E]):
    """
    Type Result abstrait — soit Ok(valeur) soit Err(erreur).

    Permet une gestion explicite des erreurs sans exceptions,
    avec chaînage fonctionnel, side-effects, et recovery.
    Supporte le pattern matching Python 3.10+.
    """

    __slots__ = ()

    # ── Discriminateurs ──────────────────────────────────────

    @abstractmethod
    def is_ok(self) -> bool:
        """Retourne True si c'est un Ok."""
        ...

    @abstractmethod
    def is_err(self) -> bool:
        """Retourne True si c'est un Err."""
        ...

    # Aliases de compatibilité (convention services)
    @property
    def is_success(self) -> bool:
        """Alias de ``is_ok()`` pour compatibilité."""
        return self.is_ok()

    @property
    def is_failure(self) -> bool:
        """Alias de ``is_err()`` pour compatibilité."""
        return self.is_err()

    # ── Extracteurs ──────────────────────────────────────────

    @abstractmethod
    def ok(self) -> T | None:
        """Retourne la valeur si Ok, sinon None."""
        ...

    @abstractmethod
    def err(self) -> E | None:
        """Retourne l'erreur si Err, sinon None."""
        ...

    # Aliases property (convention services)
    @property
    def value(self) -> T | None:
        """Alias property de ``ok()`` pour compatibilité."""
        return self.ok()

    @property
    def error(self) -> E | None:
        """Alias property de ``err()`` pour compatibilité."""
        return self.err()

    # ── Unwrap family ────────────────────────────────────────

    @abstractmethod
    def unwrap(self) -> T:
        """Retourne la valeur ou lève ValueError si Err."""
        ...

    @abstractmethod
    def unwrap_or(self, default: T) -> T:
        """Retourne la valeur ou le default si Err."""
        ...

    @abstractmethod
    def unwrap_or_else(self, fn: Callable[[E], T]) -> T:
        """Retourne la valeur ou applique fn sur l'erreur."""
        ...

    def expect(self, message: str) -> T:
        """Retourne la valeur ou lève avec message custom."""
        if self.is_ok():
            return self.unwrap()
        raise ValueError(f"{message}: {self.err()}")

    def unwrap_err(self) -> E:
        """Retourne l'erreur ou lève ValueError si Ok.

        Symétrique de ``unwrap()`` — utile pour extraire l'erreur
        de manière type-safe quand on sait que c'est un Err.

        Raises:
            ValueError: Si c'est un Ok.
        """
        if self.is_err():
            return self.err()  # type: ignore[return-value]
        raise ValueError(f"Appelé unwrap_err() sur Ok: {self.ok()}")

    # ── Transformations ──────────────────────────────────────

    @abstractmethod
    def map(self, fn: Callable[[T], U]) -> Result[U, E]:
        """Applique fn sur la valeur si Ok."""
        ...

    @abstractmethod
    def map_err(self, fn: Callable[[E], F]) -> Result[T, F]:
        """Applique fn sur l'erreur si Err."""
        ...

    @abstractmethod
    def and_then(self, fn: Callable[[T], Result[U, E]]) -> Result[U, E]:
        """Chaîne un autre Result si Ok (flatMap)."""
        ...

    @abstractmethod
    def or_else(self, fn: Callable[[E], Result[T, F]]) -> Result[T, F]:
        """Chaîne un autre Result si Err."""
        ...

    def flat_map(self, fn: Callable[[T], Result[U, E]]) -> Result[U, E]:
        """Alias de ``and_then()`` pour compatibilité."""
        return self.and_then(fn)

    # ── Side-effects ─────────────────────────────────────────

    @abstractmethod
    def on_success(self, fn: Callable[[T], None]) -> Result[T, E]:
        """Exécute un side-effect si Ok (tap pattern). Retourne self."""
        ...

    @abstractmethod
    def on_failure(self, fn: Callable[[E], None]) -> Result[T, E]:
        """Exécute un side-effect si Err (tap pattern). Retourne self."""
        ...

    # ── Recovery ─────────────────────────────────────────────

    @abstractmethod
    def recover(self, fn: Callable[[E], T]) -> Result[T, E]:
        """Tente de récupérer un Err en Ok via fn(error)."""
        ...

    # ── Bool coercion ────────────────────────────────────────

    def __bool__(self) -> bool:
        """Permet ``if result:`` comme raccourci pour ``if result.is_ok():``."""
        return self.is_ok()


# ═══════════════════════════════════════════════════════════
# OK — Variante succès
# ═══════════════════════════════════════════════════════════


@dataclass(frozen=True, slots=True)
class Ok(Result[T, E]):
    """Variante succès du Result."""

    _value: T

    def is_ok(self) -> bool:
        return True

    def is_err(self) -> bool:
        return False

    def ok(self) -> T:
        return self._value

    def err(self) -> None:
        return None

    def unwrap(self) -> T:
        return self._value

    def unwrap_or(self, default: T) -> T:
        return self._value

    def unwrap_or_else(self, fn: Callable[[E], T]) -> T:
        return self._value

    def map(self, fn: Callable[[T], U]) -> Result[U, E]:
        return Ok(fn(self._value))

    def map_err(self, fn: Callable[[E], F]) -> Result[T, F]:
        return Ok(self._value)

    def and_then(self, fn: Callable[[T], Result[U, E]]) -> Result[U, E]:
        return fn(self._value)

    def or_else(self, fn: Callable[[E], Result[T, F]]) -> Result[T, F]:
        return Ok(self._value)

    def on_success(self, fn: Callable[[T], None]) -> Result[T, E]:
        """Exécute fn(value), retourne self même si fn lève."""
        try:
            fn(self._value)
        except Exception as e:
            logger.warning(f"Erreur dans on_success callback: {e}")
        return self

    def on_failure(self, fn: Callable[[E], None]) -> Result[T, E]:
        """Ne fait rien (c'est un succès)."""
        return self

    def recover(self, fn: Callable[[E], T]) -> Result[T, E]:
        """Ne fait rien (c'est déjà un succès)."""
        return self

    def __repr__(self) -> str:
        return f"Ok({self._value!r})"


# ═══════════════════════════════════════════════════════════
# ERR — Variante échec
# ═══════════════════════════════════════════════════════════


@dataclass(frozen=True, slots=True)
class Err(Result[T, E]):
    """Variante échec du Result."""

    _error: E

    def is_ok(self) -> bool:
        return False

    def is_err(self) -> bool:
        return True

    def ok(self) -> None:
        return None

    def err(self) -> E:
        return self._error

    def unwrap(self) -> NoReturn:
        if isinstance(self._error, ErrorInfo):
            raise ValueError(f"[{self._error.code.value}] {self._error.message}")
        raise ValueError(f"Appelé unwrap() sur Err: {self._error}")

    def unwrap_or(self, default: T) -> T:
        return default

    def unwrap_or_else(self, fn: Callable[[E], T]) -> T:
        return fn(self._error)

    def map(self, fn: Callable[[T], U]) -> Result[U, E]:
        return Err(self._error)

    def map_err(self, fn: Callable[[E], F]) -> Result[T, F]:
        return Err(fn(self._error))

    def and_then(self, fn: Callable[[T], Result[U, E]]) -> Result[U, E]:
        return Err(self._error)

    def or_else(self, fn: Callable[[E], Result[T, F]]) -> Result[T, F]:
        try:
            return fn(self._error)
        except Exception as e:
            return Err(
                ErrorInfo(  # type: ignore[arg-type]
                    code=ErrorCode.INTERNAL_ERROR,
                    message=f"Erreur dans or_else: {e}",
                    stack_trace=traceback.format_exc(),
                )
            )

    def on_success(self, fn: Callable[[T], None]) -> Result[T, E]:
        """Ne fait rien (c'est un échec)."""
        return self

    def on_failure(self, fn: Callable[[E], None]) -> Result[T, E]:
        """Exécute fn(error), retourne self même si fn lève."""
        try:
            fn(self._error)
        except Exception as e:
            logger.warning(f"Erreur dans on_failure callback: {e}")
        return self

    def recover(self, fn: Callable[[E], T]) -> Result[T, E]:
        """Tente de récupérer: Success(fn(error)) ou self si fn lève."""
        try:
            return Ok(fn(self._error))
        except Exception:
            return self

    def __repr__(self) -> str:
        return f"Err({self._error!r})"


# ═══════════════════════════════════════════════════════════
# ALIASES COMPATIBILITÉ (Success/Failure)
# ═══════════════════════════════════════════════════════════

Success = Ok
"""Alias de ``Ok`` pour compatibilité avec l'ancienne API services."""

Failure = Err
"""Alias de ``Err`` pour compatibilité avec l'ancienne API services."""


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


# ═══════════════════════════════════════════════════════════
# COMBINATEURS
# ═══════════════════════════════════════════════════════════


def combiner(*results: Result[T, E]) -> Result[list[T], E]:
    """
    Combine plusieurs Results en un seul.

    Retourne Ok(list[T]) si tous sont Ok, sinon la première Err.

    Usage::
        >>> combiner(Ok(1), Ok(2), Ok(3))
        Ok([1, 2, 3])
        >>> combiner(Ok(1), Err("oops"), Ok(3))
        Err('oops')
    """
    valeurs: list[T] = []
    for r in results:
        if r.is_err():
            return Err(r.err())  # type: ignore
        valeurs.append(r.unwrap())
    return Ok(valeurs)


def premier_ok(*results: Result[T, E]) -> Result[T, list[E]]:
    """
    Retourne le premier Ok ou toutes les erreurs.

    Usage::
        >>> premier_ok(Err("a"), Ok(42), Err("b"))
        Ok(42)
        >>> premier_ok(Err("a"), Err("b"))
        Err(['a', 'b'])
    """
    erreurs: list[E] = []
    for r in results:
        if r.is_ok():
            return Ok(r.unwrap())
        erreurs.append(r.err())  # type: ignore
    return Err(erreurs)


def collect(results: list[Result[T, E]]) -> Result[list[T], E]:
    """
    Combine une liste de Result en un seul (variante liste de combiner).

    Si tous sont Ok → Ok(list[T])
    Si un seul est Err → Err(premier échec)
    """
    return combiner(*results)


def collect_all(results: list[Result[T, E]]) -> tuple[list[T], list[E]]:
    """
    Sépare les succès et les échecs sans short-circuit.

    Returns:
        Tuple (succès, échecs)

    Usage::
        successes, failures = collect_all(results)
    """
    successes: list[T] = []
    failures: list[E] = []
    for result in results:
        if result.is_ok():
            successes.append(result.unwrap())
        else:
            failures.append(result.err())  # type: ignore
    return successes, failures


# ═══════════════════════════════════════════════════════════
# MAPPING EXCEPTION → ERROR CODE
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
    Enregistre un mapping exception → ErrorCode.

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
) -> Callable:
    """Décorateur: fonction → Result[T, Exception].

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

    def decorator(func: Callable) -> Callable:
        if inspect.iscoroutinefunction(func):

            @functools.wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Result:
                try:
                    return Ok(await func(*args, **kwargs))
                except exceptions_cibles as e:
                    return Err(e)

            return async_wrapper
        else:

            @functools.wraps(func)
            def sync_wrapper(*args: Any, **kwargs: Any) -> Result:
                try:
                    return Ok(func(*args, **kwargs))
                except exceptions_cibles as e:
                    return Err(e)

            return sync_wrapper

    return decorator


def safe(func: Callable[..., T]) -> Callable[..., Result[T, ErrorInfo]]:
    """Décorateur: fonction → Result[T, ErrorInfo] avec classification auto.

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
) -> Callable:
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
    # Types principaux
    "Result",
    "Ok",
    "Err",
    "ErrorInfo",
    "ErrorCode",
    # Aliases backward compat
    "Success",
    "Failure",
    # Factories
    "success",
    "failure",
    "from_exception",
    # Helpers conversion
    "capturer",
    "capturer_async",
    "depuis_option",
    "depuis_bool",
    # Combinateurs
    "combiner",
    "premier_ok",
    "collect",
    "collect_all",
    # Décorateurs
    "avec_result",
    "safe",
    "result_api",
    # Extension
    "register_error_mapping",
]
