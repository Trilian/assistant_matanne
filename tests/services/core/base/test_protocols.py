"""Tests pour Protocols PEP 544 — Contrats d'interface structurels."""

import pytest

from src.services.core.base.protocols import (
    AIServiceProtocol,
    CacheableProtocol,
    CRUDProtocol,
    HealthCheckProtocol,
    IOProtocol,
    ObservableProtocol,
    ServiceHealth,
    ServiceStatus,
)

# ═══════════════════════════════════════════════════════════
# HELPERS — Classes de test
# ═══════════════════════════════════════════════════════════


class FakeCRUD:
    """Implémente toutes les méthodes du CRUDProtocol."""

    def create(self, data, db=None):
        return {"id": 1, **data}

    def get_by_id(self, entity_id, db=None):
        return {"id": entity_id}

    def get_all(self, skip=0, limit=100, filters=None, order_by="id", desc_order=False, db=None):
        return []

    def update(self, entity_id, data, db=None):
        return {"id": entity_id, **data}

    def delete(self, entity_id, db=None):
        return True

    def count(self, filters=None, db=None):
        return 0


class IncompleteCRUD:
    """Manque la méthode count — ne satisfait PAS le protocol."""

    def create(self, data, db=None):
        return data

    def get_by_id(self, entity_id, db=None):
        return None

    def get_all(self, skip=0, limit=100, filters=None, order_by="id", desc_order=False, db=None):
        return []

    def update(self, entity_id, data, db=None):
        return None

    def delete(self, entity_id, db=None):
        return True

    # Pas de count() !


class FakeCacheable:
    """Implémente CacheableProtocol."""

    def clear_cache(self):
        pass

    def get_cache_stats(self):
        return {"hits": 10, "misses": 5}


class FakeIO:
    """Implémente IOProtocol."""

    def exporter_csv(self, data, colonnes=None):
        return "csv data"

    def exporter_json(self, data):
        return "{}"

    def importer_csv(self, contenu, mapping=None):
        return []


class NotIO:
    """N'implémente PAS IOProtocol."""

    def exporter_csv(self, data):
        return "csv"

    # Manque exporter_json et importer_csv


class FakeHealthy:
    """Implémente HealthCheckProtocol."""

    def health_check(self):
        return ServiceHealth(
            status=ServiceStatus.HEALTHY,
            service_name="fake",
            message="Tout va bien",
        )


class FakeObservable:
    """Implémente ObservableProtocol."""

    def __init__(self):
        self._handlers: dict = {}

    def subscribe(self, event_type, handler):
        self._handlers[event_type] = handler

    def unsubscribe(self, event_type, handler):
        self._handlers.pop(event_type, None)


# ═══════════════════════════════════════════════════════════
# TESTS CRUD PROTOCOL
# ═══════════════════════════════════════════════════════════


class TestCRUDProtocol:
    """Tests du protocol CRUD avec structural subtyping."""

    def test_implementation_complete_satisfait(self):
        crud = FakeCRUD()
        assert isinstance(crud, CRUDProtocol)

    def test_implementation_incomplete_ne_satisfait_pas(self):
        incomplete = IncompleteCRUD()
        assert not isinstance(incomplete, CRUDProtocol)

    def test_create(self):
        crud = FakeCRUD()
        result = crud.create({"nom": "Tarte"})
        assert result["nom"] == "Tarte"
        assert result["id"] == 1

    def test_get_all(self):
        crud = FakeCRUD()
        result = crud.get_all(limit=10)
        assert isinstance(result, list)


# ═══════════════════════════════════════════════════════════
# TESTS CACHEABLE PROTOCOL
# ═══════════════════════════════════════════════════════════


class TestCacheableProtocol:
    def test_satisfait(self):
        cacheable = FakeCacheable()
        assert isinstance(cacheable, CacheableProtocol)

    def test_non_satisfait(self):
        assert not isinstance(object(), CacheableProtocol)

    def test_get_cache_stats(self):
        cacheable = FakeCacheable()
        stats = cacheable.get_cache_stats()
        assert stats["hits"] == 10


# ═══════════════════════════════════════════════════════════
# TESTS IO PROTOCOL
# ═══════════════════════════════════════════════════════════


class TestIOProtocol:
    def test_satisfait(self):
        io = FakeIO()
        assert isinstance(io, IOProtocol)

    def test_non_satisfait(self):
        not_io = NotIO()
        assert not isinstance(not_io, IOProtocol)


# ═══════════════════════════════════════════════════════════
# TESTS HEALTH CHECK PROTOCOL
# ═══════════════════════════════════════════════════════════


class TestHealthCheckProtocol:
    def test_satisfait(self):
        healthy = FakeHealthy()
        assert isinstance(healthy, HealthCheckProtocol)

    def test_health_check_retourne_service_health(self):
        healthy = FakeHealthy()
        health = healthy.health_check()
        assert isinstance(health, ServiceHealth)
        assert health.is_healthy is True
        assert health.is_degraded is False
        assert health.service_name == "fake"


# ═══════════════════════════════════════════════════════════
# TESTS OBSERVABLE PROTOCOL
# ═══════════════════════════════════════════════════════════


class TestObservableProtocol:
    def test_satisfait(self):
        observable = FakeObservable()
        assert isinstance(observable, ObservableProtocol)

    def test_non_satisfait(self):
        assert not isinstance(object(), ObservableProtocol)


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
