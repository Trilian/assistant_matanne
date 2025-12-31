"""
Utils - Point d'Entrée Unifié
Exports consolidés
"""

# Formatters (inchangés)
from .formatters import (
    format_quantity,
    format_quantity_with_unit,
    format_price,
    format_percentage,
    format_time,
    format_weight,
    format_volume,
    format_date,
    format_datetime,
    format_relative_date,
    clean_number_string,
    smart_round
)

# Helpers (consolidés)
from .helpers import (
    # Data
    safe_get,
    group_by,
    count_by,
    deduplicate,

    # Dates
    get_week_bounds,
    date_range,
    relative_date,

    # Hash & ID
    generate_id,
    slugify,

    # Validation
    is_valid_email,
    clamp,

    # Strings
    truncate,
    clean_text,
    extract_number,

    # Stats
    calculate_average,
    calculate_median,

    # Ingrédients
    find_or_create_ingredient,
    batch_find_or_create_ingredients,
    get_all_ingredients_cached,
    enrich_with_ingredient_info,

    # Consolidation
    consolidate_duplicates,

    # Métier
    validate_stock_level,
    format_recipe_summary,
    format_inventory_summary
)

__all__ = [
    # Formatters
    "format_quantity", "format_quantity_with_unit", "format_price",
    "format_percentage", "format_time", "format_weight", "format_volume",
    "format_date", "format_datetime", "format_relative_date",
    "clean_number_string", "smart_round",

    # Helpers - Data
    "safe_get", "group_by", "count_by", "deduplicate",

    # Helpers - Dates
    "get_week_bounds", "date_range", "relative_date",

    # Helpers - Hash/ID
    "generate_id", "slugify",

    # Helpers - Validation
    "is_valid_email", "clamp",

    # Helpers - Strings
    "truncate", "clean_text", "extract_number",

    # Helpers - Stats
    "calculate_average", "calculate_median",

    # Helpers - Ingrédients
    "find_or_create_ingredient", "batch_find_or_create_ingredients",
    "get_all_ingredients_cached", "enrich_with_ingredient_info",

    # Helpers - Consolidation
    "consolidate_duplicates",

    # Helpers - Métier
    "validate_stock_level", "format_recipe_summary", "format_inventory_summary"
]