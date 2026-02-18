"""
Module cuisine - Gestion des recettes, inventaire et courses.

Ce module regroupe tous les services liés à la cuisine:
- Recettes (création, import, recherche, suggestions IA)
- Inventaire alimentaire
- Listes de courses
- Batch cooking et planification des préparations
"""

# Ré-export depuis les sous-modules pour compatibilité
from src.services.batch_cooking import (
    BatchCookingService,
    ServiceBatchCooking,
    get_batch_cooking_service,
    obtenir_service_batch_cooking,
)
from src.services.courses import (
    CoursesService,
    ServiceCourses,
    get_courses_service,
    obtenir_service_courses,
)
from src.services.inventaire import (
    InventaireService,
    ServiceInventaire,
    get_inventaire_service,
    obtenir_service_inventaire,
)
from src.services.recettes import (
    RecetteService,
    RecipeImportService,
    ServiceRecettes,
    get_recette_service,
    get_recipe_import_service,
    obtenir_service_recettes,
)
from src.services.suggestions import (
    PredictionService,
    ServiceSuggestions,
    SuggestionsIAService,
    get_suggestions_ia_service,
    obtenir_service_predictions,
    obtenir_service_suggestions,
)

__all__ = [
    # Recettes
    "RecetteService",
    "ServiceRecettes",
    "get_recette_service",
    "obtenir_service_recettes",
    "RecipeImportService",
    "get_recipe_import_service",
    # Inventaire
    "InventaireService",
    "ServiceInventaire",
    "get_inventaire_service",
    "obtenir_service_inventaire",
    # Courses
    "CoursesService",
    "ServiceCourses",
    "get_courses_service",
    "obtenir_service_courses",
    # Batch cooking
    "BatchCookingService",
    "ServiceBatchCooking",
    "get_batch_cooking_service",
    "obtenir_service_batch_cooking",
    # Suggestions
    "ServiceSuggestions",
    "SuggestionsIAService",
    "obtenir_service_suggestions",
    "get_suggestions_ia_service",
    "PredictionService",
    "obtenir_service_predictions",
]
