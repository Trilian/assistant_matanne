"""
Utilitaires pour l'API REST.
"""

from .cache import (
    ETagMiddleware,
    add_cache_headers,
    check_etag_match,
    generate_etag,
)
from .crud import (
    construire_reponse_paginee,
    creer_dependance_session,
    executer_avec_session,
)
from .exceptions import gerer_exception_api
from .metrics import (
    MetricsMiddleware,
    get_metrics,
    record_ai_request,
    record_rate_limit_hit,
    record_request,
    reset_metrics,
)

__all__ = [
    # CRUD
    "construire_reponse_paginee",
    "creer_dependance_session",
    "executer_avec_session",
    # Exceptions
    "gerer_exception_api",
    # Metrics
    "MetricsMiddleware",
    "record_request",
    "record_rate_limit_hit",
    "record_ai_request",
    "get_metrics",
    "reset_metrics",
    # Cache
    "generate_etag",
    "add_cache_headers",
    "check_etag_match",
    "ETagMiddleware",
]
