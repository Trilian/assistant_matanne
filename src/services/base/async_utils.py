"""
Utilitaires async/sync pour les services.

Fournit des helpers pour convertir des méthodes async en méthodes sync,
utile pour l'intégration avec Streamlit qui ne supporte pas nativement async.
"""

import asyncio
import concurrent.futures
import functools
import logging
from collections.abc import Awaitable, Callable
from typing import Any, ParamSpec, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")
P = ParamSpec("P")


def sync_wrapper(async_method: Callable[P, Awaitable[T]]) -> Callable[P, T]:
    """
    Décorateur qui crée automatiquement une version synchrone d'une méthode async.

    Gère intelligemment les cas où une boucle d'événements est déjà en cours
    (comme dans certains contextes Streamlit) en utilisant un ThreadPoolExecutor.

    Args:
        async_method: La méthode async à wrapper

    Returns:
        Une fonction sync qui exécute la méthode async

    Usage:
        class MyService:
            async def call_api(self, prompt: str) -> str:
                ...

            # Crée automatiquement la version sync
            call_api_sync = sync_wrapper(call_api)

    Note:
        Le nom de la méthode wrappée est préservé via functools.wraps
    """

    @functools.wraps(async_method)
    def sync_method(*args: P.args, **kwargs: P.kwargs) -> T:
        # Essayer d'obtenir la boucle courante
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        # Créer la coroutine
        coro = async_method(*args, **kwargs)

        if loop is not None:
            # Si une boucle d'événements est en cours, utiliser un thread séparé
            logger.debug(
                f"Event loop détectée, exécution de {async_method.__name__} dans un thread..."
            )
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(asyncio.run, coro)
                return future.result()  # type: ignore[return-value]

        # Pas de boucle d'événements, créer une nouvelle et exécuter
        return asyncio.run(coro)  # type: ignore[return-value]

    return sync_method


def make_sync_alias(
    async_method: Callable[P, Awaitable[T]], suffix: str = "_sync"
) -> Callable[P, T]:
    """
    Variante de sync_wrapper qui permet de personnaliser le suffixe.

    Args:
        async_method: La méthode async à wrapper
        suffix: Suffixe à ajouter au nom (défaut: "_sync")

    Returns:
        Une fonction sync avec le nom modifié
    """
    sync_fn = sync_wrapper(async_method)
    sync_fn.__name__ = f"{async_method.__name__}{suffix}"
    sync_fn.__qualname__ = f"{async_method.__qualname__}{suffix}"
    return sync_fn


__all__ = ["sync_wrapper", "make_sync_alias"]
