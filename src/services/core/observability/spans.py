"""
Spans — Traces d'exécution pour le suivi des opérations.

Pattern OpenTelemetry-inspired pour tracer les opérations
à travers les services.

Usage:
    from src.services.core.observability import Span, current_span

    # Context manager (recommandé)
    with Span("RecetteService", "generer_suggestions") as span:
        span.set_attribute("nb_suggestions", 5)
        span.set_attribute("user_id", user.id)
        result = do_generation()

    # Spans imbriqués
    with Span("PlanningService", "generer_semaine") as parent:
        for jour in jours:
            with Span("PlanningService", "generer_jour") as child:
                child.set_attribute("jour", jour)
                # child a automatiquement parent comme parent_span
"""

from __future__ import annotations

import contextvars
import logging
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, StrEnum
from typing import Any
from uuid import uuid4

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# TYPES
# ═══════════════════════════════════════════════════════════


class SpanStatus(StrEnum):
    """Statuts possibles d'un span."""

    UNSET = "unset"  # En cours
    OK = "ok"  # Terminé avec succès
    ERROR = "error"  # Terminé avec erreur


@dataclass
class SpanContext:
    """Contexte de trace partagé entre spans."""

    trace_id: str = field(default_factory=lambda: str(uuid4()))
    span_id: str = field(default_factory=lambda: str(uuid4())[:16])
    parent_span_id: str | None = None


# Context variable pour le span courant (thread-local)
_current_span: contextvars.ContextVar[Span | None] = contextvars.ContextVar(
    "current_span", default=None
)


def current_span() -> Span | None:
    """Retourne le span courant (ou None si aucun)."""
    return _current_span.get()


# ═══════════════════════════════════════════════════════════
# SPAN
# ═══════════════════════════════════════════════════════════


class Span:
    """
    Trace span pour le suivi des opérations.

    Représente une unité de travail avec:
    - Nom du service et de l'opération
    - Durée d'exécution
    - Attributs clé-valeur
    - Relations parent-enfant

    Usage:
        with Span("ServiceRecettes", "generer") as span:
            span.set_attribute("count", 5)
            result = do_work()
            if error:
                span.set_status(SpanStatus.ERROR, "Échec génération")
    """

    def __init__(
        self,
        service_name: str,
        operation_name: str,
        parent: Span | None = None,
    ):
        """
        Crée un nouveau span.

        Args:
            service_name: Nom du service (ex: "RecetteService").
            operation_name: Nom de l'opération (ex: "generer_suggestions").
            parent: Span parent optionnel (auto-détecté si omis).
        """
        self.service_name = service_name
        self.operation_name = operation_name

        # Contexte de trace
        self.trace_id = str(uuid4())
        self.span_id = str(uuid4())[:16]

        # Parent (auto-détection)
        if parent is None:
            parent = current_span()

        self.parent_span = parent
        self.parent_span_id = parent.span_id if parent else None

        if parent:
            # Hériter le trace_id du parent
            self.trace_id = parent.trace_id

        # Timing
        self.start_time: datetime | None = None
        self.end_time: datetime | None = None
        self._start_perf: float = 0.0

        # État
        self.status = SpanStatus.UNSET
        self.status_message: str = ""
        self.attributes: dict[str, Any] = {}
        self.events: list[dict[str, Any]] = []

        # Token pour context var
        self._token: contextvars.Token | None = None

    @property
    def duration_ms(self) -> float:
        """Durée d'exécution en millisecondes."""
        if self.end_time and self.start_time:
            return (self.end_time - self.start_time).total_seconds() * 1000
        return 0.0

    @property
    def name(self) -> str:
        """Nom complet du span."""
        return f"{self.service_name}.{self.operation_name}"

    def set_attribute(self, key: str, value: Any) -> Span:
        """
        Définit un attribut sur le span.

        Args:
            key: Clé de l'attribut.
            value: Valeur de l'attribut.

        Returns:
            Self pour chaînage.
        """
        self.attributes[key] = value
        return self

    def set_attributes(self, attributes: dict[str, Any]) -> Span:
        """
        Définit plusieurs attributs.

        Args:
            attributes: Dict d'attributs.

        Returns:
            Self pour chaînage.
        """
        self.attributes.update(attributes)
        return self

    def add_event(self, name: str, attributes: dict[str, Any] | None = None) -> Span:
        """
        Ajoute un événement au span.

        Args:
            name: Nom de l'événement.
            attributes: Attributs de l'événement.

        Returns:
            Self pour chaînage.
        """
        self.events.append(
            {
                "name": name,
                "timestamp": datetime.now().isoformat(),
                "attributes": attributes or {},
            }
        )
        return self

    def set_status(self, status: SpanStatus, message: str = "") -> Span:
        """
        Définit le statut du span.

        Args:
            status: Statut final.
            message: Message optionnel (pour les erreurs).

        Returns:
            Self pour chaînage.
        """
        self.status = status
        self.status_message = message
        return self

    def record_exception(self, exception: Exception) -> Span:
        """
        Enregistre une exception sur le span.

        Args:
            exception: L'exception à enregistrer.

        Returns:
            Self pour chaînage.
        """
        self.set_status(SpanStatus.ERROR, str(exception))
        self.add_event(
            "exception",
            {
                "type": type(exception).__name__,
                "message": str(exception),
            },
        )
        return self

    # ───────────────────────────────────────────────────────
    # CONTEXT MANAGER
    # ───────────────────────────────────────────────────────

    def __enter__(self) -> Span:
        """Démarre le span."""
        self.start_time = datetime.now()
        self._start_perf = time.perf_counter()
        self._token = _current_span.set(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        """
        Termine le span.

        Si une exception non gérée survient, le span est marqué ERROR.
        """
        self.end_time = datetime.now()

        # Restaurer le span parent
        if self._token:
            _current_span.reset(self._token)

        # Gérer les exceptions
        if exc_val is not None:
            self.record_exception(exc_val)

        # Si pas de statut défini, marquer comme OK
        if self.status == SpanStatus.UNSET:
            self.status = SpanStatus.OK

        # Log du span terminé
        status_emoji = "✅" if self.status == SpanStatus.OK else "❌"
        logger.debug(
            f"{status_emoji} Span {self.name} terminé: "
            f"{self.duration_ms:.1f}ms - {self.status.value}"
        )

        # Ne pas supprimer l'exception
        return False

    # ───────────────────────────────────────────────────────
    # SERIALIZATION
    # ───────────────────────────────────────────────────────

    def to_dict(self) -> dict[str, Any]:
        """Sérialise le span."""
        return {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "service": self.service_name,
            "operation": self.operation_name,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_ms": self.duration_ms,
            "status": self.status.value,
            "status_message": self.status_message,
            "attributes": self.attributes,
            "events": self.events,
        }

    def __repr__(self) -> str:
        status = self.status.value
        duration = f"{self.duration_ms:.1f}ms" if self.end_time else "running"
        return f"Span({self.name}, {status}, {duration})"


# ═══════════════════════════════════════════════════════════
# SPAN STORE (pour debugging/inspection)
# ═══════════════════════════════════════════════════════════


class SpanStore:
    """
    Stockage temporaire des spans pour debugging.

    Garde les N derniers spans en mémoire pour inspection.
    """

    def __init__(self, max_spans: int = 1000):
        self._spans: list[dict[str, Any]] = []
        self._max_spans = max_spans
        self._lock = threading.Lock()

    def record(self, span: Span) -> None:
        """Enregistre un span terminé."""
        with self._lock:
            self._spans.append(span.to_dict())
            if len(self._spans) > self._max_spans:
                self._spans = self._spans[-self._max_spans // 2 :]

    def get_by_trace(self, trace_id: str) -> list[dict[str, Any]]:
        """Retourne tous les spans d'une trace."""
        with self._lock:
            return [s for s in self._spans if s["trace_id"] == trace_id]

    def get_recent(self, limit: int = 50) -> list[dict[str, Any]]:
        """Retourne les spans récents."""
        with self._lock:
            return self._spans[-limit:]

    def clear(self) -> None:
        """Vide le store."""
        with self._lock:
            self._spans.clear()


# Singleton global
_span_store: SpanStore | None = None
_store_lock = threading.Lock()


def get_span_store() -> SpanStore:
    """Obtient le store de spans global."""
    global _span_store
    if _span_store is None:
        with _store_lock:
            if _span_store is None:
                _span_store = SpanStore()
    return _span_store
