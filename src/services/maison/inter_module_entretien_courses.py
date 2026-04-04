"""Compatibilité legacy pour le bridge Entretien → Courses."""

from src.services.maison.bridges_entretien_courses import (
    EntretienCoursesInteractionService,
    obtenir_service_entretien_courses_interaction,
)

__all__ = [
    "EntretienCoursesInteractionService",
    "obtenir_service_entretien_courses_interaction",
]
