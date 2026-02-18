"""
Session - Cache L2 basé sur Streamlit session_state.

Cache persistant pendant la session utilisateur:
- Partagé entre reruns Streamlit
- Plus lent que L1 mais plus stable
"""

import logging

from .base import EntreeCache

logger = logging.getLogger(__name__)


class CacheSessionN2:
    """
    Cache L2 basé sur Streamlit session_state.

    - Persistant pendant la session utilisateur
    - Partagé entre reruns Streamlit
    - Plus lent que L1 mais plus stable
    """

    CACHE_KEY = "_cache_l2_data"

    def __init__(self):
        self._ensure_initialized()

    def _ensure_initialized(self) -> None:
        """Initialise le cache dans session_state."""
        try:
            import streamlit as st

            if self.CACHE_KEY not in st.session_state:
                st.session_state[self.CACHE_KEY] = {}
        except Exception:
            pass  # Pas en contexte Streamlit

    def _get_store(self) -> dict:
        """Retourne le store de cache."""
        try:
            import streamlit as st

            self._ensure_initialized()
            return st.session_state.get(self.CACHE_KEY, {})
        except Exception:
            return {}

    def _set_store(self, store: dict) -> None:
        """Met à jour le store."""
        try:
            import streamlit as st

            st.session_state[self.CACHE_KEY] = store
        except Exception:
            pass

    def get(self, key: str) -> EntreeCache | None:
        """Récupère une entrée du cache L2."""
        store = self._get_store()
        data = store.get(key)

        if data is None:
            return None

        try:
            entry = EntreeCache(**data)
            if entry.is_expired:
                self.remove(key)
                return None
            entry.hits += 1
            return entry
        except Exception:
            return None

    def set(self, key: str, entry: EntreeCache) -> None:
        """Stocke une entrée dans le cache L2."""
        store = self._get_store()
        store[key] = {
            "value": entry.value,
            "created_at": entry.created_at,
            "ttl": entry.ttl,
            "tags": entry.tags,
            "hits": entry.hits,
        }
        self._set_store(store)

    def remove(self, key: str) -> None:
        """Supprime une entrée."""
        store = self._get_store()
        if key in store:
            del store[key]
            self._set_store(store)

    def invalidate(self, pattern: str | None = None, tags: list[str] | None = None) -> int:
        """Invalide des entrées."""
        store = self._get_store()
        to_remove = []

        for key, data in store.items():
            if pattern and pattern in key:
                to_remove.append(key)
            elif tags and any(tag in data.get("tags", []) for tag in tags):
                to_remove.append(key)

        for key in to_remove:
            del store[key]

        self._set_store(store)
        return len(to_remove)

    def clear(self) -> None:
        """Vide le cache L2."""
        self._set_store({})

    @property
    def size(self) -> int:
        return len(self._get_store())
