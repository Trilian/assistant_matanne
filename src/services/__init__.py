"""
Services - Point d'Entrée Unifié

Exporte tous les services métier de l'application.
Architecture refactorisée avec BaseService + BaseAIService.
"""

# Base Services (génériques)
from .base_service import BaseService
from .base_ai_service import (
    BaseAIService,
    RecipeAIMixin,
    PlanningAIMixin,
    InventoryAIMixin
)

# Service IO (Import/Export universel)
from .io_service import IOService

# ═══════════════════════════════════════════════════════════
# RECETTES
# ═══════════════════════════════════════════════════════════

from .recettes import (
    # Service CRUD
    recette_service,

    # Service IA
    recette_ai_service,

    # Service Versions (Bébé/Batch)
    recette_version_service,

    # Service Scraping Web
    RecipeWebScraper,
    RecipeImageGenerator,

    # Import/Export
    RecetteExporter,
    RecetteImporter,
)

# ═══════════════════════════════════════════════════════════
# INVENTAIRE
# ═══════════════════════════════════════════════════════════

from .inventaire import (
    # Service CRUD
    inventaire_service,

    # Service IA
    inventaire_ai_service,

    # Import/Export
    InventaireExporter,
    InventaireImporter,

    # Constantes
    CATEGORIES,
    EMPLACEMENTS,
)

# ═══════════════════════════════════════════════════════════
# COURSES
# ═══════════════════════════════════════════════════════════

from .courses import (
    # Service CRUD
    courses_service,

    # Service IA
    courses_ai_service,

    # Constantes
    MAGASINS_CONFIG,
)

# ═══════════════════════════════════════════════════════════
# PLANNING
# ═══════════════════════════════════════════════════════════

from .planning import (
    # Services CRUD
    planning_service,
    repas_service,

    # Service IA Génération
    planning_generation_service,

    # Constantes
    JOURS_SEMAINE,
)

# ═══════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════

__all__ = [
    # Base
    "BaseService",
    "BaseAIService",
    "RecipeAIMixin",
    "PlanningAIMixin",
    "InventoryAIMixin",
    "IOService",

    # Recettes
    "recette_service",
    "recette_ai_service",
    "recette_version_service",
    "RecipeWebScraper",
    "RecipeImageGenerator",
    "RecetteExporter",
    "RecetteImporter",

    # Inventaire
    "inventaire_service",
    "inventaire_ai_service",
    "InventaireExporter",
    "InventaireImporter",
    "CATEGORIES",
    "EMPLACEMENTS",

    # Courses
    "courses_service",
    "courses_ai_service",
    "MAGASINS_CONFIG",

    # Planning
    "planning_service",
    "repas_service",
    "planning_generation_service",
    "JOURS_SEMAINE",
]