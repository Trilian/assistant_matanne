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
    IOService,
    PlanningAIMixin,
    RecipeAIMixin,
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
# 🔌 INTÉGRATIONS EXTERNES
# ═══════════════════════════════════════════════════════════
from .integrations import (
    BarcodeArticle,
    BarcodeData,
    BarcodeRecette,
    # Codes-barres
    BarcodeService,
    DonneesFacture,
    # Facture OCR
    FactureOCRService,
    NutritionInfo,
    # OpenFoodFacts
    OpenFoodFactsService,
    ProduitOpenFoodFacts,
    ResultatOCR,
    ScanResultat,
    get_barcode_service,
    get_facture_ocr_service,
    get_openfoodfacts_service,
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
# ServicePlanning: Gestion repas hebdomadaires + génération IA menus
# ServicePlanningUnifie: Vue unifiée (repas + activités + projets + routines)
from .planning import (
    JourCompletSchema,
    # Schémas
    JourPlanning,
    ParametresEquilibre,
    SemaineCompleSchema,
    # Services CRUD
    ServicePlanning,
    # Service Unifié (repas + activités + projets + routines)
    ServicePlanningUnifie,
    get_planning_service,
    get_planning_unified_service,
)

# ═══════════════════════════════════════════════════════════
# 📚 RECETTES (6 fichiers)
# ═══════════════════════════════════════════════════════════
from .recettes import (
    # Import URL (scraping)
    ImportedIngredient,
    ImportedRecipe,
    ImportResult,
    # Service CRUD
    RecetteService,
    # Schémas
    RecetteSuggestion,
    RecipeImportService,
    VersionBebeGeneree,
    get_recipe_import_service,
    recette_service,
)

# BaseService importé depuis base/
# ═══════════════════════════════════════════════════════════
# 🧑 UTILISATEUR (auth, historique, préférences)
# ═══════════════════════════════════════════════════════════
from .utilisateur import (
    ActionEntry,
    ActionFilter,
    # Historique
    ActionHistoryService,
    ActionStats,
    ActionType,
    AuthResult,
    # Auth
    AuthService,
    Permission,
    Role,
    # Préférences
    UserPreferenceService,
    UserProfile,
    get_action_history_service,
    get_auth_service,
    get_user_preference_service,
    render_activity_stats,
    render_activity_timeline,
    render_login_form,
    render_profile_settings,
    render_user_activity,
    render_user_menu,
    require_authenticated,
    require_role,
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
    "ServicePlanning",
    "ServicePlanningUnifie",
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
