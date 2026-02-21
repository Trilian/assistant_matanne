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


__all__ = [
    "State",
    "use_state",
]
