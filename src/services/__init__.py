"""
Services - Point d'Entrée Unifié COMPLET

Exporte tous les services métier de l'application.
Architecture refactorisée avec BaseService depuis types.py (pas de cycle).

✅ MODULES COMPLETS:
- Recettes (6 fichiers)
- Inventaire (3 fichiers)
- Courses (3 fichiers)
- Planning (3 fichiers)
"""

# ═══════════════════════════════════════════════════════════
# BASE SERVICES (génériques) - Import depuis types.py
# ═══════════════════════════════════════════════════════════

from .base_ai_service import BaseAIService, InventoryAIMixin, PlanningAIMixin, RecipeAIMixin

# ═══════════════════════════════════════════════════════════
# 🛒 COURSES (3 fichiers)
# ═══════════════════════════════════════════════════════════
from .courses import (
    # Service CRUD
    CoursesService,
    courses_service,
)

# ═══════════════════════════════════════════════════════════
# 📦 INVENTAIRE (3 fichiers)
# ═══════════════════════════════════════════════════════════
from .inventaire import (
    # Constantes métier
    CATEGORIES,
    EMPLACEMENTS,
    # Service CRUD
    InventaireService,
    inventaire_service,
)

# Service IO (Import/Export universel)
from .io_service import IOService

# ═══════════════════════════════════════════════════════════
# 📅 PLANNING (3 fichiers)
# ═══════════════════════════════════════════════════════════
from .planning import (
    # Services CRUD
    PlanningService,
    planning_service,
)

# ═══════════════════════════════════════════════════════════
# 📚 RECETTES (6 fichiers)
# ═══════════════════════════════════════════════════════════
from .recettes import (
    # Service CRUD
    RecetteService,
    # Schémas
    RecetteSuggestion,
    VersionBebeGeneree,
    VersionBebeGeneree,
    recette_service,
)
from .types import BaseService  # ✅ Plus de cycle ici

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
    "RecetteSuggestion",
    "VersionBebeGeneree",
    "VersionBebeGeneree",
    # Instances
    "recette_service",
    # ═══════════════════════════════════════════════════════════
    # INVENTAIRE
    # ═══════════════════════════════════════════════════════════
    # Classes
    "InventaireService",
    # Instances
    "inventaire_service",
    # Constantes
    "CATEGORIES",
    "EMPLACEMENTS",
    # ═══════════════════════════════════════════════════════════
    # COURSES
    # ═══════════════════════════════════════════════════════════
    # Classes
    "CoursesService",
    # Instances
    "courses_service",
    # ═══════════════════════════════════════════════════════════
    # PLANNING
    # ═══════════════════════════════════════════════════════════
    # Classes
    "PlanningService",
    # Instances
    "planning_service",
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
        >>> logger.info(f"{info['total_services']} services disponibles")
    """
    return {
        "total_services": len(__all__),
        "modules": {"recettes": 4, "inventaire": 3, "courses": 2, "planning": 2, "base": 6},
        "services_crud": [
            "recette_service",
            "inventaire_service",
            "courses_service",
            "planning_service",
        ],
    }
