"""
Middleware Pipeline - Pipeline composable pour les appels de service.

Remplace les 3 patterns concurrents (@gerer_erreurs, @avec_gestion_erreurs,
_with_session) par un pipeline middleware unique et composable.

Architecture:
    Service Method → [Logging] → [RateLimit] → [Cache] → [ErrorHandler] → [Session] → Execute

Usage:
    from src.services.core.middleware import service_method, with_pipeline

    class MonService:
        # Option 1: Configuration fine
        @service_method(cache=True, rate_limit=True, session=True)
        def ma_methode(self, data: dict, db: Session = None) -> Recette:
            return db.query(Recette).first()

        # Option 2: Preset nommé (plus simple)
        @with_pipeline("ia")
        def suggerer(self, prompt: str) -> str:
            return self.client.appeler(prompt)

        @with_pipeline("db")
        def charger(self, id: int, db: Session = None) -> Recette:
            return db.query(Recette).get(id)

Presets:
    - PIPELINE_MINIMAL : Logging + ErrorHandler
    - PIPELINE_DB      : Logging + ErrorHandler + Session
    - PIPELINE_IA      : Logging + RateLimit + Cache + ErrorHandler
    - PIPELINE_FULL    : Tous les middlewares
"""

from .pipeline import (
    # Presets
    PIPELINE_DB,
    PIPELINE_FULL,
    PIPELINE_IA,
    PIPELINE_MINIMAL,
    # Core
    CacheMiddleware,
    ErrorHandlerMiddleware,
    LoggingMiddleware,
    Middleware,
    MiddlewareContext,
    PipelinePreset,
    RateLimitMiddleware,
    ServicePipeline,
    SessionMiddleware,
    # Décorateurs
    service_method,
    with_pipeline,
)

__all__ = [
    # Core
    "Middleware",
    "MiddlewareContext",
    "ServicePipeline",
    "PipelinePreset",
    # Middlewares
    "CacheMiddleware",
    "ErrorHandlerMiddleware",
    "LoggingMiddleware",
    "RateLimitMiddleware",
    "SessionMiddleware",
    # Décorateurs
    "service_method",
    "with_pipeline",
    # Presets
    "PIPELINE_MINIMAL",
    "PIPELINE_DB",
    "PIPELINE_IA",
    "PIPELINE_FULL",
]
