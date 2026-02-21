"""
use_lifecycle - Hooks de cycle de vie pour Streamlit.

Hooks inspirés de React pour gérer les effets de bord, la mémorisation
et les callbacks dans le contexte Streamlit:
- use_memo: Mémorisation de calculs coûteux avec dépendances
- use_effect: Effets de bord avec cleanup automatique
- use_callback: Mémorisation de fonctions callback
- use_previous: Accès à la valeur précédente d'une variable

Usage:
    from src.ui.hooks_v2 import use_memo, use_effect, use_previous

    # Mémoriser un calcul
    filtered = use_memo(
        lambda: [d for d in data if d.active],
        deps=[data],
        cache_key="filtered_data",
    )

    # Effet de bord
    use_effect(
        lambda: logger.info(f"Data: {len(data)} items"),
        deps=[data],
        effect_key="log_data",
    )
"""

from __future__ import annotations

import hashlib
import logging
from typing import Any, Callable, TypeVar

import streamlit as st

logger = logging.getLogger(__name__)

T = TypeVar("T")


def use_memo(
    compute_fn: Callable[[], T],
    deps: list[Any],
    cache_key: str = "",
) -> T:
    """Hook pour mémoriser un calcul coûteux.

    Le calcul est refait seulement si les dépendances changent.
    Utilise un hash MD5 des dépendances pour détecter les changements.

    Args:
        compute_fn: Fonction de calcul (sans argument).
        deps: Liste des dépendances — le calcul est refait si elles changent.
        cache_key: Clé de cache (auto-générée depuis le nom de la fonction si vide).

    Returns:
        Résultat du calcul (mémorisé tant que les deps ne changent pas).

    Example:
        # Filtrage coûteux mémorisé
        filtered_data = use_memo(
            lambda: [d for d in data if d.active],
            deps=[data, "active"],
            cache_key="filtered_data",
        )

        # Statistiques mémorisées
        stats = use_memo(
            lambda: compute_heavy_stats(records),
            deps=[len(records)],
            cache_key="dashboard_stats",
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
    La fonction peut retourner une fonction de cleanup qui sera appelée
    avant la prochaine exécution de l'effet.

    Args:
        effect_fn: Fonction effet. Peut retourner une fonction de cleanup
            (appelée avant la prochaine exécution) ou None.
        deps: Liste des dépendances — l'effet est ré-exécuté si elles changent.
        effect_key: Clé unique pour identifier l'effet (auto-générée si vide).

    Example:
        # Effet simple (logging)
        use_effect(
            lambda: logger.info(f"Data changed: {len(data)} items"),
            deps=[data],
            effect_key="log_data_change",
        )

        # Effet avec cleanup
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
    des callbacks à des composants enfants. Le callback est
    recréé seulement si les dépendances changent.

    Args:
        callback_fn: Fonction callback à mémoriser.
        deps: Dépendances — le callback est recréé si elles changent.
        callback_key: Clé unique (auto-générée si vide).

    Returns:
        Callback mémorisé (même référence tant que les deps ne changent pas).

    Example:
        handle_click = use_callback(
            lambda item: process(item),
            deps=[config],
            callback_key="handle_click",
        )
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

    Stocke la valeur actuelle et retourne la valeur du cycle précédent.
    Retourne None lors de la première exécution.

    Args:
        value: Valeur actuelle à stocker.
        key: Clé unique pour identifier la valeur.

    Returns:
        Valeur précédente (ou None si première exécution).

    Example:
        prev_count = use_previous(count, "count")
        if prev_count is not None and count != prev_count:
            st.write(f"Count changed from {prev_count} to {count}")
    """
    state_key = f"_prev_{key}"
    previous = st.session_state.get(state_key)
    st.session_state[state_key] = value
    return previous


__all__ = [
    "use_memo",
    "use_effect",
    "use_callback",
    "use_previous",
]
