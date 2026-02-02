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
# 📅 PLANNING (2 services distincts)
# ═══════════════════════════════════════════════════════════
# PlanningService: Gestion repas hebdomadaires + génération IA menus
# PlanningAIService: Vue unifiée (repas + activités + projets + routines)
from .planning import (
    # Services CRUD
    PlanningService,
    get_planning_service,
    planning_service,
    # Schémas
    JourPlanning,
    ParametresEquilibre,
)
from .planning_unified import (
    # Service Unifié (repas + activités + projets + routines)
    PlanningAIService,
    get_planning_unified_service,
    # Schémas
    JourCompletSchema,
    SemaineCompleSchema,
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
# � PRÉFÉRENCES UTILISATEUR
# ═══════════════════════════════════════════════════════════
from .user_preferences import (
    UserPreferenceService,
    get_user_preference_service,
)

# ═══════════════════════════════════════════════════════════
# �📤 EXPORTS GLOBAUX
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
    "PlanningAIService",
    # Factories
    "get_planning_service",
    "get_planning_unified_service",
    # Instances
    "planning_service",
    # Schémas
    "JourPlanning",
    "ParametresEquilibre",
    "JourCompletSchema",
    "SemaineCompleSchema",
    # ═══════════════════════════════════════════════════════════
    # PRÉFÉRENCES UTILISATEUR
    # ═══════════════════════════════════════════════════════════
    # Classes
    "UserPreferenceService",
    # Factories
    "get_user_preference_service",
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
