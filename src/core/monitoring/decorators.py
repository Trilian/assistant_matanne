"""
Décorateurs de monitoring — chronométrage automatique des fonctions.

Usage::

    from src.core.monitoring import chronometre

    @chronometre("ia.generation_recettes")
    def generer_recettes(context: str) -> list:
        ...

    # Avec seuil d'alerte (log warning si > 2s)
    @chronometre("db.requete_lourde", seuil_alerte_ms=2000)
    def requete_complexe():
        ...
"""

from __future__ import annotations

import functools
import logging
import time
from typing import Any, Callable, ParamSpec, TypeVar

from .collector import MetriqueType, collecteur

logger = logging.getLogger(__name__)

P = ParamSpec("P")
T = TypeVar("T")


def chronometre(
    nom: str,
    seuil_alerte_ms: float | None = None,
    labels: dict[str, str] | None = None,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Décorateur de chronométrage automatique.

    Enregistre la durée d'exécution en millisecondes comme un
    histogramme dans le collecteur global.  Incrémente aussi un
    compteur ``{nom}.appels`` à chaque invocation.

    Parameters
    ----------
    nom : str
        Nom hiérarchique de la métrique (ex: ``ia.generation``).
    seuil_alerte_ms : float, optional
        Si la durée dépasse ce seuil, un WARNING est loggé.
    labels : dict, optional
        Labels additionnels attachés à chaque point.
    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            start = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                return result
            except Exception:
                collecteur.incrementer(f"{nom}.erreurs", labels=labels)
                raise
            finally:
                duree_ms = (time.perf_counter() - start) * 1000
                collecteur.histogramme(f"{nom}.duree_ms", duree_ms, labels)
                collecteur.incrementer(f"{nom}.appels", labels=labels)

                if seuil_alerte_ms is not None and duree_ms > seuil_alerte_ms:
                    logger.warning(
                        "Alerte performance: %s a pris %.1f ms (seuil: %.0f ms)",
                        nom,
                        duree_ms,
                        seuil_alerte_ms,
                    )

        return wrapper

    return decorator


def chronometre_async(
    nom: str,
    seuil_alerte_ms: float | None = None,
    labels: dict[str, str] | None = None,
) -> Callable:
    """Version asynchrone du décorateur de chronométrage.

    Même API que :func:`chronometre` mais pour les coroutines ``async def``.
    """
    import asyncio

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            start = time.perf_counter()
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception:
                collecteur.incrementer(f"{nom}.erreurs", labels=labels)
                raise
            finally:
                duree_ms = (time.perf_counter() - start) * 1000
                collecteur.histogramme(f"{nom}.duree_ms", duree_ms, labels)
                collecteur.incrementer(f"{nom}.appels", labels=labels)

                if seuil_alerte_ms is not None and duree_ms > seuil_alerte_ms:
                    logger.warning(
                        "Alerte performance: %s a pris %.1f ms (seuil: %.0f ms)",
                        nom,
                        duree_ms,
                        seuil_alerte_ms,
                    )

        return wrapper

    return decorator
