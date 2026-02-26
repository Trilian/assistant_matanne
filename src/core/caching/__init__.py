"""
Caching - Module de cache multi-niveaux.

Architecture à 3 niveaux + option Redis:
- L1: Mémoire (dict Python) - Ultra rapide, volatile
- L2: Session Streamlit - Persistant pendant la session
- L3: Fichier local (pickle) - Persistant entre sessions
- Redis (optionnel): Cache distribué pour multi-instances

Ce module fournit:
- Classes de cache par niveau (L1, L2, L3, Redis)
- Orchestrateur multi-niveaux unifié
- Décorateur unifié @avec_cache dans src.core.decorators
"""

from .base import EntreeCache, StatistiquesCache
from .file import CacheFichierN3
from .memory import CacheMemoireN1
from .orchestrator import (
    CacheMultiNiveau,
    obtenir_cache,
    reinitialiser_cache,
)
from .session import CacheSessionN2

# Optional Redis import (requires redis package)
try:
    from .redis import CacheRedis, est_redis_disponible, is_redis_available, obtenir_cache_redis
except ImportError:
    CacheRedis = None  # type: ignore
    est_redis_disponible = lambda: False  # noqa: E731
    is_redis_available = lambda: False  # noqa: E731  # Alias rétrocompatibilité
    obtenir_cache_redis = lambda: None  # noqa: E731

__all__ = [
    # Types
    "EntreeCache",
    "StatistiquesCache",
    # Caches par niveau
    "CacheMemoireN1",
    "CacheSessionN2",
    "CacheFichierN3",
    # Redis (optionnel)
    "CacheRedis",
    "est_redis_disponible",
    "is_redis_available",  # Alias rétrocompatibilité
    "obtenir_cache_redis",
    # Orchestrateur (usage recommandé)
    "CacheMultiNiveau",
    "obtenir_cache",
    "reinitialiser_cache",
]
