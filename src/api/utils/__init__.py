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
    executer_async,
    executer_avec_session,
    query_async,
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
from .security_headers import SecurityHeadersMiddleware

__all__ = [
    # CRUD
    "construire_reponse_paginee",
    "executer_avec_session",
    "executer_async",
    "query_async",
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
    # Security
    "SecurityHeadersMiddleware",
]
