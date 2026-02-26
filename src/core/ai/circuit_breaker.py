"""
Circuit Breaker - Protection contre les défaillances de services externes.

Module canonique pour le circuit breaker des services IA (client Mistral,
BaseAIService).  Fournit un registre singleton ``obtenir_circuit()``.

.. note::

    Pour les politiques de résilience composables (retry, timeout, bulkhead,
    fallback), voir ``src.core.resilience.policies``.

Implémente le pattern Circuit Breaker pour:
- Éviter de marteler un service externe en panne
- Reprise automatique progressive (half-open)
- Métriques de santé du circuit

États:
- CLOSED: Fonctionnement normal, les appels passent
- OPEN: Service en panne, les appels sont court-circuités
- HALF_OPEN: Test de reprise (1 appel à la fois)
"""

import asyncio
import inspect
import logging
import threading
import time
from collections.abc import Callable
from enum import StrEnum
from typing import Any, TypeVar

from ..exceptions import ErreurServiceExterne

logger = logging.getLogger(__name__)

__all__ = ["CircuitBreaker", "EtatCircuit", "obtenir_circuit"]

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
            return self._verifier_etat_interne()

    def appeler(self, fn: Callable[[], T], fallback: Callable[[], T] | None = None) -> T:
        """
        Exécute une fonction à travers le circuit breaker.

        Gère automatiquement les coroutines : si ``fn()`` retourne une coroutine,
        elle sera exécutée via ``asyncio.run()`` ou un event loop existant.

        Thread-safe : en état SEMI_OUVERT, un seul appel de test est autorisé
        à la fois ; les appels concurrents reçoivent le fallback ou une erreur.

        Args:
            fn: Fonction à appeler (sync ou async)
            fallback: Fonction de repli si le circuit est ouvert

        Returns:
            Résultat de fn ou du fallback

        Raises:
            ErreurServiceExterne: Si le circuit est ouvert et pas de fallback
        """
        # Vérifier l'état sous verrou pour éviter les TOCTOU
        with self._lock:
            etat = self._verifier_etat_interne()

            if etat == EtatCircuit.OUVERT:
                logger.warning(f"⚡ Circuit '{self.nom}' OUVERT — appel bloqué")
                if fallback:
                    return fallback()
                raise ErreurServiceExterne(
                    f"Circuit '{self.nom}' ouvert (service indisponible)",
                    message_utilisateur="Service temporairement indisponible, veuillez réessayer",
                )

            if etat == EtatCircuit.SEMI_OUVERT:
                # En semi-ouvert, empêcher les appels concurrents :
                # on passe temporairement en OUVERT pour bloquer les autres threads
                # pendant que ce thread teste la reprise.
                self._etat = EtatCircuit.OUVERT
                est_appel_test = True
            else:
                est_appel_test = False

        try:
            result = fn()
            # Gérer les coroutines retournées par des fonctions async
            if inspect.iscoroutine(result):
                try:
                    loop = asyncio.get_running_loop()
                except RuntimeError:
                    loop = None

                if loop and loop.is_running():
                    # Event loop déjà en cours - créer une tâche
                    # Note: cas rare, préférer appeler_async() dans ce contexte
                    import concurrent.futures

                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(asyncio.run, result)
                        result = future.result()
                else:
                    # Pas d'event loop - utiliser asyncio.run()
                    result = asyncio.run(result)

            self._enregistrer_succes()
            return result

        except Exception as e:
            self._enregistrer_echec(est_appel_test=est_appel_test)
            if fallback and self.etat == EtatCircuit.OUVERT:
                logger.info(f"🔄 Circuit '{self.nom}' — utilisation du fallback")
                return fallback()
            raise

    def _verifier_etat_interne(self) -> EtatCircuit:
        """Vérifie et met à jour l'état interne (appelé sous self._lock)."""
        if self._etat == EtatCircuit.OUVERT:
            if time.time() - self._derniere_ouverture >= self.delai_reset:
                self._etat = EtatCircuit.SEMI_OUVERT
                logger.info(f"🔄 Circuit '{self.nom}' → SEMI_OUVERT (test de reprise)")
        return self._etat

    def _enregistrer_succes(self):
        """Enregistre un appel réussi."""
        with self._lock:
            self._succes_total += 1
            self._echecs_consecutifs = 0
            if self._etat in (EtatCircuit.SEMI_OUVERT, EtatCircuit.OUVERT):
                self._etat = EtatCircuit.FERME
                logger.info(f"✅ Circuit '{self.nom}' → FERMÉ (reprise confirmée)")

    def _enregistrer_echec(self, *, est_appel_test: bool = False):
        """Enregistre un échec."""
        with self._lock:
            self._echecs_total += 1
            self._echecs_consecutifs += 1

            if est_appel_test:
                # L'appel de test en semi-ouvert a échoué → rester ouvert
                self._etat = EtatCircuit.OUVERT
                self._derniere_ouverture = time.time()
                logger.warning(f"🔴 Circuit '{self.nom}' — test de reprise échoué, reste OUVERT")
            elif self._echecs_consecutifs >= self.seuil_echecs:
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

    async def appeler_async(
        self, fn: Callable[..., Any], fallback: Callable[[], T] | None = None
    ) -> T:
        """
        Exécute une coroutine à travers le circuit breaker.

        Thread-safe : même logique que ``appeler()`` pour le SEMI_OUVERT.

        Args:
            fn: Coroutine function à appeler (sera awaitée)
            fallback: Fonction de repli si le circuit est ouvert

        Returns:
            Résultat de fn ou du fallback

        Raises:
            ErreurServiceExterne: Si le circuit est ouvert et pas de fallback
        """
        with self._lock:
            etat = self._verifier_etat_interne()

            if etat == EtatCircuit.OUVERT:
                logger.warning(f"⚡ Circuit '{self.nom}' OUVERT — appel bloqué")
                if fallback:
                    return fallback()
                raise ErreurServiceExterne(
                    f"Circuit '{self.nom}' ouvert (service indisponible)",
                    message_utilisateur="Service temporairement indisponible, veuillez réessayer",
                )

            if etat == EtatCircuit.SEMI_OUVERT:
                self._etat = EtatCircuit.OUVERT
                est_appel_test = True
            else:
                est_appel_test = False

        try:
            result = await fn()
            self._enregistrer_succes()
            return result

        except Exception as e:
            self._enregistrer_echec(est_appel_test=est_appel_test)
            if fallback and self.etat == EtatCircuit.OUVERT:
                logger.info(f"🔄 Circuit '{self.nom}' — utilisation du fallback")
                return fallback()
            raise

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
