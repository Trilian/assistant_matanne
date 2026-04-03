"""
Observability — Métriques, health checks et logs structurés.

Collecte les métriques de performance et fournit des outils de diagnostic.

Usage:
    from src.services.core.observability import (
        ServiceMetrics, obtenir_collector
    )

    # Créer des métriques pour un service
    metrics = ServiceMetrics("recettes")
    metrics.increment("recettes_creees")
    metrics.gauge("cache_size", 1500)

    with metrics.timer("generation_ia"):
        result = generer_recettes()
"""

from .health import (
    HealthCheck,
    HealthStatus,
    ServiceHealth,
    health_registry,
)
from .metrics import (
    Metric,
    MetricsCollector,
    MetricType,
    ServiceMetrics,
    obtenir_collector,
)

__all__ = [
    # Metrics
    "Metric",
    "MetricType",
    "ServiceMetrics",
    "MetricsCollector",
    "obtenir_collector",
    # Health
    "HealthCheck",
    "HealthStatus",
    "ServiceHealth",
    "health_registry",
]
