"""
Health Checks par Service — Monitoring granulaire.

Permet à chaque service d'enregistrer ses propres vérifications de santé
qui sont agrégées dans le système de monitoring global.

Usage:
    from src.services.core.service_health import (
        ServiceHealthMixin,
        ServiceHealthCheck,
        enregistrer_health_service,
        obtenir_sante_services,
    )

    # Via Mixin (recommandé)
    class MonService(ServiceHealthMixin, BaseService):
        def _health_check_custom(self) -> ServiceHealthCheck:
            return ServiceHealthCheck(
                service="mon_service",
                status="healthy",
                details={"cache_size": 100}
            )

    # Via enregistrement manuel
    enregistrer_health_service("mon_service", lambda: check_fn())

    # Obtenir l'état de tous les services
    sante = obtenir_sante_services()
"""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Callable, Protocol, runtime_checkable

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# TYPES
# ═══════════════════════════════════════════════════════════


class StatutService(Enum):
    """États de santé d'un service."""

    HEALTHY = auto()
    DEGRADED = auto()
    UNHEALTHY = auto()
    UNKNOWN = auto()

    def __str__(self) -> str:
        return self.name.lower()


@dataclass
class ServiceHealthCheck:
    """Résultat d'un health check de service."""

    service: str
    status: StatutService | str
    message: str = ""
    details: dict[str, Any] = field(default_factory=dict)
    latency_ms: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    dependencies: dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        if isinstance(self.status, str):
            try:
                self.status = StatutService[self.status.upper()]
            except KeyError:
                self.status = StatutService.UNKNOWN

    def is_healthy(self) -> bool:
        """Retourne True si le service est en bonne santé."""
        return self.status == StatutService.HEALTHY

    def to_dict(self) -> dict[str, Any]:
        """Convertit en dictionnaire pour sérialisation."""
        return {
            "service": self.service,
            "status": str(self.status),
            "message": self.message,
            "details": self.details,
            "latency_ms": self.latency_ms,
            "timestamp": self.timestamp.isoformat(),
            "dependencies": self.dependencies,
        }


@dataclass
class HealthCheckResult:
    """Résultat agrégé des health checks."""

    global_status: StatutService
    total_services: int
    healthy_count: int
    degraded_count: int
    unhealthy_count: int
    services: dict[str, ServiceHealthCheck] = field(default_factory=dict)
    check_duration_ms: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        """Convertit en dictionnaire pour sérialisation JSON."""
        return {
            "global_status": str(self.global_status),
            "total_services": self.total_services,
            "healthy_count": self.healthy_count,
            "degraded_count": self.degraded_count,
            "unhealthy_count": self.unhealthy_count,
            "check_duration_ms": self.check_duration_ms,
            "timestamp": self.timestamp.isoformat(),
            "services": {k: v.to_dict() for k, v in self.services.items()},
        }


# ═══════════════════════════════════════════════════════════
# PROTOCOL
# ═══════════════════════════════════════════════════════════


@runtime_checkable
class HealthCheckable(Protocol):
    """Protocol pour les services avec health check."""

    def health_check(self) -> ServiceHealthCheck: ...


# ═══════════════════════════════════════════════════════════
# REGISTRE HEALTH CHECKS
# ═══════════════════════════════════════════════════════════

_health_registry: dict[str, Callable[[], ServiceHealthCheck]] = {}
_registry_lock = threading.Lock()


def enregistrer_health_service(
    nom: str,
    check_fn: Callable[[], ServiceHealthCheck],
) -> None:
    """Enregistre une fonction de health check pour un service.

    Args:
        nom: Nom du service
        check_fn: Fonction retournant ServiceHealthCheck
    """
    with _registry_lock:
        _health_registry[nom] = check_fn
        logger.debug(f"🏥 Health check enregistré: {nom}")


def desenregistrer_health_service(nom: str) -> bool:
    """Retire un health check du registre.

    Returns:
        True si le service a été retiré
    """
    with _registry_lock:
        if nom in _health_registry:
            del _health_registry[nom]
            return True
        return False


def obtenir_sante_services(
    services: list[str] | None = None,
    inclure_details: bool = True,
) -> HealthCheckResult:
    """Exécute les health checks de tous les services ou d'une sélection.

    Args:
        services: Liste des services à vérifier (None = tous)
        inclure_details: Inclure les détails par service

    Returns:
        HealthCheckResult agrégé
    """
    start = time.perf_counter()
    results: dict[str, ServiceHealthCheck] = {}

    with _registry_lock:
        checks_to_run = _health_registry.copy()

    if services:
        checks_to_run = {k: v for k, v in checks_to_run.items() if k in services}

    healthy = 0
    degraded = 0
    unhealthy = 0

    for nom, check_fn in checks_to_run.items():
        try:
            check_start = time.perf_counter()
            result = check_fn()
            result.latency_ms = (time.perf_counter() - check_start) * 1000

            if result.status == StatutService.HEALTHY:
                healthy += 1
            elif result.status == StatutService.DEGRADED:
                degraded += 1
            else:
                unhealthy += 1

            if inclure_details:
                results[nom] = result

        except Exception as e:
            unhealthy += 1
            logger.error(f"❌ Health check {nom} échoué: {e}")
            if inclure_details:
                results[nom] = ServiceHealthCheck(
                    service=nom,
                    status=StatutService.UNHEALTHY,
                    message=f"Erreur: {e}",
                )

    # Déterminer le statut global
    if unhealthy > 0:
        global_status = StatutService.UNHEALTHY
    elif degraded > 0:
        global_status = StatutService.DEGRADED
    elif healthy == 0:
        global_status = StatutService.UNKNOWN
    else:
        global_status = StatutService.HEALTHY

    return HealthCheckResult(
        global_status=global_status,
        total_services=len(checks_to_run),
        healthy_count=healthy,
        degraded_count=degraded,
        unhealthy_count=unhealthy,
        services=results,
        check_duration_ms=(time.perf_counter() - start) * 1000,
    )


def lister_services_health() -> list[str]:
    """Liste les services avec health check enregistré."""
    with _registry_lock:
        return list(_health_registry.keys())


# ═══════════════════════════════════════════════════════════
# MIXIN POUR SERVICES
# ═══════════════════════════════════════════════════════════


class ServiceHealthMixin:
    """Mixin ajoutant le support health check à un service.

    Usage:
        class MonService(ServiceHealthMixin, BaseService[Model]):
            def __init__(self):
                super().__init__()
                self._register_health_check()

            def _health_check_custom(self) -> ServiceHealthCheck:
                # Vérifications personnalisées
                return ServiceHealthCheck(
                    service=self.service_name,
                    status="healthy"
                )
    """

    # Attributs attendus (définis par la classe parente)
    service_name: str = "unknown"
    _cache_prefix: str = ""

    def _register_health_check(self) -> None:
        """Enregistre le health check de ce service dans le registre global."""
        name = getattr(self, "service_name", self.__class__.__name__.lower())
        enregistrer_health_service(name, self.health_check)

    def health_check(self) -> ServiceHealthCheck:
        """Effectue le health check du service.

        Par défaut, vérifie que le service est instancié et fonctionnel.
        Surcharger _health_check_custom() pour des vérifications spécifiques.
        """
        start = time.perf_counter()
        try:
            # Vérification de base
            status = StatutService.HEALTHY
            details: dict[str, Any] = {
                "class": self.__class__.__name__,
            }
            message = "Service opérationnel"

            # Vérifier le cache si présent
            if hasattr(self, "_cache_prefix") and self._cache_prefix:
                details["cache_prefix"] = self._cache_prefix

            # Vérifier le client IA si présent (BaseAIService)
            if hasattr(self, "client") and self.client is not None:
                details["ia_enabled"] = True
                # Vérifier le rate limiter
                if hasattr(self, "_rate_limiter"):
                    stats = getattr(self._rate_limiter, "obtenir_statistiques", lambda: {})()
                    remaining = stats.get("appels_restants_jour", -1)
                    if remaining == 0:
                        status = StatutService.DEGRADED
                        message = "Rate limit atteint"
                    details["ia_rate_limit_remaining"] = remaining

            # Vérifications personnalisées
            if hasattr(self, "_health_check_custom"):
                custom = self._health_check_custom()
                if custom.status != StatutService.HEALTHY:
                    status = custom.status
                    message = custom.message
                details.update(custom.details)

            latency = (time.perf_counter() - start) * 1000
            return ServiceHealthCheck(
                service=getattr(self, "service_name", self.__class__.__name__.lower()),
                status=status,
                message=message,
                details=details,
                latency_ms=latency,
            )

        except Exception as e:
            return ServiceHealthCheck(
                service=getattr(self, "service_name", self.__class__.__name__.lower()),
                status=StatutService.UNHEALTHY,
                message=f"Erreur health check: {e}",
                latency_ms=(time.perf_counter() - start) * 1000,
            )

    def _health_check_custom(self) -> ServiceHealthCheck:
        """Hook pour vérifications personnalisées. À surcharger."""
        return ServiceHealthCheck(
            service=getattr(self, "service_name", "unknown"),
            status=StatutService.HEALTHY,
        )


# ═══════════════════════════════════════════════════════════
# INTÉGRATION AVEC core/monitoring/health.py
# ═══════════════════════════════════════════════════════════


def _verifier_services() -> SanteComposant:
    """Vérification santé des services pour le système de monitoring global."""
    from src.core.monitoring.health import SanteComposant, StatutSante

    start = time.perf_counter()
    result = obtenir_sante_services(inclure_details=False)
    duree = (time.perf_counter() - start) * 1000

    # Mapper le statut
    if result.global_status == StatutService.HEALTHY:
        statut = StatutSante.SAIN
    elif result.global_status == StatutService.DEGRADED:
        statut = StatutSante.DEGRADE
    elif result.global_status == StatutService.UNHEALTHY:
        statut = StatutSante.CRITIQUE
    else:
        statut = StatutSante.INCONNU

    return SanteComposant(
        nom="services",
        statut=statut,
        message=f"{result.healthy_count}/{result.total_services} services OK",
        details={
            "total": result.total_services,
            "healthy": result.healthy_count,
            "degraded": result.degraded_count,
            "unhealthy": result.unhealthy_count,
        },
        duree_verification_ms=duree,
    )


def initialiser_health_services() -> None:
    """Initialise l'intégration avec le système de monitoring global."""
    from src.core.monitoring.health import enregistrer_verification

    enregistrer_verification("services", _verifier_services)
    logger.info("🏥 Health checks services intégrés au monitoring global")


__all__ = [
    "StatutService",
    "ServiceHealthCheck",
    "HealthCheckResult",
    "HealthCheckable",
    "ServiceHealthMixin",
    "enregistrer_health_service",
    "desenregistrer_health_service",
    "obtenir_sante_services",
    "lister_services_health",
    "initialiser_health_services",
]
