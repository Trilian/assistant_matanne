"""Tests pour ServiceHealth et ServiceStatus — types de santé des services."""

import pytest

from src.services.core.base.protocols import (
    ServiceHealth,
    ServiceStatus,
)

# ═══════════════════════════════════════════════════════════
# TESTS SERVICE HEALTH & STATUS
# ═══════════════════════════════════════════════════════════


class TestServiceHealth:
    def test_creation(self):
        health = ServiceHealth(
            status=ServiceStatus.HEALTHY,
            service_name="recettes",
        )
        assert health.status == ServiceStatus.HEALTHY
        assert health.service_name == "recettes"
        assert health.is_healthy is True

    def test_degraded(self):
        health = ServiceHealth(
            status=ServiceStatus.DEGRADED,
            service_name="inventaire",
            message="Latence élevée",
            latency_ms=500.0,
        )
        assert health.is_healthy is False
        assert health.is_degraded is True
        assert health.latency_ms == 500.0

    def test_unhealthy(self):
        health = ServiceHealth(
            status=ServiceStatus.UNHEALTHY,
            service_name="ia",
            message="API indisponible",
        )
        assert health.is_healthy is False
        assert health.is_degraded is False

    def test_avec_details(self):
        health = ServiceHealth(
            status=ServiceStatus.HEALTHY,
            service_name="db",
            details={"pool_size": 5, "active": 2},
        )
        assert health.details["pool_size"] == 5


class TestServiceStatus:
    def test_valeurs(self):
        assert ServiceStatus.HEALTHY == "healthy"
        assert ServiceStatus.DEGRADED == "degraded"
        assert ServiceStatus.UNHEALTHY == "unhealthy"
        assert ServiceStatus.UNKNOWN == "unknown"

    def test_enum_count(self):
        assert len(ServiceStatus) == 4
