"""
File - Cache L3 basé sur fichiers pickle.

Cache persistant entre sessions:
- Plus lent mais durable
- Limité par espace disque
"""

import hashlib
import logging
import pickle
import threading
from pathlib import Path

from .base import EntreeCache

logger = logging.getLogger(__name__)


class CacheFichierN3:
    """
    Cache L3 basé sur fichiers pickle.

    - Persistant entre sessions
    - Plus lent mais durable
    - Limité par espace disque
    """

    def __init__(self, cache_dir: str = ".cache", max_size_mb: float = 100):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.max_size_bytes = int(max_size_mb * 1024 * 1024)
        self._lock = threading.RLock()

    def _key_to_filename(self, key: str) -> Path:
        """Convertit une clé en chemin de fichier."""
        # Hash pour éviter les problèmes de caractères spéciaux
        hash_key = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{hash_key}.cache"

    def get(self, key: str) -> EntreeCache | None:
        """Récupère une entrée du cache L3."""
        filepath = self._key_to_filename(key)

        if not filepath.exists():
            return None

        try:
            with self._lock:
                with open(filepath, "rb") as f:
                    data = pickle.load(f)

                entry = EntreeCache(**data)
                if entry.est_expire:
                    self.remove(key)
                    return None

                entry.hits += 1
                return entry
        except Exception as e:
            logger.debug(f"Erreur lecture cache L3: {e}")
            return None

    def set(self, key: str, entry: EntreeCache) -> None:
        """Stocke une entrée dans le cache L3."""
        filepath = self._key_to_filename(key)

        try:
            # Vérifier l'espace disponible
            self._cleanup_if_needed()

            with self._lock:
                data = {
                    "value": entry.value,
                    "created_at": entry.created_at,
                    "ttl": entry.ttl,
                    "tags": entry.tags,
                    "hits": entry.hits,
                }

                # Écrire dans un fichier temporaire puis renommer (atomique)
                temp_file = filepath.with_suffix(".tmp")
                with open(temp_file, "wb") as f:
                    pickle.dump(data, f)
                temp_file.rename(filepath)

        except Exception as e:
            logger.debug(f"Erreur écriture cache L3: {e}")

    def remove(self, key: str) -> None:
        """Supprime une entrée."""
        filepath = self._key_to_filename(key)
        try:
            if filepath.exists():
                filepath.unlink()
        except Exception:
            pass

    def invalidate(self, pattern: str | None = None, tags: list[str] | None = None) -> int:
        """Invalide des entrées (plus coûteux car lecture fichiers)."""
        count = 0

        try:
            for filepath in self.cache_dir.glob("*.cache"):
                try:
                    with open(filepath, "rb") as f:
                        data = pickle.load(f)

                    # Reconstruire la clé depuis les données n'est pas possible
                    # Donc on invalide par tags seulement
                    if tags and any(tag in data.get("tags", []) for tag in tags):
                        filepath.unlink()
                        count += 1
                except Exception:
                    continue
        except Exception:
            pass

        return count

    def clear(self) -> None:
        """Vide le cache L3."""
        try:
            for filepath in self.cache_dir.glob("*.cache"):
                filepath.unlink()
        except Exception as e:
            logger.debug(f"Erreur vidage cache L3: {e}")

    def _cleanup_if_needed(self) -> None:
        """Nettoie si la taille dépasse la limite."""
        try:
            total_size = sum(f.stat().st_size for f in self.cache_dir.glob("*.cache"))

            if total_size > self.max_size_bytes:
                # Supprimer les fichiers les plus anciens
                files = sorted(self.cache_dir.glob("*.cache"), key=lambda f: f.stat().st_mtime)

                while total_size > self.max_size_bytes * 0.8 and files:
                    oldest = files.pop(0)
                    total_size -= oldest.stat().st_size
                    oldest.unlink()

        except Exception:
            pass

    @property
    def size(self) -> int:
        try:
            return len(list(self.cache_dir.glob("*.cache")))
        except Exception:
            return 0
