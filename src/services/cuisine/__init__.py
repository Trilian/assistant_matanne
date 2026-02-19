"""Package cuisine - Services recettes, planning, courses.

Imports paresseux pour éviter les imports circulaires.
Importez directement depuis les sous-packages:

    from src.services.cuisine.recettes import ServiceRecettes, obtenir_service_recettes
    from src.services.cuisine.planning import ServicePlanning, obtenir_service_planning
    from src.services.cuisine.courses import obtenir_service_courses
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
    if name == "ServiceRecettes":
        from src.services.cuisine.recettes import ServiceRecettes

        return ServiceRecettes
    if name == "obtenir_service_recettes":
        from src.services.cuisine.recettes import obtenir_service_recettes

        return obtenir_service_recettes
    if name == "ServicePlanning":
        from src.services.cuisine.planning import ServicePlanning

        return ServicePlanning
    if name == "obtenir_service_planning":
        from src.services.cuisine.planning import obtenir_service_planning

        return obtenir_service_planning
    if name == "obtenir_service_courses":
        from src.services.cuisine.courses import obtenir_service_courses

        return obtenir_service_courses
    if name == "obtenir_service_suggestions":
        from src.services.cuisine.suggestions import obtenir_service_suggestions

        return obtenir_service_suggestions
    if name == "obtenir_service_batch_cooking":
        from src.services.cuisine.batch_cooking import obtenir_service_batch_cooking

        return obtenir_service_batch_cooking
    raise AttributeError(f"module 'src.services.cuisine' has no attribute '{name}'")
