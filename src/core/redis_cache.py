"""
Redis Cache - Cache distribué haute performance.

Fonctionnalités:
[OK] Cache Redis avec fallback mémoire
[OK] TTL automatique
[OK] Invalidation par tags
[OK] Serialisation JSON/Pickle
[OK] Connection pooling
[OK] Compression optionnelle
"""

import hashlib
import json
import logging
import pickle
import zlib
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)

# Essayer d'importer redis, sinon fallback
try:
    import redis
    from redis import ConnectionPool
    REDIS_DISPONIBLE = True
except ImportError:
    REDIS_DISPONIBLE = False
    logger.warning("Redis non installé - utilisation du cache mémoire")


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# CONFIGURATION
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class ConfigurationRedis:
    """Configuration Redis"""
    HOST: str = "localhost"
    PORT: int = 6379
    DB: int = 0
    PASSWORD: str | None = None
    SOCKET_TIMEOUT: int = 5
    SOCKET_CONNECT_TIMEOUT: int = 5
    MAX_CONNECTIONS: int = 10
    COMPRESSION_THRESHOLD: int = 1024  # Compresser si > 1KB
    DEFAULT_TTL: int = 3600  # 1 heure
    KEY_PREFIX: str = "matanne:"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# CACHE MÉMOIRE FALLBACK
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class CacheMemoire:
    """Cache en mémoire (fallback si Redis indisponible)"""
    
    def __init__(self):
        self._data: dict[str, tuple[Any, float]] = {}
        self._tags: dict[str, set[str]] = {}
    
    def get(self, key: str) -> Any | None:
        """Récupère une valeur"""
        if key not in self._data:
            return None
        
        value, expiry = self._data[key]
        if expiry and datetime.now().timestamp() > expiry:
            del self._data[key]
            return None
        
        return value
    
    def set(self, key: str, value: Any, ttl: int = None, tags: list[str] = None) -> bool:
        """Stocke une valeur"""
        expiry = datetime.now().timestamp() + ttl if ttl else None
        self._data[key] = (value, expiry)
        
        if tags:
            for tag in tags:
                if tag not in self._tags:
                    self._tags[tag] = set()
                self._tags[tag].add(key)
        
        return True
    
    def delete(self, key: str) -> bool:
        """Supprime une clé"""
        if key in self._data:
            del self._data[key]
            return True
        return False
    
    def invalidate_tag(self, tag: str) -> int:
        """Invalide toutes les clés avec un tag"""
        count = 0
        if tag in self._tags:
            for key in self._tags[tag]:
                if self.delete(key):
                    count += 1
            del self._tags[tag]
        return count
    
    def clear(self) -> int:
        """Vide tout le cache"""
        count = len(self._data)
        self._data.clear()
        self._tags.clear()
        return count
    
    def stats(self) -> dict:
        """Statistiques du cache"""
        return {
            "type": "memory",
            "keys": len(self._data),
            "tags": len(self._tags),
            "memory_bytes": sum(len(str(v)) for v, _ in self._data.values())
        }


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# CACHE REDIS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class CacheRedis:
    """
    Cache Redis haute performance avec fallback mémoire.
    
    Fonctionnalités:
    - Connection pooling
    - Compression automatique
    - Invalidation par tags
    - Statistiques temps réel
    """
    
    _instance: "CacheRedis | None" = None
    _pool: "ConnectionPool | None" = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self._fallback = CacheMemoire()
        self._redis: "redis.Redis | None" = None
        self._config = ConfigurationRedis()
        self._stats = {
            "hits": 0,
            "misses": 0,
            "errors": 0,
            "fallback_used": 0
        }
        
        self._connect()
    
    def _connect(self):
        """Établit la connexion Redis"""
        if not REDIS_DISPONIBLE:
            logger.info("Redis non disponible - mode fallback mémoire")
            return
        
        try:
            import os
            
            # Configuration depuis variables d'environnement
            host = os.getenv("REDIS_HOST", self._config.HOST)
            port = int(os.getenv("REDIS_PORT", self._config.PORT))
            password = os.getenv("REDIS_PASSWORD", self._config.PASSWORD)
            db = int(os.getenv("REDIS_DB", self._config.DB))
            
            # Créer le pool de connexions
            CacheRedis._pool = ConnectionPool(
                host=host,
                port=port,
                password=password,
                db=db,
                max_connections=self._config.MAX_CONNECTIONS,
                socket_timeout=self._config.SOCKET_TIMEOUT,
                socket_connect_timeout=self._config.SOCKET_CONNECT_TIMEOUT,
                decode_responses=False  # On gère nous-mêmes le décodage
            )
            
            self._redis = redis.Redis(connection_pool=CacheRedis._pool)
            
            # Test de connexion
            self._redis.ping()
            logger.info(f"[OK] Redis connecté: {host}:{port}")
            
        except Exception as e:
            logger.warning(f"[ERROR] Redis indisponible ({e}) - mode fallback mémoire")
            self._redis = None
    
    def _make_key(self, key: str) -> str:
        """Crée une clé avec préfixe"""
        return f"{self._config.KEY_PREFIX}{key}"
    
    def _serialize(self, value: Any) -> bytes:
        """Sérialise une valeur avec compression optionnelle"""
        try:
            # Essayer JSON d'abord (plus rapide, plus lisible)
            data = json.dumps(value).encode('utf-8')
            serializer = b'j'  # JSON marker
        except (TypeError, ValueError):
            # Fallback pickle pour objets complexes
            data = pickle.dumps(value)
            serializer = b'p'  # Pickle marker
        
        # Compression si nécessaire
        if len(data) > self._config.COMPRESSION_THRESHOLD:
            data = zlib.compress(data)
            serializer = b'c' + serializer  # Compressed marker
        
        return serializer + data
    
    def _deserialize(self, data: bytes) -> Any:
        """Désérialise une valeur"""
        if not data:
            return None
        
        # Vérifier compression
        compressed = data[0:1] == b'c'
        if compressed:
            data = data[1:]  # Enlever marker
            payload = zlib.decompress(data[1:])
        else:
            payload = data[1:]
        
        serializer = data[0:1]
        
        if serializer == b'j':
            return json.loads(payload.decode('utf-8'))
        elif serializer == b'p':
            return pickle.loads(payload)
        else:
            raise ValueError(f"Unknown serializer: {serializer}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Récupère une valeur du cache.
        
        Args:
            key: Clé de cache
            default: Valeur par défaut si non trouvé
            
        Returns:
            Valeur ou default
        """
        full_key = self._make_key(key)
        
        if self._redis:
            try:
                data = self._redis.get(full_key)
                if data:
                    self._stats["hits"] += 1
                    return self._deserialize(data)
                self._stats["misses"] += 1
                return default
            except Exception as e:
                logger.warning(f"Redis get error: {e}")
                self._stats["errors"] += 1
        
        # Fallback mémoire
        self._stats["fallback_used"] += 1
        value = self._fallback.get(key)
        return value if value is not None else default
    
    def set(
        self, 
        key: str, 
        value: Any, 
        ttl: int = None, 
        tags: list[str] = None
    ) -> bool:
        """
        Stocke une valeur dans le cache.
        
        Args:
            key: Clé de cache
            value: Valeur Ã  stocker
            ttl: Durée de vie en secondes
            tags: Tags pour invalidation groupée
            
        Returns:
            True si succès
        """
        full_key = self._make_key(key)
        ttl = ttl or self._config.DEFAULT_TTL
        
        if self._redis:
            try:
                data = self._serialize(value)
                self._redis.setex(full_key, ttl, data)
                
                # Stocker les tags
                if tags:
                    for tag in tags:
                        tag_key = f"{self._config.KEY_PREFIX}tag:{tag}"
                        self._redis.sadd(tag_key, full_key)
                        self._redis.expire(tag_key, ttl * 2)  # TTL plus long pour les tags
                
                return True
            except Exception as e:
                logger.warning(f"Redis set error: {e}")
                self._stats["errors"] += 1
        
        # Fallback mémoire
        self._stats["fallback_used"] += 1
        return self._fallback.set(key, value, ttl, tags)
    
    def delete(self, key: str) -> bool:
        """Supprime une clé"""
        full_key = self._make_key(key)
        
        if self._redis:
            try:
                return bool(self._redis.delete(full_key))
            except Exception as e:
                logger.warning(f"Redis delete error: {e}")
                self._stats["errors"] += 1
        
        return self._fallback.delete(key)
    
    def invalidate_tag(self, tag: str) -> int:
        """
        Invalide toutes les clés associées Ã  un tag.
        
        Args:
            tag: Tag Ã  invalider
            
        Returns:
            Nombre de clés supprimées
        """
        if self._redis:
            try:
                tag_key = f"{self._config.KEY_PREFIX}tag:{tag}"
                keys = self._redis.smembers(tag_key)
                
                if keys:
                    count = self._redis.delete(*keys)
                    self._redis.delete(tag_key)
                    logger.info(f"Invalidé {count} clés pour tag '{tag}'")
                    return count
                return 0
            except Exception as e:
                logger.warning(f"Redis invalidate_tag error: {e}")
                self._stats["errors"] += 1
        
        return self._fallback.invalidate_tag(tag)
    
    def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalide les clés correspondant Ã  un pattern.
        
        Args:
            pattern: Pattern avec wildcards (ex: "recettes:*")
            
        Returns:
            Nombre de clés supprimées
        """
        full_pattern = self._make_key(pattern)
        
        if self._redis:
            try:
                keys = list(self._redis.scan_iter(match=full_pattern))
                if keys:
                    count = self._redis.delete(*keys)
                    logger.info(f"Invalidé {count} clés pour pattern '{pattern}'")
                    return count
                return 0
            except Exception as e:
                logger.warning(f"Redis invalidate_pattern error: {e}")
                self._stats["errors"] += 1
        
        # Fallback: pas de support pattern
        return 0
    
    def clear(self) -> int:
        """Vide tout le cache (attention!)"""
        if self._redis:
            try:
                pattern = f"{self._config.KEY_PREFIX}*"
                keys = list(self._redis.scan_iter(match=pattern))
                if keys:
                    count = self._redis.delete(*keys)
                    logger.info(f"Cache vidé: {count} clés supprimées")
                    return count
                return 0
            except Exception as e:
                logger.warning(f"Redis clear error: {e}")
                self._stats["errors"] += 1
        
        return self._fallback.clear()
    
    def stats(self) -> dict:
        """
        Retourne les statistiques du cache.
        
        Returns:
            Dict avec stats détaillées
        """
        base_stats = {
            **self._stats,
            "hit_ratio": self._stats["hits"] / max(1, self._stats["hits"] + self._stats["misses"]),
        }
        
        if self._redis:
            try:
                info = self._redis.info("memory")
                base_stats.update({
                    "type": "redis",
                    "connected": True,
                    "memory_used": info.get("used_memory_human", "N/A"),
                    "keys_count": self._redis.dbsize()
                })
            except Exception:
                base_stats["type"] = "redis (error)"
                base_stats["connected"] = False
        else:
            fallback_stats = self._fallback.stats()
            base_stats.update(fallback_stats)
            base_stats["connected"] = False
        
        return base_stats
    
    def health_check(self) -> dict:
        """Vérifie la santé du cache"""
        result = {
            "status": "healthy",
            "backend": "redis" if self._redis else "memory",
            "connected": False
        }
        
        if self._redis:
            try:
                self._redis.ping()
                result["connected"] = True
            except Exception as e:
                result["status"] = "degraded"
                result["error"] = str(e)
        else:
            result["connected"] = True  # Fallback toujours disponible
        
        return result


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# DÉCORATEUR CACHE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def avec_cache_redis(
    ttl: int = 3600,
    key_prefix: str = "",
    tags: list[str] = None,
    key_builder: Callable = None
):
    """
    Décorateur pour mettre en cache le résultat d'une fonction.
    
    Args:
        ttl: Durée de vie en secondes
        key_prefix: Préfixe pour la clé
        tags: Tags pour invalidation groupée
        key_builder: Fonction pour construire la clé custom
        
    Example:
        @redis_cached(ttl=600, tags=["recettes"])
        def get_recettes():
            return db.query(Recette).all()
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = CacheRedis()
            
            # Construire la clé
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                # Clé par défaut basée sur fonction + args
                args_hash = hashlib.md5(
                    json.dumps([str(a) for a in args] + [f"{k}={v}" for k, v in sorted(kwargs.items())], 
                    sort_keys=True).encode()
                ).hexdigest()[:8]
                cache_key = f"{key_prefix or func.__name__}:{args_hash}"
            
            # Vérifier le cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Exécuter et mettre en cache
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl=ttl, tags=tags)
            
            return result
        
        # Ajouter méthode pour invalider
        wrapper.invalidate = lambda: CacheRedis().invalidate_pattern(f"{key_prefix or func.__name__}:*")
        
        return wrapper
    return decorator


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# FACTORY
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


_cache_instance: CacheRedis | None = None


def obtenir_cache_redis() -> CacheRedis:
    """Factory pour obtenir l'instance du cache Redis"""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = CacheRedis()
    return _cache_instance