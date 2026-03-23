"""
Session - Cache L2 basé sur un dict mémoire (par processus).

Cache persistant pendant la durée de vie du processus.
"""

import logging

from .base import EntreeCache

logger = logging.getLogger(__name__)

# Store partagé au niveau du module (même processus)
_STORE: dict[str, dict] = {}


class CacheSessionN2:
    """
    Cache L2 basé sur un dict mémoire partagé au niveau du processus.

    Remplace l'ancien cache L2 basé sur le stockage session.
    """

    CACHE_KEY = "_cache_l2_data"

    def __init__(self):
        self._ensure_initialized()

    def _ensure_initialized(self) -> None:
        """Initialise le store."""
        if self.CACHE_KEY not in _STORE:
            _STORE[self.CACHE_KEY] = {}

    def _get_store(self) -> dict:
        """Retourne le store de cache."""
        self._ensure_initialized()
        return _STORE.get(self.CACHE_KEY, {})

    def _set_store(self, store: dict) -> None:
        """Met à jour le store."""
        _STORE[self.CACHE_KEY] = store

    def get(self, key: str) -> EntreeCache | None:
        """Récupère une entrée du cache L2."""
        store = self._get_store()
        data = store.get(key)

        if data is None:
            return None

        try:
            entry = EntreeCache(**data)
            if entry.est_expire:
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
