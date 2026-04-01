"""
Métriques et observabilité pour l'API REST.

Fournit des compteurs et histogrammes pour le monitoring.
Rolling windows pour les latences (fenêtres glissantes de 15 min).
"""

import logging
import os
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from starlette.types import ASGIApp, Message, Receive, Scope, Send

logger = logging.getLogger(__name__)

# Fenêtre glissante pour les échantillons de latence (en secondes)
ROLLING_WINDOW_SECONDS = 900  # 15 minutes


@dataclass
class MetricsStore:
    """Stockage des métriques en mémoire avec rolling windows."""

    # Compteurs de requêtes par endpoint
    requests_total: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    requests_success: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    requests_errors: dict[str, int] = field(default_factory=lambda: defaultdict(int))

    # Rolling windows de latence: deque de (timestamp, latency_ms)
    latency_windows: dict[str, deque[tuple[float, float]]] = field(
        default_factory=lambda: defaultdict(lambda: deque(maxlen=MAX_LATENCY_SAMPLES))
    )

    # Métriques rate limiting
    rate_limit_hits: dict[str, int] = field(default_factory=lambda: defaultdict(int))

    # Compteurs IA
    ai_requests_total: int = 0
    ai_tokens_used: int = 0

    # Timestamp de démarrage
    start_time: datetime = field(default_factory=lambda: datetime.now(UTC))


# Instance globale
_metrics = MetricsStore()


# Limite maximale d'échantillons de latence par endpoint (borne mémoire)
MAX_LATENCY_SAMPLES = 1000

# Limite maximale d'endpoints uniques trackés (prévention memory exhaustion)
MAX_TRACKED_ENDPOINTS = 500

# Estimation coût IA (EUR) selon le volume de tokens consommés.
_AI_COST_PER_1K_TOKENS_EUR = float(os.getenv("AI_COST_PER_1K_TOKENS_EUR", "0.002"))
_AI_BUDGET_MENSUEL_EUR = float(os.getenv("AI_BUDGET_MENSUEL_EUR", "20"))


def record_request(endpoint: str, method: str, status_code: int, latency_ms: float):
    """Enregistre une requête dans les métriques (rolling window)."""
    key = f"{method}:{endpoint}"

    # Borner le nombre d'endpoints trackés pour éviter l'exhaustion mémoire
    if key not in _metrics.requests_total and len(_metrics.requests_total) >= MAX_TRACKED_ENDPOINTS:
        # Log l'avertissement une seule fois quand la limite est atteinte
        if len(_metrics.requests_total) == MAX_TRACKED_ENDPOINTS:
            logger.warning(
                f"Limite de {MAX_TRACKED_ENDPOINTS} endpoints métriques atteinte. "
                f"Endpoint ignoré: {key}"
            )
        return

    _metrics.requests_total[key] += 1

    if 200 <= status_code < 400:
        _metrics.requests_success[key] += 1
    else:
        _metrics.requests_errors[key] += 1

    # Rolling window: ajouter (timestamp, latency_ms)
    now = time.monotonic()
    window = _metrics.latency_windows[key]
    window.append((now, latency_ms))
    # Élaguer les entrées hors fenêtre
    cutoff = now - ROLLING_WINDOW_SECONDS
    while window and window[0][0] < cutoff:
        window.popleft()


def record_rate_limit_hit(identifier: str):
    """Enregistre un blocage rate limit."""
    _metrics.rate_limit_hits[identifier] += 1


def record_ai_request(tokens_used: int = 0):
    """Enregistre une requête IA."""
    _metrics.ai_requests_total += 1
    _metrics.ai_tokens_used += tokens_used


def get_metrics() -> dict[str, Any]:
    """Retourne toutes les métriques (latences calculées sur rolling window)."""
    uptime = (datetime.now(UTC) - _metrics.start_time).total_seconds()
    now = time.monotonic()
    cutoff = now - ROLLING_WINDOW_SECONDS

    # Calcul des percentiles de latence sur la fenêtre glissante
    latency_stats = {}
    for endpoint, window in _metrics.latency_windows.items():
        # Filtrer les échantillons dans la fenêtre
        samples = [lat for ts, lat in window if ts >= cutoff]
        if samples:
            sorted_samples = sorted(samples)
            n = len(sorted_samples)
            latency_stats[endpoint] = {
                "count": n,
                "window_seconds": ROLLING_WINDOW_SECONDS,
                "avg_ms": sum(samples) / n,
                "p50_ms": sorted_samples[n // 2],
                "p95_ms": sorted_samples[int(n * 0.95)] if n >= 20 else None,
                "p99_ms": sorted_samples[int(n * 0.99)] if n >= 100 else None,
            }

    ai_cost_eur = (_metrics.ai_tokens_used / 1000.0) * _AI_COST_PER_1K_TOKENS_EUR
    budget_utilisation_pct = (
        min((ai_cost_eur / _AI_BUDGET_MENSUEL_EUR) * 100.0, 100.0)
        if _AI_BUDGET_MENSUEL_EUR > 0
        else 0.0
    )

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
            "estimated_cost_eur": round(ai_cost_eur, 4),
            "budget_mensuel_eur": round(_AI_BUDGET_MENSUEL_EUR, 2),
            "budget_utilisation_pct": round(budget_utilisation_pct, 2),
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
