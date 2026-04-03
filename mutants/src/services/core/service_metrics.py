"""
Métriques par Service — Observabilité Prometheus.

Chaque service peut enregistrer ses propres métriques qui sont
agrégées et exportées au format Prometheus.

Types de métriques:
- COMPTEUR: Valeur incrémentale (ex: nb d'appels)
- JAUGE: Valeur instantanée (ex: taille cache)
- HISTOGRAMME: Distribution de valeurs (ex: latences)

Usage:
    from src.services.core.service_metrics import (
        ServiceMetricsMixin,
        MetriquesService,
        obtenir_metriques_services,
        exporter_prometheus_services,
    )

    # Via Mixin (recommandé)
    class MonService(ServiceMetricsMixin, BaseService):
        def ma_methode(self):
            self._incrementer_compteur("appels")
            with self._mesurer_duree("latence"):
                # ... travail ...

    # Export Prometheus
    metrics_text = exporter_prometheus_services()
"""

from __future__ import annotations

import logging
import statistics
import threading
import time
from collections import defaultdict, deque
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Generator

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# TYPES
# ═══════════════════════════════════════════════════════════


class TypeMetriqueService(Enum):
    """Types de métriques supportés."""

    COMPTEUR = auto()
    JAUGE = auto()
    HISTOGRAMME = auto()


@dataclass
class PointMetriqueService:
    """Un point de métrique individuel."""

    nom: str
    valeur: float
    type: TypeMetriqueService
    timestamp: float = field(default_factory=time.time)
    labels: dict[str, str] = field(default_factory=dict)


@dataclass
class SerieMetriqueService:
    """Série temporelle pour une métrique."""

    type: TypeMetriqueService
    points: deque
    total: float = 0.0
    count: int = 0

    def ajouter(self, valeur: float) -> None:
        """Ajoute un point à la série."""
        self.points.append(
            PointMetriqueService(
                nom="",
                valeur=valeur,
                type=self.type,
            )
        )
        self.count += 1
        if self.type == TypeMetriqueService.COMPTEUR:
            self.total += valeur
        elif self.type == TypeMetriqueService.JAUGE:
            self.total = valeur
        else:  # Histogramme
            self.total += valeur


@dataclass
class MetriquesService:
    """Métriques agrégées d'un service."""

    service: str
    metriques: dict[str, dict[str, Any]] = field(default_factory=dict)
    derniere_mise_a_jour: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        """Convertit en dictionnaire."""
        return {
            "service": self.service,
            "metriques": self.metriques,
            "derniere_mise_a_jour": self.derniere_mise_a_jour.isoformat(),
        }


# ═══════════════════════════════════════════════════════════
# COLLECTEUR PAR SERVICE
# ═══════════════════════════════════════════════════════════


class ServiceMetricsCollector:
    """Collecteur de métriques pour un service spécifique."""

    def __init__(self, service_name: str, max_points: int = 500):
        self.service_name = service_name
        self._max_points = max_points
        self._series: dict[str, SerieMetriqueService] = {}
        self._lock = threading.Lock()
        self._creation_time = time.monotonic()

    def incrementer(self, nom: str, increment: float = 1.0) -> None:
        """Incrémente un compteur."""
        with self._lock:
            if nom not in self._series:
                self._series[nom] = SerieMetriqueService(
                    type=TypeMetriqueService.COMPTEUR,
                    points=deque(maxlen=self._max_points),
                )
            self._series[nom].ajouter(increment)

    def jauge(self, nom: str, valeur: float) -> None:
        """Définit une jauge."""
        with self._lock:
            if nom not in self._series:
                self._series[nom] = SerieMetriqueService(
                    type=TypeMetriqueService.JAUGE,
                    points=deque(maxlen=self._max_points),
                )
            self._series[nom].ajouter(valeur)

    def histogramme(self, nom: str, valeur: float) -> None:
        """Enregistre une valeur d'histogramme."""
        with self._lock:
            if nom not in self._series:
                self._series[nom] = SerieMetriqueService(
                    type=TypeMetriqueService.HISTOGRAMME,
                    points=deque(maxlen=self._max_points),
                )
            self._series[nom].ajouter(valeur)

    @contextmanager
    def mesurer_duree(self, nom: str) -> Generator[None, None, None]:
        """Context manager pour mesurer la durée d'une opération."""
        start = time.perf_counter()
        try:
            yield
        finally:
            duree_ms = (time.perf_counter() - start) * 1000
            self.histogramme(f"{nom}_ms", duree_ms)

    def snapshot(self) -> MetriquesService:
        """Retourne un snapshot des métriques du service."""
        with self._lock:
            metriques: dict[str, dict[str, Any]] = {}

            for nom, serie in self._series.items():
                info: dict[str, Any] = {
                    "type": serie.type.name.lower(),
                    "total": serie.total,
                    "count": serie.count,
                }

                # Stats pour histogrammes
                if serie.type == TypeMetriqueService.HISTOGRAMME and len(serie.points) > 1:
                    valeurs = [p.valeur for p in serie.points]
                    info["stats"] = {
                        "min": min(valeurs),
                        "max": max(valeurs),
                        "avg": statistics.mean(valeurs),
                        "median": statistics.median(valeurs),
                        "p95": _percentile(valeurs, 0.95),
                        "p99": _percentile(valeurs, 0.99),
                    }

                metriques[nom] = info

            return MetriquesService(
                service=self.service_name,
                metriques=metriques,
            )

    def reset(self) -> None:
        """Réinitialise les métriques."""
        with self._lock:
            self._series.clear()


# ═══════════════════════════════════════════════════════════
# REGISTRE GLOBAL
# ═══════════════════════════════════════════════════════════

_metrics_registry: dict[str, ServiceMetricsCollector] = {}
_registry_lock = threading.Lock()


def obtenir_collecteur_service(service_name: str) -> ServiceMetricsCollector:
    """Obtient ou crée un collecteur de métriques pour un service.

    Args:
        service_name: Nom du service

    Returns:
        ServiceMetricsCollector pour le service
    """
    with _registry_lock:
        if service_name not in _metrics_registry:
            _metrics_registry[service_name] = ServiceMetricsCollector(service_name)
            logger.debug(f"📊 Collecteur métriques créé: {service_name}")
        return _metrics_registry[service_name]


def obtenir_metriques_services(
    services: list[str] | None = None,
) -> dict[str, MetriquesService]:
    """Obtient les métriques de tous les services ou d'une sélection.

    Args:
        services: Liste des services (None = tous)

    Returns:
        Dict service_name -> MetriquesService
    """
    with _registry_lock:
        collectors = _metrics_registry.copy()

    if services:
        collectors = {k: v for k, v in collectors.items() if k in services}

    return {name: collector.snapshot() for name, collector in collectors.items()}


def lister_services_metrics() -> list[str]:
    """Liste les services avec métriques enregistrées."""
    with _registry_lock:
        return list(_metrics_registry.keys())


# ═══════════════════════════════════════════════════════════
# EXPORT PROMETHEUS
# ═══════════════════════════════════════════════════════════

# Buckets Prometheus standards pour les latences (en ms)
PROMETHEUS_BUCKETS_MS = [1, 5, 10, 25, 50, 100, 250, 500, 1000, 2500, 5000, 10000]


def exporter_prometheus_services() -> str:
    """Exporte toutes les métriques services au format Prometheus.

    Returns:
        Texte au format Prometheus text exposition
    """
    lines: list[str] = []
    metriques = obtenir_metriques_services()

    for service_name, service_metrics in metriques.items():
        for metric_name, metric_data in service_metrics.metriques.items():
            # Nom Prometheus (préfixé avec matanne_service_)
            prom_name = f"matanne_service_{service_name}_{metric_name}".replace(".", "_")
            metric_type = metric_data.get("type", "gauge")
            total = metric_data.get("total", 0)
            count = metric_data.get("count", 0)

            if metric_type == "compteur":
                lines.append(f"# TYPE {prom_name}_total counter")
                lines.append(f'{prom_name}_total{{service="{service_name}"}} {total}')

            elif metric_type == "jauge":
                lines.append(f"# TYPE {prom_name} gauge")
                lines.append(f'{prom_name}{{service="{service_name}"}} {total}')

            elif metric_type == "histogramme":
                stats = metric_data.get("stats", {})
                lines.append(f"# TYPE {prom_name} histogram")

                # Buckets
                if stats:
                    for bucket in PROMETHEUS_BUCKETS_MS:
                        # Estimation du count dans le bucket
                        bucket_count = int(
                            count * min(1.0, bucket / max(stats.get("max", bucket), 1))
                        )
                        lines.append(
                            f'{prom_name}_bucket{{service="{service_name}",le="{bucket}"}} {bucket_count}'
                        )
                    lines.append(
                        f'{prom_name}_bucket{{service="{service_name}",le="+Inf"}} {count}'
                    )

                # Sum et count
                lines.append(f'{prom_name}_sum{{service="{service_name}"}} {total}')
                lines.append(f'{prom_name}_count{{service="{service_name}"}} {count}')

            lines.append("")  # Ligne vide entre métriques

    return "\n".join(lines)


def exporter_prometheus_service(service_name: str) -> str:
    """Exporte les métriques d'un service spécifique au format Prometheus.

    Args:
        service_name: Nom du service

    Returns:
        Texte au format Prometheus
    """
    with _registry_lock:
        collector = _metrics_registry.get(service_name)

    if not collector:
        return ""

    snapshot = collector.snapshot()
    lines: list[str] = [f"# Service: {service_name}", ""]

    for metric_name, metric_data in snapshot.metriques.items():
        prom_name = f"matanne_service_{service_name}_{metric_name}".replace(".", "_")
        metric_type = metric_data.get("type", "gauge")
        total = metric_data.get("total", 0)

        if metric_type == "compteur":
            lines.append(f"# TYPE {prom_name}_total counter")
            lines.append(f"{prom_name}_total {total}")
        elif metric_type == "jauge":
            lines.append(f"# TYPE {prom_name} gauge")
            lines.append(f"{prom_name} {total}")
        elif metric_type == "histogramme":
            stats = metric_data.get("stats", {})
            if stats:
                lines.append(f"# TYPE {prom_name} summary")
                lines.append(f'{prom_name}{{quantile="0.5"}} {stats.get("median", 0)}')
                lines.append(f'{prom_name}{{quantile="0.95"}} {stats.get("p95", 0)}')
                lines.append(f'{prom_name}{{quantile="0.99"}} {stats.get("p99", 0)}')
                lines.append(f"{prom_name}_count {metric_data.get('count', 0)}")
                lines.append(f"{prom_name}_sum {total}")

        lines.append("")

    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════
# MIXIN POUR SERVICES
# ═══════════════════════════════════════════════════════════


class ServiceMetricsMixin:
    """Mixin ajoutant le support métriques à un service.

    Usage:
        class MonService(ServiceMetricsMixin, BaseService[Model]):
            def __init__(self):
                super().__init__()
                self._init_metrics()

            def ma_methode(self):
                self._incrementer_compteur("appels")
                with self._mesurer_duree("latence"):
                    # ... travail ...
    """

    service_name: str = "unknown"
    _metrics_collector: ServiceMetricsCollector | None = None

    def _init_metrics(self) -> None:
        """Initialise le collecteur de métriques pour ce service."""
        name = getattr(self, "service_name", self.__class__.__name__.lower())
        self._metrics_collector = obtenir_collecteur_service(name)

    def _get_metrics_collector(self) -> ServiceMetricsCollector:
        """Obtient le collecteur de métriques (lazy init)."""
        if self._metrics_collector is None:
            self._init_metrics()
        return self._metrics_collector

    def _incrementer_compteur(self, nom: str, increment: float = 1.0) -> None:
        """Incrémente un compteur de métrique."""
        self._get_metrics_collector().incrementer(nom, increment)

    def _definir_jauge(self, nom: str, valeur: float) -> None:
        """Définit une valeur de jauge."""
        self._get_metrics_collector().jauge(nom, valeur)

    def _enregistrer_histogramme(self, nom: str, valeur: float) -> None:
        """Enregistre une valeur dans un histogramme."""
        self._get_metrics_collector().histogramme(nom, valeur)

    @contextmanager
    def _mesurer_duree(self, nom: str) -> Generator[None, None, None]:
        """Context manager pour mesurer la durée d'une opération."""
        with self._get_metrics_collector().mesurer_duree(nom):
            yield

    def obtenir_metriques(self) -> MetriquesService:
        """Retourne les métriques de ce service."""
        return self._get_metrics_collector().snapshot()


# ═══════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════


def _percentile(valeurs: list[float], p: float) -> float:
    """Calcule le percentile p (0-1) d'une liste."""
    if not valeurs:
        return 0.0
    sorted_vals = sorted(valeurs)
    k = (len(sorted_vals) - 1) * p
    f = int(k)
    c = f + 1
    if c >= len(sorted_vals):
        return sorted_vals[-1]
    return sorted_vals[f] + (k - f) * (sorted_vals[c] - sorted_vals[f])


# ═══════════════════════════════════════════════════════════
# INTÉGRATION AVEC L'API PROMETHEUS
# ═══════════════════════════════════════════════════════════


def integrer_api_prometheus() -> str:
    """Génère les métriques services à ajouter à l'endpoint /metrics/prometheus.

    Cette fonction est appelée par src/api/prometheus.py pour inclure
    les métriques des services dans l'export Prometheus global.
    """
    return exporter_prometheus_services()


__all__ = [
    "TypeMetriqueService",
    "MetriquesService",
    "ServiceMetricsCollector",
    "ServiceMetricsMixin",
    "obtenir_collecteur_service",
    "obtenir_metriques_services",
    "lister_services_metrics",
    "exporter_prometheus_services",
    "exporter_prometheus_service",
    "integrer_api_prometheus",
]
