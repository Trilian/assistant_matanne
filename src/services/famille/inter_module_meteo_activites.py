"""Compatibilité legacy pour le bridge Météo → Activités."""

from src.services.famille.bridges_meteo_activites import (
    MeteoActivitesInteractionService,
    obtenir_service_meteo_activites_interaction,
)

__all__ = [
    "MeteoActivitesInteractionService",
    "obtenir_service_meteo_activites_interaction",
]
