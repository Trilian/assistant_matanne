"""
State Manager - Gestion d'état pour modules BaseModule.

Module minimal - la plupart des modules utilisent le pattern fonctionnel app()
et n'ont pas besoin de cette classe.

.. admonition:: GELÉ (Audit §9.3)

   Ce module est **gelé** : utilisé uniquement par BaseModule qui lui-même
   n'est utilisé que par ParametresModule et DesignSystemModule.
"""

from __future__ import annotations

from typing import Any

import streamlit as st


class ModuleState:
    """Gestionnaire d'état préfixé pour un module.

    Encapsule l'accès à st.session_state avec préfixage automatique
    pour éviter les collisions entre modules.
    """

    def __init__(self, module_name: str, default_state: dict[str, Any] | None = None):
        """Initialise le gestionnaire d'état.

        Args:
            module_name: Nom du module pour préfixer les clés
            default_state: État initial par défaut
        """
        self._prefix = f"mod_{module_name}_"
        self._default_state = default_state or {}

        # Initialiser les valeurs par défaut
        for key, value in self._default_state.items():
            full_key = self._prefix + key
            if full_key not in st.session_state:
                st.session_state[full_key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Récupère une valeur de l'état."""
        return st.session_state.get(self._prefix + key, default)

    def set(self, key: str, value: Any) -> None:
        """Définit une valeur dans l'état."""
        st.session_state[self._prefix + key] = value

    def update(self, **kwargs: Any) -> None:
        """Met à jour plusieurs valeurs à la fois."""
        for key, value in kwargs.items():
            self.set(key, value)

    def __getitem__(self, key: str) -> Any:
        """Accès par index: state['key']."""
        return self.get(key)

    def __setitem__(self, key: str, value: Any) -> None:
        """Affectation par index: state['key'] = value."""
        self.set(key, value)

    def __contains__(self, key: str) -> bool:
        """Test de présence: 'key' in state."""
        return (self._prefix + key) in st.session_state


__all__ = ["ModuleState"]
