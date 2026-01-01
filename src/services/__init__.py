"""
Services - Point d'Entrée Unifié REFACTORISÉ
Architecture avec BaseAIService
"""

# BaseAIService
from .base_ai_service import (
    BaseAIService,
    RecipeAIMixin,
    PlanningAIMixin,
    InventoryAIMixin
)

# 🆕 Services IA Refactorisés (nouvelle version)
from .ai_services import (
    AIRecetteService,
    CoursesAIService,
    InventaireAIService,
    PlanningGenerationService,
    # Factories
    create_ai_recette_service,
    create_courses_ai_service,
    create_inventaire_ai_service,
    create_planning_generation_service
)

# Services métier (inchangés)
from .recettes import recette_service, RecetteExporter, RecetteImporter
from .inventaire import inventaire_service, CATEGORIES, EMPLACEMENTS
from .courses import courses_service, MAGASINS_CONFIG
from .planning import planning_service, repas_service

__all__ = [
    # BaseAIService & Mixins
    "BaseAIService",
    "RecipeAIMixin",
    "PlanningAIMixin",
    "InventoryAIMixin",

    # 🆕 Services IA Refactorisés
    "AIRecetteService",
    "CoursesAIService",
    "InventaireAIService",
    "PlanningGenerationService",

    # Factories IA
    "create_ai_recette_service",
    "create_courses_ai_service",
    "create_inventaire_ai_service",
    "create_planning_generation_service",

    # Services métier
    "recette_service",
    "RecetteExporter",
    "RecetteImporter",
    "inventaire_service",
    "CATEGORIES",
    "EMPLACEMENTS",
    "courses_service",
    "MAGASINS_CONFIG",
    "planning_service",
    "repas_service"
]
