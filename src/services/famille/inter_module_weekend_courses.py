"""Compatibilité legacy pour le bridge Weekend → Courses."""

from src.services.famille.bridges_weekend_courses import (
    WeekendCoursesInteractionService,
    obtenir_service_weekend_courses_interaction,
)

__all__ = [
    "WeekendCoursesInteractionService",
    "obtenir_service_weekend_courses_interaction",
]
