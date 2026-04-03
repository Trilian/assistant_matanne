"""
Types de santé pour les services.

Contient ServiceStatus et ServiceHealth utilisés par le pipeline,
les diagnostics IA et le registre de services.

Note: Les protocols PEP 544 (CRUDProtocol, AIServiceProtocol, IOProtocol,
CacheableProtocol, HealthCheckProtocol, ObservableProtocol) ont été retirés
car jamais utilisés via isinstance() dans le codebase. Les contrats sont
assurés par BaseAIService et BaseService[T] via héritage classique.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any

# ═══════════════════════════════════════════════════════════
# TYPES DE SANTÉ
# ═══════════════════════════════════════════════════════════


class ServiceStatus(StrEnum):
    """Statuts possibles d'un service."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class ServiceHealth:
    """État de santé d'un service."""

    status: ServiceStatus
    service_name: str
    message: str = ""
    latency_ms: float = 0.0
    details: dict[str, Any] = field(default_factory=dict)
    checked_at: datetime = field(default_factory=datetime.now)

    @property
    def is_healthy(self) -> bool:
        return self.status == ServiceStatus.HEALTHY

    @property
    def is_degraded(self) -> bool:
        return self.status == ServiceStatus.DEGRADED


__all__ = [
    "ServiceStatus",
    "ServiceHealth",
]
