"""
Hooks supplémentaires - Hooks utilitaires simples.

Ces hooks complètent la bibliothèque hooks_v2 avec des primitives courantes:
- use_counter: Compteur incrémentable/décrémentable
- use_toggle: Booléen toggle
- use_list: Gestion de listes avec ajout/suppression
- use_mutation: Mutations asynchrones avec états loading/error
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Generic, TypeVar

import streamlit as st

T = TypeVar("T")

# ============================================================================
# use_counter
# ============================================================================


@dataclass
class CounterState:
    """État d'un compteur avec méthodes de manipulation."""

    value: int
    _key: str = field(repr=False)

    def increment(self, step: int = 1) -> None:
        """Incrémente le compteur."""
        st.session_state[self._key] = self.value + step

    def decrement(self, step: int = 1) -> None:
        """Décrémente le compteur."""
        st.session_state[self._key] = self.value - step

    def reset(self, value: int = 0) -> None:
        """Réinitialise le compteur."""
        st.session_state[self._key] = value


def use_counter(key: str, initial: int = 0) -> CounterState:
    """
    Hook pour gérer un compteur.

    Args:
        key: Clé unique dans session_state
        initial: Valeur initiale

    Returns:
        CounterState avec value et méthodes increment/decrement/reset

    Example:
        counter = use_counter("mon_compteur", initial=0)
        st.write(f"Valeur: {counter.value}")
        if st.button("+"):
            counter.increment()
        if st.button("-"):
            counter.decrement()
    """
    if key not in st.session_state:
        st.session_state[key] = initial

    return CounterState(value=st.session_state[key], _key=key)


# ============================================================================
# use_toggle
# ============================================================================


@dataclass
class ToggleState:
    """État d'un toggle booléen."""

    value: bool
    _key: str = field(repr=False)

    def toggle(self) -> None:
        """Inverse la valeur."""
        st.session_state[self._key] = not self.value

    def set_true(self) -> None:
        """Met la valeur à True."""
        st.session_state[self._key] = True

    def set_false(self) -> None:
        """Met la valeur à False."""
        st.session_state[self._key] = False


def use_toggle(key: str, initial: bool = False) -> ToggleState:
    """
    Hook pour gérer un booléen toggle.

    Args:
        key: Clé unique dans session_state
        initial: Valeur initiale

    Returns:
        ToggleState avec value et méthodes toggle/set_true/set_false

    Example:
        modal = use_toggle("show_modal")
        if st.button("Ouvrir"):
            modal.set_true()
        if modal.value:
            st.write("Modal ouvert!")
    """
    if key not in st.session_state:
        st.session_state[key] = initial

    return ToggleState(value=st.session_state[key], _key=key)


# ============================================================================
# use_list
# ============================================================================


@dataclass
class ListState(Generic[T]):
    """État d'une liste avec méthodes de manipulation."""

    items: list[T]
    _key: str = field(repr=False)

    def append(self, item: T) -> None:
        """Ajoute un élément à la fin."""
        st.session_state[self._key] = [*self.items, item]

    def prepend(self, item: T) -> None:
        """Ajoute un élément au début."""
        st.session_state[self._key] = [item, *self.items]

    def remove(self, item: T) -> None:
        """Supprime la première occurrence de l'élément."""
        new_list = list(self.items)
        if item in new_list:
            new_list.remove(item)
        st.session_state[self._key] = new_list

    def remove_at(self, index: int) -> None:
        """Supprime l'élément à l'index donné."""
        new_list = list(self.items)
        if 0 <= index < len(new_list):
            del new_list[index]
        st.session_state[self._key] = new_list

    def clear(self) -> None:
        """Vide la liste."""
        st.session_state[self._key] = []

    def set(self, items: list[T]) -> None:
        """Remplace la liste entière."""
        st.session_state[self._key] = list(items)

    def update_at(self, index: int, item: T) -> None:
        """Met à jour l'élément à l'index donné."""
        new_list = list(self.items)
        if 0 <= index < len(new_list):
            new_list[index] = item
        st.session_state[self._key] = new_list

    def __len__(self) -> int:
        return len(self.items)

    def __iter__(self):
        return iter(self.items)

    def __getitem__(self, index: int) -> T:
        return self.items[index]


def use_list(key: str, initial: list[T] | None = None) -> ListState[T]:
    """
    Hook pour gérer une liste.

    Args:
        key: Clé unique dans session_state
        initial: Liste initiale (défaut: liste vide)

    Returns:
        ListState avec items et méthodes append/remove/clear/etc.

    Example:
        todos = use_list("todos", initial=["Task 1"])
        for i, todo in enumerate(todos):
            col1, col2 = st.columns([4, 1])
            col1.write(todo)
            if col2.button("X", key=f"del_{i}"):
                todos.remove_at(i)
        if st.button("Ajouter"):
            todos.append("Nouvelle tâche")
    """
    if initial is None:
        initial = []

    if key not in st.session_state:
        st.session_state[key] = list(initial)

    return ListState(items=st.session_state[key], _key=key)


# ============================================================================
# use_mutation
# ============================================================================


@dataclass
class MutationState(Generic[T]):
    """État d'une mutation avec loading/error/data."""

    is_loading: bool = False
    is_error: bool = False
    is_success: bool = False
    data: T | None = None
    error: Exception | None = None
    _key: str = field(default="", repr=False)
    _mutate_fn: Callable[..., T] | None = field(default=None, repr=False)

    def mutate(self, *args: Any, **kwargs: Any) -> T | None:
        """
        Exécute la mutation de manière synchrone.

        Returns:
            Le résultat de la mutation ou None si erreur
        """
        if self._mutate_fn is None:
            return None

        # Set loading state
        st.session_state[f"{self._key}_loading"] = True
        st.session_state[f"{self._key}_error"] = None

        try:
            result = self._mutate_fn(*args, **kwargs)
            st.session_state[f"{self._key}_data"] = result
            st.session_state[f"{self._key}_success"] = True
            st.session_state[f"{self._key}_loading"] = False
            return result
        except Exception as e:
            st.session_state[f"{self._key}_error"] = e
            st.session_state[f"{self._key}_success"] = False
            st.session_state[f"{self._key}_loading"] = False
            return None

    def reset(self) -> None:
        """Réinitialise l'état de la mutation."""
        st.session_state[f"{self._key}_loading"] = False
        st.session_state[f"{self._key}_error"] = None
        st.session_state[f"{self._key}_data"] = None
        st.session_state[f"{self._key}_success"] = False


def use_mutation(
    key: str,
    mutation_fn: Callable[..., T],
) -> MutationState[T]:
    """
    Hook pour gérer des mutations (opérations d'écriture).

    Args:
        key: Clé unique dans session_state
        mutation_fn: Fonction à exécuter lors de la mutation

    Returns:
        MutationState avec méthodes mutate/reset et états loading/error/success

    Example:
        def save_data(data: dict) -> bool:
            db.save(data)
            return True

        mutation = use_mutation("save", save_data)

        if st.button("Sauvegarder"):
            mutation.mutate({"name": "test"})

        if mutation.is_loading:
            st.spinner("Sauvegarde...")
        elif mutation.is_error:
            st.error(f"Erreur: {mutation.error}")
        elif mutation.is_success:
            st.success("Sauvegardé!")
    """
    # Initialize state keys if not present
    for suffix, default in [
        ("_loading", False),
        ("_error", None),
        ("_data", None),
        ("_success", False),
    ]:
        state_key = f"{key}{suffix}"
        if state_key not in st.session_state:
            st.session_state[state_key] = default

    return MutationState(
        is_loading=st.session_state[f"{key}_loading"],
        is_error=st.session_state[f"{key}_error"] is not None,
        is_success=st.session_state[f"{key}_success"],
        data=st.session_state[f"{key}_data"],
        error=st.session_state[f"{key}_error"],
        _key=key,
        _mutate_fn=mutation_fn,
    )
