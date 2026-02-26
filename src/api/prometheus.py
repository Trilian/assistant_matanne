"""
Métriques Prometheus pour l'API REST.

Expose un endpoint /metrics/prometheus au format Prometheus standard avec:
- Compteurs de requêtes par endpoint, méthode et code HTTP
- Histogrammes de latence
- Métriques rate limiting
- Métriques IA (requêtes, tokens)
- Métriques système (uptime, mémoire)

Usage:
    # Ajouter dans main.py:
    from src.api.prometheus import prometheus_router
    app.include_router(prometheus_router)

    # Scrape Prometheus:
    curl http://localhost:8000/metrics/prometheus
"""

import logging
import os
import time
from typing import Any

from fastapi import APIRouter, Depends, Response

from src.api.dependencies import require_role

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Métriques"])


# ═══════════════════════════════════════════════════════════
# FORMAT PROMETHEUS
# ═══════════════════════════════════════════════════════════


def _format_prometheus_metric(
    name: str,
    value: float | int,
    metric_type: str = "gauge",
    help_text: str = "",
    labels: dict[str, str] | None = None,
) -> str:
    """
    Formate une métrique au format Prometheus text exposition.

    Args:
        name: Nom de la métrique (ex: http_requests_total)
        value: Valeur de la métrique
        metric_type: Type (counter, gauge, histogram, summary)
        help_text: Description de la métrique
        labels: Labels optionnels {label_name: label_value}

    Returns:
        Texte formaté Prometheus
    """
    lines = []

    if help_text:
        lines.append(f"# HELP {name} {help_text}")
    lines.append(f"# TYPE {name} {metric_type}")

    if labels:
        labels_str = ",".join(f'{k}="{v}"' for k, v in labels.items())
        lines.append(f"{name}{{{labels_str}}} {value}")
    else:
        lines.append(f"{name} {value}")

    return "\n".join(lines)


def _format_histogram_prometheus(
    name: str,
    samples: list[float],
    help_text: str = "",
    labels: dict[str, str] | None = None,
) -> str:
    """
    Formate un histogramme avec buckets Prometheus.

    Utilise les buckets standards: 5ms, 10ms, 25ms, 50ms, 100ms, 250ms, 500ms, 1s, 2.5s, 5s, 10s
    """
    if not samples:
        return ""

    buckets = [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
    lines = []

    if help_text:
        lines.append(f"# HELP {name} {help_text}")
    lines.append(f"# TYPE {name} histogram")

    label_prefix = ""
    if labels:
        label_prefix = ",".join(f'{k}="{v}"' for k, v in labels.items()) + ","

    # Convertir ms → secondes pour les samples
    samples_sec = [s / 1000 for s in samples]

    # Calculer les buckets cumulatifs
    for bucket in buckets:
        count = sum(1 for s in samples_sec if s <= bucket)
        lines.append(f'{name}_bucket{{{label_prefix}le="{bucket}"}} {count}')

    # +Inf bucket (total)
    lines.append(f'{name}_bucket{{{label_prefix}le="+Inf"}} {len(samples)}')

    # Sum et count
    total_sum = sum(samples_sec)
    lines.append(f"{name}_sum{{{label_prefix[:-1] if label_prefix else ''}}} {total_sum:.6f}")
    lines.append(f"{name}_count{{{label_prefix[:-1] if label_prefix else ''}}} {len(samples)}")

    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════
# ENDPOINT PROMETHEUS
# ═══════════════════════════════════════════════════════════


@router.get(
    "/metrics/prometheus",
    summary="Métriques Prometheus",
    description="Expose les métriques au format Prometheus pour le scraping.",
    response_class=Response,
    responses={
        200: {
            "content": {"text/plain": {}},
            "description": "Métriques au format Prometheus",
        }
    },
)
async def get_prometheus_metrics(
    user: dict = Depends(require_role("admin")),
) -> Response:
    """
    Expose les métriques API au format Prometheus.

    Nécessite le rôle admin.

    Métriques exposées:
    - matanne_http_requests_total: Compteur de requêtes par endpoint/méthode/status
    - matanne_http_request_duration_seconds: Histogramme de latence
    - matanne_rate_limit_hits_total: Compteur de blocages rate limit
    - matanne_ai_requests_total: Compteur de requêtes IA
    - matanne_ai_tokens_used_total: Compteur de tokens IA consommés
    - matanne_uptime_seconds: Uptime de l'API
    - process_resident_memory_bytes: Mémoire utilisée (si disponible)

    Returns:
        Texte au format Prometheus text exposition
    """
    from src.api.utils import get_metrics

    metrics = get_metrics()
    output_lines = []

    # Info de base
    output_lines.append(
        _format_prometheus_metric(
            "matanne_api_info",
            1,
            "gauge",
            "API information",
            {"version": "1.0.0", "environment": os.getenv("ENVIRONMENT", "unknown")},
        )
    )

    # Uptime
    output_lines.append(
        _format_prometheus_metric(
            "matanne_uptime_seconds",
            metrics.get("uptime_seconds", 0),
            "gauge",
            "Temps depuis le démarrage de l'API en secondes",
        )
    )

    # Requêtes par endpoint
    requests_total = metrics.get("requests", {}).get("total", {})
    requests_success = metrics.get("requests", {}).get("success", {})
    requests_errors = metrics.get("requests", {}).get("errors", {})

    if requests_total:
        output_lines.append("# HELP matanne_http_requests_total Total HTTP requests by endpoint")
        output_lines.append("# TYPE matanne_http_requests_total counter")

        for endpoint, count in requests_total.items():
            method, path = endpoint.split(":", 1) if ":" in endpoint else ("GET", endpoint)
            success = requests_success.get(endpoint, 0)
            errors = requests_errors.get(endpoint, 0)

            # Requêtes réussies (2xx, 3xx)
            output_lines.append(
                f'matanne_http_requests_total{{method="{method}",endpoint="{path}",status="success"}} {success}'
            )
            # Requêtes en erreur (4xx, 5xx)
            output_lines.append(
                f'matanne_http_requests_total{{method="{method}",endpoint="{path}",status="error"}} {errors}'
            )

    # Latence par endpoint (histogramme)
    latency_data = metrics.get("latency", {})
    if latency_data:
        # On génère un histogramme agrégé par endpoint
        output_lines.append("# HELP matanne_http_request_duration_seconds HTTP request duration")
        output_lines.append("# TYPE matanne_http_request_duration_seconds histogram")

        for endpoint, stats in latency_data.items():
            method, path = endpoint.split(":", 1) if ":" in endpoint else ("GET", endpoint)
            if "avg_ms" in stats:
                # Approximation: on n'a pas les samples bruts, on utilise les stats
                count = stats.get("count", 1)
                avg_sec = stats.get("avg_ms", 0) / 1000

                # Générer des buckets approximatifs basés sur les percentiles
                p50 = (stats.get("p50_ms") or stats.get("avg_ms", 50)) / 1000
                p95 = (stats.get("p95_ms") or p50 * 2) / 1000
                p99 = (stats.get("p99_ms") or p95 * 1.5) / 1000

                # Buckets standard avec approximation
                buckets = [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
                for bucket in buckets:
                    # Estimation du % de requêtes dans ce bucket
                    if bucket < p50:
                        bucket_count = int(count * 0.4 * (bucket / p50))
                    elif bucket < p95:
                        bucket_count = int(count * 0.9 * (bucket / p95))
                    else:
                        bucket_count = count
                    output_lines.append(
                        f'matanne_http_request_duration_seconds_bucket{{method="{method}",endpoint="{path}",le="{bucket}"}} {bucket_count}'
                    )

                output_lines.append(
                    f'matanne_http_request_duration_seconds_bucket{{method="{method}",endpoint="{path}",le="+Inf"}} {count}'
                )
                output_lines.append(
                    f'matanne_http_request_duration_seconds_sum{{method="{method}",endpoint="{path}"}} {avg_sec * count:.6f}'
                )
                output_lines.append(
                    f'matanne_http_request_duration_seconds_count{{method="{method}",endpoint="{path}"}} {count}'
                )

    # Rate limiting
    rate_limit_hits = metrics.get("rate_limiting", {}).get("hits", {})
    if rate_limit_hits:
        output_lines.append(
            "# HELP matanne_rate_limit_hits_total Total rate limit blocks by identifier"
        )
        output_lines.append("# TYPE matanne_rate_limit_hits_total counter")
        for identifier, count in rate_limit_hits.items():
            output_lines.append(
                f'matanne_rate_limit_hits_total{{identifier="{identifier}"}} {count}'
            )

    # Métriques IA
    ai_metrics = metrics.get("ai", {})
    output_lines.append(
        _format_prometheus_metric(
            "matanne_ai_requests_total",
            ai_metrics.get("requests_total", 0),
            "counter",
            "Total AI requests to Mistral API",
        )
    )
    output_lines.append(
        _format_prometheus_metric(
            "matanne_ai_tokens_used_total",
            ai_metrics.get("tokens_used", 0),
            "counter",
            "Total tokens consumed by AI requests",
        )
    )

    # Mémoire (si disponible)
    try:
        import resource

        mem_usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024  # KB → bytes
        output_lines.append(
            _format_prometheus_metric(
                "process_resident_memory_bytes",
                mem_usage,
                "gauge",
                "Resident memory size in bytes",
            )
        )
    except (ImportError, AttributeError):
        # resource n'est pas disponible sur Windows
        try:
            import psutil

            process = psutil.Process()
            mem_info = process.memory_info()
            output_lines.append(
                _format_prometheus_metric(
                    "process_resident_memory_bytes",
                    mem_info.rss,
                    "gauge",
                    "Resident memory size in bytes",
                )
            )
        except ImportError:
            pass

    # Timestamp de la collecte
    output_lines.append(
        _format_prometheus_metric(
            "matanne_metrics_collection_timestamp",
            time.time(),
            "gauge",
            "Unix timestamp of metrics collection",
        )
    )

    # ─────────────────────────────────────────────────────────
    # MÉTRIQUES PAR SERVICE (Sprint 6)
    # ─────────────────────────────────────────────────────────
    try:
        from src.services.core.service_metrics import exporter_prometheus_services

        service_metrics = exporter_prometheus_services()
        if service_metrics:
            output_lines.append("\n# ═══════════ SERVICE METRICS ═══════════")
            output_lines.append(service_metrics)
    except Exception as e:
        logger.warning(f"Erreur chargement métriques services: {e}")

    content = "\n".join(output_lines) + "\n"

    return Response(
        content=content,
        media_type="text/plain; version=0.0.4; charset=utf-8",
    )


# Export du router pour inclusion dans main.py
prometheus_router = router
