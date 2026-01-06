"""
Utils - Point d'entrée unifié optimisé
Organisation claire : formatters/ validators/ helpers/ media/
"""

# Constants
from .constants import *

# Formatters
from .formatters import (
    # Numbers
    format_quantity,
    format_quantity_with_unit,
    format_price,
    format_currency,
    format_percentage,
    format_number,
    format_file_size,
    format_range,
    smart_round,

    # Dates
    format_date,
    format_datetime,
    format_relative_date,
    format_time,
    format_duration,

    # Units
    format_weight,
    format_volume,

    # Text
    truncate,
    clean_text,
    slugify,
    extract_number,
    capitalize_first
)

# Validators
from .validators import (
    # Common
    is_valid_email,
    is_valid_phone,
    clamp,
    validate_range,
    validate_string_length,
    validate_required_fields,
    validate_choice,

    # Food
    validate_recipe,
    validate_ingredient,
    validate_inventory_item,
    validate_shopping_item,
    validate_meal,

    # Dates
    validate_date_range,
    is_future_date,
    is_past_date,
    validate_expiry_date,
    days_until,
    is_within_days
)

# Helpers
from .helpers import (
    # Data
    safe_get,
    group_by,
    count_by,
    deduplicate,
    flatten,
    partition,
    merge_dicts,
    pick,
    omit,

    # Dates
    get_week_bounds,
    date_range,
    get_month_bounds,
    add_business_days,
    weeks_between,
    is_weekend,
    get_quarter,

    # Strings
    generate_id,
    normalize_whitespace,
    remove_accents,
    camel_to_snake,
    snake_to_camel,
    pluralize,
    mask_sensitive,

    # Stats
    calculate_average,
    calculate_median,
    calculate_variance,
    calculate_std_dev,
    calculate_percentile,
    calculate_mode,
    calculate_range,
    moving_average,

    # Food (métier)
    find_or_create_ingredient,
    batch_find_or_create_ingredients,
    get_all_ingredients_cached,
    enrich_with_ingredient_info,
    validate_stock_level,
    consolidate_duplicates,
    format_recipe_summary,
    format_inventory_summary,
    calculate_recipe_cost,
    suggest_ingredient_substitutes
)

# Media
from .media import (
    ImageOptimizer,
    ImageCache,
    ImageConfig,
    optimize_uploaded_image,
    get_cache_stats
)

__all__ = [
    # Formatters - Numbers
    "format_quantity",
    "format_quantity_with_unit",
    "format_price",
    "format_currency",
    "format_percentage",
    "format_number",
    "format_file_size",
    "format_range",
    "smart_round",

    # Formatters - Dates
    "format_date",
    "format_datetime",
    "format_relative_date",
    "format_time",
    "format_duration",

    # Formatters - Units
    "format_weight",
    "format_volume",

    # Formatters - Text
    "truncate",
    "clean_text",
    "slugify",
    "extract_number",
    "capitalize_first",

    # Validators - Common
    "is_valid_email",
    "is_valid_phone",
    "clamp",
    "validate_range",
    "validate_string_length",
    "validate_required_fields",
    "validate_choice",

    # Validators - Food
    "validate_recipe",
    "validate_ingredient",
    "validate_inventory_item",
    "validate_shopping_item",
    "validate_meal",

    # Validators - Dates
    "validate_date_range",
    "is_future_date",
    "is_past_date",
    "validate_expiry_date",
    "days_until",
    "is_within_days",

    # Helpers - Data
    "safe_get",
    "group_by",
    "count_by",
    "deduplicate",
    "flatten",
    "partition",
    "merge_dicts",
    "pick",
    "omit",

    # Helpers - Dates
    "get_week_bounds",
    "date_range",
    "get_month_bounds",
    "add_business_days",
    "weeks_between",
    "is_weekend",
    "get_quarter",

    # Helpers - Strings
    "generate_id",
    "normalize_whitespace",
    "remove_accents",
    "camel_to_snake",
    "snake_to_camel",
    "pluralize",
    "mask_sensitive",

    # Helpers - Stats
    "calculate_average",
    "calculate_median",
    "calculate_variance",
    "calculate_std_dev",
    "calculate_percentile",
    "calculate_mode",
    "calculate_range",
    "moving_average",

    # Helpers - Food
    "find_or_create_ingredient",
    "batch_find_or_create_ingredients",
    "get_all_ingredients_cached",
    "enrich_with_ingredient_info",
    "validate_stock_level",
    "consolidate_duplicates",
    "format_recipe_summary",
    "format_inventory_summary",
    "calculate_recipe_cost",
    "suggest_ingredient_substitutes",

    # Media
    "ImageOptimizer",
    "ImageCache",
    "ImageConfig",
    "optimize_uploaded_image",
    "get_cache_stats"
]