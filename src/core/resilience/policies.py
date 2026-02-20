"""
Policies - Stratégies de résilience individuelles et composables.
"""

from __future__ import annotations

import logging
import random
import threading
import time
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FuturesTimeoutError
from dataclasses import dataclass, field
from typing import Any, Callable, Generic, TypeVar

from ..result import Err, Ok, Result

logger = logging.getLogger(__name__)

T = TypeVar("T")


class Policy(ABC, Generic[T]):
    """Politique de résilience abstraite."""

    @abstractmethod
    def executer(self, fn: Callable[[], T]) -> Result[T, Exception]:
        """Exécute fn avec la politique appliquée."""
        ...

    def __add__(self, other: Policy[T]) -> PolicyComposee[T]:
        """Compose deux policies: self puis other."""
        if isinstance(other, PolicyComposee):
            return PolicyComposee([self, *other.policies])
        return PolicyComposee([self, other])

    def __radd__(self, other: Policy[T]) -> PolicyComposee[T]:
        """Support addition inversée."""
        if isinstance(other, PolicyComposee):
            return PolicyComposee([*other.policies, self])
        return PolicyComposee([other, self])


@dataclass
class RetryPolicy(Policy[T]):
    """
    Politique de retentatives avec backoff exponentiel.

    Args:
        max_tentatives: Nombre max de tentatives (défaut: 3)
        delai_base: Délai initial en secondes (défaut: 1.0)
        facteur_backoff: Multiplicateur entre tentatives (défaut: 2.0)
        jitter: Ajouter du bruit aléatoire pour éviter thundering herd (défaut: True)
        exceptions_a_retry: Types d'exceptions à retenter (toutes si vide)

    Usage::
        policy = RetryPolicy(max_tentatives=3, delai_base=1.0)
        result = policy.executer(lambda: unstable_api.call())
    """

    max_tentatives: int = 3
    delai_base: float = 1.0
    facteur_backoff: float = 2.0
    jitter: bool = True
    exceptions_a_retry: tuple[type[Exception], ...] = field(default_factory=tuple)

    def executer(self, fn: Callable[[], T]) -> Result[T, Exception]:
        derniere_exception: Exception | None = None

        for tentative in range(self.max_tentatives):
            try:
                return Ok(fn())
            except Exception as e:
                # Vérifier si on doit retenter cette exception
                if self.exceptions_a_retry and not isinstance(e, self.exceptions_a_retry):
                    return Err(e)

                derniere_exception = e

                if tentative < self.max_tentatives - 1:
                    delai = self.delai_base * (self.facteur_backoff**tentative)
                    if self.jitter:
                        delai *= 0.5 + random.random()

                    logger.warning(
                        f"[Retry] Tentative {tentative + 1}/{self.max_tentatives} "
                        f"échouée, retry dans {delai:.2f}s: {e}"
                    )
                    time.sleep(delai)

        return Err(derniere_exception or Exception("Échec après toutes les tentatives"))


@dataclass
class TimeoutPolicy(Policy[T]):
    """
    Politique de timeout.

    Args:
        timeout_secondes: Durée max d'exécution (défaut: 30.0)

    Usage::
        policy = TimeoutPolicy(timeout_secondes=10.0)
        result = policy.executer(lambda: slow_operation())
    """

    timeout_secondes: float = 30.0

    def executer(self, fn: Callable[[], T]) -> Result[T, Exception]:
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(fn)
            try:
                result = future.result(timeout=self.timeout_secondes)
                return Ok(result)
            except FuturesTimeoutError:
                future.cancel()
                return Err(TimeoutError(f"Timeout après {self.timeout_secondes}s"))
            except Exception as e:
                return Err(e)


@dataclass
class BulkheadPolicy(Policy[T]):
    """
    Politique d'isolation (bulkhead pattern).

    Limite le nombre d'exécutions concurrentes pour protéger
    les ressources partagées et éviter l'épuisement.

    Args:
        max_concurrent: Nombre max d'exécutions simultanées (défaut: 10)
        timeout_acquisition: Temps max pour obtenir un slot (défaut: 5.0)

    Usage::
        policy = BulkheadPolicy(max_concurrent=5)
        result = policy.executer(lambda: expensive_operation())
    """

    max_concurrent: int = 10
    timeout_acquisition: float = 5.0
    _semaphore: threading.Semaphore = field(init=False, repr=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "_semaphore", threading.Semaphore(self.max_concurrent))

    def executer(self, fn: Callable[[], T]) -> Result[T, Exception]:
        acquired = self._semaphore.acquire(timeout=self.timeout_acquisition)
        if not acquired:
            return Err(
                RuntimeError(
                    f"Bulkhead saturé ({self.max_concurrent} exécutions en cours), "
                    f"impossible d'acquérir un slot après {self.timeout_acquisition}s"
                )
            )

        try:
            return Ok(fn())
        except Exception as e:
            return Err(e)
        finally:
            self._semaphore.release()


@dataclass
class FallbackPolicy(Policy[T]):
    """
    Politique de fallback.

    Retourne une valeur de repli en cas d'échec.

    Args:
        fallback_value: Valeur à retourner en cas d'erreur
        fallback_fn: Ou fonction pour générer la valeur (reçoit l'exception)
        log_erreur: Logger l'erreur originale (défaut: True)

    Usage::
        policy = FallbackPolicy(fallback_value=[])
        result = policy.executer(lambda: fetch_items())

        # Avec fonction
        policy = FallbackPolicy(fallback_fn=lambda e: {"error": str(e)})
    """

    fallback_value: T | None = None
    fallback_fn: Callable[[Exception], T] | None = None
    log_erreur: bool = True

    def executer(self, fn: Callable[[], T]) -> Result[T, Exception]:
        try:
            return Ok(fn())
        except Exception as e:
            if self.log_erreur:
                logger.warning(f"[Fallback] Erreur capturée, utilisation fallback: {e}")

            if self.fallback_fn:
                try:
                    return Ok(self.fallback_fn(e))
                except Exception as fallback_error:
                    return Err(fallback_error)

            if self.fallback_value is not None:
                return Ok(self.fallback_value)

            return Err(e)


@dataclass
class PolicyComposee(Policy[T]):
    """
    Composition de plusieurs policies.

    Les policies sont exécutées dans l'ordre (première → dernière),
    chaque policy enrobant la suivante (onion model).

    Usage::
        policy = PolicyComposee([
            TimeoutPolicy(30),
            RetryPolicy(3),
            BulkheadPolicy(5),
        ])
    """

    policies: list[Policy[Any]]

    def executer(self, fn: Callable[[], T]) -> Result[T, Exception]:
        """Exécute la chaîne de policies."""
        if not self.policies:
            try:
                return Ok(fn())
            except Exception as e:
                return Err(e)

        # Construire la chaîne de l'intérieur vers l'extérieur
        def make_wrapper(p: Policy[Any], f: Callable[[], T]) -> Callable[[], T]:
            def wrapper() -> T:
                result = p.executer(f)
                if result.is_err():
                    raise result.err()  # type: ignore
                return result.unwrap()

            return wrapper

        wrapped_fn = fn
        for policy in reversed(self.policies):
            wrapped_fn = make_wrapper(policy, wrapped_fn)

        try:
            return Ok(wrapped_fn())
        except Exception as e:
            return Err(e)

    def __add__(self, other: Policy[T]) -> PolicyComposee[T]:
        if isinstance(other, PolicyComposee):
            return PolicyComposee(self.policies + other.policies)
        return PolicyComposee(self.policies + [other])

    def __repr__(self) -> str:
        noms = [p.__class__.__name__ for p in self.policies]
        return f"PolicyComposee({noms})"


# ═══════════════════════════════════════════════════════════
# FACTORIES POUR POLICIES COURANTES
# ═══════════════════════════════════════════════════════════


def politique_api_externe() -> PolicyComposee[Any]:
    """
    Policy optimisée pour appels API externes.

    Combine: Timeout(30s) → Retry(3x, backoff) → Bulkhead(5 concurrent)
    """
    return PolicyComposee(
        [
            TimeoutPolicy(timeout_secondes=30.0),
            RetryPolicy(max_tentatives=3, delai_base=1.0, jitter=True),
            BulkheadPolicy(max_concurrent=5),
        ]
    )


def politique_base_de_donnees() -> PolicyComposee[Any]:
    """
    Policy optimisée pour requêtes base de données.

    Combine: Timeout(10s) → Retry(2x, délai court)
    """
    return PolicyComposee(
        [
            TimeoutPolicy(timeout_secondes=10.0),
            RetryPolicy(max_tentatives=2, delai_base=0.5, jitter=False),
        ]
    )


def politique_cache() -> PolicyComposee[Any]:
    """
    Policy pour accès cache (rapide, avec fallback None).

    Combine: Timeout(1s) → Fallback(None)
    """
    return PolicyComposee(
        [
            TimeoutPolicy(timeout_secondes=1.0),
            FallbackPolicy(fallback_value=None, log_erreur=False),
        ]
    )


def politique_ia() -> PolicyComposee[Any]:
    """
    Policy pour appels IA (Mistral).

    Combine: Timeout(60s) → Retry(3x, backoff long) → Bulkhead(3 concurrent)
    """
    return PolicyComposee(
        [
            TimeoutPolicy(timeout_secondes=60.0),
            RetryPolicy(max_tentatives=3, delai_base=2.0, facteur_backoff=3.0, jitter=True),
            BulkheadPolicy(max_concurrent=3, timeout_acquisition=30.0),
        ]
    )


__all__ = [
    "Policy",
    "RetryPolicy",
    "TimeoutPolicy",
    "BulkheadPolicy",
    "FallbackPolicy",
    "PolicyComposee",
    "politique_api_externe",
    "politique_base_de_donnees",
    "politique_cache",
    "politique_ia",
]
