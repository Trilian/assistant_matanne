"""
Dispatcher CQRS — Coordonne l'exécution des Queries et Commands.

Le dispatcher:
- Route les queries/commands vers leurs handlers
- Gère le cache automatique pour les queries
- Exécute la validation avant les commands
- Émet des événements pour l'audit
- Collecte les métriques d'exécution

Usage:
    from src.services.core.cqrs import obtenir_dispatcher

    dispatcher = obtenir_dispatcher()

    # Query avec cache automatique
    result = dispatcher.dispatch_query(RecherchRecettesQuery(terme="tarte"))

    # Command avec validation et audit
    result = dispatcher.dispatch_command(CreerRecetteCommand(nom="Tarte"))
"""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Generic, TypeVar

from src.services.core.base.result import ErrorCode, ErrorInfo, Failure, Result, Success

from .commands import Command, CommandHandler, CommandResult
from .queries import Query, QueryHandler

logger = logging.getLogger(__name__)

T = TypeVar("T")


# ═══════════════════════════════════════════════════════════
# MÉTRIQUES CQRS
# ═══════════════════════════════════════════════════════════


@dataclass
class CQRSMetrics:
    """Métriques d'exécution du dispatcher."""

    queries_executed: int = 0
    queries_cached: int = 0
    commands_executed: int = 0
    commands_failed: int = 0
    validation_failures: int = 0
    total_query_time_ms: float = 0.0
    total_command_time_ms: float = 0.0

    @property
    def cache_hit_rate(self) -> float:
        """Taux de cache hit pour les queries."""
        total = self.queries_executed + self.queries_cached
        if total == 0:
            return 0.0
        return self.queries_cached / total

    @property
    def command_success_rate(self) -> float:
        """Taux de succès des commands."""
        total = self.commands_executed + self.commands_failed
        if total == 0:
            return 1.0
        return self.commands_executed / total

    @property
    def avg_query_time_ms(self) -> float:
        """Temps moyen d'exécution des queries."""
        if self.queries_executed == 0:
            return 0.0
        return self.total_query_time_ms / self.queries_executed

    @property
    def avg_command_time_ms(self) -> float:
        """Temps moyen d'exécution des commands."""
        if self.commands_executed == 0:
            return 0.0
        return self.total_command_time_ms / self.commands_executed

    def to_dict(self) -> dict[str, Any]:
        return {
            "queries": {
                "executed": self.queries_executed,
                "cached": self.queries_cached,
                "cache_hit_rate": f"{self.cache_hit_rate:.1%}",
                "avg_time_ms": f"{self.avg_query_time_ms:.2f}",
            },
            "commands": {
                "executed": self.commands_executed,
                "failed": self.commands_failed,
                "validation_failures": self.validation_failures,
                "success_rate": f"{self.command_success_rate:.1%}",
                "avg_time_ms": f"{self.avg_command_time_ms:.2f}",
            },
        }


# ═══════════════════════════════════════════════════════════
# DISPATCHER CQRS
# ═══════════════════════════════════════════════════════════


class CQRSDispatcher:
    """
    Dispatcher central pour queries et commands.

    Thread-safe avec locks séparés pour handlers et métriques.
    Cache intégré pour les queries.
    Émission d'événements pour l'audit des commands.

    Attributes:
        default_cache_ttl: TTL par défaut pour le cache des queries (300s).
        emit_events: Si True, émet des événements via le bus d'événements.
    """

    def __init__(
        self,
        default_cache_ttl: int = 300,
        emit_events: bool = True,
    ):
        self._query_handlers: dict[type, QueryHandler] = {}
        self._command_handlers: dict[type, CommandHandler] = {}
        self._handlers_lock = threading.Lock()
        self._metrics = CQRSMetrics()
        self._metrics_lock = threading.Lock()
        self.default_cache_ttl = default_cache_ttl
        self.emit_events = emit_events

    # ───────────────────────────────────────────────────────
    # REGISTRATION
    # ───────────────────────────────────────────────────────

    def register_query_handler(
        self,
        query_type: type[Query],
        handler: QueryHandler,
    ) -> None:
        """
        Enregistre un handler pour un type de query.

        Args:
            query_type: Type de la query (classe).
            handler: Instance du handler.
        """
        with self._handlers_lock:
            self._query_handlers[query_type] = handler
            logger.debug(f"📥 Query handler enregistré: {query_type.__name__}")

    def register_command_handler(
        self,
        command_type: type[Command],
        handler: CommandHandler,
    ) -> None:
        """
        Enregistre un handler pour un type de command.

        Args:
            command_type: Type de la command (classe).
            handler: Instance du handler.
        """
        with self._handlers_lock:
            self._command_handlers[command_type] = handler
            logger.debug(f"📤 Command handler enregistré: {command_type.__name__}")

    # ───────────────────────────────────────────────────────
    # QUERY DISPATCH
    # ───────────────────────────────────────────────────────

    def dispatch_query(
        self,
        query: Query[T],
        use_cache: bool = True,
        cache_ttl: int | None = None,
    ) -> Result[T, ErrorInfo]:
        """
        Dispatch une query vers son handler avec cache automatique.

        1. Vérifie le cache si use_cache=True
        2. Exécute le handler ou query.execute() directement
        3. Met en cache le résultat si succès

        Args:
            query: La query à exécuter.
            use_cache: Utiliser le cache (défaut: True).
            cache_ttl: TTL du cache en secondes (défaut: default_cache_ttl).

        Returns:
            Result[T, ErrorInfo]: Résultat de la query.
        """
        from src.core.caching import Cache

        ttl = cache_ttl or self.default_cache_ttl
        cache_key = f"cqrs_query_{query.cache_key()}"

        # Check cache
        if use_cache:
            cached = Cache.obtenir(cache_key, ttl=ttl)
            if cached is not None:
                with self._metrics_lock:
                    self._metrics.queries_cached += 1
                logger.debug(f"📦 Cache HIT: {query.__class__.__name__}")
                return Success(cached)

        # Exécution
        start = time.perf_counter()

        try:
            # Chercher un handler enregistré
            handler = self._query_handlers.get(type(query))

            if handler:
                result = handler.handle(query)
            else:
                # Exécution directe via query.execute()
                result = query.execute()

        except Exception as e:
            logger.error(f"❌ Erreur query {query.__class__.__name__}: {e}")
            return Failure(
                ErrorInfo(
                    code=ErrorCode.INTERNAL_ERROR,
                    message=f"Erreur lors de l'exécution de la query: {e}",
                    source=f"CQRSDispatcher.dispatch_query({query.__class__.__name__})",
                )
            )

        duration = (time.perf_counter() - start) * 1000

        # Métriques
        with self._metrics_lock:
            self._metrics.queries_executed += 1
            self._metrics.total_query_time_ms += duration

        # Cache si succès
        if use_cache and result.is_success and result.value is not None:
            Cache.definir(cache_key, result.value, ttl=ttl)
            logger.debug(f"📦 Cache SET: {query.__class__.__name__} ({duration:.1f}ms)")

        return result

    # ───────────────────────────────────────────────────────
    # COMMAND DISPATCH
    # ───────────────────────────────────────────────────────

    def dispatch_command(self, command: Command[T]) -> CommandResult[T]:
        """
        Dispatch une command avec validation et audit.

        1. Valide la command (command.validate())
        2. Exécute le handler ou command.execute()
        3. Émet un événement d'audit
        4. Retourne CommandResult avec métadonnées

        Args:
            command: La command à exécuter.

        Returns:
            CommandResult[T]: Résultat avec métadonnées d'audit.
        """
        command_type = command.__class__.__name__
        start = time.perf_counter()

        # Validation
        validation = command.validate()
        if validation.is_failure:
            with self._metrics_lock:
                self._metrics.validation_failures += 1

            logger.warning(f"⚠️ Validation échouée: {command_type} - {validation.error}")

            return CommandResult(
                result=validation,  # type: ignore
                command_id=command.id,
                command_type=command_type,
                executed_at=datetime.now(),
                duration_ms=0.0,
                user_id=command.user_id,
            )

        # Exécution
        try:
            handler = self._command_handlers.get(type(command))

            if handler:
                result = handler.handle(command)
            else:
                result = command.execute()

        except Exception as e:
            logger.error(f"❌ Erreur command {command_type}: {e}", exc_info=True)
            result = Failure(
                ErrorInfo(
                    code=ErrorCode.INTERNAL_ERROR,
                    message=f"Erreur lors de l'exécution de la command: {e}",
                    source=f"CQRSDispatcher.dispatch_command({command_type})",
                )
            )

        duration = (time.perf_counter() - start) * 1000
        executed_at = datetime.now()

        # Métriques
        with self._metrics_lock:
            if result.is_success:
                self._metrics.commands_executed += 1
            else:
                self._metrics.commands_failed += 1
            self._metrics.total_command_time_ms += duration

        # Événement d'audit
        if self.emit_events:
            self._emit_command_event(command, result, duration)

        logger.info(
            f"{'✅' if result.is_success else '❌'} Command {command_type} "
            f"({duration:.1f}ms) - ID: {command.id[:8]}..."
        )

        return CommandResult(
            result=result,
            command_id=command.id,
            command_type=command_type,
            executed_at=executed_at,
            duration_ms=duration,
            user_id=command.user_id,
        )

    def _emit_command_event(
        self,
        command: Command,
        result: Result,
        duration_ms: float,
    ) -> None:
        """Émet un événement d'audit pour la command."""
        try:
            from src.services.core.events import obtenir_bus

            bus = obtenir_bus()
            bus.emettre(
                "command.executed",
                {
                    "command_type": command.__class__.__name__,
                    "command_id": command.id,
                    "user_id": command.user_id,
                    "success": result.is_success,
                    "duration_ms": duration_ms,
                    "error": str(result.error) if result.is_failure else None,
                },
                source="cqrs_dispatcher",
            )
        except Exception as e:
            logger.debug(f"Event bus non disponible: {e}")

    # ───────────────────────────────────────────────────────
    # MÉTRIQUES
    # ───────────────────────────────────────────────────────

    def get_metrics(self) -> dict[str, Any]:
        """Retourne les métriques du dispatcher."""
        with self._metrics_lock:
            return self._metrics.to_dict()

    def reset_metrics(self) -> None:
        """Remet les métriques à zéro."""
        with self._metrics_lock:
            self._metrics = CQRSMetrics()

    # ───────────────────────────────────────────────────────
    # INTROSPECTION
    # ───────────────────────────────────────────────────────

    def list_handlers(self) -> dict[str, list[str]]:
        """Liste les handlers enregistrés."""
        with self._handlers_lock:
            return {
                "query_handlers": [t.__name__ for t in self._query_handlers.keys()],
                "command_handlers": [t.__name__ for t in self._command_handlers.keys()],
            }


# ═══════════════════════════════════════════════════════════
# SINGLETON
# ═══════════════════════════════════════════════════════════

_dispatcher: CQRSDispatcher | None = None
_dispatcher_lock = threading.Lock()


def obtenir_dispatcher() -> CQRSDispatcher:
    """
    Obtient le dispatcher CQRS singleton (thread-safe).

    Returns:
        CQRSDispatcher: Instance unique du dispatcher.
    """
    global _dispatcher

    if _dispatcher is None:
        with _dispatcher_lock:
            if _dispatcher is None:
                _dispatcher = CQRSDispatcher()
                logger.info("🚀 CQRS Dispatcher initialisé")
    return _dispatcher


def reset_dispatcher() -> None:
    """Réinitialise le dispatcher (utile pour les tests)."""
    global _dispatcher
    with _dispatcher_lock:
        _dispatcher = None
