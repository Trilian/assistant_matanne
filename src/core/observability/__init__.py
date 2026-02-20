"""
Observability - Contexte d'exécution avec correlation ID.

Propage un ID unique à travers tous les composants pour
tracer une requête end-to-end (logs, métriques, traces).

Usage::
    from src.core.observability import contexte_operation, obtenir_contexte

    with contexte_operation("charger_recettes", module="cuisine"):
        # Le contexte est propagé automatiquement
        logger.info("Chargement...")  # [abc123] Chargement...
        recettes = service.charger()
"""

from .context import (
    ContexteExecution,
    FiltreCorrelation,
    configurer_logging_avec_correlation,
    contexte_operation,
    definir_contexte,
    obtenir_contexte,
    reset_contexte,
)

__all__ = [
    "ContexteExecution",
    "obtenir_contexte",
    "definir_contexte",
    "reset_contexte",
    "contexte_operation",
    "FiltreCorrelation",
    "configurer_logging_avec_correlation",
]
