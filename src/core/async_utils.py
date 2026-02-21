from __future__ import annotations

"""
Utilitaire async pour Streamlit.

Streamlit tourne dans un event loop existant. L'utilisation directe de
``asyncio.run()`` ou ``asyncio.new_event_loop()`` provoque des conflits.
Ce module fournit un wrapper sûr qui fonctionne dans tous les contextes.
"""

__all__ = ["executer_async"]

import asyncio
import atexit
import concurrent.futures
import logging
from collections.abc import Coroutine
from typing import TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")

# Executor singleton réutilisé entre appels (évite la création/destruction
# d'un ThreadPoolExecutor à chaque invocation)
_EXECUTOR = concurrent.futures.ThreadPoolExecutor(max_workers=2, thread_name_prefix="async-bridge")
atexit.register(_EXECUTOR.shutdown, wait=False)


def executer_async(coro: Coroutine[object, object, T]) -> T:
    """Exécute une coroutine de manière sûre, compatible Streamlit.

    - S'il existe déjà un event loop running (Streamlit), utilise un thread
      dédié pour éviter les deadlocks.
    - Sinon, crée un loop temporaire.

    Args:
        coro: La coroutine à exécuter.

    Returns:
        Le résultat de la coroutine.

    Raises:
        Exception: Toute exception levée par la coroutine est re-propagée.

    Example::

        from src.core.async_utils import executer_async

        result = executer_async(service.suggerer_activites(age, meteo))
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        # Streamlit tourne déjà un loop — on exécute dans un thread séparé
        future = _EXECUTOR.submit(asyncio.run, coro)
        return future.result(timeout=120)
    else:
        return asyncio.run(coro)
