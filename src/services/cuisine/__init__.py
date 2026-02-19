"""Package cuisine - Services recettes, planning, courses.

Imports paresseux pour éviter les imports circulaires.
Importez directement depuis les sous-packages:

    from src.services.cuisine.recettes import RecetteService, get_recette_service
    from src.services.cuisine.planning import ServicePlanning, get_planning_service
    from src.services.cuisine.courses import get_courses_service
"""

__all__ = [
    "recettes",
    "planning",
    "courses",
    "suggestions",
    "batch_cooking",
]


def __getattr__(name: str):
    """Lazy import pour éviter les imports circulaires."""
    if name == "RecetteService":
        from src.services.cuisine.recettes import RecetteService
        return RecetteService
    if name == "get_recette_service":
        from src.services.cuisine.recettes import get_recette_service
        return get_recette_service
    if name == "ServicePlanning":
        from src.services.cuisine.planning import ServicePlanning
        return ServicePlanning
    if name == "get_planning_service":
        from src.services.cuisine.planning import get_planning_service
        return get_planning_service
    if name == "get_courses_service":
        from src.services.cuisine.courses import get_courses_service
        return get_courses_service
    if name == "obtenir_service_suggestions":
        from src.services.cuisine.suggestions import obtenir_service_suggestions
        return obtenir_service_suggestions
    if name == "obtenir_service_batch_cooking":
        from src.services.cuisine.batch_cooking import obtenir_service_batch_cooking
        return obtenir_service_batch_cooking
    raise AttributeError(f"module 'src.services.cuisine' has no attribute '{name}'")
