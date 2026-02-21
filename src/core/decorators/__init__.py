"""
Package décorateurs — réexporte toute l'API publique.

Usage inchangé::

    from src.core.decorators import avec_session_db, avec_cache, avec_gestion_erreurs
"""

from .cache import avec_cache, cache_ui
from .db import avec_session_db
from .errors import avec_gestion_erreurs
from .validation import avec_resilience, avec_validation

__all__ = [
    "avec_session_db",
    "avec_cache",
    "avec_gestion_erreurs",
    "avec_validation",
    "avec_resilience",
    "cache_ui",
]
