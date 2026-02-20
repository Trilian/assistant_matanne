"""Tests pour le package Observability — Métriques, spans, health checks."""

import time
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from src.services.core.observability.health import (
    HealthCheck,
    HealthRegistry,
    HealthStatus,
    ServiceHealth,
)
from src.services.core.observability.metrics import (
    Metric,
    MetricsCollector,
    MetricType,
    ServiceMetrics,
)
from src.services.core.observability.spans import (
    Span,
    SpanContext,
    SpanStatus,
    SpanStore,
)

# ═══════════════════════════════════════════════════════════
# TESTS METRICS
# ═══════════════════════════════════════════════════════════


class TestMetric:
    """Tests de la classe Metric."""

    def test_metric_creation(self):
        """Création d'une métrique."""
        metric = Metric(
            name="requests_total",
            type=MetricType.COUNTER,
            value=42.0,
            labels={"service": "recettes"},
        )

        assert metric.name == "requests_total"
        assert metric.type == MetricType.COUNTER
        assert metric.value == 42.0
        assert metric.labels["service"] == "recettes"

    def test_metric_timestamp(self):
        """La métrique a un timestamp."""
        metric = Metric(
            name="test",
            type=MetricType.GAUGE,
            value=1.0,
        )

        assert metric.timestamp is not None
        assert isinstance(metric.timestamp, datetime)


class TestServiceMetrics:
    """Tests de ServiceMetrics."""

    def test_increment_counter(self):
        """Incrémenter un compteur."""
        metrics = ServiceMetrics(service_name="test")
        metrics.increment("calls")
        metrics.increment("calls")
        metrics.increment("calls", 5)

        count_value = metrics.count("calls")
        assert count_value == 7.0

    def test_set_gauge(self):
        """Définir une jauge."""
        metrics = ServiceMetrics(service_name="test")
        metrics.gauge("active_sessions", 42.0)

        value = metrics.get_gauge("active_sessions")
        assert value is not None
        assert value == 42.0

    def test_observe_histogram(self):
        """Observer un histogramme."""
        metrics = ServiceMetrics(service_name="test")
        metrics.histogram("response_time", 0.5)
        metrics.histogram("response_time", 1.2)
        metrics.histogram("response_time", 0.3)

        # Les stats contiennent les histogrammes
        stats = metrics.get_stats()
        assert "histograms" in stats
        # Histogramme enregistré avec 3 valeurs
        hist_key = "test.response_time"
        assert hist_key in stats["histograms"]
        assert stats["histograms"][hist_key]["count"] == 3

    def test_timer_context_manager(self):
        """Timer avec context manager."""
        metrics = ServiceMetrics(service_name="test")

        with metrics.timer("operation_duration"):
            time.sleep(0.01)  # 10ms

        # Le timer enregistre dans les histogrammes avec suffixe _ms
        stats = metrics.get_stats()
        hist_key = "test.operation_duration_ms"
        assert hist_key in stats["histograms"]
        assert stats["histograms"][hist_key]["min"] >= 10  # Au moins 10ms

    def test_get_stats(self):
        """Récupérer toutes les statistiques."""
        metrics = ServiceMetrics(service_name="test")
        metrics.increment("calls")
        metrics.gauge("active", 5.0)

        stats = metrics.get_stats()
        assert "counters" in stats
        assert "gauges" in stats
        assert "test.calls" in stats["counters"]
        assert "test.active" in stats["gauges"]

    def test_reset_metrics(self):
        """Effacer les métriques."""
        metrics = ServiceMetrics(service_name="test")
        metrics.increment("calls")
        metrics.reset()

        count_value = metrics.count("calls")
        assert count_value == 0.0


class TestMetricsCollector:
    """Tests du MetricsCollector singleton."""

    def test_register_service(self):
        """Enregistrer un service (ou récupérer existant)."""
        collector = MetricsCollector()

        metrics = collector.get_service("test_service_1")
        assert metrics is not None
        assert metrics.service_name == "test_service_1"

    def test_get_service_same_instance(self):
        """Récupérer le même service retourne la même instance."""
        collector = MetricsCollector()

        m1 = collector.get_service("same_service")
        m2 = collector.get_service("same_service")

        assert m1 is m2

    def test_get_all_stats(self):
        """Obtenir les stats de tous les services."""
        collector = MetricsCollector()

        m1 = collector.get_service("stats_service_a")
        m1.increment("calls")

        m2 = collector.get_service("stats_service_b")
        m2.gauge("active", 10.0)

        all_stats = collector.get_all_stats()
        # Les stats sont dans services
        assert "stats_service_a" in all_stats["services"]
        assert "stats_service_b" in all_stats["services"]


# ═══════════════════════════════════════════════════════════
# TESTS SPANS
# ═══════════════════════════════════════════════════════════


class TestSpan:
    """Tests de la classe Span."""

    def test_span_creation(self):
        """Création d'un span."""
        span = Span(
            service_name="test_service",
            operation_name="test_operation",
        )

        assert span.operation_name == "test_operation"
        assert span.service_name == "test_service"
        assert span.trace_id is not None
        assert span.span_id is not None

    def test_span_context_manager(self):
        """Span comme context manager."""
        with Span(service_name="svc", operation_name="test") as span:
            span.set_attribute("key", "value")
            time.sleep(0.01)

        assert span.status == SpanStatus.OK
        assert span.duration_ms >= 10  # Au moins 10ms
        assert span.attributes["key"] == "value"

    def test_span_error(self):
        """Span avec erreur."""
        try:
            with Span(service_name="svc", operation_name="failing") as span:
                raise ValueError("Test error")
        except ValueError:
            pass

        assert span.status == SpanStatus.ERROR
        # L'exception est enregistrée dans les events
        assert len(span.events) >= 1
        exception_event = span.events[-1]
        assert exception_event["name"] == "exception"
        assert exception_event["attributes"]["type"] == "ValueError"

    def test_span_add_event(self):
        """Ajouter un événement au span."""
        span = Span(service_name="svc", operation_name="test")
        span.add_event("cache_hit", {"key": "recipe_123"})

        assert len(span.events) == 1
        assert span.events[0]["name"] == "cache_hit"


class TestSpanContext:
    """Tests de SpanContext avec le registre."""

    def test_span_enter_sets_current(self):
        """Span.__enter__ définit le span courant."""
        from src.services.core.observability.spans import current_span

        with Span(service_name="svc", operation_name="outer") as span:
            current = current_span()
            assert current is not None
            assert current.operation_name == "outer"

    def test_nested_spans_parent(self):
        """Spans imbriqués héritent du parent."""
        with Span(service_name="svc", operation_name="parent") as parent:
            with Span(service_name="svc", operation_name="child") as child:
                assert child.parent_span_id == parent.span_id
                assert child.trace_id == parent.trace_id


class TestSpanStore:
    """Tests de SpanStore."""

    def test_record_span(self):
        """Enregistrer un span."""
        store = SpanStore()
        store.clear()

        span = Span(service_name="svc", operation_name="test")
        span.__enter__()  # Démarre le span
        span.__exit__(None, None, None)  # Termine le span
        store.record(span)

        recent = store.get_recent()
        assert len(recent) == 1

    def test_get_by_trace(self):
        """Récupérer par trace_id."""
        store = SpanStore()
        store.clear()

        span = Span(service_name="svc", operation_name="test")
        span.__enter__()
        span.__exit__(None, None, None)
        store.record(span)

        retrieved = store.get_by_trace(span.trace_id)
        assert len(retrieved) == 1
        # Les spans stockés sont des dicts
        assert retrieved[0]["span_id"] == span.span_id


# ═══════════════════════════════════════════════════════════
# TESTS HEALTH CHECKS
# ═══════════════════════════════════════════════════════════


class TestHealthCheck:
    """Tests de HealthCheck (dataclass résultat)."""

    def test_healthy_check_creation(self):
        """Créer un HealthCheck healthy."""
        check = HealthCheck(
            name="database",
            status=HealthStatus.HEALTHY,
            message="Connected",
        )

        assert check.name == "database"
        assert check.status == HealthStatus.HEALTHY
        assert check.is_healthy is True

    def test_unhealthy_check(self):
        """Créer un HealthCheck unhealthy."""
        check = HealthCheck(
            name="external_api",
            status=HealthStatus.UNHEALTHY,
            message="Connection refused",
        )

        assert check.status == HealthStatus.UNHEALTHY
        assert check.is_healthy is False

    def test_degraded_check(self):
        """Créer un HealthCheck dégradé."""
        check = HealthCheck(
            name="cache",
            status=HealthStatus.DEGRADED,
            message="High latency",
            details={"latency_ms": 500},
        )

        assert check.status == HealthStatus.DEGRADED
        assert check.details["latency_ms"] == 500


class TestHealthRegistry:
    """Tests de HealthRegistry."""

    def test_add_check(self):
        """Ajouter un health check au registre."""
        registry = HealthRegistry()
        registry._checks.clear()

        def db_check() -> HealthCheck:
            return HealthCheck(name="db", status=HealthStatus.HEALTHY)

        registry.add("db", db_check)

        assert "db" in registry._checks

    def test_check_execution(self):
        """Exécuter un health check."""
        registry = HealthRegistry()
        registry._checks.clear()

        def healthy_check() -> HealthCheck:
            return HealthCheck(name="test", status=HealthStatus.HEALTHY)

        registry.add("test", healthy_check)

        result = registry.check("test")
        assert result.status == HealthStatus.HEALTHY

    def test_check_unknown_name(self):
        """Check d'un nom inexistant retourne UNKNOWN."""
        registry = HealthRegistry()
        registry._checks.clear()

        result = registry.check("nonexistent")
        assert result.status == HealthStatus.UNKNOWN

    def test_check_all(self):
        """Vérifier tous les health checks."""
        registry = HealthRegistry()
        registry._checks.clear()

        def db_check() -> HealthCheck:
            return HealthCheck(name="db", status=HealthStatus.HEALTHY)

        def cache_check() -> HealthCheck:
            return HealthCheck(name="cache", status=HealthStatus.HEALTHY)

        registry.add("db", db_check)
        registry.add("cache", cache_check)

        result = registry.check_all()
        assert len(result.checks) == 2
        assert result.overall_status == HealthStatus.HEALTHY

    def test_unhealthy_global_status(self):
        """Statut global UNHEALTHY si un check échoue."""
        registry = HealthRegistry()
        registry._checks.clear()

        def healthy() -> HealthCheck:
            return HealthCheck(name="ok", status=HealthStatus.HEALTHY)

        def unhealthy() -> HealthCheck:
            return HealthCheck(name="fail", status=HealthStatus.UNHEALTHY)

        registry.add("ok", healthy)
        registry.add("fail", unhealthy)

        result = registry.check_all()
        assert result.overall_status == HealthStatus.UNHEALTHY


class TestServiceHealth:
    """Tests de ServiceHealth."""

    def test_service_health_creation(self):
        """Création de ServiceHealth."""
        checks = [
            HealthCheck(name="db", status=HealthStatus.HEALTHY),
            HealthCheck(name="cache", status=HealthStatus.HEALTHY),
        ]
        health = ServiceHealth(
            checks=checks,
            overall_status=HealthStatus.HEALTHY,
            total_latency_ms=50.0,
        )

        assert len(health.checks) == 2
        assert health.overall_status == HealthStatus.HEALTHY

    def test_service_health_to_dict(self):
        """ServiceHealth vers dict."""
        health = ServiceHealth(
            checks=[],
            overall_status=HealthStatus.HEALTHY,
            total_latency_ms=10.0,
        )

        d = health.to_dict()
        assert d["overall_status"] == "healthy"
        assert "checks" in d
