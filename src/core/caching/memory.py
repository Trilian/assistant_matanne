"""
Memory - Cache L1 en mémoire (dict Python).

Cache ultra rapide (accès O(1)):
- Limité en taille (éviction LRU)
- Volatile (perdu au redémarrage)
"""

import logging
import threading
from collections import OrderedDict

from .base import EntreeCache

logger = logging.getLogger(__name__)


class CacheMemoireN1:
    """
    Cache L1 en mémoire pure (OrderedDict Python).

    - Ultra rapide (accès O(1), LRU O(1))
    - Limité en taille (éviction LRU via OrderedDict.move_to_end/popitem)
    - Volatile (perdu au redémarrage)
    """

    def __init__(self, max_entries: int = 500, max_size_mb: float = 50):
        self._cache: OrderedDict[str, EntreeCache] = OrderedDict()
        self._lock = threading.RLock()
        self.max_entries = max_entries
        self.max_size_bytes = int(max_size_mb * 1024 * 1024)

    def get(self, key: str) -> EntreeCache | None:
        """Récupère une entrée du cache L1."""
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return None

            if entry.est_expire:
                self._remove(key)
                return None

            # Mettre à jour LRU — O(1) via move_to_end
            self._cache.move_to_end(key)
            entry.hits += 1

            return entry

    def set(self, key: str, entry: EntreeCache) -> None:
        """Stocke une entrée dans le cache L1."""
        with self._lock:
            # Éviction LRU si nécessaire — O(1) via popitem(last=False)
            while len(self._cache) >= self.max_entries:
                self._cache.popitem(last=False)

            self._cache[key] = entry
            self._cache.move_to_end(key)

    def invalidate(self, pattern: str | None = None, tags: list[str] | None = None) -> int:
        """Invalide des entrées par pattern ou tags."""
        with self._lock:
            to_remove = []

            for key, entry in self._cache.items():
                if pattern and pattern in key:
                    to_remove.append(key)
                elif tags and any(tag in entry.tags for tag in tags):
                    to_remove.append(key)

            for key in to_remove:
                self._remove(key)

            return len(to_remove)

    def clear(self) -> None:
        """Vide le cache L1."""
        with self._lock:
            self._cache.clear()

    def cleanup_expired(self) -> int:
        """Supprime toutes les entrées expirées.

        Returns:
            Nombre d'entrées supprimées.
        """
        with self._lock:
            expired = [k for k, e in self._cache.items() if e.est_expire]
            for key in expired:
                self._remove(key)
            return len(expired)

    def _remove(self, key: str) -> None:
        """Supprime une entrée — O(1)."""
        self._cache.pop(key, None)

    @property
    def size(self) -> int:
        return len(self._cache)

    def obtenir_statistiques(self) -> dict:
        """Statistiques du cache L1."""
        return {
            "entries": len(self._cache),
            "max_entries": self.max_entries,
            "usage_percent": len(self._cache) / self.max_entries * 100,
        }
