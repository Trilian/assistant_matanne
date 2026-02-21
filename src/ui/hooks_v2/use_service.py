"""
use_service - Hook pour injection de services avec cache session.

Lazy-load un service via sa factory et le met en cache dans session_state.
Le service est créé une seule fois par session Streamlit.

Usage:
    from src.ui.hooks_v2 import use_service

    service = use_service(obtenir_service_recettes)
    recettes = service.get_recettes()

    # Avec clé de cache personnalisée
    service = use_service(ma_factory, cache_key="mon_service")
"""

from __future__ import annotations

import logging
from typing import Callable, TypeVar

import streamlit as st

logger = logging.getLogger(__name__)

T = TypeVar("T")


def use_service(service_factory: Callable[[], T], cache_key: str = "") -> T:
    """Hook pour lazy-load un service avec cache session.

    Le service est créé une seule fois via la factory et mis en cache
    dans ``st.session_state``. Les appels suivants retournent l'instance
    en cache sans recréer le service.

    Args:
        service_factory: Factory (fonction sans argument) qui crée le service.
        cache_key: Clé de cache dans session_state (auto-générée depuis le
            nom de la factory si vide).

    Returns:
        Instance du service (typée selon le retour de la factory).

    Raises:
        Exception: Propage l'exception de la factory si la création échoue.

    Example:
        # Service injection simple
        service = use_service(obtenir_service_recettes)
        recettes = service.get_recettes()

        # Avec clé explicite pour éviter les collisions
        svc_a = use_service(factory_a, cache_key="service_a")
        svc_b = use_service(factory_b, cache_key="service_b")
    """
    if not cache_key:
        cache_key = f"_svc_{service_factory.__name__}"

    if cache_key not in st.session_state:
        try:
            st.session_state[cache_key] = service_factory()
        except Exception as e:
            logger.error(f"Erreur création service {cache_key}: {e}")
            raise

    return st.session_state[cache_key]


__all__ = [
    "use_service",
]
