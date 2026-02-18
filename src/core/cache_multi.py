"""
Cache Multi-Niveaux - Module de retrocompatibilite.

DEPRECATED: Importer depuis src.core.caching a la place.
Ce fichier existe uniquement pour la retrocompatibilite.

Exemple de migration:
    # Ancien import (toujours supporte)
    from src.core.cache_multi import CacheMultiNiveau

    # Nouvel import (recommande)
    from src.core.caching import CacheMultiNiveau
    # ou
    from src.core import CacheMultiNiveau
"""

# Re-exports depuis le nouveau module
from .caching import (
    CacheFichierN3,
    CacheMemoireN1,
    CacheMultiNiveau,
    CacheSessionN2,
    EntreeCache,
    StatistiquesCache,
    avec_cache_multi,
    cached,
    obtenir_cache,
)

__all__ = [
    "EntreeCache",
    "StatistiquesCache",
    "CacheMemoireN1",
    "CacheSessionN2",
    "CacheFichierN3",
    "CacheMultiNiveau",
    "obtenir_cache",
    "avec_cache_multi",
    "cached",
]
