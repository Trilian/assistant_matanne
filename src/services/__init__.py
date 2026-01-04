"""
Services - Point d'Entrée Unifié (VERSION NETTOYÉE)
"""

# Base Service (générique CRUD)
from .base_service import BaseService

# 🆕 Services IA Refactorisés
try:
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
    AI_SERVICES_AVAILABLE = True
except ImportError as e:
    import logging
    logging.warning(f"Services IA non disponibles: {e}")
    AI_SERVICES_AVAILABLE = False
    # Stubs pour éviter erreurs import
    AIRecetteService = None
    CoursesAIService = None
    InventaireAIService = None
    PlanningGenerationService = None
    create_ai_recette_service = None
    create_courses_ai_service = None
    create_inventaire_ai_service = None
    create_planning_generation_service = None

# Services métier (recettes, inventaire, courses, planning)
from .recettes import recette_service, RecetteExporter, RecetteImporter
from .inventaire import inventaire_service, CATEGORIES, EMPLACEMENTS
from .courses import courses_service, MAGASINS_CONFIG
from .planning import planning_service, repas_service

# ⚠️ IO Service maintenant dans src/ui/base_io_service
# Ne plus importer depuis ici

__all__ = [
    # Base
    "BaseService",

    # 🆕 Services IA (si disponibles)
    "AIRecetteService",
    "CoursesAIService",
    "InventaireAIService",
    "PlanningGenerationService",

    # Factories IA
    "create_ai_recette_service",
    "create_courses_ai_service",
    "create_inventaire_ai_service",
    "create_planning_generation_service",

    # Flag disponibilité
    "AI_SERVICES_AVAILABLE",

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
    "repas_service",
]