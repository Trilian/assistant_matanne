"""
Utilitaires async/sync pour les services.

Fournit des helpers pour convertir des méthodes async en méthodes sync,
utile pour l'intégration avec Streamlit qui ne supporte pas nativement async.

Features:
- sync_wrapper: Décorateur pour créer une version sync d'une méthode async
- ServiceMeta: Metaclass qui génère automatiquement les méthodes _sync
- @dual_api: Décorateur de classe pour activer le dual API async/sync
"""

from __future__ import annotations

import asyncio
import concurrent.futures
import functools
import inspect
import logging
from collections.abc import Awaitable, Callable
from typing import Any, ParamSpec, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")
P = ParamSpec("P")


# ═══════════════════════════════════════════════════════════
# CONFIGURATION — Méthodes à exclure de la génération sync
# ═══════════════════════════════════════════════════════════

# Préfixes de méthodes à ignorer (méthodes privées, dunder)
_IGNORED_PREFIXES = ("_", "__")

# Méthodes spécifiques à ignorer (ne pas générer de version sync)
_IGNORED_METHODS = frozenset(
    {
        "aclose",
        "aiter",
        "anext",
        "__aenter__",
        "__aexit__",
        "__aiter__",
        "__anext__",
    }
)


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


# ═══════════════════════════════════════════════════════════
# SERVICE META — Metaclass pour génération automatique sync
# ═══════════════════════════════════════════════════════════


class ServiceMeta(type):
    """
    Metaclass qui génère automatiquement les versions synchrones
    des méthodes async d'un service.

    Pour chaque méthode `async def foo(...)`, génère automatiquement
    `foo_sync(...)` qui exécute la version async de manière synchrone.

    Features:
    - Génération automatique au moment de la définition de classe
    - Préservation des signatures et docstrings
    - Exclusion des méthodes privées et spéciales
    - Compatible avec l'héritage (ne re-génère pas les méthodes héritées)
    - Thread-safe via sync_wrapper

    Usage:
        class MonService(BaseAIService, metaclass=ServiceMeta):
            async def generer_suggestions(self, context: str) -> list[str]:
                ...

        # Génère automatiquement:
        # - generer_suggestions_sync(self, context: str) -> list[str]

        service = MonService()
        # Appel async (dans contexte async)
        result = await service.generer_suggestions("test")
        # Appel sync (dans Streamlit)
        result = service.generer_suggestions_sync("test")

    Note:
        Les méthodes qui ont déjà une version _sync définie manuellement
        ne sont pas re-générées (permet le override).
    """

    def __new__(
        mcs,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
        **kwargs: Any,
    ) -> type:
        """Crée la classe avec les méthodes sync auto-générées."""
        # Collecter les méthodes async définies dans CETTE classe uniquement
        async_methods: dict[str, Callable] = {}

        for attr_name, attr_value in namespace.items():
            # Ignorer si déjà une version _sync existe
            sync_name = f"{attr_name}_sync"
            if sync_name in namespace:
                logger.debug(f"Skip {attr_name}: {sync_name} déjà défini")
                continue

            # Ignorer les méthodes privées/spéciales
            if attr_name.startswith(_IGNORED_PREFIXES) or attr_name in _IGNORED_METHODS:
                continue

            # Vérifier si c'est une coroutine
            if inspect.iscoroutinefunction(attr_value):
                async_methods[attr_name] = attr_value

        # Générer les versions sync
        for method_name, async_method in async_methods.items():
            sync_name = f"{method_name}_sync"
            sync_method = make_sync_alias(async_method, "_sync")

            # Enrichir la docstring
            original_doc = async_method.__doc__ or ""
            sync_method.__doc__ = (
                f"{original_doc}\n\n"
                f"[Auto-generated sync version of {method_name}()]\n"
                f"Safe to call from Streamlit or any synchronous context."
            )

            namespace[sync_name] = sync_method
            logger.debug(f"✨ Auto-generated: {name}.{sync_name}()")

        # Log résumé
        if async_methods:
            logger.debug(f"📦 ServiceMeta: {name} — {len(async_methods)} méthodes sync générées")

        return super().__new__(mcs, name, bases, namespace, **kwargs)


# ═══════════════════════════════════════════════════════════
# DÉCORATEUR @dual_api — Alternative au metaclass
# ═══════════════════════════════════════════════════════════


def dual_api(cls: type[T]) -> type[T]:
    """
    Décorateur de classe qui génère les versions sync des méthodes async.

    Alternative au metaclass ServiceMeta pour les classes qui ne peuvent pas
    l'utiliser (ex: héritage multiple avec autre metaclass).

    Usage:
        @dual_api
        class MonService:
            async def foo(self) -> str:
                return "bar"

        service = MonService()
        assert service.foo_sync() == "bar"

    Args:
        cls: La classe à décorer

    Returns:
        La même classe avec les méthodes _sync ajoutées
    """
    # Scanner les méthodes async de la classe
    for attr_name in dir(cls):
        # Ignorer les méthodes privées/spéciales
        if attr_name.startswith(_IGNORED_PREFIXES) or attr_name in _IGNORED_METHODS:
            continue

        # Vérifier si version sync existe déjà
        sync_name = f"{attr_name}_sync"
        if hasattr(cls, sync_name):
            continue

        attr_value = getattr(cls, attr_name)

        # Générer la version sync si c'est une coroutine
        if inspect.iscoroutinefunction(attr_value):
            sync_method = make_sync_alias(attr_value, "_sync")
            setattr(cls, sync_name, sync_method)
            logger.debug(f"✨ @dual_api: {cls.__name__}.{sync_name}()")

    return cls


# ═══════════════════════════════════════════════════════════
# HELPERS AVANCÉS
# ═══════════════════════════════════════════════════════════


def run_sync(coro: Awaitable[T]) -> T:
    """
    Exécute une coroutine de manière synchrone.

    Gère intelligemment les cas où une boucle d'événements est déjà active.

    Args:
        coro: La coroutine à exécuter

    Returns:
        Le résultat de la coroutine

    Usage:
        async def fetch_data():
            return await api.get("/data")

        # Dans Streamlit:
        data = run_sync(fetch_data())
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop is not None:
        # Event loop active — use thread
        with concurrent.futures.ThreadPoolExecutor() as pool:
            future = pool.submit(asyncio.run, coro)
            return future.result()  # type: ignore[return-value]

    return asyncio.run(coro)  # type: ignore[return-value]


def is_async_method(method: Any) -> bool:
    """Vérifie si une méthode est async."""
    return inspect.iscoroutinefunction(method)


def get_sync_name(method_name: str) -> str:
    """Retourne le nom de la version sync d'une méthode async."""
    return f"{method_name}_sync"


__all__ = [
    "sync_wrapper",
    "make_sync_alias",
    "ServiceMeta",
    "dual_api",
    "run_sync",
    "is_async_method",
    "get_sync_name",
]
