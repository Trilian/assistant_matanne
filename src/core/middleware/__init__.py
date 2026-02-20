"""
Middleware — Pipeline composable pour services.

Fournit un pattern middleware inspiré d'ASP.NET / Express
pour composer des préoccupations transversales (logging, cache,
validation, retry, timing) de manière déclarative.

Usage basique::

    from src.core.middleware import Pipeline, Contexte

    pipeline = (
        Pipeline("recettes")
        .utiliser(LogMiddleware())
        .utiliser(TimingMiddleware(seuil_ms=200))
        .utiliser(RetryMiddleware(max_tentatives=3))
        .construire()
    )

    ctx = Contexte(operation="charger_recettes", params={"page": 1})
    resultat = pipeline.executer(ctx, lambda c: service.charger(c.params))

Usage décorateur::

    @pipeline.decorer
    def charger_recettes(page: int = 1) -> list:
        return db.query(Recette).all()
"""

from .base import Contexte, Middleware, NextFn
from .builtin import (
    CacheMiddleware,
    CircuitBreakerMiddleware,
    LogMiddleware,
    RetryMiddleware,
    TimingMiddleware,
    ValidationMiddleware,
)
from .pipeline import Pipeline

__all__ = [
    # Core
    "Contexte",
    "Middleware",
    "NextFn",
    "Pipeline",
    # Built-in
    "CacheMiddleware",
    "CircuitBreakerMiddleware",
    "LogMiddleware",
    "RetryMiddleware",
    "TimingMiddleware",
    "ValidationMiddleware",
]
