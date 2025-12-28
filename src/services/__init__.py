"""
Services - Point d'Entrée Unifié
Architecture refactorisée avec core/ui/utils
"""

# ═══════════════════════════════════════════════════════════════
# RECETTES
# ═══════════════════════════════════════════════════════════════

from .recettes import (
    recette_service,
    ai_recette_service,
    RecetteExporter,
    RecetteImporter,
    RecipeWebScraper,
    RecipeImageGenerator,
    create_recette_version_service
)

# ═══════════════════════════════════════════════════════════════
# INVENTAIRE
# ═══════════════════════════════════════════════════════════════

from .inventaire import (
    inventaire_service,
    CATEGORIES,
    EMPLACEMENTS,
    create_inventaire_ai_service,
    InventaireExporter,
    InventaireImporter
)

# ═══════════════════════════════════════════════════════════════
# COURSES
# ═══════════════════════════════════════════════════════════════

from .courses import (
    courses_service,
    MAGASINS_CONFIG,
    create_courses_ai_service
)

# ═══════════════════════════════════════════════════════════════
# PLANNING
# ═══════════════════════════════════════════════════════════════

from .planning import (
    planning_service,
    create_planning_generation_service,
    repas_service
)

# ═══════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════

__all__ = [
    # Recettes
    "recette_service",
    "ai_recette_service",
    "RecetteExporter",
    "RecetteImporter",
    "RecipeWebScraper",
    "RecipeImageGenerator",
    "create_recette_version_service",

    # Inventaire
    "inventaire_service",
    "CATEGORIES",
    "EMPLACEMENTS",
    "create_inventaire_ai_service",
    "InventaireExporter",
    "InventaireImporter",

    # Courses
    "courses_service",
    "MAGASINS_CONFIG",
    "create_courses_ai_service",

    # Planning
    "planning_service",
    "create_planning_generation_service",
    "repas_service"
]