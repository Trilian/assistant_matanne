"""
Module de compatibilité - Réexporte les fonctions des sous-modules.

DEPRECATED: Ce fichier existe uniquement pour la rétrocompatibilité.
Préférez importer directement depuis les modules spécifiques:
- src.core.date_utils pour les fonctions de dates
- src.services.planning.nutrition pour l'équilibre nutritionnel
- src.services.planning.formatters pour le formatage
- src.services.planning.agregation pour l'agrégation des courses
- src.services.planning.validators pour la validation
- src.services.planning.prompts pour les prompts IA

TODO: Supprimer ce fichier une fois les derniers consommateurs migrés.
"""

import warnings as _warnings

_warnings.warn(
    "src.services.cuisine.planning.utils est déprécié. "
    "Importer directement depuis les sous-modules (nutrition, formatters, etc.).",
    DeprecationWarning,
    stacklevel=2,
)

# ═══════════════════════════════════════════════════════════
# DATES ET CALENDRIER
# Maintenant centralisées dans core/date_utils.py
# ═══════════════════════════════════════════════════════════

from src.core.date_utils import (
    format_week_label,
    get_weekday_index,
    get_weekday_name,
    get_weekday_names,
)
from src.core.date_utils import (
    obtenir_bornes_semaine as get_week_range,
)
from src.core.date_utils import (
    obtenir_debut_semaine as get_monday_of_week,
)
from src.core.date_utils import (
    obtenir_jours_semaine as calculate_week_dates,
)

# ═══════════════════════════════════════════════════════════
# AGRÉGATION DES COURSES
# ═══════════════════════════════════════════════════════════
from src.services.cuisine.planning.agregation import (
    aggregate_ingredients,
    get_rayon_order,
    sort_ingredients_by_rayon,
)

# ═══════════════════════════════════════════════════════════
# FORMATAGE ET AFFICHAGE
# ═══════════════════════════════════════════════════════════
from src.services.cuisine.planning.formatters import (
    format_meal_for_display,
    format_planning_summary,
    group_meals_by_type,
)

# ═══════════════════════════════════════════════════════════
# ÉQUILIBRE NUTRITIONNEL
# ═══════════════════════════════════════════════════════════
from src.services.cuisine.planning.nutrition import (
    calculate_week_balance,
    determine_protein_type,
    get_default_protein_schedule,
    is_balanced_week,
)

# ═══════════════════════════════════════════════════════════
# GÉNÉRATION DE PROMPT IA
# ═══════════════════════════════════════════════════════════
from src.services.cuisine.planning.prompts import (
    build_planning_prompt_context,
    parse_ai_planning_response,
)

# ═══════════════════════════════════════════════════════════
# VALIDATION
# ═══════════════════════════════════════════════════════════
from src.services.cuisine.planning.validators import (
    validate_meal_selection,
    validate_planning_dates,
)

# ═══════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════

__all__ = [
    # Dates (depuis core/date_utils)
    "get_weekday_names",
    "get_weekday_name",
    "get_weekday_index",
    "calculate_week_dates",
    "get_week_range",
    "get_monday_of_week",
    "format_week_label",
    # Équilibre (depuis nutrition.py)
    "determine_protein_type",
    "get_default_protein_schedule",
    "calculate_week_balance",
    "is_balanced_week",
    # Formatage (depuis formatters.py)
    "format_meal_for_display",
    "format_planning_summary",
    "group_meals_by_type",
    # Courses (depuis agregation.py)
    "aggregate_ingredients",
    "sort_ingredients_by_rayon",
    "get_rayon_order",
    # Validation (depuis validators.py)
    "validate_planning_dates",
    "validate_meal_selection",
    # IA (depuis prompts.py)
    "build_planning_prompt_context",
    "parse_ai_planning_response",
]
