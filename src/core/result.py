"""
Result Monad - Gestion explicite des succès/échecs.

Élimine les exceptions implicites et rend le code auto-documenté.
Inspiré de Rust Result<T, E> et functional programming.

Usage::
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
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable, Generic, NoReturn, TypeVar

if TYPE_CHECKING:
    from collections.abc import Awaitable

T = TypeVar("T")  # Type de la valeur OK
E = TypeVar("E")  # Type de l'erreur
U = TypeVar("U")  # Type transformé
F = TypeVar("F")  # Type erreur transformée


class Result(ABC, Generic[T, E]):
    """
    Type Result abstrait — soit Ok(valeur) soit Err(erreur).

    Permet une gestion explicite des erreurs sans exceptions,
    avec chaînage fonctionnel (map, and_then, or_else).
    """

    __slots__ = ()

    @abstractmethod
    def is_ok(self) -> bool:
        """Retourne True si c'est un Ok."""
        ...

    @abstractmethod
    def is_err(self) -> bool:
        """Retourne True si c'est un Err."""
        ...

    @abstractmethod
    def ok(self) -> T | None:
        """Retourne la valeur si Ok, sinon None."""
        ...

    @abstractmethod
    def err(self) -> E | None:
        """Retourne l'erreur si Err, sinon None."""
        ...

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

    def __bool__(self) -> bool:
        """Permet `if result:` comme raccourci pour `if result.is_ok():`."""
        return self.is_ok()


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

    def __repr__(self) -> str:
        return f"Ok({self._value!r})"


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
        return fn(self._error)

    def __repr__(self) -> str:
        return f"Err({self._error!r})"


# ═══════════════════════════════════════════════════════════
# HELPERS POUR CONVERSION DEPUIS EXCEPTIONS
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


# ═══════════════════════════════════════════════════════════
# DÉCORATEUR — Transformation automatique en Result
# ═══════════════════════════════════════════════════════════

import functools
import inspect


def avec_result(
    *exceptions: type[Exception],
) -> Callable:
    """Décorateur qui transforme une fonction en version Result.

    La fonction décorée ne lève plus d'exception — elle retourne
    ``Ok(valeur)`` en cas de succès ou ``Err(exception)`` si une
    exception survient.

    Args:
        *exceptions: Types d'exceptions à capturer.
                     Par défaut, capture ``Exception``.

    Usage::

        @avec_result(ValueError, TypeError)
        def diviser(a: int, b: int) -> float:
            return a / b

        result = diviser(10, 0)  # Err(ZeroDivisionError(...))
        result = diviser(10, 2)  # Ok(5.0)

        # Version async supportée aussi
        @avec_result(httpx.HTTPError)
        async def fetch(url: str) -> str:
            async with httpx.AsyncClient() as c:
                r = await c.get(url)
                return r.text
    """
    exceptions_cibles = exceptions or (Exception,)

    def decorator(func: Callable) -> Callable:
        if inspect.iscoroutinefunction(func):

            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs) -> Result:
                try:
                    valeur = await func(*args, **kwargs)
                    return Ok(valeur)
                except exceptions_cibles as e:
                    return Err(e)

            return async_wrapper
        else:

            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs) -> Result:
                try:
                    valeur = func(*args, **kwargs)
                    return Ok(valeur)
                except exceptions_cibles as e:
                    return Err(e)

            return sync_wrapper

    return decorator


__all__ = [
    "Result",
    "Ok",
    "Err",
    "capturer",
    "capturer_async",
    "depuis_option",
    "depuis_bool",
    "combiner",
    "premier_ok",
    "avec_result",
]
