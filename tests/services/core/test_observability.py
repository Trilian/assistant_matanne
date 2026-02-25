"""Tests pour le package Observability — Métriques, health checks."""

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
