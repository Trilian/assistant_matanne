"""
use_state - Hook d'état typé pour Streamlit.

Alternative type-safe à st.session_state brut.
Fournit un getter typé et un setter avec callback optionnel.

Usage:
    from src.ui.hooks_v2 import use_state

    # Simple
    count = use_state("counter", 0)
    st.write(f"Count: {count.value}")
    if st.button("+"):
        count.set(count.value + 1)
        st.rerun()

    # Avec update function
    count.update(lambda x: x + 1)

    # Avec callback on_change
    name = use_state("name", "", on_change=lambda v: print(f"Changed to: {v}"))
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Generic, TypeVar

import streamlit as st

T = TypeVar("T")


@dataclass
class State(Generic[T]):
    """État typé avec getter et setter.

    Attributes:
        value: Valeur actuelle de l'état.
        set: Fonction pour mettre à jour l'état.
        key: Clé de session_state.
    """

    value: T
    set: Callable[[T], None]
    key: str

    def update(self, fn: Callable[[T], T]) -> None:
        """Met à jour l'état via une fonction de transformation.

        Args:
            fn: Fonction qui reçoit la valeur actuelle et retourne la nouvelle.

        Example:
            count.update(lambda x: x + 1)
            items.update(lambda lst: lst + [new_item])
        """
        self.set(fn(self.value))

    def reset(self, initial: T) -> None:
        """Remet l'état à une valeur initiale.

        Args:
            initial: Valeur de reset.
        """
        self.set(initial)


def use_state(
    key: str,
    initial: T,
    on_change: Callable[[T], None] | None = None,
) -> State[T]:
    """Hook d'état typé avec persistance session.

    Crée ou récupère un état persistant dans st.session_state.
    Fournit une API type-safe pour lire et modifier l'état.

    Args:
        key: Clé unique pour identifier l'état.
        initial: Valeur initiale (utilisée si l'état n'existe pas).
        on_change: Callback appelé à chaque modification.

    Returns:
        State[T] avec value, set(), update(), reset().

    Example:
        # Counter
        count = use_state("counter", 0)
        st.write(count.value)
        if st.button("Increment"):
            count.set(count.value + 1)
            st.rerun()

        # List
        items = use_state("items", [])
        items.update(lambda lst: lst + ["nouveau"])

        # Object
        user = use_state("user", {"name": "", "email": ""})
        user.update(lambda u: {**u, "name": "John"})
    """
    full_key = f"_state_{key}"

    # Initialiser si nécessaire
    if full_key not in st.session_state:
        st.session_state[full_key] = initial

    def setter(new_value: T) -> None:
        """Met à jour l'état et appelle le callback."""
        old_value = st.session_state[full_key]
        st.session_state[full_key] = new_value

        if on_change and new_value != old_value:
            on_change(new_value)

    return State(
        value=st.session_state[full_key],
        set=setter,
        key=full_key,
    )


# ═══════════════════════════════════════════════════════════
# VARIANTES SPÉCIALISÉES
# ═══════════════════════════════════════════════════════════


def use_toggle(key: str, initial: bool = False) -> tuple[bool, Callable[[], None]]:
    """Hook pour un état boolean toggle.

    Args:
        key: Clé unique.
        initial: Valeur initiale.

    Returns:
        Tuple (valeur, toggle_fn).

    Example:
        is_open, toggle = use_toggle("modal")
        if st.button("Toggle"):
            toggle()
            st.rerun()
    """
    state = use_state(key, initial)

    def toggle() -> None:
        state.set(not state.value)

    return state.value, toggle


def use_counter(key: str, initial: int = 0) -> tuple[int, Callable[[], None], Callable[[], None]]:
    """Hook pour un compteur.

    Args:
        key: Clé unique.
        initial: Valeur initiale.

    Returns:
        Tuple (valeur, increment_fn, decrement_fn).

    Example:
        count, inc, dec = use_counter("qty", 1)
        st.write(count)
        if st.button("+"): inc(); st.rerun()
        if st.button("-"): dec(); st.rerun()
    """
    state = use_state(key, initial)

    def increment() -> None:
        state.update(lambda x: x + 1)

    def decrement() -> None:
        state.update(lambda x: x - 1)

    return state.value, increment, decrement


def use_list(key: str, initial: list[T] | None = None) -> State[list[T]]:
    """Hook pour une liste avec helpers.

    Args:
        key: Clé unique.
        initial: Liste initiale.

    Returns:
        State avec la liste.

    Note:
        Pour ajouter: state.update(lambda lst: lst + [item])
        Pour supprimer: state.update(lambda lst: [x for x in lst if x != item])
    """
    return use_state(key, initial or [])


__all__ = [
    "State",
    "use_state",
    "use_toggle",
    "use_counter",
    "use_list",
]
