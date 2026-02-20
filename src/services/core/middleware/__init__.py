"""
Middleware Pipeline - Pipeline composable pour les appels de service.

Remplace les 3 patterns concurrents (@gerer_erreurs, @avec_gestion_erreurs,
_with_session) par un pipeline middleware unique et composable.

Architecture:
    Service Method → [RateLimit] → [Cache] → [ErrorHandler] → [Session] → [Logging] → Execute

Usage:
    from src.services.core.middleware import ServicePipeline, service_method

    class MonService:
        pipeline = ServicePipeline.default()

        @service_method(cache=True, rate_limit=True, session=True)
        def ma_methode(self, data: dict, db: Session = None) -> Recette:
            return db.query(Recette).first()
"""

from .pipeline import (
    CacheMiddleware,
    ErrorHandlerMiddleware,
    LoggingMiddleware,
    Middleware,
    MiddlewareContext,
    RateLimitMiddleware,
    ServicePipeline,
    SessionMiddleware,
    service_method,
)

__all__ = [
    "Middleware",
    "MiddlewareContext",
    "ServicePipeline",
    "CacheMiddleware",
    "ErrorHandlerMiddleware",
    "LoggingMiddleware",
    "RateLimitMiddleware",
    "SessionMiddleware",
    "service_method",
]
