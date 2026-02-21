"""
Circuit Breaker - Protection contre les défaillances de services externes.

.. deprecated:: 2026.02
    Préférer ``src.core.resilience.policies`` pour les nouvelles intégrations.
    Ce module est conservé pour compatibilité avec le client IA existant.
    Voir :class:`src.core.resilience.RetryPolicy` et
    :class:`src.core.resilience.FallbackPolicy` pour les alternatives composables.

Implémente le pattern Circuit Breaker pour:
- Éviter de marteler un service externe en panne
- Reprise automatique progressive (half-open)
- Métriques de santé du circuit

États:
- CLOSED: Fonctionnement normal, les appels passent
- OPEN: Service en panne, les appels sont court-circuités
- HALF_OPEN: Test de reprise (1 appel à la fois)
"""

import logging
import threading
import time
from collections.abc import Callable
from enum import StrEnum
from functools import wraps
from typing import Any, TypeVar

from ..errors_base import ErreurServiceExterne

logger = logging.getLogger(__name__)

__all__ = ["CircuitBreaker", "EtatCircuit", "obtenir_circuit", "avec_circuit_breaker"]

T = TypeVar("T")


class EtatCircuit(StrEnum):
    """États du circuit breaker."""

    FERME = "closed"
    OUVERT = "open"
    SEMI_OUVERT = "half_open"


class CircuitBreaker:
    """
    Circuit Breaker configurable.

    Args:
        nom: Nom du circuit (pour les logs)
        seuil_echecs: Nombre d'échecs avant ouverture
        delai_reset: Secondes avant de passer en semi-ouvert
        timeout: Timeout par appel en secondes

    Example:
        >>> cb = CircuitBreaker("mistral_api", seuil_echecs=5, delai_reset=60)
        >>> result = cb.appeler(lambda: client.chat("prompt"))
    """

    def __init__(
        self,
        nom: str,
        seuil_echecs: int = 5,
        delai_reset: float = 60.0,
        timeout: float | None = None,
    ):
        self.nom = nom
        self.seuil_echecs = seuil_echecs
        self.delai_reset = delai_reset
        self.timeout = timeout

        self._etat = EtatCircuit.FERME
        self._echecs_consecutifs = 0
        self._derniere_ouverture: float = 0.0
        self._succes_total = 0
        self._echecs_total = 0
        self._lock = threading.RLock()

    @property
    def etat(self) -> EtatCircuit:
        """État actuel du circuit."""
        with self._lock:
            if self._etat == EtatCircuit.OUVERT:
                # Vérifier si le délai de reset est passé
                if time.time() - self._derniere_ouverture >= self.delai_reset:
                    self._etat = EtatCircuit.SEMI_OUVERT
                    logger.info(f"🔄 Circuit '{self.nom}' → SEMI_OUVERT (test de reprise)")
            return self._etat

    def appeler(self, fn: Callable[[], T], fallback: Callable[[], T] | None = None) -> T:
        """
        Exécute une fonction à travers le circuit breaker.

        Args:
            fn: Fonction à appeler
            fallback: Fonction de repli si le circuit est ouvert

        Returns:
            Résultat de fn ou du fallback

        Raises:
            ErreurServiceExterne: Si le circuit est ouvert et pas de fallback
        """
        etat = self.etat

        if etat == EtatCircuit.OUVERT:
            logger.warning(f"⚡ Circuit '{self.nom}' OUVERT — appel bloqué")
            if fallback:
                return fallback()
            raise ErreurServiceExterne(
                f"Circuit '{self.nom}' ouvert (service indisponible)",
                message_utilisateur="Service temporairement indisponible, veuillez réessayer",
            )

        try:
            result = fn()
            self._enregistrer_succes()
            return result

        except Exception as e:
            self._enregistrer_echec()
            if fallback and self.etat == EtatCircuit.OUVERT:
                logger.info(f"🔄 Circuit '{self.nom}' — utilisation du fallback")
                return fallback()
            raise

    def _enregistrer_succes(self):
        """Enregistre un appel réussi."""
        with self._lock:
            self._succes_total += 1
            self._echecs_consecutifs = 0
            if self._etat == EtatCircuit.SEMI_OUVERT:
                self._etat = EtatCircuit.FERME
                logger.info(f"✅ Circuit '{self.nom}' → FERMÉ (reprise confirmée)")

    def _enregistrer_echec(self):
        """Enregistre un échec."""
        with self._lock:
            self._echecs_total += 1
            self._echecs_consecutifs += 1

            if self._echecs_consecutifs >= self.seuil_echecs:
                self._etat = EtatCircuit.OUVERT
                self._derniere_ouverture = time.time()
                logger.error(
                    f"🔴 Circuit '{self.nom}' → OUVERT "
                    f"({self._echecs_consecutifs} échecs consécutifs)"
                )

    def obtenir_statistiques(self) -> dict[str, Any]:
        """Retourne les métriques du circuit."""
        with self._lock:
            return {
                "nom": self.nom,
                "etat": self.etat.value,
                "echecs_consecutifs": self._echecs_consecutifs,
                "seuil_echecs": self.seuil_echecs,
                "succes_total": self._succes_total,
                "echecs_total": self._echecs_total,
                "delai_reset": self.delai_reset,
            }

    def reset(self):
        """Reset manuel du circuit breaker."""
        with self._lock:
            self._etat = EtatCircuit.FERME
            self._echecs_consecutifs = 0
            logger.info(f"🔄 Circuit '{self.nom}' reset manuellement → FERMÉ")


# ═══════════════════════════════════════════════════════════
# REGISTRE GLOBAL DES CIRCUITS
# ═══════════════════════════════════════════════════════════

_circuits: dict[str, CircuitBreaker] = {}
_circuits_lock = threading.Lock()


def obtenir_circuit(
    nom: str,
    seuil_echecs: int = 5,
    delai_reset: float = 60.0,
) -> CircuitBreaker:
    """
    Obtient ou crée un circuit breaker nommé.

    Args:
        nom: Nom unique du circuit
        seuil_echecs: Seuil d'échecs avant ouverture
        delai_reset: Délai de reset en secondes

    Returns:
        Instance CircuitBreaker (singleton par nom)
    """
    with _circuits_lock:
        if nom not in _circuits:
            _circuits[nom] = CircuitBreaker(
                nom=nom,
                seuil_echecs=seuil_echecs,
                delai_reset=delai_reset,
            )
        return _circuits[nom]


def avec_circuit_breaker(
    nom: str = "default",
    seuil_echecs: int = 5,
    delai_reset: float = 60.0,
    fallback: Callable | None = None,
):
    """
    Décorateur Circuit Breaker.

    Args:
        nom: Nom du circuit
        seuil_echecs: Seuil d'échecs
        delai_reset: Délai de reset
        fallback: Fonction de repli

    Example:
        >>> @avec_circuit_breaker("mistral", seuil_echecs=3, delai_reset=30)
        >>> async def appeler_mistral(prompt: str) -> str:
        >>>     return await client.chat(prompt)
    """

    def decorator(func):
        cb = obtenir_circuit(nom, seuil_echecs, delai_reset)

        @wraps(func)
        def wrapper(*args, **kwargs):
            return cb.appeler(
                fn=lambda: func(*args, **kwargs),
                fallback=fallback,
            )

        return wrapper

    return decorator
