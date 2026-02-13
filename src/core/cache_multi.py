"""
Cache Multi-Niveaux - Système de cache hiérarchique performant.

Architecture à 3 niveaux :
- L1 : Mémoire (dict Python) - Ultra rapide, volatile
- L2 : Session Streamlit - Persistant pendant la session
- L3 : Fichier local (pickle) - Persistant entre sessions

Stratégie de lecture : L1 â†’ L2 â†’ L3 â†’ Source
Stratégie d'écriture : Propagation vers tous les niveaux
"""

import hashlib
import logging
import pickle
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


# ═══════════════════════════════════════════════════════════
# TYPES ET CONFIGURATION
# ═══════════════════════════════════════════════════════════


@dataclass
class EntreeCache:
    """Entrée de cache avec métadonnées."""

    value: Any
    created_at: float = field(default_factory=time.time)
    ttl: int = 300
    tags: list[str] = field(default_factory=list)
    hits: int = 0

    @property
    def est_expire(self) -> bool:
        """Vérifie si l'entrée est expirée."""
        return time.time() - self.created_at > self.ttl

    # Alias anglais
    is_expired = est_expire

    @property
    def age_seconds(self) -> float:
        """Ã‚ge de l'entrée en secondes."""
        return time.time() - self.created_at


@dataclass
class StatistiquesCache:
    """Statistiques du cache."""

    l1_hits: int = 0
    l2_hits: int = 0
    l3_hits: int = 0
    misses: int = 0
    writes: int = 0
    evictions: int = 0

    @property
    def total_hits(self) -> int:
        return self.l1_hits + self.l2_hits + self.l3_hits

    @property
    def hit_rate(self) -> float:
        total = self.total_hits + self.misses
        return (self.total_hits / total * 100) if total > 0 else 0.0

    def to_dict(self) -> dict:
        return {
            "l1_hits": self.l1_hits,
            "l2_hits": self.l2_hits,
            "l3_hits": self.l3_hits,
            "total_hits": self.total_hits,
            "misses": self.misses,
            "writes": self.writes,
            "evictions": self.evictions,
            "hit_rate": f"{self.hit_rate:.1f}%",
        }


# ═══════════════════════════════════════════════════════════
# CACHE L1 - MÉMOIRE (DICT PYTHON)
# ═══════════════════════════════════════════════════════════


class CacheMemoireN1:
    """
    Cache L1 en mémoire pure (dict Python).

    - Ultra rapide (accès O(1))
    - Limité en taille (éviction LRU)
    - Volatile (perdu au redémarrage)
    """

    def __init__(self, max_entries: int = 500, max_size_mb: float = 50):
        self._cache: dict[str, EntreeCache] = {}
        self._access_order: list[str] = []  # Pour LRU
        self._lock = threading.RLock()
        self.max_entries = max_entries
        self.max_size_bytes = int(max_size_mb * 1024 * 1024)

    def get(self, key: str) -> EntreeCache | None:
        """Récupère une entrée du cache L1."""
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return None

            if entry.is_expired:
                self._remove(key)
                return None

            # Mettre à jour LRU
            if key in self._access_order:
                self._access_order.remove(key)
            self._access_order.append(key)
            entry.hits += 1

            return entry

    def set(self, key: str, entry: EntreeCache) -> None:
        """Stocke une entrée dans le cache L1."""
        with self._lock:
            # Éviction si nécessaire
            while len(self._cache) >= self.max_entries and self._access_order:
                oldest = self._access_order.pop(0)
                self._remove(oldest)

            self._cache[key] = entry
            self._access_order.append(key)

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
            self._access_order.clear()

    def _remove(self, key: str) -> None:
        """Supprime une entrée."""
        if key in self._cache:
            del self._cache[key]
        if key in self._access_order:
            self._access_order.remove(key)

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

    # Alias anglais
    get_stats = obtenir_statistiques


# ═══════════════════════════════════════════════════════════
# CACHE L2 - SESSION STREAMLIT
# ═══════════════════════════════════════════════════════════


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


# ═══════════════════════════════════════════════════════════
# CACHE L3 - FICHIER LOCAL
# ═══════════════════════════════════════════════════════════


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
                if entry.is_expired:
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


# ═══════════════════════════════════════════════════════════
# CACHE MULTI-NIVEAUX UNIFIÉ
# ═══════════════════════════════════════════════════════════


class CacheMultiNiveau:
    """
    Cache multi-niveaux unifié.

    Combine L1 (mémoire), L2 (session) et L3 (fichier)
    pour une performance optimale avec persistance.

    Stratégie de lecture : L1 â†’ L2 â†’ L3 â†’ miss
    Stratégie d'écriture : L1 + L2 (L3 optionnel si persistent=True)
    """

    _instance: "CacheMultiNiveau | None" = None

    def __new__(cls, *args, **kwargs):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(
        self,
        l1_max_entries: int = 500,
        l2_enabled: bool = True,
        l3_enabled: bool = True,
        l3_cache_dir: str = ".cache",
    ):
        if self._initialized:
            return

        self.l1 = CacheMemoireN1(max_entries=l1_max_entries)
        self.l2 = CacheSessionN2() if l2_enabled else None
        self.l3 = CacheFichierN3(cache_dir=l3_cache_dir) if l3_enabled else None
        self.stats = StatistiquesCache()
        self._initialized = True

        logger.info(
            f"CacheMultiNiveau initialisé (L1={l1_max_entries}, L2={l2_enabled}, L3={l3_enabled})"
        )

    def get(
        self,
        key: str,
        default: Any = None,
        promote: bool = True,
    ) -> Any:
        """
        Récupère une valeur du cache.

        Args:
            key: Clé de cache
            default: Valeur par défaut si non trouvé
            promote: Promouvoir aux niveaux supérieurs si trouvé en L2/L3

        Returns:
            Valeur ou default
        """
        # Essayer L1
        entry = self.l1.get(key)
        if entry is not None:
            self.stats.l1_hits += 1
            return entry.value

        # Essayer L2
        if self.l2:
            entry = self.l2.get(key)
            if entry is not None:
                self.stats.l2_hits += 1
                if promote:
                    self.l1.set(key, entry)
                return entry.value

        # Essayer L3
        if self.l3:
            entry = self.l3.get(key)
            if entry is not None:
                self.stats.l3_hits += 1
                if promote:
                    self.l1.set(key, entry)
                    if self.l2:
                        self.l2.set(key, entry)
                return entry.value

        self.stats.misses += 1
        return default

    def set(
        self,
        key: str,
        value: Any,
        ttl: int = 300,
        tags: list[str] | None = None,
        persistent: bool = False,
    ) -> None:
        """
        Stocke une valeur dans le cache.

        Args:
            key: Clé de cache
            value: Valeur à stocker
            ttl: Durée de vie en secondes
            tags: Tags pour invalidation groupée
            persistent: Si True, écrit aussi en L3
        """
        entry = EntreeCache(
            value=value,
            ttl=ttl,
            tags=tags or [],
        )

        # Toujours écrire en L1
        self.l1.set(key, entry)

        # Écrire en L2 si disponible
        if self.l2:
            self.l2.set(key, entry)

        # Écrire en L3 si persistant demandé
        if persistent and self.l3:
            self.l3.set(key, entry)

        self.stats.writes += 1

    def invalidate(
        self,
        pattern: str | None = None,
        tags: list[str] | None = None,
    ) -> int:
        """
        Invalide des entrées de cache.

        Args:
            pattern: Pattern dans la clé
            tags: Tags à invalider

        Returns:
            Nombre d'entrées invalidées
        """
        total = 0

        total += self.l1.invalidate(pattern=pattern, tags=tags)
        if self.l2:
            total += self.l2.invalidate(pattern=pattern, tags=tags)
        if self.l3:
            total += self.l3.invalidate(pattern=pattern, tags=tags)

        self.stats.evictions += total
        logger.debug(f"Cache invalidé: {total} entrées (pattern={pattern}, tags={tags})")

        return total

    def clear(self, levels: str = "all") -> None:
        """
        Vide le cache.

        Args:
            levels: "l1", "l2", "l3", "l1l2", ou "all"
        """
        if "l1" in levels or levels == "all":
            self.l1.clear()
        if ("l2" in levels or levels == "all") and self.l2:
            self.l2.clear()
        if ("l3" in levels or levels == "all") and self.l3:
            self.l3.clear()

        logger.info(f"Cache vidé (niveaux: {levels})")

    def obtenir_statistiques(self) -> dict:
        """Retourne les statistiques complètes."""
        return {
            **self.stats.to_dict(),
            "l1": self.l1.obtenir_statistiques(),
            "l2_size": self.l2.size if self.l2 else 0,
            "l3_size": self.l3.size if self.l3 else 0,
        }

    def obtenir_ou_calculer(
        self,
        key: str,
        compute_fn: Callable[[], T],
        ttl: int = 300,
        tags: list[str] | None = None,
        persistent: bool = False,
    ) -> T:
        """
        Récupère du cache ou calcule et cache.

        Pattern "cache-aside" automatisé.

        Args:
            key: Clé de cache
            compute_fn: Fonction pour calculer la valeur
            ttl: Durée de vie
            tags: Tags
            persistent: Persister en L3

        Returns:
            Valeur (du cache ou calculée)
        """
        value = self.get(key)
        if value is not None:
            return value

        # Calculer et cacher
        value = compute_fn()
        self.set(key, value, ttl=ttl, tags=tags, persistent=persistent)

        return value

    # Alias anglais
    get_stats = obtenir_statistiques
    get_or_compute = obtenir_ou_calculer


# ═══════════════════════════════════════════════════════════
# DÉCORATEUR CACHE MULTI-NIVEAUX
# ═══════════════════════════════════════════════════════════


def avec_cache_multi(
    ttl: int = 300,
    key_prefix: str | None = None,
    tags: list[str] | None = None,
    persistent: bool = False,
):
    """
    Décorateur pour cacher automatiquement les résultats.

    Args:
        ttl: Durée de vie en secondes
        key_prefix: Préfixe pour la clé
        tags: Tags pour invalidation groupée
        persistent: Persister en L3

    Example:
        >>> @cached(ttl=600, tags=["recettes"])
        >>> def charger_recettes(page: int) -> list:
        >>>     return db.query(Recette).offset(page * 20).limit(20).all()
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        from functools import wraps

        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            # Générer la clé
            prefix = key_prefix or func.__name__
            key_parts = [prefix]

            # Exclure 'db' et 'session' des arguments
            filtered_args = [str(a) for a in args if not hasattr(a, "execute")]
            filtered_kwargs = {
                k: str(v)
                for k, v in kwargs.items()
                if k not in ("db", "session") and not hasattr(v, "execute")
            }

            if filtered_args:
                key_parts.append(str(filtered_args))
            if filtered_kwargs:
                key_parts.append(str(sorted(filtered_kwargs.items())))

            cache_key = "_".join(key_parts)

            # Utiliser le cache
            cache = CacheMultiNiveau()
            return cache.obtenir_ou_calculer(
                key=cache_key,
                compute_fn=lambda: func(*args, **kwargs),
                ttl=ttl,
                tags=tags,
                persistent=persistent,
            )

        return wrapper

    return decorator


# ═══════════════════════════════════════════════════════════
# INSTANCE GLOBALE
# ═══════════════════════════════════════════════════════════


def obtenir_cache() -> CacheMultiNiveau:
    """Retourne l'instance globale du cache."""
    return CacheMultiNiveau()


# Alias anglais
cache = obtenir_cache()
cached = avec_cache_multi
get_cache = obtenir_cache
