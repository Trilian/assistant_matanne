"""
Performance Optimizations - Redis Cache, N+1 Prevention, Lazy Loading

Ce module centralise les optimisations de performance avancées:
- Cache Redis pour la production
- Prévention des requêtes N+1 via joinedload/selectinload
- Lazy loading d'images pour les recettes
"""

import logging
from typing import Any, TypeVar, Callable, Optional
from functools import wraps
import hashlib
import json

logger = logging.getLogger(__name__)

T = TypeVar("T")


# ═══════════════════════════════════════════════════════════
# SECTION 1: REDIS CACHE LAYER
# ═══════════════════════════════════════════════════════════

class RedisCache:
    """
    Cache Redis pour la production.
    Fallback sur cache mémoire si Redis non disponible.
    """
    
    _instance: Optional["RedisCache"] = None
    _client = None
    _fallback_cache: dict[str, tuple[Any, float]] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_redis()
        return cls._instance
    
    def _init_redis(self):
        """Initialise la connexion Redis"""
        try:
            import redis
            from src.core.config import obtenir_parametres
            
            params = obtenir_parametres()
            redis_url = getattr(params, 'REDIS_URL', None)
            
            if redis_url:
                self._client = redis.from_url(redis_url, decode_responses=True)
                self._client.ping()  # Test connexion
                logger.info("✅ Redis connecté")
            else:
                logger.info("ℹ️ Redis non configuré, utilisation cache mémoire")
                
        except ImportError:
            logger.warning("⚠️ Package redis non installé")
        except Exception as e:
            logger.warning(f"⚠️ Connexion Redis échouée: {e}")
            self._client = None
    
    @property
    def is_available(self) -> bool:
        """Vérifie si Redis est disponible"""
        return self._client is not None
    
    def get(self, key: str) -> Any | None:
        """Récupère une valeur du cache"""
        if self._client:
            try:
                value = self._client.get(key)
                if value:
                    return json.loads(value)
            except Exception as e:
                logger.debug(f"Redis get error: {e}")
        
        # Fallback mémoire
        import time
        if key in self._fallback_cache:
            value, expiry = self._fallback_cache[key]
            if time.time() < expiry:
                return value
            del self._fallback_cache[key]
        return None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Stocke une valeur dans le cache"""
        if self._client:
            try:
                self._client.setex(key, ttl, json.dumps(value, default=str))
                return True
            except Exception as e:
                logger.debug(f"Redis set error: {e}")
        
        # Fallback mémoire
        import time
        self._fallback_cache[key] = (value, time.time() + ttl)
        return True
    
    def delete(self, key: str) -> bool:
        """Supprime une clé"""
        if self._client:
            try:
                self._client.delete(key)
                return True
            except Exception:
                pass
        
        if key in self._fallback_cache:
            del self._fallback_cache[key]
        return True
    
    def clear_pattern(self, pattern: str) -> int:
        """Supprime toutes les clés matching le pattern"""
        count = 0
        if self._client:
            try:
                for key in self._client.scan_iter(match=pattern):
                    self._client.delete(key)
                    count += 1
            except Exception:
                pass
        
        # Fallback: nettoyer les clés mémoire matching
        keys_to_delete = [k for k in self._fallback_cache if pattern.replace("*", "") in k]
        for k in keys_to_delete:
            del self._fallback_cache[k]
            count += 1
        
        return count
    
    def stats(self) -> dict:
        """Retourne les statistiques du cache"""
        stats = {
            "backend": "redis" if self._client else "memory",
            "memory_keys": len(self._fallback_cache)
        }
        
        if self._client:
            try:
                info = self._client.info("memory")
                stats["redis_memory"] = info.get("used_memory_human", "N/A")
                stats["redis_keys"] = self._client.dbsize()
            except Exception:
                pass
        
        return stats


def redis_cached(prefix: str, ttl: int = 3600):
    """
    Décorateur pour mettre en cache via Redis.
    
    Usage:
        @redis_cached("recettes", ttl=1800)
        def get_recettes():
            return db.query(Recette).all()
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            cache = RedisCache()
            
            # Génère une clé unique basée sur les arguments
            key_data = f"{func.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"
            cache_key = f"{prefix}:{hashlib.md5(key_data.encode()).hexdigest()}"
            
            # Tente de récupérer du cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache HIT: {cache_key}")
                return cached_value
            
            # Exécute la fonction et met en cache
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            logger.debug(f"Cache MISS: {cache_key}")
            
            return result
        return wrapper
    return decorator


# ═══════════════════════════════════════════════════════════
# SECTION 2: PRÉVENTION REQUÊTES N+1
# ═══════════════════════════════════════════════════════════

def get_query_optimizer(session):
    """
    Factory pour créer un QueryOptimizer.
    
    Usage:
        with get_db_context() as db:
            optimizer = get_query_optimizer(db)
            recettes = optimizer.query(Recette).with_related("ingredients").all()
    """
    return QueryOptimizer(session)


class QueryOptimizer:
    """
    Utilitaire pour prévenir les requêtes N+1.
    
    Usage:
        optimizer = QueryOptimizer(session)
        recettes = optimizer.query(Recette).with_related("ingredients", "tags").all()
    """
    
    def __init__(self, session):
        self.session = session
        self._query = None
        self._model = None
    
    def query(self, model) -> "QueryOptimizer":
        """Démarre une requête"""
        self._model = model
        self._query = self.session.query(model)
        return self
    
    def with_related(self, *relations: str) -> "QueryOptimizer":
        """
        Charge les relations en une seule requête (évite N+1).
        Utilise joinedload pour les relations simples.
        
        Args:
            *relations: Noms des relations à charger
            
        Example:
            optimizer.query(Recette).with_related("ingredients", "etapes")
        """
        if self._query is None:
            raise ValueError("Appelez query() d'abord")
        
        from sqlalchemy.orm import joinedload
        
        for relation in relations:
            if hasattr(self._model, relation):
                self._query = self._query.options(joinedload(getattr(self._model, relation)))
        
        return self
    
    def with_selectin(self, *relations: str) -> "QueryOptimizer":
        """
        Charge les relations via SELECT IN (meilleur pour grandes collections).
        """
        if self._query is None:
            raise ValueError("Appelez query() d'abord")
        
        from sqlalchemy.orm import selectinload
        
        for relation in relations:
            if hasattr(self._model, relation):
                self._query = self._query.options(selectinload(getattr(self._model, relation)))
        
        return self
    
    def filter(self, *criterion) -> "QueryOptimizer":
        """Ajoute des filtres"""
        if self._query:
            self._query = self._query.filter(*criterion)
        return self
    
    def filter_by(self, **kwargs) -> "QueryOptimizer":
        """Ajoute des filtres par attribut"""
        if self._query:
            self._query = self._query.filter_by(**kwargs)
        return self
    
    def order_by(self, *criterion) -> "QueryOptimizer":
        """Ajoute un tri"""
        if self._query:
            self._query = self._query.order_by(*criterion)
        return self
    
    def limit(self, n: int) -> "QueryOptimizer":
        """Limite les résultats"""
        if self._query:
            self._query = self._query.limit(n)
        return self
    
    def offset(self, n: int) -> "QueryOptimizer":
        """Offset pour pagination"""
        if self._query:
            self._query = self._query.offset(n)
        return self
    
    def all(self) -> list:
        """Exécute la requête et retourne tous les résultats"""
        if self._query is None:
            return []
        return self._query.all()
    
    def first(self):
        """Retourne le premier résultat"""
        if self._query is None:
            return None
        return self._query.first()
    
    def one_or_none(self):
        """Retourne un résultat ou None"""
        if self._query is None:
            return None
        return self._query.one_or_none()
    
    def count(self) -> int:
        """Compte les résultats"""
        if self._query is None:
            return 0
        return self._query.count()
    
    def exists(self) -> bool:
        """Vérifie si des résultats existent"""
        return self.count() > 0


def with_eager_loading(*relations: str):
    """
    Décorateur pour charger automatiquement les relations.
    
    Usage:
        @with_eager_loading("ingredients", "etapes")
        def get_recette_complete(recette_id: int, db: Session) -> Recette:
            return db.query(Recette).filter(Recette.id == recette_id).first()
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Ajoute un hint pour les relations à charger
            kwargs['_eager_load'] = relations
            return func(*args, **kwargs)
        return wrapper
    return decorator


# ═══════════════════════════════════════════════════════════
# SECTION 3: LAZY LOADING IMAGES
# ═══════════════════════════════════════════════════════════

class LazyImageLoader:
    """
    Gestionnaire de lazy loading pour les images de recettes.
    
    Charge les images à la demande au lieu de les charger toutes au départ.
    """
    
    _placeholder_url = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='200'%3E%3Crect fill='%23f0f0f0' width='200' height='200'/%3E%3Ctext x='50%25' y='50%25' dominant-baseline='middle' text-anchor='middle' fill='%23999'%3E🍽️%3C/text%3E%3C/svg%3E"
    
    def __init__(self, cache_ttl: int = 3600):
        self.cache_ttl = cache_ttl
        self._loading: set[int] = set()
        self._loaded_urls: dict[int, str] = {}
    
    @property
    def placeholder(self) -> str:
        """Retourne l'URL du placeholder"""
        return self._placeholder_url
    
    def get_image_url(self, recette_id: int, image_url: str | None) -> str:
        """
        Retourne l'URL de l'image ou un placeholder.
        
        Args:
            recette_id: ID de la recette
            image_url: URL de l'image (peut être None)
            
        Returns:
            URL de l'image ou placeholder
        """
        if image_url:
            return image_url
        
        # Vérifie si déjà chargée
        if recette_id in self._loaded_urls:
            return self._loaded_urls[recette_id]
        
        return self._placeholder_url
    
    def should_load(self, recette_id: int) -> bool:
        """Vérifie si l'image doit être chargée"""
        return recette_id not in self._loading and recette_id not in self._loaded_urls
    
    def mark_loading(self, recette_id: int) -> None:
        """Marque une image comme en cours de chargement"""
        self._loading.add(recette_id)
    
    def mark_loaded(self, recette_id: int, url: str) -> None:
        """Marque une image comme chargée"""
        self._loading.discard(recette_id)
        self._loaded_urls[recette_id] = url
    
    def generate_lazy_html(self, recette_id: int, image_url: str | None, alt: str = "") -> str:
        """
        Génère le HTML pour lazy loading.
        
        Args:
            recette_id: ID de la recette
            image_url: URL de l'image
            alt: Texte alternatif
            
        Returns:
            HTML avec attributs data-* pour lazy loading
        """
        actual_url = image_url or ""
        
        return f'''<img 
            src="{self._placeholder_url}" 
            data-src="{actual_url}" 
            data-recette-id="{recette_id}"
            alt="{alt}"
            class="lazy-image"
            loading="lazy"
        />'''
    
    def get_css(self) -> str:
        """Retourne le CSS pour les images lazy"""
        return '''
        <style>
        .lazy-image {
            opacity: 0.5;
            transition: opacity 0.3s ease;
            background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
            background-size: 200% 100%;
            animation: shimmer 1.5s infinite;
        }
        .lazy-image[src]:not([src^="data:"]) {
            opacity: 1;
            animation: none;
        }
        @keyframes shimmer {
            0% { background-position: -200% 0; }
            100% { background-position: 200% 0; }
        }
        </style>
        '''
    
    def get_javascript(self) -> str:
        """
        Retourne le JavaScript pour activer le lazy loading.
        À inclure une fois dans la page.
        """
        return '''
        <script>
        document.addEventListener("DOMContentLoaded", function() {
            const lazyImages = document.querySelectorAll("img.lazy-image");
            
            if ("IntersectionObserver" in window) {
                const imageObserver = new IntersectionObserver((entries, observer) => {
                    entries.forEach(entry => {
                        if (entry.isIntersecting) {
                            const img = entry.target;
                            const src = img.dataset.src;
                            if (src) {
                                img.src = src;
                            }
                            observer.unobserve(img);
                        }
                    });
                }, {
                    rootMargin: "50px 0px",
                    threshold: 0.01
                });
                
                lazyImages.forEach(img => imageObserver.observe(img));
            } else {
                // Fallback pour navigateurs anciens
                lazyImages.forEach(img => {
                    if (img.dataset.src) {
                        img.src = img.dataset.src;
                    }
                });
            }
        });
        </script>
        '''
    
    def clear_cache(self) -> None:
        """Vide le cache d'images"""
        self._loading.clear()
        self._loaded_urls.clear()


# ═══════════════════════════════════════════════════════════
# SECTION 4: HELPERS & SINGLETONS
# ═══════════════════════════════════════════════════════════

_redis_cache_instance: RedisCache | None = None
_lazy_loader_instance: LazyImageLoader | None = None


def get_redis_cache() -> RedisCache:
    """Retourne l'instance Redis singleton"""
    global _redis_cache_instance
    if _redis_cache_instance is None:
        _redis_cache_instance = RedisCache()
    return _redis_cache_instance


def get_lazy_image_loader() -> LazyImageLoader:
    """Retourne un loader d'images lazy singleton"""
    global _lazy_loader_instance
    if _lazy_loader_instance is None:
        _lazy_loader_instance = LazyImageLoader()
    return _lazy_loader_instance


def invalidate_cache(pattern: str = "*") -> int:
    """
    Invalide le cache (utile après modifications).
    
    Args:
        pattern: Pattern de clés à supprimer (ex: "recettes:*")
        
    Returns:
        Nombre de clés supprimées
    """
    cache = get_redis_cache()
    return cache.clear_pattern(pattern)


# ═══════════════════════════════════════════════════════════
# SECTION 5: BATCH OPERATIONS
# ═══════════════════════════════════════════════════════════

def batch_load_images(recette_ids: list[int], get_url_func: Callable[[int], str | None]) -> dict[int, str]:
    """
    Charge les URLs d'images en batch.
    
    Args:
        recette_ids: Liste des IDs de recettes
        get_url_func: Fonction pour obtenir l'URL d'une image
        
    Returns:
        Dict {recette_id: url}
    """
    loader = get_lazy_image_loader()
    results = {}
    
    for rid in recette_ids:
        if loader.should_load(rid):
            loader.mark_loading(rid)
            try:
                url = get_url_func(rid)
                if url:
                    loader.mark_loaded(rid, url)
                    results[rid] = url
            except Exception as e:
                logger.warning(f"Erreur chargement image {rid}: {e}")
                loader._loading.discard(rid)
    
    return results


def prefetch_related(session, model, ids: list[int], *relations: str) -> list:
    """
    Précharge des entités avec leurs relations.
    
    Args:
        session: Session SQLAlchemy
        model: Modèle à charger
        ids: Liste des IDs
        *relations: Relations à charger
        
    Returns:
        Liste des entités avec relations chargées
    """
    if not ids:
        return []
    
    optimizer = QueryOptimizer(session)
    return (
        optimizer
        .query(model)
        .with_related(*relations)
        .filter(model.id.in_(ids))
        .all()
    )
