"""Compatibilité legacy pour le bridge Documents → Calendrier."""

from src.services.famille.bridges_documents_calendrier import (
    DocumentsCalendrierInteractionService,
    obtenir_service_documents_calendrier_interaction,
)

__all__ = [
    "DocumentsCalendrierInteractionService",
    "obtenir_service_documents_calendrier_interaction",
]
