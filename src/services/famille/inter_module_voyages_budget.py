"""Compatibilité legacy pour le bridge Voyages → Budget."""

from src.services.famille.bridges_voyages_budget import (
    VoyagesBudgetInteractionService,
    obtenir_service_voyages_budget_interaction,
)

__all__ = [
    "VoyagesBudgetInteractionService",
    "obtenir_service_voyages_budget_interaction",
]
