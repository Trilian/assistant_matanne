"""
Redis Cache Layer - Couche de cache distribué Redis.

Fournit un cache partagé entre instances pour les déploiements
multi-processus/multi-containers.

Usage:
    Se configure via ``REDIS_URL`` dans les variables d'environnement.

    >>> from src.core.caching.redis import CacheRedis, est_redis_disponible
    >>> if est_redis_disponible():
    ...     cache = CacheRedis()
    ...     cache.set("key", EntreeCache("value", 300))
"""

import json
import logging
import os
from typing import Any

from .base import EntreeCache

logger = logging.getLogger(__name__)

__all__ = ["CacheRedis", "est_redis_disponible", "is_redis_available", "obtenir_cache_redis"]

# Singleton instance
_redis_cache_instance: "CacheRedis | None" = None


def est_redis_disponible() -> bool:
    """
    Vérifie si Redis est disponible.

    Returns:
        True si REDIS_URL est configuré et connexion possible
    """
    redis_url = os.getenv("REDIS_URL", "")
    if not redis_url:
        # Fallback: charger depuis les settings Pydantic
        try:
            from src.core.config import obtenir_parametres

            redis_url = obtenir_parametres().REDIS_URL
        except Exception:
            pass
    if not redis_url:
        return False

    try:
        import redis

        client = redis.from_url(redis_url, decode_responses=True)
        client.ping()
        return True
    except Exception as e:
        logger.warning(f"Redis non disponible: {e}")
        return False


# Alias rétrocompatibilité
is_redis_available = est_redis_disponible


class CacheRedis:
    """
    Couche de cache Redis distribuée.

    Utilisée comme alternative ou complément à L2/L3 pour les
    déploiements multi-instances.

    Note:
        Nécessite le package ``redis`` (pip install redis).
        Se configure via REDIS_URL.
    """

    def __init__(self, redis_url: str | None = None, prefix: str = "cache:"):
        """
        Initialise la connexion Redis.

        Args:
            redis_url: URL Redis (défaut: REDIS_URL env var)
            prefix: Préfixe pour les clés Redis
        """
        self._redis_url = redis_url or os.getenv("REDIS_URL", "")
        self._prefix = prefix
        self._client = None
        self._available = False

        if self._redis_url:
            try:
                import redis

                self._client = redis.from_url(self._redis_url, decode_responses=True)
                self._client.ping()
                self._available = True
                logger.info(f"CacheRedis connecté: {self._redis_url[:30]}...")
            except ImportError:
                logger.warning("Package redis non installé - cache Redis désactivé")
            except Exception as e:
                logger.warning(f"Connexion Redis échouée: {e}")

    @property
    def is_available(self) -> bool:
        """Indique si Redis est connecté et disponible."""
        return self._available

    def _make_key(self, key: str) -> str:
        """Génère la clé Redis avec préfixe."""
        return f"{self._prefix}{key}"

    def get(self, key: str) -> EntreeCache | None:
        """
        Récupère une entrée du cache Redis.

        Args:
            key: Clé de cache

        Returns:
            EntreeCache ou None si non trouvé/expiré
        """
        if not self._available or not self._client:
            return None

        try:
            redis_key = self._make_key(key)
            data = self._client.get(redis_key)

            if data is None:
                return None

            # Désérialiser
            parsed = json.loads(data)
            entry = EntreeCache(
                value=parsed["value"],
                ttl=parsed.get("ttl", 300),
                created_at=parsed.get("created_at", 0),
                tags=list(parsed.get("tags", [])),
            )

            # Vérifier expiration (est_expire est une property)
            if entry.est_expire:
                self._client.delete(redis_key)
                return None

            return entry

        except Exception as e:
            logger.debug(f"Erreur lecture Redis ({key}): {e}")
            return None

    def set(
        self,
        key: str,
        entry: EntreeCache,
    ) -> bool:
        """
        Stocke une entrée dans le cache Redis.

        Args:
            key: Clé de cache
            entry: Entrée à stocker

        Returns:
            True si succès
        """
        if not self._available or not self._client:
            return False

        try:
            redis_key = self._make_key(key)

            # Sérialiser (created_at est un float de time.time())
            data = json.dumps(
                {
                    "value": entry.value,
                    "ttl": entry.ttl,
                    "created_at": entry.created_at,
                    "tags": list(entry.tags) if entry.tags else [],
                },
                default=str,
            )

            # Stocker avec expiration
            self._client.setex(redis_key, entry.ttl, data)
            return True

        except Exception as e:
            logger.debug(f"Erreur écriture Redis ({key}): {e}")
            return False

    def delete(self, key: str) -> bool:
        """
        Supprime une entrée du cache.

        Args:
            key: Clé à supprimer

        Returns:
            True si supprimé
        """
        if not self._available or not self._client:
            return False

        try:
            redis_key = self._make_key(key)
            return bool(self._client.delete(redis_key))
        except Exception as e:
            logger.debug(f"Erreur suppression Redis ({key}): {e}")
            return False

    def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalide les clés correspondant à un pattern.

        Args:
            pattern: Pattern glob (ex: "user_*")

        Returns:
            Nombre de clés supprimées
        """
        if not self._available or not self._client:
            return 0

        try:
            redis_pattern = self._make_key(pattern)
            keys = list(self._client.scan_iter(match=redis_pattern))
            if keys:
                return self._client.delete(*keys)
            return 0
        except Exception as e:
            logger.debug(f"Erreur invalidation pattern Redis ({pattern}): {e}")
            return 0

    def clear(self) -> int:
        """
        Vide le cache (clés avec le préfixe uniquement).

        Returns:
            Nombre de clés supprimées
        """
        return self.invalidate_pattern("*")

    def get_stats(self) -> dict[str, Any]:
        """
        Récupère les statistiques Redis.

        Returns:
            Dictionnaire de statistiques
        """
        if not self._available or not self._client:
            return {"available": False}

        try:
            info = self._client.info("stats")
            keys_count = sum(
                1 for _ in self._client.scan_iter(match=self._make_key("*"), count=100)
            )
            return {
                "available": True,
                "keys_count": keys_count,
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0),
                "connected_clients": self._client.info("clients").get("connected_clients", 0),
            }
        except Exception as e:
            return {"available": True, "error": str(e)}


def obtenir_cache_redis() -> CacheRedis | None:
    """
    Obtient l'instance singleton du cache Redis.

    Returns:
        CacheRedis si disponible, None sinon
    """
    global _redis_cache_instance

    if _redis_cache_instance is None:
        cache = CacheRedis()
        if cache.is_available:
            _redis_cache_instance = cache
            return _redis_cache_instance
        return None

    return _redis_cache_instance
