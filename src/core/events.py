"""
Event Bus - Pont rétrocompatible vers le bus d'événements unifié.

Le bus canonique est dans src.services.core.events.bus (API typée,
wildcards, historique, métriques, dataclass EvenementDomaine).

Ce module maintient l'ancienne API kwargs pour la rétrocompatibilité :
    >>> from src.core.events import bus_evenements
    >>> bus_evenements.emettre("recette.creee", recette=nouvelle_recette)

Nouveau code doit utiliser directement :
    >>> from src.services.core.events.bus import obtenir_bus
    >>> obtenir_bus().emettre("recette.creee", {"recette": nouvelle_recette})

.. deprecated::
    L'import depuis ``src.core.events`` est déprécié.
    Utiliser ``src.services.core.events.bus`` à la place.
"""

from __future__ import annotations

import logging
import warnings
from collections.abc import Callable
from typing import Any

logger = logging.getLogger(__name__)


class _BusEvenementsProxy:
    """
    Proxy rétrocompatible qui délègue au bus canonique.

    Traduit l'ancienne API kwargs (``emettre("type", **kwargs)``)
    vers la nouvelle API dict (``emettre("type", data_dict)``).
    """

    def __init__(self) -> None:
        self._warned = False

    def _warn_deprecated(self) -> None:
        if not self._warned:
            warnings.warn(
                "src.core.events.bus_evenements est déprécié. "
                "Utiliser src.services.core.events.bus.obtenir_bus() à la place.",
                DeprecationWarning,
                stacklevel=3,
            )
            self._warned = True

    @property
    def _bus(self):
        """Accès lazy au bus canonique pour éviter les imports circulaires."""
        from src.services.core.events.bus import obtenir_bus

        return obtenir_bus()

    def on(self, evenement: str, priorite: int = 0) -> Callable:
        """Décorateur pour s'abonner (rétrocompatible)."""
        self._warn_deprecated()

        def decorator(func: Callable) -> Callable:
            # Adapter le handler kwargs vers le handler EvenementDomaine
            def _adapted_handler(event):
                try:
                    func(**event.data)
                except TypeError:
                    func(event)

            self._bus.souscrire(evenement, _adapted_handler, priority=priorite)
            return func

        return decorator

    def abonner(self, evenement: str, handler: Callable, priorite: int = 0) -> None:
        """Abonne un handler (rétrocompatible)."""
        self._warn_deprecated()

        def _adapted_handler(event):
            try:
                handler(**event.data)
            except TypeError:
                handler(event)

        self._bus.souscrire(evenement, _adapted_handler, priority=priorite)

    def desabonner(self, evenement: str, handler: Callable) -> None:
        """Désabonne un handler."""
        self._warn_deprecated()
        self._bus.desouscrire(evenement, handler)

    def emettre(self, evenement: str, **kwargs: Any) -> int:
        """
        Émet un événement (rétrocompatible).

        Traduit ``emettre("type", key=val)`` vers ``emettre("type", {"key": val})``.
        """
        self._warn_deprecated()
        return self._bus.emettre(evenement, kwargs, source="core.events.proxy")

    def obtenir_statistiques(self) -> dict[str, Any]:
        """Retourne les statistiques du bus."""
        return self._bus.obtenir_metriques()

    def reset(self) -> None:
        """Réinitialise le bus."""
        self._bus.reinitialiser()


# ═══════════════════════════════════════════════════════════
# INSTANCE GLOBALE (PROXY — rétrocompatible)
# ═══════════════════════════════════════════════════════════

bus_evenements = _BusEvenementsProxy()
"""Instance proxy rétrocompatible du bus d'événements."""

# Re-exports pour transition douce
BusEvenements = _BusEvenementsProxy
