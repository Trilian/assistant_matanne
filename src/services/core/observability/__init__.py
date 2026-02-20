"""
Observability — Métriques, traces et logs structurés.

Pattern OpenTelemetry-inspired pour une observabilité uniforme.
Collecte les métriques de performance, les traces d'exécution,
et fournit des outils de diagnostic.

Usage:
    from src.services.core.observability import (
        ServiceMetrics, Span, obtenir_collector
    )

    # Créer des métriques pour un service
    metrics = ServiceMetrics("recettes")
    metrics.increment("recettes_creees")
    metrics.gauge("cache_size", 1500)

    with metrics.timer("generation_ia"):
        result = generer_recettes()

    # Traces
    with Span("RecetteService", "generer") as span:
        span.set_attribute("nb_recettes", 5)
        result = do_work()
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
from .spans import (
    Span,
    SpanContext,
    SpanStatus,
    current_span,
)

__all__ = [
    # Metrics
    "Metric",
    "MetricType",
    "ServiceMetrics",
    "MetricsCollector",
    "obtenir_collector",
    # Spans
    "Span",
    "SpanContext",
    "SpanStatus",
    "current_span",
    # Health
    "HealthCheck",
    "HealthStatus",
    "ServiceHealth",
    "health_registry",
]
