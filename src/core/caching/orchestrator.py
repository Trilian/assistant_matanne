"""
Orchestrator - Cache multi-niveaux unifié.

Combine L1 (mémoire), L2 (session) et L3 (fichier)
pour une performance optimale avec persistance.

Stratégie de lecture: L1 → L2 → L3 → miss
Stratégie d'écriture: L1 + L2 (L3 optionnel si persistent=True)
"""

import logging
import threading
from collections.abc import Callable
from functools import wraps
from typing import Any, ParamSpec, TypeVar

from .base import EntreeCache, StatistiquesCache
from .file import CacheFichierN3
from .memory import CacheMemoireN1
from .session import CacheSessionN2

logger = logging.getLogger(__name__)

P = ParamSpec("P")
T = TypeVar("T")


class CacheMultiNiveau:
    """
    Cache multi-niveaux unifié.

    Combine L1 (mémoire), L2 (session) et L3 (fichier)
    pour une performance optimale avec persistance.
    """

    _instance: "CacheMultiNiveau | None" = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        """Singleton thread-safe."""
        if cls._instance is None:
            with cls._lock:
                # Double-check locking
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


def avec_cache_multi(
    ttl: int = 300,
    key_prefix: str | None = None,
    tags: list[str] | None = None,
    persistent: bool = False,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """
    Décorateur pour cacher automatiquement les résultats.

    Args:
        ttl: Durée de vie en secondes
        key_prefix: Préfixe pour la clé
        tags: Tags pour invalidation groupée
        persistent: Persister en L3

    Example:
        >>> @avec_cache_multi(ttl=600, tags=["recettes"])
        >>> def charger_recettes(page: int) -> list:
        >>>     return db.query(Recette).offset(page * 20).limit(20).all()
    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
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


def obtenir_cache() -> CacheMultiNiveau:
    """Retourne l'instance globale du cache."""
    return CacheMultiNiveau()
