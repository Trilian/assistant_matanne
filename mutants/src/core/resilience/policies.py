"""
Policies - Stratégies de résilience individuelles et composables.

Chaque policy exécute une fonction et retourne le résultat directement.
En cas d'échec, l'exception est propagée (pas de wrapper Result).
"""

from __future__ import annotations

import atexit
import logging
import random
import threading
import time
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FuturesTimeoutError
from dataclasses import dataclass, field
from typing import Any, Callable, Generic, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


class Policy(ABC, Generic[T]):
    """Politique de résilience abstraite."""

    @abstractmethod
    def executer(self, fn: Callable[[], T]) -> T:
        """Exécute fn avec la politique appliquée. Lève une exception en cas d'échec."""
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

    def executer(self, fn: Callable[[], T]) -> T:
        derniere_exception: Exception | None = None

        for tentative in range(self.max_tentatives):
            try:
                return fn()
            except Exception as e:
                # Vérifier si on doit retenter cette exception
                if self.exceptions_a_retry and not isinstance(e, self.exceptions_a_retry):
                    raise

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

        raise derniere_exception or Exception("Échec après toutes les tentatives")


# Shared executor pour TimeoutPolicy (évite la création par appel)
_TIMEOUT_EXECUTOR: ThreadPoolExecutor | None = None
_TIMEOUT_EXECUTOR_LOCK = threading.Lock()


def _get_timeout_executor() -> ThreadPoolExecutor:
    """Retourne l'executor partagé pour TimeoutPolicy (lazy singleton)."""
    global _TIMEOUT_EXECUTOR
    if _TIMEOUT_EXECUTOR is None:
        with _TIMEOUT_EXECUTOR_LOCK:
            if _TIMEOUT_EXECUTOR is None:
                _TIMEOUT_EXECUTOR = ThreadPoolExecutor(
                    max_workers=4, thread_name_prefix="timeout-policy"
                )
                atexit.register(_shutdown_timeout_executor)
    return _TIMEOUT_EXECUTOR


def _shutdown_timeout_executor() -> None:
    """Cleanup propre du ThreadPoolExecutor à la sortie du processus."""
    global _TIMEOUT_EXECUTOR
    if _TIMEOUT_EXECUTOR is not None:
        logger.debug("[Resilience] Shutdown timeout executor")
        _TIMEOUT_EXECUTOR.shutdown(wait=False)
        _TIMEOUT_EXECUTOR = None


@dataclass
class TimeoutPolicy(Policy[T]):
    """
    Politique de timeout.

    Utilise un ThreadPoolExecutor partagé pour éviter la surcharge.

    Args:
        timeout_secondes: Durée max d'exécution (défaut: 30.0)

    Usage::
        policy = TimeoutPolicy(timeout_secondes=10.0)
        result = policy.executer(lambda: slow_operation())
    """

    timeout_secondes: float = 30.0

    def executer(self, fn: Callable[[], T]) -> T:
        executor = _get_timeout_executor()
        future = executor.submit(fn)
        try:
            return future.result(timeout=self.timeout_secondes)
        except FuturesTimeoutError:
            future.cancel()
            raise TimeoutError(f"Timeout après {self.timeout_secondes}s")


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

    def executer(self, fn: Callable[[], T]) -> T:
        acquired = self._semaphore.acquire(timeout=self.timeout_acquisition)
        if not acquired:
            raise RuntimeError(
                f"Bulkhead saturé ({self.max_concurrent} exécutions en cours), "
                f"impossible d'acquérir un slot après {self.timeout_acquisition}s"
            )

        try:
            return fn()
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

    def executer(self, fn: Callable[[], T]) -> T:
        try:
            return fn()
        except Exception as e:
            if self.log_erreur:
                logger.warning(f"[Fallback] Erreur capturée, utilisation fallback: {e}")

            if self.fallback_fn:
                return self.fallback_fn(e)

            if self.fallback_value is not None:
                return self.fallback_value

            raise


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

    def executer(self, fn: Callable[[], T]) -> T:
        """Exécute la chaîne de policies (préserve les tracebacks)."""
        if not self.policies:
            return fn()

        # Construire la chaîne de l'intérieur vers l'extérieur
        wrapped_fn = fn
        for policy in reversed(self.policies):
            # Capture en closure
            wrapped_fn = _make_policy_wrapper(policy, wrapped_fn)

        return wrapped_fn()

    def __add__(self, other: Policy[T]) -> PolicyComposee[T]:
        if isinstance(other, PolicyComposee):
            return PolicyComposee(self.policies + other.policies)
        return PolicyComposee(self.policies + [other])

    def __repr__(self) -> str:
        noms = [p.__class__.__name__ for p in self.policies]
        return f"PolicyComposee({noms})"


def _make_policy_wrapper(p: Policy[Any], f: Callable[[], Any]) -> Callable[[], Any]:
    """Crée un wrapper qui applique une policy sur une fonction."""

    def wrapper() -> Any:
        return p.executer(f)

    return wrapper


__all__ = [
    "Policy",
    "RetryPolicy",
    "TimeoutPolicy",
    "BulkheadPolicy",
    "FallbackPolicy",
    "PolicyComposee",
]
