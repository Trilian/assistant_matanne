"""Compatibilité legacy pour le bridge Saison → Menu."""

from src.services.cuisine.bridges_saison_menu import (
    SaisonMenuInteractionService,
    obtenir_service_saison_menu_interaction,
)

__all__ = [
    "SaisonMenuInteractionService",
    "obtenir_service_saison_menu_interaction",
]
