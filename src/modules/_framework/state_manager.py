"""
State Manager - Gestion centralisée du session_state pour modules.

Fournit une gestion typée et préfixée du state pour éviter les collisions
entre modules et simplifier l'initialisation.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, TypeVar

import streamlit as st

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass
class ModuleState:
    """Gestionnaire d'état pour un module spécifique.

    Usage:
        state = ModuleState("inventaire", {"show_form": False, "filter": None})

        # Lecture
        if state.get("show_form"):
            ...

        # Écriture
        state.set("show_form", True)

        # Mise à jour multiple
        state.update({"show_form": False, "filter": "fruits"})
    """

    module_name: str
    defaults: dict[str, Any] = field(default_factory=dict)
    _prefix: str = field(init=False)

    def __post_init__(self):
        self._prefix = f"_mod_{self.module_name}_"
        self._init_defaults()

    def _init_defaults(self) -> None:
        """Initialise les valeurs par défaut."""
        for key, value in self.defaults.items():
            full_key = f"{self._prefix}{key}"
            if full_key not in st.session_state:
                st.session_state[full_key] = value

    def _full_key(self, key: str) -> str:
        return f"{self._prefix}{key}"

    def get(self, key: str, default: T = None) -> T:
        """Récupère une valeur du state."""
        return st.session_state.get(self._full_key(key), default)

    def set(self, key: str, value: Any) -> None:
        """Définit une valeur dans le state."""
        st.session_state[self._full_key(key)] = value

    def update(self, values: dict[str, Any]) -> None:
        """Met à jour plusieurs valeurs."""
        for key, value in values.items():
            self.set(key, value)

    def delete(self, key: str) -> None:
        """Supprime une clé du state."""
        full_key = self._full_key(key)
        if full_key in st.session_state:
            del st.session_state[full_key]

    def reset(self) -> None:
        """Remet le state aux valeurs par défaut."""
        for key in list(st.session_state.keys()):
            if key.startswith(self._prefix):
                del st.session_state[key]
        self._init_defaults()

    def all(self) -> dict[str, Any]:
        """Retourne tout le state du module."""
        result = {}
        prefix_len = len(self._prefix)
        for key, value in st.session_state.items():
            if key.startswith(self._prefix):
                result[key[prefix_len:]] = value
        return result

    def has(self, key: str) -> bool:
        """Vérifie si une clé existe."""
        return self._full_key(key) in st.session_state

    def increment(self, key: str, amount: int = 1) -> int:
        """Incrémente une valeur numérique et retourne la nouvelle valeur."""
        current = self.get(key, 0)
        new_value = current + amount
        self.set(key, new_value)
        return new_value

    def toggle(self, key: str) -> bool:
        """Inverse une valeur booléenne et retourne la nouvelle valeur."""
        current = self.get(key, False)
        new_value = not current
        self.set(key, new_value)
        return new_value


def init_module_state(module_name: str, defaults: dict[str, Any]) -> ModuleState:
    """Initialise et retourne un gestionnaire d'état pour un module.

    Usage:
        state = init_module_state("inventaire", {
            "show_form": False,
            "filter_category": None,
            "sort_by": "nom",
        })
    """
    return ModuleState(module_name, defaults)


def reset_module_state(module_name: str) -> None:
    """Réinitialise tout le state d'un module.

    Usage:
        reset_module_state("inventaire")  # Supprime toutes les clés _mod_inventaire_*
    """
    prefix = f"_mod_{module_name}_"
    keys_to_delete = [k for k in st.session_state.keys() if k.startswith(prefix)]
    for key in keys_to_delete:
        del st.session_state[key]
    logger.debug(f"Reset state module {module_name}: {len(keys_to_delete)} clés supprimées")


def get_all_module_states() -> dict[str, dict[str, Any]]:
    """Retourne le state de tous les modules (pour debug).

    Returns:
        Dict {module_name: {key: value, ...}, ...}
    """
    modules: dict[str, dict[str, Any]] = {}

    for key, value in st.session_state.items():
        if key.startswith("_mod_"):
            parts = key.split("_", 3)
            if len(parts) >= 4:
                module_name = parts[2]
                state_key = parts[3]
                if module_name not in modules:
                    modules[module_name] = {}
                modules[module_name][state_key] = value

    return modules


def clear_all_module_states() -> int:
    """Supprime tous les states de modules.

    Returns:
        Nombre de clés supprimées
    """
    keys_to_delete = [k for k in st.session_state.keys() if k.startswith("_mod_")]
    for key in keys_to_delete:
        del st.session_state[key]
    logger.info(f"Cleared all module states: {len(keys_to_delete)} keys deleted")
    return len(keys_to_delete)


__all__ = [
    "ModuleState",
    "init_module_state",
    "reset_module_state",
    "get_all_module_states",
    "clear_all_module_states",
]
