"""
Hooks - Pattern React-like pour Streamlit.

Ce module est un proxy rétro-compatible vers le système de hooks unifié
dans ``src.ui.hooks_v2``. Tous les hooks sont désormais centralisés là-bas.

Hooks disponibles:
- use_state: État local avec setter (→ hooks_v2.use_state)
- use_service: Injection de service avec cache (→ hooks_v2.use_service)
- use_query: Requête avec cache, loading et error states (→ hooks_v2.use_query)
- use_memo: Mémorisation de calculs coûteux (→ hooks_v2.use_memo)
- use_effect: Effets de bord avec cleanup (→ hooks_v2.use_effect)
- use_callback: Mémorisation de callbacks (→ hooks_v2.use_callback)
- use_previous: Accès à la valeur précédente (→ hooks_v2.use_previous)

Usage:
    # Import recommandé (source unique) :
    from src.ui.hooks_v2 import use_state, use_query, use_service

    # Rétro-compatible (proxy) :
    from src.modules._framework import use_state, use_query, use_service
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any, Callable, Generic, TypeVar

import streamlit as st

# ── Hooks unifiés (re-exports depuis hooks_v2) ──────────────
from src.ui.hooks_v2 import use_service  # noqa: F401
from src.ui.hooks_v2.use_lifecycle import (  # noqa: F401
    use_callback,
    use_effect,
    use_memo,
    use_previous,
)

logger = logging.getLogger(__name__)

T = TypeVar("T")


# ═══════════════════════════════════════════════════════════
# RÉTRO-COMPATIBILITÉ : StateHook + QueryResult + use_state + use_query
# ═══════════════════════════════════════════════════════════
# Ces classes/fonctions conservent l'API originale (_framework)
# que le module cuisine/inventaire et les tests utilisent déjà.
# La source de vérité pour les NOUVEAUX développements est hooks_v2.


@dataclass
class StateHook(Generic[T]):
    """Hook pour état local avec persistance session.

    Note: Pour les nouveaux développements, utilisez ``State[T]`` de hooks_v2.

    Attributes:
        value: Valeur actuelle
        setter: Fonction pour modifier la valeur
        key: Clé utilisée dans session_state
    """

    value: T
    setter: Callable[[T], None]
    key: str

    def update(self, updater: Callable[[T], T]) -> None:
        """Met à jour la valeur via une fonction."""
        self.setter(updater(self.value))

    def reset(self, default: T) -> None:
        """Remet à la valeur par défaut."""
        self.setter(default)


@dataclass
class QueryResult(Generic[T]):
    """Résultat d'une requête avec états loading/error.

    Note: Pour les nouveaux développements, utilisez ``QueryResult`` de hooks_v2
    qui offre ``QueryStatus``, ``stale_time``, ``retry``, etc.

    Attributes:
        data: Données retournées (ou None)
        loading: True si en cours de chargement
        error: Exception si erreur
        refetch: Fonction pour forcer le rechargement
    """

    data: T | None
    loading: bool
    error: Exception | None
    refetch: Callable[[], None]

    @property
    def is_success(self) -> bool:
        """True si les données sont disponibles sans erreur."""
        return self.data is not None and self.error is None

    @property
    def is_error(self) -> bool:
        """True si une erreur s'est produite."""
        return self.error is not None

    @property
    def is_loading(self) -> bool:
        """True si en cours de chargement."""
        return self.loading

    @property
    def is_empty(self) -> bool:
        """True si data est None ou vide."""
        if self.data is None:
            return True
        if hasattr(self.data, "__len__"):
            return len(self.data) == 0
        return False


def use_state(key: str, default: T, prefix: str = "") -> StateHook[T]:
    """Hook React-like pour la gestion d'état.

    Note: Pour les nouveaux développements, utilisez ``use_state`` de hooks_v2
    qui offre ``on_change`` et le préfixe ``_state_`` automatique.

    Args:
        key: Clé unique pour le state
        default: Valeur par défaut
        prefix: Préfixe optionnel pour éviter les collisions

    Returns:
        StateHook avec value et setter
    """
    full_key = f"{prefix}_{key}" if prefix else key

    if full_key not in st.session_state:
        st.session_state[full_key] = default

    def setter(value: T) -> None:
        st.session_state[full_key] = value

    return StateHook(
        value=st.session_state[full_key],
        setter=setter,
        key=full_key,
    )


def use_query(
    query_fn: Callable[[], T],
    cache_key: str,
    ttl: int = 300,
    enabled: bool = True,
    on_success: Callable[[T], None] | None = None,
    on_error: Callable[[Exception], None] | None = None,
) -> QueryResult[T]:
    """Hook pour requêtes avec cache, loading state et erreur.

    Note: Pour les nouveaux développements, utilisez ``use_query`` de hooks_v2
    qui offre ``retry``, ``stale_time``, ``QueryStatus``, etc.

    Args:
        query_fn: Fonction à exécuter pour obtenir les données
        cache_key: Clé unique pour le cache
        ttl: Durée de vie du cache en secondes (défaut: 5 min)
        enabled: Si False, ne déclenche pas la requête
        on_success: Callback appelé en cas de succès
        on_error: Callback appelé en cas d'erreur

    Returns:
        QueryResult avec data, loading, error et refetch
    """
    state_key = f"_query_{cache_key}"

    if state_key not in st.session_state:
        st.session_state[state_key] = {
            "data": None,
            "loading": True,
            "error": None,
            "timestamp": 0,
        }

    state = st.session_state[state_key]
    now = time.time()

    def refetch() -> None:
        """Force le rechargement des données."""
        state["loading"] = True
        state["timestamp"] = 0
        state["error"] = None

    # Exécuter la requête si nécessaire
    needs_fetch = enabled and (state["loading"] or (now - state["timestamp"] > ttl))

    if needs_fetch:
        try:
            data = query_fn()
            state["data"] = data
            state["loading"] = False
            state["error"] = None
            state["timestamp"] = now

            if on_success:
                on_success(data)

        except Exception as e:
            logger.error(f"Erreur use_query({cache_key}): {e}")
            state["loading"] = False
            state["error"] = e

            if on_error:
                on_error(e)

    return QueryResult(
        data=state["data"],
        loading=state["loading"],
        error=state["error"],
        refetch=refetch,
    )


__all__ = [
    "StateHook",
    "QueryResult",
    "use_state",
    "use_service",
    "use_query",
    "use_memo",
    "use_effect",
    "use_callback",
    "use_previous",
]
