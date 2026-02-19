"""
Package Planning - Services de gestion du planning familial.

Ce package fournit:
- ServicePlanning: Gestion du planning repas hebdomadaire avec IA
- ServicePlanningUnifie: Agrégation complète (repas, activités, projets, routines)
- Types Pydantic: Schémas de validation pour tous les modèles planning
- Utilitaires: Fonctions pures pour dates, équilibre, formatage

Utilisation:
    ```python
    from src.services.cuisine.planning import obtenir_service_planning, ServicePlanning

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

# ═══════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════
from src.core.constants import (
    JOURS_SEMAINE,
    JOURS_SEMAINE_LOWER,
    TYPES_PROTEINES,
)
from src.core.constants import (
    TYPES_REPAS_KEYS as TYPES_REPAS,
)

from .global_planning import (
    # Classe principale
    ServicePlanningUnifie,
    get_planning_unified_service,
    get_unified_planning_service,
    # Factories
    obtenir_service_planning_unifie,
)

# ═══════════════════════════════════════════════════════════
# UTILITAIRES
# ═══════════════════════════════════════════════════════════
from .rappels import (
    OPTIONS_RAPPEL,
    ServiceRappels,
    format_rappel,
    get_rappels_service,
    obtenir_service_rappels,
)
from .recurrence import (
    JOURS_SEMAINE_INDEX as JOURS_SEMAINE_RECURRENCE,
)
from .recurrence import (
    OPTIONS_RECURRENCE,
    ServiceRecurrence,
    TypeRecurrence,
    format_recurrence,
    get_recurrence_service,
    obtenir_service_recurrence,
)

# ═══════════════════════════════════════════════════════════
# SERVICES
# ═══════════════════════════════════════════════════════════
from .service import (
    # Classe principale
    ServicePlanning,
    get_planning_service,
    # Factory
    obtenir_service_planning,
)
from .templates import (
    ServiceTemplates,
    get_templates_service,
    obtenir_service_templates,
)
from .types import (
    # Schémas planning unifié
    JourCompletSchema,
    # Schémas planning de base
    JourPlanning,
    ParametresEquilibre,
    SemaineCompleSchema,
    SemaineGenereeIASchema,
    SuggestionRecettesDay,
)
from .utils import (
    # Courses
    aggregate_ingredients,
    # IA
    build_planning_prompt_context,
    calculate_week_balance,
    calculate_week_dates,
    # Équilibre nutritionnel
    determine_protein_type,
    # Formatage
    format_meal_for_display,
    format_planning_summary,
    format_week_label,
    get_default_protein_schedule,
    get_monday_of_week,
    get_rayon_order,
    get_week_range,
    get_weekday_index,
    get_weekday_name,
    # Dates
    get_weekday_names,
    group_meals_by_type,
    is_balanced_week,
    parse_ai_planning_response,
    sort_ingredients_by_rayon,
    validate_meal_selection,
    # Validation
    validate_planning_dates,
)

# ═══════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════

# Alias de compatibilité (anciens noms)
PlanningService = ServicePlanning
PlanningAIService = ServicePlanningUnifie

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
    # ─────────────────────────────────────────────────────────
    # Services - Rappels
    # ─────────────────────────────────────────────────────────
    "OPTIONS_RAPPEL",
    "ServiceRappels",
    "format_rappel",
    "get_rappels_service",
    "obtenir_service_rappels",
    # ─────────────────────────────────────────────────────────
    # Services - Récurrence
    # ─────────────────────────────────────────────────────────
    "JOURS_SEMAINE_RECURRENCE",
    "OPTIONS_RECURRENCE",
    "ServiceRecurrence",
    "TypeRecurrence",
    "format_recurrence",
    "get_recurrence_service",
    "obtenir_service_recurrence",
    # ─────────────────────────────────────────────────────────
    # Services - Templates de semaine
    # ─────────────────────────────────────────────────────────
    "ServiceTemplates",
    "get_templates_service",
    "obtenir_service_templates",
]
