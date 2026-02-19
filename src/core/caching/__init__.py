"""
Caching - Module de cache multi-niveaux.

Architecture à 3 niveaux:
- L1: Mémoire (dict Python) - Ultra rapide, volatile
- L2: Session Streamlit - Persistant pendant la session
- L3: Fichier local (pickle) - Persistant entre sessions

Ce module fournit:
- Classes de cache par niveau (L1, L2, L3)
- Orchestrateur multi-niveaux unifié
- Décorateur @avec_cache_multi
"""

from .base import EntreeCache, StatistiquesCache
from .cache import Cache, cached, clear_all
from .file import CacheFichierN3
from .memory import CacheMemoireN1
from .orchestrator import (
    CacheMultiNiveau,
    avec_cache_multi,
    obtenir_cache,
)
from .session import CacheSessionN2

__all__ = [
    # Types
    "EntreeCache",
    "StatistiquesCache",
    # Cache session simple
    "Cache",
    "cached",
    "clear_all",
    # Caches par niveau
    "CacheMemoireN1",
    "CacheSessionN2",
    "CacheFichierN3",
    # Orchestrateur
    "CacheMultiNiveau",
    "obtenir_cache",
    "avec_cache_multi",
]
