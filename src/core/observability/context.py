"""
Context - Contexte d'exécution thread-local avec correlation ID.
"""

from __future__ import annotations

import contextvars
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)

# Context var pour le contexte d'exécution (thread-safe + async-safe)
_contexte_execution: contextvars.ContextVar[ContexteExecution | None] = contextvars.ContextVar(
    "contexte_execution", default=None
)


@dataclass
class ContexteExecution:
    """
    Contexte d'exécution avec métadonnées de traçage.

    Propagé automatiquement à travers tous les appels
    pour permettre la corrélation des logs et métriques.

    Attributes:
        correlation_id: ID unique pour tracer la requête (8 chars)
        operation: Nom de l'opération en cours
        utilisateur: Nom de l'utilisateur (optionnel)
        module: Module Streamlit (optionnel)
        debut: Timestamp de début
        metadata: Métadonnées additionnelles libres
        parent_id: ID du contexte parent pour traçage hiérarchique
    """

    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    operation: str = ""
    utilisateur: str | None = None
    module: str | None = None
    debut: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)
    parent_id: str | None = None

    def creer_enfant(self, operation: str, **metadata: Any) -> ContexteExecution:
        """
        Crée un contexte enfant (pour sous-opérations).

        Le correlation_id est hérité, parent_id pointe vers le parent.
        """
        return ContexteExecution(
            correlation_id=self.correlation_id,
            operation=operation,
            utilisateur=self.utilisateur,
            module=self.module,
            parent_id=self.correlation_id,
            metadata={**self.metadata, **metadata},
        )

    def duree_ms(self) -> float:
        """Retourne la durée depuis le début en millisecondes."""
        return (datetime.now() - self.debut).total_seconds() * 1000

    def to_dict(self) -> dict[str, Any]:
        """Convertit en dictionnaire pour sérialisation."""
        return {
            "correlation_id": self.correlation_id,
            "operation": self.operation,
            "utilisateur": self.utilisateur,
            "module": self.module,
            "debut": self.debut.isoformat(),
            "duree_ms": self.duree_ms(),
            "parent_id": self.parent_id,
            "metadata": self.metadata,
        }


def obtenir_contexte() -> ContexteExecution:
    """
    Obtient le contexte d'exécution actuel.

    Crée un nouveau contexte si aucun n'existe.
    """
    ctx = _contexte_execution.get()
    if ctx is None:
        ctx = ContexteExecution()
        _contexte_execution.set(ctx)
    return ctx


def definir_contexte(ctx: ContexteExecution) -> contextvars.Token[ContexteExecution | None]:
    """
    Définit le contexte d'exécution.

    Returns:
        Token pour reset ultérieur via reset_contexte()
    """
    return _contexte_execution.set(ctx)


def reset_contexte(token: contextvars.Token[ContexteExecution | None]) -> None:
    """Reset le contexte avec le token obtenu de definir_contexte()."""
    _contexte_execution.reset(token)


class contexte_operation:
    """
    Context manager pour une opération avec contexte automatique.

    Usage::
        with contexte_operation("charger_recettes", module="cuisine"):
            # Le contexte est automatiquement propagé
            recettes = service.charger()

        # Avec métadonnées
        with contexte_operation("import_recette", url=url) as ctx:
            logger.info(f"[{ctx.correlation_id}] Import depuis {url}")
    """

    def __init__(
        self,
        operation: str,
        module: str | None = None,
        utilisateur: str | None = None,
        **metadata: Any,
    ) -> None:
        self.operation = operation
        self.module = module
        self.utilisateur = utilisateur
        self.metadata = metadata
        self._token: contextvars.Token[ContexteExecution | None] | None = None
        self._ctx: ContexteExecution | None = None

    def __enter__(self) -> ContexteExecution:
        parent = _contexte_execution.get()

        if parent:
            self._ctx = parent.creer_enfant(self.operation, **self.metadata)
            if self.module:
                self._ctx.module = self.module
            if self.utilisateur:
                self._ctx.utilisateur = self.utilisateur
        else:
            self._ctx = ContexteExecution(
                operation=self.operation,
                module=self.module,
                utilisateur=self.utilisateur,
                metadata=self.metadata,
            )

        self._token = definir_contexte(self._ctx)
        logger.debug(f"[{self._ctx.correlation_id}] ▶ Début: {self.operation}")
        return self._ctx

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        if self._ctx:
            duree = self._ctx.duree_ms()
            if exc_type:
                logger.warning(
                    f"[{self._ctx.correlation_id}] ✗ Fin: {self.operation} "
                    f"({duree:.1f}ms) - ERREUR: {exc_val}"
                )
            else:
                logger.debug(
                    f"[{self._ctx.correlation_id}] ✓ Fin: {self.operation} ({duree:.1f}ms)"
                )

        if self._token:
            reset_contexte(self._token)


# ═══════════════════════════════════════════════════════════
# LOGGING FILTER AVEC CORRELATION ID
# ═══════════════════════════════════════════════════════════


class FiltreCorrelation(logging.Filter):
    """
    Filtre logging qui ajoute le correlation_id aux records.

    Usage dans la config logging::
        handler = logging.StreamHandler()
        handler.addFilter(FiltreCorrelation())
        formatter = logging.Formatter('[%(correlation_id)s] %(message)s')
        handler.setFormatter(formatter)

    Format recommandé::
        '[%(correlation_id)s] %(levelname)s - %(name)s - %(message)s'
    """

    def filter(self, record: logging.LogRecord) -> bool:
        ctx = _contexte_execution.get()
        record.correlation_id = ctx.correlation_id if ctx else "--------"  # type: ignore
        record.operation = ctx.operation if ctx else ""  # type: ignore
        record.module_ctx = ctx.module if ctx else ""  # type: ignore
        return True


def configurer_logging_avec_correlation(
    niveau: int = logging.INFO,
    format_str: str = "[%(correlation_id)s] %(levelname)s - %(name)s - %(message)s",
) -> None:
    """
    Configure le logging avec correlation ID automatique.

    Args:
        niveau: Niveau de logging (défaut: INFO)
        format_str: Format du message avec %(correlation_id)s
    """
    handler = logging.StreamHandler()
    handler.addFilter(FiltreCorrelation())
    handler.setFormatter(logging.Formatter(format_str))

    root_logger = logging.getLogger()
    root_logger.setLevel(niveau)

    # Éviter les doublons - retirer les handlers avec FiltreCorrelation
    root_logger.handlers = [
        h
        for h in root_logger.handlers
        if not any(isinstance(f, FiltreCorrelation) for f in getattr(h, "filters", []))
    ]
    root_logger.addHandler(handler)


__all__ = [
    "ContexteExecution",
    "obtenir_contexte",
    "definir_contexte",
    "reset_contexte",
    "contexte_operation",
    "FiltreCorrelation",
    "configurer_logging_avec_correlation",
]
