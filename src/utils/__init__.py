"""
Utils - Point d'Entrée Unifié REFACTORISÉ
Helpers consolidés + Service Helpers
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

# Helpers génériques (nouveau)
from .helpers import (
    # Data
    safe_get,
    deep_merge,
    flatten_dict,
    group_by,
    count_by,
    deduplicate,
    chunk_list,

    # Dates
    get_week_bounds,
    get_month_bounds,
    date_range,
    relative_date,
    days_between,

    # Hash & ID
    generate_id,
    short_id,
    slugify,

    # Validation
    is_valid_email,
    is_valid_url,
    clamp,
    validate_positive,
    validate_range,

    # Strings
    truncate,
    pluralize,
    clean_text,
    extract_number,

    # Retry & Error
    retry,
    safe_execute,
    memoize,

    # Stats
    calculate_average,
    calculate_median,
    calculate_percentile,

    # Conversion
    model_to_dict,
    batch_to_dicts
)

# Service Helpers (nouveau)
from .service_helpers import (
    # Ingrédients
    find_or_create_ingredient,
    batch_find_or_create_ingredients,

    # Enrichissement
    enrich_with_ingredient_info,

    # Cache queries
    get_all_ingredients_cached,
    get_ingredient_by_name,

    # Validation métier
    validate_quantity,
    validate_date_not_past,
    validate_stock_level,

    # Consolidation
    consolidate_duplicates,

    # Stats métier
    calculate_stock_value,
    calculate_waste_score,
    calculate_shopping_urgency,

    # Formatage métier
    format_recipe_summary,
    format_inventory_summary
)

__all__ = [
    # Formatters
    "format_quantity",
    "format_quantity_with_unit",
    "format_price",
    "format_percentage",
    "format_time",
    "format_weight",
    "format_volume",
    "format_date",
    "format_datetime",
    "format_relative_date",
    "clean_number_string",
    "smart_round",

    # Helpers - Data
    "safe_get",
    "deep_merge",
    "flatten_dict",
    "group_by",
    "count_by",
    "deduplicate",
    "chunk_list",

    # Helpers - Dates
    "get_week_bounds",
    "get_month_bounds",
    "date_range",
    "relative_date",
    "days_between",

    # Helpers - Hash/ID
    "generate_id",
    "short_id",
    "slugify",

    # Helpers - Validation
    "is_valid_email",
    "is_valid_url",
    "clamp",
    "validate_positive",
    "validate_range",

    # Helpers - Strings
    "truncate",
    "pluralize",
    "clean_text",
    "extract_number",

    # Helpers - Retry
    "retry",
    "safe_execute",
    "memoize",

    # Helpers - Stats
    "calculate_average",
    "calculate_median",
    "calculate_percentile",

    # Helpers - Conversion
    "model_to_dict",
    "batch_to_dicts",

    # Service Helpers - Ingrédients
    "find_or_create_ingredient",
    "batch_find_or_create_ingredients",

    # Service Helpers - Enrichissement
    "enrich_with_ingredient_info",

    # Service Helpers - Cache
    "get_all_ingredients_cached",
    "get_ingredient_by_name",

    # Service Helpers - Validation métier
    "validate_quantity",
    "validate_date_not_past",
    "validate_stock_level",

    # Service Helpers - Consolidation
    "consolidate_duplicates",

    # Service Helpers - Stats métier
    "calculate_stock_value",
    "calculate_waste_score",
    "calculate_shopping_urgency",

    # Service Helpers - Formatage métier
    "format_recipe_summary",
    "format_inventory_summary"
]
