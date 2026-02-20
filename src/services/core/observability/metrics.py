"""
Metrics — Collecte de métriques pour les services.

Types de métriques:
- Counter: Compteur monotone (ex: requêtes, erreurs)
- Gauge: Valeur instantanée (ex: connexions actives, cache size)
- Histogram: Distribution de valeurs (ex: latence, taille de réponse)

Usage:
    metrics = ServiceMetrics("inventaire")

    # Compteur
    metrics.increment("articles_ajoutes")
    metrics.increment("erreurs", labels={"type": "validation"})

    # Gauge
    metrics.gauge("stock_total", 1500)
    metrics.gauge("cache_entries", cache.size())

    # Timer (histogram)
    with metrics.timer("query_time"):
        result = db.query(...).all()

    # Ou manuellement
    metrics.histogram("response_size_bytes", len(response))
"""

from __future__ import annotations

import logging
import threading
import time
from collections import defaultdict
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Generator

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# TYPES
# ═══════════════════════════════════════════════════════════


class MetricType(str, Enum):
    """Types de métriques supportés."""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"


@dataclass(slots=True)
class Metric:
    """
    Une métrique individuelle.

    Attributes:
        name: Nom de la métrique (ex: "recettes.creees").
        type: Type de métrique (counter, gauge, histogram).
        value: Valeur actuelle.
        labels: Labels clé-valeur pour la segmentation.
        timestamp: Horodatage de la mesure.
        description: Description optionnelle.
    """

    name: str
    type: MetricType
    value: float
    labels: dict[str, str] = field(default_factory=lambda: {})
    timestamp: datetime = field(default_factory=datetime.now)
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Sérialise la métrique."""
        return {
            "name": self.name,
            "type": self.type.value,
            "value": self.value,
            "labels": self.labels,
            "timestamp": self.timestamp.isoformat(),
            "description": self.description,
        }

    @property
    def full_name(self) -> str:
        """Nom complet avec labels."""
        if not self.labels:
            return self.name
        labels_str = ",".join(f"{k}={v}" for k, v in sorted(self.labels.items()))
        return f"{self.name}{{{labels_str}}}"


# ═══════════════════════════════════════════════════════════
# SERVICE METRICS
# ═══════════════════════════════════════════════════════════


class ServiceMetrics:
    """
    Collecteur de métriques pour un service spécifique.

    Préfixe automatiquement les métriques avec le nom du service.
    Thread-safe via locks.

    Example:
        metrics = ServiceMetrics("recettes")
        metrics.increment("generees")  # → recettes.generees
        metrics.gauge("cache_hit_rate", 0.85)

        with metrics.timer("generation_ia"):
            result = generer()

        stats = metrics.get_stats()
    """

    def __init__(self, service_name: str):
        """
        Initialise le collecteur de métriques.

        Args:
            service_name: Nom du service (préfixe des métriques).
        """
        self.service_name = service_name
        self._counters: dict[str, float] = defaultdict(float)
        self._gauges: dict[str, float] = {}
        self._histograms: dict[str, list[float]] = defaultdict(list)
        self._lock = threading.Lock()
        self._start_time = datetime.now()

    def _full_name(self, name: str) -> str:
        """Préfixe le nom avec le service."""
        return f"{self.service_name}.{name}"

    # ───────────────────────────────────────────────────────
    # COUNTERS
    # ───────────────────────────────────────────────────────

    def increment(
        self,
        name: str,
        value: float = 1.0,
        labels: dict[str, str] | None = None,
    ) -> None:
        """
        Incrémente un compteur.

        Args:
            name: Nom du compteur.
            value: Valeur à ajouter (défaut: 1).
            labels: Labels optionnels.
        """
        full_name = self._full_name(name)
        if labels:
            labels_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
            full_name = f"{full_name}{{{labels_str}}}"

        with self._lock:
            self._counters[full_name] += value

    def count(self, name: str) -> float:
        """Retourne la valeur actuelle d'un compteur."""
        full_name = self._full_name(name)
        with self._lock:
            return self._counters.get(full_name, 0.0)

    # ───────────────────────────────────────────────────────
    # GAUGES
    # ───────────────────────────────────────────────────────

    def gauge(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """
        Définit une valeur gauge (instantanée).

        Args:
            name: Nom du gauge.
            value: Valeur actuelle.
            labels: Labels optionnels.
        """
        full_name = self._full_name(name)
        if labels:
            labels_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
            full_name = f"{full_name}{{{labels_str}}}"

        with self._lock:
            self._gauges[full_name] = value

    def get_gauge(self, name: str) -> float | None:
        """Retourne la valeur actuelle d'un gauge."""
        full_name = self._full_name(name)
        with self._lock:
            return self._gauges.get(full_name)

    # ───────────────────────────────────────────────────────
    # HISTOGRAMS
    # ───────────────────────────────────────────────────────

    def histogram(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """
        Enregistre une valeur dans un histogramme.

        Args:
            name: Nom de l'histogramme.
            value: Valeur à enregistrer.
            labels: Labels optionnels.
        """
        full_name = self._full_name(name)
        if labels:
            labels_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
            full_name = f"{full_name}{{{labels_str}}}"

        with self._lock:
            self._histograms[full_name].append(value)
            # Limiter la taille pour éviter les fuites mémoire
            if len(self._histograms[full_name]) > 10000:
                self._histograms[full_name] = self._histograms[full_name][-5000:]

    @contextmanager
    def timer(
        self,
        name: str,
        labels: dict[str, str] | None = None,
    ) -> Generator[None, None, None]:
        """
        Context manager pour mesurer la durée d'une opération.

        La durée est enregistrée dans un histogramme en millisecondes.

        Args:
            name: Nom du timer.
            labels: Labels optionnels.

        Yields:
            None

        Example:
            with metrics.timer("query_duration"):
                results = db.query(...).all()
        """
        start = time.perf_counter()
        try:
            yield
        finally:
            duration_ms = (time.perf_counter() - start) * 1000
            self.histogram(f"{name}_ms", duration_ms, labels)

    # ───────────────────────────────────────────────────────
    # STATISTIQUES
    # ───────────────────────────────────────────────────────

    def get_stats(self) -> dict[str, Any]:
        """
        Retourne les statistiques agrégées.

        Returns:
            Dict avec counters, gauges, histograms (avec percentiles).
        """
        with self._lock:
            histograms_stats: dict[str, dict[str, float | int]] = {}

            # Calculer les percentiles pour les histogrammes
            for name, values in self._histograms.items():
                if values:
                    sorted_values = sorted(values)
                    n = len(sorted_values)
                    histograms_stats[name] = {
                        "count": n,
                        "min": sorted_values[0],
                        "max": sorted_values[-1],
                        "avg": sum(sorted_values) / n,
                        "p50": sorted_values[int(n * 0.5)],
                        "p95": sorted_values[int(n * 0.95)] if n >= 20 else sorted_values[-1],
                        "p99": sorted_values[int(n * 0.99)] if n >= 100 else sorted_values[-1],
                    }

            return {
                "service": self.service_name,
                "uptime_seconds": (datetime.now() - self._start_time).total_seconds(),
                "counters": dict(self._counters),
                "gauges": dict(self._gauges),
                "histograms": histograms_stats,
            }

    def reset(self) -> None:
        """Remet toutes les métriques à zéro."""
        with self._lock:
            self._counters.clear()
            self._gauges.clear()
            self._histograms.clear()
            self._start_time = datetime.now()


# ═══════════════════════════════════════════════════════════
# METRICS COLLECTOR (Aggregateur global)
# ═══════════════════════════════════════════════════════════


class MetricsCollector:
    """
    Collecteur global de métriques pour tous les services.

    Agrège les métriques de tous les ServiceMetrics enregistrés.
    """

    def __init__(self):
        self._services: dict[str, ServiceMetrics] = {}
        self._lock = threading.Lock()

    def register(self, metrics: ServiceMetrics) -> None:
        """Enregistre un ServiceMetrics."""
        with self._lock:
            self._services[metrics.service_name] = metrics

    def get_service(self, name: str) -> ServiceMetrics:
        """Obtient ou crée un ServiceMetrics."""
        with self._lock:
            if name not in self._services:
                self._services[name] = ServiceMetrics(name)
            return self._services[name]

    def get_all_stats(self) -> dict[str, Any]:
        """Retourne les statistiques de tous les services."""
        with self._lock:
            return {
                "services": {name: m.get_stats() for name, m in self._services.items()},
                "total_services": len(self._services),
            }

    def list_services(self) -> list[str]:
        """Liste les services enregistrés."""
        with self._lock:
            return list(self._services.keys())


# ═══════════════════════════════════════════════════════════
# SINGLETON
# ═══════════════════════════════════════════════════════════

_collector: MetricsCollector | None = None
_collector_lock = threading.Lock()


def obtenir_collector() -> MetricsCollector:
    """Obtient le collecteur global de métriques (singleton)."""
    global _collector
    if _collector is None:
        with _collector_lock:
            if _collector is None:
                _collector = MetricsCollector()
    return _collector
