"""
Result ABC — Ok(valeur) | Err(erreur).

Pattern monad style Rust pour gestion explicite des erreurs.

Usage::
    from src.core.result import Ok, Err

    def diviser(a: int, b: int) -> Result[float, str]:
        if b == 0:
            return Err("Division par zéro")
        return Ok(a / b)

    # Pattern matching (Python 3.10+)
    match diviser(10, 2):
        case Ok(v): print(f"Résultat: {v}")
        case Err(e): print(f"Erreur: {e}")
"""

from __future__ import annotations

import logging
import traceback
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from typing import Generic, NoReturn, TypeVar

from .codes import ErrorCode, ErrorInfo

logger = logging.getLogger(__name__)

T = TypeVar("T")  # Type de la valeur OK
E = TypeVar("E")  # Type de l'erreur
U = TypeVar("U")  # Type transformé
F = TypeVar("F")  # Type erreur transformée


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
        try:
            return Ok(fn(self._value))
        except Exception as e:
            return Err(
                ErrorInfo(  # type: ignore[arg-type]
                    code=ErrorCode.INTERNAL_ERROR,
                    message=str(e),
                    stack_trace=traceback.format_exc(),
                )
            )

    def map_err(self, fn: Callable[[E], F]) -> Result[T, F]:
        return Ok(self._value)

    def and_then(self, fn: Callable[[T], Result[U, E]]) -> Result[U, E]:
        try:
            return fn(self._value)
        except Exception as e:
            return Err(
                ErrorInfo(  # type: ignore[arg-type]
                    code=ErrorCode.INTERNAL_ERROR,
                    message=str(e),
                    stack_trace=traceback.format_exc(),
                )
            )

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
            raise ValueError(
                f"Tentative de unwrap sur Failure [{self._error.code.value}]: {self._error.message}"
            )
        raise ValueError(f"Tentative de unwrap sur Failure: {self._error}")

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


__all__ = [
    "Result",
    "Ok",
    "Err",
    "Success",
    "Failure",
]
