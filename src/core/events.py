"""
Event Bus - Système d'événements inter-modules.

Permet la communication découplée entre modules via
un pattern publish/subscribe (Observer).

Usage:
    >>> from src.core.events import bus_evenements
    >>>
    >>> # Module A: s'abonner
    >>> @bus_evenements.on("recette.creee")
    >>> def on_recette_creee(recette):
    >>>     invalider_cache_recettes()
    >>>
    >>> # Module B: publier
    >>> bus_evenements.emettre("recette.creee", recette=nouvelle_recette)
"""

import logging
import threading
from collections import defaultdict
from collections.abc import Callable
from typing import Any

logger = logging.getLogger(__name__)


class BusEvenements:
    """
    Bus d'événements in-process (synchrone).

    Features:
    - Abonnements par nom d'événement (pattern dotted: "module.action")
    - Wildcards : ``*`` pour un segment, ``**`` pour tous
    - Handlers ordonnés par priorité
    - Gestion d'erreur isolée (un handler qui échoue ne bloque pas les autres)
    """

    def __init__(self) -> None:
        self._handlers: dict[str, list[tuple[int, Callable]]] = defaultdict(list)
        self._lock = threading.RLock()

    def on(
        self,
        evenement: str,
        priorite: int = 0,
    ) -> Callable:
        """
        Décorateur pour s'abonner à un événement.

        Args:
            evenement: Nom de l'événement (ex: "recette.creee")
            priorite: Priorité d'exécution (plus bas = plus tôt)

        Returns:
            Décorateur

        Example:
            >>> @bus.on("inventaire.modifie")
            >>> def recalculer_courses(article):
            >>>     ...
        """

        def decorator(func: Callable) -> Callable:
            self.abonner(evenement, func, priorite)
            return func

        return decorator

    def abonner(
        self,
        evenement: str,
        handler: Callable,
        priorite: int = 0,
    ) -> None:
        """
        Abonne un handler à un événement.

        Args:
            evenement: Nom de l'événement
            handler: Fonction à appeler
            priorite: Priorité d'exécution
        """
        with self._lock:
            self._handlers[evenement].append((priorite, handler))
            # Trier par priorité
            self._handlers[evenement].sort(key=lambda x: x[0])
            logger.debug(f"📡 Handler '{handler.__name__}' abonné à '{evenement}' (p={priorite})")

    def desabonner(self, evenement: str, handler: Callable) -> None:
        """Désabonne un handler d'un événement."""
        with self._lock:
            if evenement in self._handlers:
                self._handlers[evenement] = [
                    (p, h) for p, h in self._handlers[evenement] if h is not handler
                ]

    def emettre(self, evenement: str, **kwargs: Any) -> int:
        """
        Émet un événement.

        Args:
            evenement: Nom de l'événement
            **kwargs: Données transmises aux handlers

        Returns:
            Nombre de handlers exécutés

        Example:
            >>> bus.emettre("recette.creee", recette=ma_recette)
        """
        handlers = self._trouver_handlers(evenement)

        if not handlers:
            logger.debug(f"📡 Événement '{evenement}' émis (0 handlers)")
            return 0

        executes = 0
        for _, handler in handlers:
            try:
                handler(**kwargs)
                executes += 1
            except Exception as e:
                logger.error(f"❌ Erreur handler '{handler.__name__}' " f"pour '{evenement}': {e}")

        logger.debug(f"📡 Événement '{evenement}' émis ({executes}/{len(handlers)} handlers)")
        return executes

    def _trouver_handlers(self, evenement: str) -> list[tuple[int, Callable]]:
        """Trouve tous les handlers correspondants (exacts + wildcards)."""
        with self._lock:
            handlers = list(self._handlers.get(evenement, []))

            # Ajouter les handlers wildcard "**"
            if "**" in self._handlers:
                handlers.extend(self._handlers["**"])

            # Wildcards par segment (ex: "recette.*")
            parts = evenement.split(".")
            for i in range(len(parts)):
                pattern = ".".join(parts[:i] + ["*"])
                if pattern in self._handlers:
                    handlers.extend(self._handlers[pattern])

            # Trier par priorité
            handlers.sort(key=lambda x: x[0])
            return handlers

    def obtenir_statistiques(self) -> dict[str, Any]:
        """Retourne les statistiques du bus."""
        with self._lock:
            return {
                "evenements": list(self._handlers.keys()),
                "total_handlers": sum(len(h) for h in self._handlers.values()),
                "detail": {evt: len(handlers) for evt, handlers in self._handlers.items()},
            }

    def reset(self) -> None:
        """Supprime tous les abonnements (utile pour les tests)."""
        with self._lock:
            self._handlers.clear()
            logger.info("📡 Event bus reset")


# ═══════════════════════════════════════════════════════════
# INSTANCE GLOBALE
# ═══════════════════════════════════════════════════════════

bus_evenements = BusEvenements()
"""Instance globale du bus d'événements."""
