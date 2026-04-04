"""Compatibilité legacy pour le bridge Jardin → Entretien."""

from src.services.maison.bridges_jardin_entretien import (
    JardinEntretienInteractionService,
    obtenir_service_jardin_entretien_interaction,
)

__all__ = [
    "JardinEntretienInteractionService",
    "obtenir_service_jardin_entretien_interaction",
]
