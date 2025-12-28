"""
Utils - Point d'Entrée Unifié
Import simplifié de toutes les fonctions utilitaires
"""

# ═══════════════════════════════════════════════════════════════
# FORMATTERS (Formatage quantités, dates, prix)
# ═══════════════════════════════════════════════════════════════

from .formatters import (
    format_quantity,
    format_quantity_with_unit,
    format_price,
    format_percentage,
    format_time,
    format_weight,
    format_volume,
    clean_number_string,
    smart_round
)

# ═══════════════════════════════════════════════════════════════
# HELPERS (Fonctions génériques)
# ═══════════════════════════════════════════════════════════════

from .helpers import (
    # Manipulation données
    safe_get,
    deep_merge,
    flatten_dict,
    group_by,
    deduplicate,

    # Dates
    get_week_bounds,
    get_month_bounds,
    date_range,
    relative_date,

    # Hash & ID
    generate_id,
    short_id,

    # Validation
    is_valid_email,
    is_valid_url,
    clamp,

    # Strings
    truncate,
    slugify,
    pluralize,

    # Retry & Error
    retry,
    safe_execute,
    memoize
)

# ═══════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════

__all__ = [
    # Formatters
    "format_quantity", "format_quantity_with_unit", "format_price",
    "format_percentage", "format_time", "format_weight", "format_volume",
    "clean_number_string", "smart_round",

    # Helpers - Data
    "safe_get", "deep_merge", "flatten_dict", "group_by", "deduplicate",

    # Helpers - Dates
    "get_week_bounds", "get_month_bounds", "date_range", "relative_date",

    # Helpers - ID
    "generate_id", "short_id",

    # Helpers - Validation
    "is_valid_email", "is_valid_url", "clamp",

    # Helpers - Strings
    "truncate", "slugify", "pluralize",

    # Helpers - Error
    "retry", "safe_execute", "memoize"
]