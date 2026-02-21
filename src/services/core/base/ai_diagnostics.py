"""Mixin: métriques, debug et health check pour BaseAIService."""

from __future__ import annotations

import logging

from src.core.ai import RateLimitIA
from src.core.ai.cache import CacheIA

logger = logging.getLogger(__name__)


class AIDiagnosticsMixin:
    """Fournit get_cache_stats, get_rate_limit_stats, clear_cache,
    get_circuit_breaker_stats, reset_circuit_breaker, health_check.

    Attend sur ``self``: client, cache_prefix, service_name, circuit_breaker.
    """

    def get_cache_stats(self) -> dict:
        """Retourne statistiques cache"""
        return CacheIA.obtenir_statistiques()

    def get_rate_limit_stats(self) -> dict:
        """Retourne statistiques rate limiting"""
        return RateLimitIA.obtenir_statistiques()

    def clear_cache(self):
        """Vide le cache"""
        CacheIA.invalider_tout()
        logger.info(f"🗑️ Cache {self.cache_prefix} vidé")

    def get_circuit_breaker_stats(self) -> dict:
        """Retourne statistiques du circuit breaker."""
        return self.circuit_breaker.obtenir_statistiques()

    def reset_circuit_breaker(self):
        """Reset manuel du circuit breaker."""
        self.circuit_breaker.reset()

    # ═══════════════════════════════════════════════════════════
    # HEALTH CHECK — Satisfait HealthCheckProtocol
    # ═══════════════════════════════════════════════════════════

    def health_check(self):
        """Vérifie la santé du service IA (client, rate limit).

        Returns:
            ServiceHealth avec statut, latence et détails quotas
        """
        import time

        from src.services.core.base.protocols import ServiceHealth, ServiceStatus

        start = time.perf_counter()
        details: dict = {"service_name": self.service_name}

        try:
            # Vérifier client
            client_ok = self.client is not None
            details["client_available"] = client_ok

            # Vérifier rate limit
            autorise, msg = RateLimitIA.peut_appeler()
            details["rate_limit_ok"] = autorise
            if not autorise:
                details["rate_limit_message"] = msg

            # Vérifier circuit breaker
            cb_stats = self.circuit_breaker.obtenir_statistiques()
            details["circuit_breaker"] = cb_stats

            # Récupérer stats
            details["rate_limit_stats"] = self.get_rate_limit_stats()
            details["cache_stats"] = self.get_cache_stats()

            latency = (time.perf_counter() - start) * 1000

            if not client_ok:
                return ServiceHealth(
                    status=ServiceStatus.UNHEALTHY,
                    service_name=f"AI:{self.service_name}",
                    message="Client IA indisponible",
                    latency_ms=latency,
                    details=details,
                )

            if not autorise:
                return ServiceHealth(
                    status=ServiceStatus.DEGRADED,
                    service_name=f"AI:{self.service_name}",
                    message=f"Rate limité: {msg}",
                    latency_ms=latency,
                    details=details,
                )

            # Vérifier état du circuit breaker
            from src.core.ai.circuit_breaker import EtatCircuit

            if cb_stats["etat"] != EtatCircuit.FERME.value:
                return ServiceHealth(
                    status=ServiceStatus.DEGRADED,
                    service_name=f"AI:{self.service_name}",
                    message=f"Circuit breaker {cb_stats['etat']} "
                    f"({cb_stats['echecs_consecutifs']} échecs)",
                    latency_ms=latency,
                    details=details,
                )

            return ServiceHealth(
                status=ServiceStatus.HEALTHY,
                service_name=f"AI:{self.service_name}",
                message="Service IA opérationnel",
                latency_ms=latency,
                details=details,
            )
        except Exception as e:
            latency = (time.perf_counter() - start) * 1000
            return ServiceHealth(
                status=ServiceStatus.UNHEALTHY,
                service_name=f"AI:{self.service_name}",
                message=f"Erreur health check: {e}",
                latency_ms=latency,
                details={"error": str(e)},
            )
