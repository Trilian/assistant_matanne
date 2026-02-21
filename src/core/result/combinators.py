"""
Combinateurs Result — Composition et agrégation.

Usage::
    from src.core.result import combiner, collect, premier_ok, collect_all

    # Combiner plusieurs Results
    result = combiner(Ok(1), Ok(2), Ok(3))  # Ok([1, 2, 3])

    # Premier succès
    result = premier_ok(try_source_a(), try_source_b())
"""

from __future__ import annotations

from typing import TypeVar

from .base import Err, Ok, Result

T = TypeVar("T")
E = TypeVar("E")


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


__all__ = [
    "combiner",
    "premier_ok",
    "collect",
    "collect_all",
]
