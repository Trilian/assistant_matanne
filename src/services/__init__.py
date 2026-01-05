"""
Services - Point d'Entrée Unifié COMPLET

Exporte tous les services métier de l'application.
Architecture refactorisée avec BaseService + BaseAIService.

✅ MODULES COMPLETS:
- Recettes (6 fichiers)
- Inventaire (3 fichiers)
- Courses (3 fichiers)
- Planning (3 fichiers)
"""

# ═══════════════════════════════════════════════════════════
# BASE SERVICES (génériques)
# ═══════════════════════════════════════════════════════════

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
# 📚 RECETTES (6 fichiers)
# ═══════════════════════════════════════════════════════════

from .recettes import (
    # Service CRUD
    RecetteService,
    recette_service,

    # Service IA
    RecetteAIService,
    recette_ai_service,

    # Service Versions (Bébé/Batch)
    RecetteVersionService,
    recette_version_service,

    # Service Scraping Web
    RecipeWebScraper,
    RecipeImageGenerator,

    # Import/Export
    RecetteExporter,
    RecetteImporter,
)

# ═══════════════════════════════════════════════════════════
# 📦 INVENTAIRE (3 fichiers)
# ═══════════════════════════════════════════════════════════

from .inventaire import (
    # Service CRUD
    InventaireService,
    inventaire_service,

    # Service IA
    InventaireAIService,
    inventaire_ai_service,

    # Import/Export
    InventaireExporter,
    InventaireImporter,

    # Constantes métier
    CATEGORIES,
    EMPLACEMENTS,
)

# ═══════════════════════════════════════════════════════════
# 🛒 COURSES (3 fichiers)
# ═══════════════════════════════════════════════════════════

from .courses import (
    # Service CRUD
    CoursesService,
    courses_service,

    # Service IA
    CoursesAIService,
    create_courses_ai_service,

    # Import/Export
    CoursesExporter,
    CoursesImporter,

    # Constantes métier
    MAGASINS_CONFIG,
)

# ═══════════════════════════════════════════════════════════
# 📅 PLANNING (3 fichiers)
# ═══════════════════════════════════════════════════════════

from .planning import (
    # Services CRUD
    PlanningService,
    planning_service,
    RepasService,
    repas_service,

    # Service IA Génération
    PlanningGenerationService,
    create_planning_generation_service,

    # Constantes métier
    JOURS_SEMAINE,
)

# ═══════════════════════════════════════════════════════════
# 📤 EXPORTS GLOBAUX
# ═══════════════════════════════════════════════════════════

__all__ = [
    # ═══════════════════════════════════════════════════════════
    # BASE
    # ═══════════════════════════════════════════════════════════
    "BaseService",
    "BaseAIService",
    "RecipeAIMixin",
    "PlanningAIMixin",
    "InventoryAIMixin",
    "IOService",

    # ═══════════════════════════════════════════════════════════
    # RECETTES
    # ═══════════════════════════════════════════════════════════
    # Classes
    "RecetteService",
    "RecetteAIService",
    "RecetteVersionService",
    "RecipeWebScraper",
    "RecipeImageGenerator",
    "RecetteExporter",
    "RecetteImporter",

    # Instances
    "recette_service",
    "recette_ai_service",
    "recette_version_service",

    # ═══════════════════════════════════════════════════════════
    # INVENTAIRE
    # ═══════════════════════════════════════════════════════════
    # Classes
    "InventaireService",
    "InventaireAIService",
    "InventaireExporter",
    "InventaireImporter",

    # Instances
    "inventaire_service",
    "inventaire_ai_service",

    # Constantes
    "CATEGORIES",
    "EMPLACEMENTS",

    # ═══════════════════════════════════════════════════════════
    # COURSES
    # ═══════════════════════════════════════════════════════════
    # Classes
    "CoursesService",
    "CoursesAIService",
    "CoursesExporter",
    "CoursesImporter",

    # Instances
    "courses_service",
    "create_courses_ai_service",

    # Constantes
    "MAGASINS_CONFIG",

    # ═══════════════════════════════════════════════════════════
    # PLANNING
    # ═══════════════════════════════════════════════════════════
    # Classes
    "PlanningService",
    "RepasService",
    "PlanningGenerationService",

    # Instances
    "planning_service",
    "repas_service",
    "create_planning_generation_service",

    # Constantes
    "JOURS_SEMAINE",
]


# ═══════════════════════════════════════════════════════════
# 📊 MÉTA-INFORMATIONS
# ═══════════════════════════════════════════════════════════

def get_services_info() -> dict:
    """
    Retourne informations sur tous les services disponibles.

    Returns:
        Dict avec stats et métadonnées

    Example:
        >>> from src.services import get_services_info
        >>> info = get_services_info()
        >>> print(f"{info['total_services']} services disponibles")
    """
    return {
        "total_services": len(__all__),
        "modules": {
            "recettes": 7,
            "inventaire": 6,
            "courses": 6,
            "planning": 6,
            "base": 6
        },
        "services_ia": [
            "recette_ai_service",
            "inventaire_ai_service",
            "create_courses_ai_service",
            "create_planning_generation_service"
        ],
        "services_crud": [
            "recette_service",
            "inventaire_service",
            "courses_service",
            "planning_service",
            "repas_service"
        ],
        "services_io": [
            "RecetteExporter", "RecetteImporter",
            "InventaireExporter", "InventaireImporter",
            "CoursesExporter", "CoursesImporter"
        ]
    }