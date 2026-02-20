"""
Storage - Abstraction de stockage session.

Découple le code métier de ``st.session_state`` pour:
- Tester sans Streamlit
- Swapper le backend (memory, Redis, etc.)

Implémentations:
- ``StreamlitSessionStorage``: Wraps ``st.session_state``
- ``MemorySessionStorage``: Dict en mémoire (tests)

Helpers de découplage:
- ``obtenir_session_state()``: MutableMapping vers ``st.session_state``
- ``obtenir_rerun_callback()``: Callback vers ``st.rerun``
"""

__all__ = [
    "SessionStorage",
    "StreamlitSessionStorage",
    "MemorySessionStorage",
    "obtenir_storage",
    "configurer_storage",
    "obtenir_session_state",
    "obtenir_rerun_callback",
]

import logging
from collections.abc import Callable, MutableMapping
from typing import Any, Protocol, runtime_checkable

logger = logging.getLogger(__name__)


@runtime_checkable
class SessionStorage(Protocol):
    """Interface de stockage session key-value."""

    def get(self, key: str, default: Any = None) -> Any:
        """Récupère une valeur."""
        ...

    def set(self, key: str, value: Any) -> None:
        """Stocke une valeur."""
        ...

    def delete(self, key: str) -> None:
        """Supprime une clé."""
        ...

    def contains(self, key: str) -> bool:
        """Vérifie si une clé existe."""
        ...

    def keys(self) -> list[str]:
        """Liste toutes les clés."""
        ...


class StreamlitSessionStorage:
    """Stockage basé sur ``st.session_state``."""

    def get(self, key: str, default: Any = None) -> Any:
        import streamlit as st

        return st.session_state.get(key, default)

    def set(self, key: str, value: Any) -> None:
        import streamlit as st

        st.session_state[key] = value

    def delete(self, key: str) -> None:
        import streamlit as st

        if key in st.session_state:
            del st.session_state[key]

    def contains(self, key: str) -> bool:
        import streamlit as st

        return key in st.session_state

    def keys(self) -> list[str]:
        import streamlit as st

        return list(st.session_state.keys())


class MemorySessionStorage:
    """Stockage en mémoire (pour les tests et le mode CLI)."""

    def __init__(self) -> None:
        self._data: dict[str, Any] = {}

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value

    def delete(self, key: str) -> None:
        self._data.pop(key, None)

    def contains(self, key: str) -> bool:
        return key in self._data

    def keys(self) -> list[str]:
        return list(self._data.keys())

    def clear(self) -> None:
        """Vide tout le stockage (utile pour les tests)."""
        self._data.clear()


# ═══════════════════════════════════════════════════════════
# INSTANCE GLOBALE (configurable)
# ═══════════════════════════════════════════════════════════

_storage: SessionStorage | None = None


def obtenir_storage() -> SessionStorage:
    """
    Retourne l'instance de stockage session.

    Par défaut, utilise ``StreamlitSessionStorage``.
    En mode test, utilise ``MemorySessionStorage`` via :func:`configurer_storage`.

    Returns:
        Instance de SessionStorage
    """
    global _storage
    if _storage is None:
        try:
            import streamlit as st

            # Vérifier si on est dans un contexte Streamlit réel
            _ = st.session_state
            _storage = StreamlitSessionStorage()
        except Exception:
            logger.info("Streamlit non disponible, utilisation MemorySessionStorage")
            _storage = MemorySessionStorage()
    return _storage


def configurer_storage(storage: SessionStorage) -> None:
    """
    Configure le backend de stockage (injection de dépendance).

    Args:
        storage: Instance de SessionStorage à utiliser

    Example:
        >>> from src.core.storage import configurer_storage, MemorySessionStorage
        >>> configurer_storage(MemorySessionStorage())  # Pour les tests
    """
    global _storage
    _storage = storage
    logger.info(f"Storage configuré: {type(storage).__name__}")


# ═══════════════════════════════════════════════════════════
# HELPERS DE DÉCOUPLAGE — Centralisent les imports Streamlit
# ═══════════════════════════════════════════════════════════

_fallback_state: dict[str, Any] | None = None


def obtenir_session_state() -> MutableMapping[str, Any]:
    """Retourne ``st.session_state`` comme ``MutableMapping``.

    Utilisé par les services qui ont besoin d'un stockage clé-valeur
    directement compatible ``MutableMapping`` (``__getitem__``, ``__setitem__``,
    ``__contains__``).  Centralise l'import Streamlit pour découpler
    la couche service du framework UI.

    En dehors d'un contexte Streamlit (tests, CLI), retourne un dict
    en mémoire partagé.
    """
    try:
        import streamlit as st

        return st.session_state
    except Exception:
        global _fallback_state
        if _fallback_state is None:
            _fallback_state = {}
            logger.info("Streamlit non disponible, utilisation dict en mémoire")
        return _fallback_state


def obtenir_rerun_callback() -> Callable[[], None]:
    """Retourne ``st.rerun`` comme callable.

    Utilisé par les services qui doivent déclencher un rafraîchissement
    de l'interface.  Centralise l'import pour découpler du framework.

    En dehors d'un contexte Streamlit, retourne un no-op.
    """
    try:
        import streamlit as st

        return st.rerun
    except Exception:

        def _noop_rerun() -> None:
            logger.debug("Rerun ignoré (Streamlit non disponible)")

        return _noop_rerun
