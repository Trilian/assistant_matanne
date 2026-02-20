"""
Hooks - Pattern React-like pour Streamlit.

Fournit des hooks pour gérer l'état, les services et les requêtes
de manière déclarative et composable.

Hooks disponibles:
- use_state: État local avec setter
- use_service: Injection de service avec cache
- use_query: Requête avec cache, loading et error states
- use_memo: Mémorisation de calculs coûteux
- use_effect: Effets de bord avec cleanup

Usage:
    from src.modules._framework import use_state, use_query, use_service

    # État local
    count = use_state("counter", 0)
    if st.button("+"): count.setter(count.value + 1)

    # Service injection
    service = use_service(obtenir_service_recettes)

    # Requête avec cache
    result = use_query(service.get_recettes, "recettes", ttl=300)
    if result.is_success:
        for r in result.data:
            st.write(r.nom)
"""

from __future__ import annotations

import hashlib
import logging
import time
from dataclasses import dataclass
from functools import wraps
from typing import Any, Callable, Generic, TypeVar

import streamlit as st

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass
class StateHook(Generic[T]):
    """Hook pour état local avec persistance session.

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

    Args:
        key: Clé unique pour le state
        default: Valeur par défaut
        prefix: Préfixe optionnel pour éviter les collisions

    Returns:
        StateHook avec value et setter

    Usage:
        count = use_state("counter", 0)
        st.write(f"Count: {count.value}")
        if st.button("+"):
            count.setter(count.value + 1)

        # Ou avec update
        count.update(lambda x: x + 1)
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


def use_service(service_factory: Callable[[], T], cache_key: str = "") -> T:
    """Hook pour lazy-load un service avec cache session.

    Le service est créé une seule fois et mis en cache dans session_state.

    Args:
        service_factory: Factory qui crée le service
        cache_key: Clé de cache (auto-générée si vide)

    Returns:
        Instance du service

    Usage:
        service = use_service(obtenir_service_recettes)
        recettes = service.get_recettes()
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


def use_query(
    query_fn: Callable[[], T],
    cache_key: str,
    ttl: int = 300,
    enabled: bool = True,
    on_success: Callable[[T], None] | None = None,
    on_error: Callable[[Exception], None] | None = None,
) -> QueryResult[T]:
    """Hook pour requêtes avec cache, loading state et erreur.

    Args:
        query_fn: Fonction à exécuter pour obtenir les données
        cache_key: Clé unique pour le cache
        ttl: Durée de vie du cache en secondes (défaut: 5 min)
        enabled: Si False, ne déclenche pas la requête
        on_success: Callback appelé en cas de succès
        on_error: Callback appelé en cas d'erreur

    Returns:
        QueryResult avec data, loading, error et refetch

    Usage:
        result = use_query(
            lambda: service.get_articles(),
            cache_key="articles",
            ttl=300
        )

        if result.loading:
            st.spinner("Chargement...")
        elif result.is_error:
            st.error(str(result.error))
        elif result.is_empty:
            st.info("Aucun article")
        else:
            for article in result.data:
                st.write(article.nom)
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


def use_memo(
    compute_fn: Callable[[], T],
    deps: list[Any],
    cache_key: str = "",
) -> T:
    """Hook pour mémoriser un calcul coûteux.

    Le calcul est refait seulement si les dépendances changent.

    Args:
        compute_fn: Fonction de calcul
        deps: Liste des dépendances
        cache_key: Clé de cache (auto-générée si vide)

    Returns:
        Résultat du calcul (mémorisé)

    Usage:
        filtered_data = use_memo(
            lambda: [d for d in data if d.active],
            deps=[data, "active"],
            cache_key="filtered_data"
        )
    """
    if not cache_key:
        cache_key = f"_memo_{compute_fn.__name__}"

    # Hash des dépendances
    deps_str = str(deps)
    deps_hash = hashlib.md5(deps_str.encode()).hexdigest()
    hash_key = f"{cache_key}_deps"

    # Recalculer si les deps ont changé
    if hash_key not in st.session_state or st.session_state[hash_key] != deps_hash:
        st.session_state[cache_key] = compute_fn()
        st.session_state[hash_key] = deps_hash

    return st.session_state[cache_key]


def use_effect(
    effect_fn: Callable[[], Callable[[], None] | None],
    deps: list[Any],
    effect_key: str = "",
) -> None:
    """Hook pour effets de bord (similaire à useEffect React).

    L'effet est exécuté quand les dépendances changent.
    La fonction peut retourner une fonction de cleanup.

    Args:
        effect_fn: Fonction effet qui peut retourner un cleanup
        deps: Liste des dépendances
        effect_key: Clé unique pour l'effet

    Usage:
        use_effect(
            lambda: logger.info(f"Data changed: {len(data)} items"),
            deps=[data],
            effect_key="log_data_change"
        )

        # Avec cleanup
        def setup_listener():
            listener = EventListener()
            listener.start()
            return lambda: listener.stop()  # cleanup

        use_effect(setup_listener, deps=[], effect_key="listener")
    """
    if not effect_key:
        effect_key = f"_effect_{id(effect_fn)}"

    deps_str = str(deps)
    deps_hash = hashlib.md5(deps_str.encode()).hexdigest()
    hash_key = f"{effect_key}_deps"
    cleanup_key = f"{effect_key}_cleanup"

    if hash_key not in st.session_state or st.session_state[hash_key] != deps_hash:
        # Exécuter le cleanup précédent si existant
        if cleanup_key in st.session_state and st.session_state[cleanup_key]:
            try:
                st.session_state[cleanup_key]()
            except Exception as e:
                logger.warning(f"Erreur cleanup {effect_key}: {e}")

        # Exécuter l'effet
        try:
            cleanup = effect_fn()
            st.session_state[cleanup_key] = cleanup
        except Exception as e:
            logger.error(f"Erreur effect {effect_key}: {e}")
            st.session_state[cleanup_key] = None

        st.session_state[hash_key] = deps_hash


def use_callback(
    callback_fn: Callable[..., T],
    deps: list[Any],
    callback_key: str = "",
) -> Callable[..., T]:
    """Hook pour mémoriser une fonction callback.

    Utile pour éviter les re-renders inutiles quand on passe
    des callbacks à des composants enfants.

    Args:
        callback_fn: Fonction callback
        deps: Dépendances
        callback_key: Clé unique

    Returns:
        Callback mémorisé
    """
    if not callback_key:
        callback_key = f"_callback_{id(callback_fn)}"

    deps_str = str(deps)
    deps_hash = hashlib.md5(deps_str.encode()).hexdigest()
    hash_key = f"{callback_key}_deps"

    if hash_key not in st.session_state or st.session_state[hash_key] != deps_hash:
        st.session_state[callback_key] = callback_fn
        st.session_state[hash_key] = deps_hash

    return st.session_state[callback_key]


def use_previous(value: T, key: str) -> T | None:
    """Hook pour accéder à la valeur précédente d'une variable.

    Args:
        value: Valeur actuelle
        key: Clé unique

    Returns:
        Valeur précédente (ou None si première exécution)

    Usage:
        prev_count = use_previous(count, "count")
        if prev_count is not None and count != prev_count:
            st.write(f"Count changed from {prev_count} to {count}")
    """
    state_key = f"_prev_{key}"
    previous = st.session_state.get(state_key)
    st.session_state[state_key] = value
    return previous


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
