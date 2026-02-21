"""
Health — Health checks pour les services.

Système de health check centralisé pour surveiller l'état
des services et dépendances.

Usage:
    from src.services.core.observability import (
        HealthCheck, HealthStatus, health_registry
    )

    # Définir un health check
    @health_registry.register("database")
    def check_database() -> HealthCheck:
        try:
            db.execute("SELECT 1")
            return HealthCheck.healthy("database", "Connected")
        except Exception as e:
            return HealthCheck.unhealthy("database", str(e))

    # Vérifier la santé globale
    status = health_registry.check_all()
    if status.is_healthy:
        print("Tous les services sont opérationnels")
"""

from __future__ import annotations

import logging
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, StrEnum
from typing import Any

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# TYPES
# ═══════════════════════════════════════════════════════════


class HealthStatus(StrEnum):
    """Statuts de santé possibles."""

    HEALTHY = "healthy"  # Service opérationnel
    DEGRADED = "degraded"  # Service partiellement fonctionnel
    UNHEALTHY = "unhealthy"  # Service non fonctionnel
    UNKNOWN = "unknown"  # Statut inconnu


@dataclass(frozen=True, slots=True)
class HealthCheck:
    """
    Résultat d'un health check individuel.

    Attributes:
        name: Nom du service/composant vérifié.
        status: Statut de santé.
        message: Message descriptif.
        latency_ms: Temps de vérification en ms.
        details: Détails supplémentaires.
        checked_at: Horodatage de la vérification.
    """

    name: str
    status: HealthStatus
    message: str = ""
    latency_ms: float = 0.0
    details: dict[str, Any] = field(default_factory=dict)
    checked_at: datetime = field(default_factory=datetime.now)

    @property
    def is_healthy(self) -> bool:
        """Retourne True si le statut est HEALTHY."""
        return self.status == HealthStatus.HEALTHY

    @property
    def is_degraded(self) -> bool:
        """Retourne True si le statut est DEGRADED."""
        return self.status == HealthStatus.DEGRADED

    @property
    def is_unhealthy(self) -> bool:
        """Retourne True si le statut est UNHEALTHY."""
        return self.status == HealthStatus.UNHEALTHY

    def to_dict(self) -> dict[str, Any]:
        """Sérialise le health check."""
        return {
            "name": self.name,
            "status": self.status.value,
            "message": self.message,
            "latency_ms": self.latency_ms,
            "details": self.details,
            "checked_at": self.checked_at.isoformat(),
        }

    # ───────────────────────────────────────────────────────
    # FACTORY METHODS
    # ───────────────────────────────────────────────────────

    @classmethod
    def healthy(
        cls,
        name: str,
        message: str = "OK",
        latency_ms: float = 0.0,
        **details,
    ) -> HealthCheck:
        """Crée un health check HEALTHY."""
        return cls(
            name=name,
            status=HealthStatus.HEALTHY,
            message=message,
            latency_ms=latency_ms,
            details=details,
        )

    @classmethod
    def degraded(
        cls,
        name: str,
        message: str,
        latency_ms: float = 0.0,
        **details,
    ) -> HealthCheck:
        """Crée un health check DEGRADED."""
        return cls(
            name=name,
            status=HealthStatus.DEGRADED,
            message=message,
            latency_ms=latency_ms,
            details=details,
        )

    @classmethod
    def unhealthy(
        cls,
        name: str,
        message: str,
        latency_ms: float = 0.0,
        **details,
    ) -> HealthCheck:
        """Crée un health check UNHEALTHY."""
        return cls(
            name=name,
            status=HealthStatus.UNHEALTHY,
            message=message,
            latency_ms=latency_ms,
            details=details,
        )


# ═══════════════════════════════════════════════════════════
# SERVICE HEALTH (Agrégation)
# ═══════════════════════════════════════════════════════════


@dataclass
class ServiceHealth:
    """
    État de santé agrégé de tous les services.

    Attributes:
        checks: Liste des health checks individuels.
        overall_status: Statut global (le pire des statuts individuels).
        total_latency_ms: Temps total de vérification.
    """

    checks: list[HealthCheck] = field(default_factory=list)
    overall_status: HealthStatus = HealthStatus.UNKNOWN
    total_latency_ms: float = 0.0
    checked_at: datetime = field(default_factory=datetime.now)

    @property
    def is_healthy(self) -> bool:
        """Retourne True si le statut global est HEALTHY."""
        return self.overall_status == HealthStatus.HEALTHY

    @property
    def healthy_count(self) -> int:
        """Nombre de services HEALTHY."""
        return sum(1 for c in self.checks if c.is_healthy)

    @property
    def unhealthy_count(self) -> int:
        """Nombre de services UNHEALTHY."""
        return sum(1 for c in self.checks if c.is_unhealthy)

    def to_dict(self) -> dict[str, Any]:
        """Sérialise l'état de santé."""
        return {
            "overall_status": self.overall_status.value,
            "is_healthy": self.is_healthy,
            "total_latency_ms": self.total_latency_ms,
            "checked_at": self.checked_at.isoformat(),
            "summary": {
                "total": len(self.checks),
                "healthy": self.healthy_count,
                "unhealthy": self.unhealthy_count,
            },
            "checks": [c.to_dict() for c in self.checks],
        }


# ═══════════════════════════════════════════════════════════
# HEALTH REGISTRY
# ═══════════════════════════════════════════════════════════

# Type pour les fonctions de health check
HealthCheckFunc = Callable[[], HealthCheck]


class HealthRegistry:
    """
    Registre centralisé des health checks.

    Permet d'enregistrer et d'exécuter les health checks
    de tous les services.

    Usage:
        registry = HealthRegistry()

        @registry.register("database")
        def check_db() -> HealthCheck:
            ...

        # Ou manuellement
        registry.add("cache", check_cache_func)

        # Vérifier tout
        health = registry.check_all()
    """

    def __init__(self):
        self._checks: dict[str, HealthCheckFunc] = {}
        self._lock = threading.Lock()

    def register(self, name: str) -> Callable[[HealthCheckFunc], HealthCheckFunc]:
        """
        Décorateur pour enregistrer un health check.

        Args:
            name: Nom du composant à vérifier.

        Returns:
            Décorateur.

        Example:
            @registry.register("database")
            def check_database() -> HealthCheck:
                ...
        """

        def decorator(func: HealthCheckFunc) -> HealthCheckFunc:
            self.add(name, func)
            return func

        return decorator

    def add(self, name: str, check_func: HealthCheckFunc) -> None:
        """
        Ajoute un health check au registre.

        Args:
            name: Nom du composant.
            check_func: Fonction de vérification.
        """
        with self._lock:
            self._checks[name] = check_func
            logger.debug(f"🏥 Health check enregistré: {name}")

    def remove(self, name: str) -> bool:
        """
        Retire un health check du registre.

        Args:
            name: Nom du composant.

        Returns:
            True si trouvé et retiré.
        """
        with self._lock:
            if name in self._checks:
                del self._checks[name]
                return True
            return False

    def check(self, name: str) -> HealthCheck:
        """
        Exécute un health check spécifique.

        Args:
            name: Nom du composant.

        Returns:
            Résultat du health check.

        Raises:
            KeyError: Si le check n'existe pas.
        """
        with self._lock:
            check_func = self._checks.get(name)

        if check_func is None:
            return HealthCheck(
                name=name,
                status=HealthStatus.UNKNOWN,
                message=f"Health check '{name}' non trouvé",
            )

        start = time.perf_counter()
        try:
            result = check_func()
            latency = (time.perf_counter() - start) * 1000

            # Mettre à jour la latence si pas déjà définie
            if result.latency_ms == 0.0:
                result = HealthCheck(
                    name=result.name,
                    status=result.status,
                    message=result.message,
                    latency_ms=latency,
                    details=result.details,
                )

            return result

        except Exception as e:
            latency = (time.perf_counter() - start) * 1000
            logger.error(f"Erreur health check {name}: {e}")
            return HealthCheck.unhealthy(name, f"Exception: {e}", latency_ms=latency)

    def check_all(self) -> ServiceHealth:
        """
        Exécute tous les health checks.

        Returns:
            État de santé agrégé.
        """
        start = time.perf_counter()
        checks: list[HealthCheck] = []

        with self._lock:
            check_names = list(self._checks.keys())

        for name in check_names:
            checks.append(self.check(name))

        total_latency = (time.perf_counter() - start) * 1000

        # Déterminer le statut global (le pire gagne)
        if not checks:
            overall = HealthStatus.UNKNOWN
        elif any(c.status == HealthStatus.UNHEALTHY for c in checks):
            overall = HealthStatus.UNHEALTHY
        elif any(c.status == HealthStatus.DEGRADED for c in checks):
            overall = HealthStatus.DEGRADED
        elif all(c.status == HealthStatus.HEALTHY for c in checks):
            overall = HealthStatus.HEALTHY
        else:
            overall = HealthStatus.UNKNOWN

        return ServiceHealth(
            checks=checks,
            overall_status=overall,
            total_latency_ms=total_latency,
        )

    def list_checks(self) -> list[str]:
        """Liste les health checks enregistrés."""
        with self._lock:
            return list(self._checks.keys())


# ═══════════════════════════════════════════════════════════
# SINGLETON
# ═══════════════════════════════════════════════════════════

_registry: HealthRegistry | None = None
_registry_lock = threading.Lock()


def get_health_registry() -> HealthRegistry:
    """Obtient le registre global de health checks."""
    global _registry
    if _registry is None:
        with _registry_lock:
            if _registry is None:
                _registry = HealthRegistry()
    return _registry


# Alias pour import direct
health_registry = get_health_registry()


# ═══════════════════════════════════════════════════════════
# HEALTH CHECKS PRÉDÉFINIS
# ═══════════════════════════════════════════════════════════


def register_default_checks() -> None:
    """Enregistre les health checks par défaut."""
    registry = get_health_registry()

    @registry.register("database")
    def check_database() -> HealthCheck:
        """Vérifie la connexion à la base de données."""
        try:
            from src.core.db import obtenir_moteur

            engine = obtenir_moteur()
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            return HealthCheck.healthy("database", "PostgreSQL connected")
        except Exception as e:
            return HealthCheck.unhealthy("database", str(e))

    @registry.register("cache")
    def check_cache() -> HealthCheck:
        """Vérifie le système de cache."""
        try:
            from src.core.caching import Cache

            # Tester un write/read
            test_key = "_health_check_test"
            Cache.definir(test_key, "ok", ttl=10)
            value = Cache.obtenir(test_key)
            Cache.supprimer(test_key)

            if value == "ok":
                return HealthCheck.healthy("cache", "Cache operational")
            return HealthCheck.degraded("cache", "Cache read mismatch")
        except Exception as e:
            return HealthCheck.unhealthy("cache", str(e))

    @registry.register("ai")
    def check_ai() -> HealthCheck:
        """Vérifie le service IA (rate limit status)."""
        try:
            from src.core.ai import RateLimitIA

            autorise, msg = RateLimitIA.peut_appeler()
            if autorise:
                return HealthCheck.healthy("ai", "AI service available")
            return HealthCheck.degraded("ai", f"Rate limited: {msg}")
        except Exception as e:
            return HealthCheck.unhealthy("ai", str(e))
