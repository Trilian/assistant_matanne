"""
Protocols - Contrats d'interface pour les services (PEP 544).

Définit les contrats structurels que les services doivent respecter.
Utilise le structural subtyping (duck typing typé) — pas besoin d'hériter
explicitement, il suffit d'implémenter les méthodes.

Usage:
    from src.services.core.base.protocols import CRUDProtocol, AIServiceProtocol

    def process(service: CRUDProtocol[Recette]) -> list[Recette]:
        return service.get_all(limit=10)

    # Fonctionne avec tout service qui a les bonnes méthodes,
    # même sans héritage explicite du Protocol.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Protocol, TypeVar, runtime_checkable

from pydantic import BaseModel
from sqlalchemy.orm import Session

T = TypeVar("T")


# ═══════════════════════════════════════════════════════════
# PROTOCOL: CRUD
# ═══════════════════════════════════════════════════════════


@runtime_checkable
class CRUDProtocol(Protocol[T]):
    """
    Contrat pour les opérations CRUD.

    Tout service implémentant ces méthodes est automatiquement
    compatible, même sans héritage explicite.
    """

    def create(self, data: dict, db: Session | None = None) -> T: ...

    def get_by_id(self, entity_id: int, db: Session | None = None) -> T | None: ...

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: dict | None = None,
        order_by: str = "id",
        desc_order: bool = False,
        db: Session | None = None,
    ) -> list[T]: ...

    def update(self, entity_id: int, data: dict, db: Session | None = None) -> T | None: ...

    def delete(self, entity_id: int, db: Session | None = None) -> bool: ...

    def count(self, filters: dict | None = None, db: Session | None = None) -> int: ...


# ═══════════════════════════════════════════════════════════
# PROTOCOL: AI SERVICE
# ═══════════════════════════════════════════════════════════


@runtime_checkable
class AIServiceProtocol(Protocol):
    """
    Contrat pour les services IA.

    Garantit que tout service utilisant l'IA passe par le rate limiting
    et le cache. Empêche le bypass accidentel de l'infrastructure IA.
    """

    service_name: str

    async def call_with_cache(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float | None = None,
        max_tokens: int = 1000,
        use_cache: bool = True,
        category: str | None = None,
    ) -> str | None: ...

    async def call_with_parsing(
        self,
        prompt: str,
        response_model: type[BaseModel],
        system_prompt: str = "",
        temperature: float | None = None,
        max_tokens: int = 1000,
        use_cache: bool = True,
        fallback: dict | None = None,
    ) -> BaseModel | None: ...

    def get_cache_stats(self) -> dict: ...

    def get_rate_limit_stats(self) -> dict: ...

    def clear_cache(self) -> None: ...


# ═══════════════════════════════════════════════════════════
# PROTOCOL: IO (IMPORT/EXPORT)
# ═══════════════════════════════════════════════════════════


@runtime_checkable
class IOProtocol(Protocol):
    """Contrat pour les services d'import/export."""

    def exporter_csv(self, data: list[dict], colonnes: list[str] | None = None) -> str: ...

    def exporter_json(self, data: list[dict]) -> str: ...

    def importer_csv(self, contenu: str, mapping: dict[str, str] | None = None) -> list[dict]: ...


# ═══════════════════════════════════════════════════════════
# PROTOCOL: CACHEABLE
# ═══════════════════════════════════════════════════════════


@runtime_checkable
class CacheableProtocol(Protocol):
    """Contrat pour les services avec cache intégré."""

    def clear_cache(self) -> None: ...

    def get_cache_stats(self) -> dict: ...


# ═══════════════════════════════════════════════════════════
# PROTOCOL: HEALTH CHECK
# ═══════════════════════════════════════════════════════════


class ServiceStatus(str, Enum):
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


@runtime_checkable
class HealthCheckProtocol(Protocol):
    """Contrat pour les services avec health check."""

    def health_check(self) -> ServiceHealth: ...


# ═══════════════════════════════════════════════════════════
# PROTOCOL: OBSERVABLE (pour Event Bus)
# ═══════════════════════════════════════════════════════════


@runtime_checkable
class ObservableProtocol(Protocol):
    """Contrat pour les services qui émettent des événements."""

    def subscribe(self, event_type: str, handler: Any) -> None: ...

    def unsubscribe(self, event_type: str, handler: Any) -> None: ...


__all__ = [
    # Protocols
    "CRUDProtocol",
    "AIServiceProtocol",
    "IOProtocol",
    "CacheableProtocol",
    "HealthCheckProtocol",
    "ObservableProtocol",
    # Types
    "ServiceStatus",
    "ServiceHealth",
    # TypeVars
    "T",
]
