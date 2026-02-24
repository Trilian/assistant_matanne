"""
Métriques et observabilité pour l'API REST.

Fournit des compteurs et histogrammes pour le monitoring.
"""

import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from starlette.types import ASGIApp, Message, Receive, Scope, Send

logger = logging.getLogger(__name__)


@dataclass
class MetricsStore:
    """Stockage des métriques en mémoire."""

    # Compteurs de requêtes par endpoint
    requests_total: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    requests_success: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    requests_errors: dict[str, int] = field(default_factory=lambda: defaultdict(int))

    # Histogrammes de latence (en ms)
    latency_samples: dict[str, list[float]] = field(default_factory=lambda: defaultdict(list))

    # Métriques rate limiting
    rate_limit_hits: dict[str, int] = field(default_factory=lambda: defaultdict(int))

    # Compteurs IA
    ai_requests_total: int = 0
    ai_tokens_used: int = 0

    # Timestamp de démarrage
    start_time: datetime = field(default_factory=datetime.now)


# Instance globale
_metrics = MetricsStore()


# Limite maximale d'échantillons de latence par endpoint (borne mémoire)
MAX_LATENCY_SAMPLES = 1000

# Limite maximale d'endpoints uniques trackés (prévention memory exhaustion)
MAX_TRACKED_ENDPOINTS = 500


def record_request(endpoint: str, method: str, status_code: int, latency_ms: float):
    """Enregistre une requête dans les métriques."""
    key = f"{method}:{endpoint}"

    # Borner le nombre d'endpoints trackés pour éviter l'exhaustion mémoire
    if key not in _metrics.requests_total and len(_metrics.requests_total) >= MAX_TRACKED_ENDPOINTS:
        return

    _metrics.requests_total[key] += 1

    if 200 <= status_code < 400:
        _metrics.requests_success[key] += 1
    else:
        _metrics.requests_errors[key] += 1

    # Limite à MAX_LATENCY_SAMPLES échantillons par endpoint
    if len(_metrics.latency_samples[key]) < MAX_LATENCY_SAMPLES:
        _metrics.latency_samples[key].append(latency_ms)


def record_rate_limit_hit(identifier: str):
    """Enregistre un blocage rate limit."""
    _metrics.rate_limit_hits[identifier] += 1


def record_ai_request(tokens_used: int = 0):
    """Enregistre une requête IA."""
    _metrics.ai_requests_total += 1
    _metrics.ai_tokens_used += tokens_used


def get_metrics() -> dict[str, Any]:
    """Retourne toutes les métriques."""
    uptime = (datetime.now() - _metrics.start_time).total_seconds()

    # Calcul des percentiles de latence
    latency_stats = {}
    for endpoint, samples in _metrics.latency_samples.items():
        if samples:
            sorted_samples = sorted(samples)
            latency_stats[endpoint] = {
                "count": len(samples),
                "avg_ms": sum(samples) / len(samples),
                "p50_ms": sorted_samples[len(samples) // 2],
                "p95_ms": sorted_samples[int(len(samples) * 0.95)] if len(samples) >= 20 else None,
                "p99_ms": sorted_samples[int(len(samples) * 0.99)] if len(samples) >= 100 else None,
            }

    return {
        "uptime_seconds": uptime,
        "requests": {
            "total": dict(_metrics.requests_total),
            "success": dict(_metrics.requests_success),
            "errors": dict(_metrics.requests_errors),
        },
        "latency": latency_stats,
        "rate_limiting": {
            "hits": dict(_metrics.rate_limit_hits),
        },
        "ai": {
            "requests_total": _metrics.ai_requests_total,
            "tokens_used": _metrics.ai_tokens_used,
        },
    }


def reset_metrics():
    """Réinitialise les métriques (pour les tests)."""
    global _metrics
    _metrics = MetricsStore()


class MetricsMiddleware:
    """
    Middleware pour collecter les métriques automatiquement.

    Usage:
        app.add_middleware(MetricsMiddleware)
    """

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start_time = time.time()
        status_code = 500  # Par défaut

        async def send_wrapper(message: Message) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            latency_ms = (time.time() - start_time) * 1000
            path = str(scope.get("path", "/"))
            method = str(scope.get("method", "GET"))
            record_request(path, method, status_code, latency_ms)
