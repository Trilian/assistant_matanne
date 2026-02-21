"""
File - Cache L3 basé sur fichiers JSON.

Cache persistant entre sessions:
- Plus lent mais durable
- Limité par espace disque
- Sérialisé en JSON (sûr — pas de pickle/exécution de code arbitraire)
"""

import hashlib
import json
import logging
import threading
from pathlib import Path
from typing import Any

from .base import EntreeCache

logger = logging.getLogger(__name__)


def _json_serialisable(obj: Any) -> Any:
    """Convertit un objet en type sérialisable JSON."""
    if isinstance(obj, str | bytes | int | float | bool | type(None)):
        return obj
    if isinstance(obj, list | tuple):
        return [_json_serialisable(item) for item in obj]
    if isinstance(obj, dict):
        return {str(k): _json_serialisable(v) for k, v in obj.items()}
    # Fallback: convertir en string
    return str(obj)


class CacheFichierN3:
    """
    Cache L3 basé sur fichiers JSON.

    - Persistant entre sessions
    - Plus lent mais durable
    - Limité par espace disque
    - Sérialisé en JSON (sûr — pas de risque d'exécution de code arbitraire)
    """

    def __init__(self, cache_dir: str = ".cache", max_size_mb: float = 100):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.max_size_bytes = int(max_size_mb * 1024 * 1024)
        self._lock = threading.RLock()

    def _key_to_filename(self, key: str) -> Path:
        """Convertit une clé en chemin de fichier."""
        hash_key = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{hash_key}.json"

    def get(self, key: str) -> EntreeCache | None:
        """Récupère une entrée du cache L3."""
        filepath = self._key_to_filename(key)

        if not filepath.exists():
            return None

        try:
            with self._lock:
                with open(filepath, encoding="utf-8") as f:
                    data = json.load(f)

                entry = EntreeCache(**data)
                if entry.est_expire:
                    self.remove(key)
                    return None

                entry.hits += 1
                return entry
        except Exception as e:
            logger.debug(f"Erreur lecture cache L3: {e}")
            # Fichier corrompu ou ancien format pickle → supprimer
            try:
                filepath.unlink(missing_ok=True)
            except Exception:
                pass
            return None

    def set(self, key: str, entry: EntreeCache) -> None:
        """Stocke une entrée dans le cache L3."""
        filepath = self._key_to_filename(key)

        try:
            # Vérifier l'espace disponible
            self._cleanup_if_needed()

            with self._lock:
                data = {
                    "value": _json_serialisable(entry.value),
                    "created_at": entry.created_at,
                    "ttl": entry.ttl,
                    "tags": entry.tags,
                    "hits": entry.hits,
                }

                # Écrire dans un fichier temporaire puis renommer (atomique)
                temp_file = filepath.with_suffix(".tmp")
                with open(temp_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, default=str)
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
            for filepath in self.cache_dir.glob("*.json"):
                try:
                    with open(filepath, encoding="utf-8") as f:
                        data = json.load(f)

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
            # Nettoyer aussi d'anciens fichiers .cache (format pickle legacy)
            for ext in ("*.json", "*.cache"):
                for filepath in self.cache_dir.glob(ext):
                    filepath.unlink()
        except Exception as e:
            logger.debug(f"Erreur vidage cache L3: {e}")

    def _cleanup_if_needed(self) -> None:
        """Nettoie si la taille dépasse la limite."""
        try:
            total_size = sum(f.stat().st_size for f in self.cache_dir.glob("*.json"))

            if total_size > self.max_size_bytes:
                # Supprimer les fichiers les plus anciens
                files = sorted(self.cache_dir.glob("*.json"), key=lambda f: f.stat().st_mtime)

                while total_size > self.max_size_bytes * 0.8 and files:
                    oldest = files.pop(0)
                    total_size -= oldest.stat().st_size
                    oldest.unlink()

        except Exception:
            pass

    @property
    def size(self) -> int:
        try:
            return len(list(self.cache_dir.glob("*.json")))
        except Exception:
            return 0
