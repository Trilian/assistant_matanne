"""
Package Planning - Services de gestion du planning familial.

Ce package fournit:
- ServicePlanning: Gestion du planning repas hebdomadaire avec IA
- ServicePlanningUnifie: Agrégation complète (repas, activités, projets, routines)
- Types Pydantic: Schémas de validation pour tous les modèles planning
- Utilitaires: Fonctions pures pour dates, équilibre, formatage

Utilisation:
    ```python
    from src.services.planning import obtenir_service_planning, ServicePlanning
    
    service = obtenir_service_planning()
    planning = service.get_planning()
    ```

Compatibilité:
    Les anciens noms sont conservés comme alias:
    - PlanningService = ServicePlanning
    - PlanningAIService = ServicePlanningUnifie
    - get_planning_service = obtenir_service_planning
    - get_planning_unified_service = obtenir_service_planning_unifie
"""

# ═══════════════════════════════════════════════════════════
# TYPES & SCHÉMAS PYDANTIC
# ═══════════════════════════════════════════════════════════

from .types import (
    # Schémas planning de base
    JourPlanning,
    SuggestionRecettesDay,
    ParametresEquilibre,
    # Schémas planning unifié
    JourCompletSchema,
    SemaineCompleSchema,
    SemaineGenereeIASchema,
)

# ═══════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════

from .constantes import (
    JOURS_SEMAINE,
    JOURS_SEMAINE_LOWER,
    TYPES_REPAS,
    TYPES_PROTEINES,
)

# ═══════════════════════════════════════════════════════════
# UTILITAIRES
# ═══════════════════════════════════════════════════════════

from .utils import (
    # Dates
    get_weekday_names,
    get_weekday_name,
    get_weekday_index,
    calculate_week_dates,
    get_week_range,
    get_monday_of_week,
    format_week_label,
    # Équilibre nutritionnel
    determine_protein_type,
    get_default_protein_schedule,
    calculate_week_balance,
    is_balanced_week,
    # Formatage
    format_meal_for_display,
    format_planning_summary,
    group_meals_by_type,
    # Courses
    aggregate_ingredients,
    sort_ingredients_by_rayon,
    get_rayon_order,
    # Validation
    validate_planning_dates,
    validate_meal_selection,
    # IA
    build_planning_prompt_context,
    parse_ai_planning_response,
)

# ═══════════════════════════════════════════════════════════
# SERVICES
# ═══════════════════════════════════════════════════════════

from .service import (
    # Classe principale
    ServicePlanning,
    # Alias de compatibilité
    PlanningService,
    # Factory
    obtenir_service_planning,
    get_planning_service,
)

from .global_planning import (
    # Classe principale
    ServicePlanningUnifie,
    # Alias de compatibilité
    PlanningAIService,
    # Factories
    obtenir_service_planning_unifie,
    get_planning_unified_service,
    get_unified_planning_service,
)


# ═══════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════

__all__ = [
    # ─────────────────────────────────────────────────────────
    # Types & Schémas
    # ─────────────────────────────────────────────────────────
    "JourPlanning",
    "SuggestionRecettesDay",
    "ParametresEquilibre",
    "JourCompletSchema",
    "SemaineCompleSchema",
    "SemaineGenereeIASchema",
    # ─────────────────────────────────────────────────────────
    # Constantes
    # ─────────────────────────────────────────────────────────
    "JOURS_SEMAINE",
    "JOURS_SEMAINE_LOWER",
    "TYPES_REPAS",
    "TYPES_PROTEINES",
    # ─────────────────────────────────────────────────────────
    # Utilitaires - Dates
    # ─────────────────────────────────────────────────────────
    "get_weekday_names",
    "get_weekday_name",
    "get_weekday_index",
    "calculate_week_dates",
    "get_week_range",
    "get_monday_of_week",
    "format_week_label",
    # ─────────────────────────────────────────────────────────
    # Utilitaires - Équilibre
    # ─────────────────────────────────────────────────────────
    "determine_protein_type",
    "get_default_protein_schedule",
    "calculate_week_balance",
    "is_balanced_week",
    # ─────────────────────────────────────────────────────────
    # Utilitaires - Formatage
    # ─────────────────────────────────────────────────────────
    "format_meal_for_display",
    "format_planning_summary",
    "group_meals_by_type",
    # ─────────────────────────────────────────────────────────
    # Utilitaires - Courses
    # ─────────────────────────────────────────────────────────
    "aggregate_ingredients",
    "sort_ingredients_by_rayon",
    "get_rayon_order",
    # ─────────────────────────────────────────────────────────
    # Utilitaires - Validation
    # ─────────────────────────────────────────────────────────
    "validate_planning_dates",
    "validate_meal_selection",
    # ─────────────────────────────────────────────────────────
    # Utilitaires - IA
    # ─────────────────────────────────────────────────────────
    "build_planning_prompt_context",
    "parse_ai_planning_response",
    # ─────────────────────────────────────────────────────────
    # Services - Planning de base
    # ─────────────────────────────────────────────────────────
    "ServicePlanning",
    "PlanningService",  # Alias compatibilité
    "obtenir_service_planning",
    "get_planning_service",  # Alias compatibilité
    # ─────────────────────────────────────────────────────────
    # Services - Planning unifié
    # ─────────────────────────────────────────────────────────
    "ServicePlanningUnifie",
    "PlanningAIService",  # Alias compatibilité
    "obtenir_service_planning_unifie",
    "get_planning_unified_service",  # Alias compatibilité
    "get_unified_planning_service",  # Alias compatibilité
]
