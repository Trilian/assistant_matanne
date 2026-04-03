"""Mixin: pipeline middleware et health check."""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

logger = logging.getLogger(__name__)


class PipelineMixin:
    """Fournit pipeline property, execute_via_pipeline et health_check.

    Attend sur ``self``: model_name, count.
    """

    _pipeline_instance = None  # Lazy singleton partagé par sous-classes

    @property
    def pipeline(self):
        """Pipeline middleware minimal (lazy, partagé entre instances).

        Utilisé par ``execute_via_pipeline()`` et ``@service_method``.
        Créé au premier accès uniquement.
        """
        if PipelineMixin._pipeline_instance is None:
            from src.services.core.middleware import ServicePipeline

            PipelineMixin._pipeline_instance = ServicePipeline.default()
        return PipelineMixin._pipeline_instance

    def execute_via_pipeline(
        self,
        func: Callable,
        *args: Any,
        cache: bool = False,
        cache_ttl: int = 300,
        rate_limit: bool = False,
        session: bool = False,
        fallback: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Exécute une callable à travers le pipeline middleware.

        Raccourci pour utiliser le pipeline sans le décorateur
        ``@service_method``.  Pratique pour les appels ponctuels.

        Args:
            func: Fonction à exécuter
            *args: Arguments positionnels passés à func
            cache: Activer le cache
            cache_ttl: TTL du cache (secondes)
            rate_limit: Activer le rate limiting
            session: Injecter une session DB
            fallback: Valeur de retour en cas d'erreur
            **kwargs: Arguments nommés passés à func

        Returns:
            Résultat de func

        Example:
            >>> result = self.execute_via_pipeline(
            ...     self._expensive_query,
            ...     cache=True, cache_ttl=600, session=True
            ... )
        """
        from src.services.core.middleware.pipeline import MiddlewareContext

        ctx = MiddlewareContext(
            service_name=self.model_name,
            method_name=func.__name__,
            args=args,
            kwargs=kwargs,
            use_cache=cache,
            cache_ttl=cache_ttl,
            use_rate_limit=rate_limit,
            use_session=session,
            fallback_value=fallback,
        )
        return self.pipeline.execute(func, ctx)

    # ════════════════════════════════════════════════════════════
    # HEALTH CHECK — Satisfait HealthCheckProtocol
    # ════════════════════════════════════════════════════════════

    def health_check(self):
        """Vérifie la santé du service (connexion DB, modèle accessible).

        Returns:
            ServiceHealth avec statut et latence
        """
        import time

        from src.services.core.base.protocols import ServiceHealth, ServiceStatus

        start = time.perf_counter()
        try:
            total = self.count()
            latency = (time.perf_counter() - start) * 1000
            return ServiceHealth(
                status=ServiceStatus.HEALTHY,
                service_name=f"BaseService<{self.model_name}>",
                message=f"{total} entités en base",
                latency_ms=latency,
                details={"model": self.model_name, "count": total},
            )
        except Exception as e:
            latency = (time.perf_counter() - start) * 1000
            return ServiceHealth(
                status=ServiceStatus.UNHEALTHY,
                service_name=f"BaseService<{self.model_name}>",
                message=f"Erreur: {e}",
                latency_ms=latency,
                details={"error": str(e)},
            )
