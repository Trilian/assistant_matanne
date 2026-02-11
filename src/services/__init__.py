"""
Services - Point d'Entrée Unifié COMPLET

Exporte tous les services métier de l'application.
Architecture refactorisée avec BaseService depuis base/ (pas de cycle).

✅ MODULES COMPLETS:
- Base (types, AI, IO)
- Recettes (6 fichiers)
- Inventaire (3 fichiers)
- Courses (3 fichiers)
- Planning (3 fichiers)
"""

# ═══════════════════════════════════════════════════════════
# BASE SERVICES (génériques) - Import depuis base/
# ═══════════════════════════════════════════════════════════

from .base import (
    BaseAIService,
    BaseService,
    InventoryAIMixin,
    PlanningAIMixin,
    RecipeAIMixin,
    IOService,
    create_base_ai_service,
)

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

# Service IO importé depuis base/

# ═══════════════════════════════════════════════════════════
# 📅 PLANNING (Package unifié)
# ═══════════════════════════════════════════════════════════
# PlanningService: Gestion repas hebdomadaires + génération IA menus
# PlanningAIService: Vue unifiée (repas + activités + projets + routines)
from .planning import (
    # Services CRUD
    PlanningService,
    get_planning_service,
    # Service Unifié (repas + activités + projets + routines)
    PlanningAIService,
    get_planning_unified_service,
    # Schémas
    JourPlanning,
    ParametresEquilibre,
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
    # Import URL (scraping)
    ImportedIngredient,
    ImportedRecipe,
    ImportResult,
    RecipeImportService,
    get_recipe_import_service,
)
# BaseService importé depuis base/

# ═══════════════════════════════════════════════════════════
# 🧑 UTILISATEUR (auth, historique, préférences)
# ═══════════════════════════════════════════════════════════
from .utilisateur import (
    # Auth
    AuthService,
    get_auth_service,
    UserProfile,
    AuthResult,
    Role,
    Permission,
    render_login_form,
    render_user_menu,
    render_profile_settings,
    require_authenticated,
    require_role,
    # Historique
    ActionHistoryService,
    get_action_history_service,
    ActionType,
    ActionEntry,
    ActionFilter,
    ActionStats,
    render_activity_timeline,
    render_user_activity,
    render_activity_stats,
    # Préférences
    UserPreferenceService,
    get_user_preference_service,
)

# ═══════════════════════════════════════════════════════════
# 🔌 INTÉGRATIONS EXTERNES
# ═══════════════════════════════════════════════════════════
from .integrations import (
    # Codes-barres
    BarcodeService,
    get_barcode_service,
    BarcodeData,
    BarcodeArticle,
    BarcodeRecette,
    ScanResultat,
    # OpenFoodFacts
    OpenFoodFactsService,
    get_openfoodfacts_service,
    NutritionInfo,
    ProduitOpenFoodFacts,
    # Facture OCR
    FactureOCRService,
    get_facture_ocr_service,
    DonneesFacture,
    ResultatOCR,
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
    "RecetteSuggestion",
    "VersionBebeGeneree",
    "VersionBebeGeneree",
    # Import URL (scraping)
    "ImportedIngredient",
    "ImportedRecipe",
    "ImportResult",
    "RecipeImportService",
    "get_recipe_import_service",
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
    # UTILISATEUR (auth, historique, préférences)
    # ═══════════════════════════════════════════════════════════
    # Auth
    "AuthService",
    "get_auth_service",
    "UserProfile",
    "AuthResult",
    "Role",
    "Permission",
    "render_login_form",
    "render_user_menu",
    "render_profile_settings",
    "require_authenticated",
    "require_role",
    # Historique
    "ActionHistoryService",
    "get_action_history_service",
    "ActionType",
    "ActionEntry",
    "ActionFilter",
    "ActionStats",
    "render_activity_timeline",
    "render_user_activity",
    "render_activity_stats",
    # Préférences
    "UserPreferenceService",
    "get_user_preference_service",
    # ═══════════════════════════════════════════════════════════
    # INTÉGRATIONS EXTERNES
    # ═══════════════════════════════════════════════════════════
    # Codes-barres
    "BarcodeService",
    "get_barcode_service",
    "BarcodeData",
    "BarcodeArticle",
    "BarcodeRecette",
    "ScanResultat",
    # OpenFoodFacts
    "OpenFoodFactsService",
    "get_openfoodfacts_service",
    "NutritionInfo",
    "ProduitOpenFoodFacts",
    # Facture OCR
    "FactureOCRService",
    "get_facture_ocr_service",
    "DonneesFacture",
    "ResultatOCR",
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
