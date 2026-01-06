"""
Helpers - Point d'entrée unifié
"""

# Data
from .data import (
    safe_get,
    group_by,
    count_by,
    deduplicate,
    flatten,
    partition,
    merge_dicts,
    pick,
    omit
)

# Dates
from .dates import (
    get_week_bounds,
    date_range,
    get_month_bounds,
    add_business_days,
    weeks_between,
    is_weekend,
    get_quarter
)

# Strings
from .strings import (
    generate_id,
    normalize_whitespace,
    remove_accents,
    camel_to_snake,
    snake_to_camel,
    pluralize,
    mask_sensitive
)

# Stats
from .stats import (
    calculate_average,
    calculate_median,
    calculate_variance,
    calculate_std_dev,
    calculate_percentile,
    calculate_mode,
    calculate_range,
    moving_average
)

# Food (métier cuisine)
from .food import (
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

__all__ = [
    # Data
    "safe_get",
    "group_by",
    "count_by",
    "deduplicate",
    "flatten",
    "partition",
    "merge_dicts",
    "pick",
    "omit",

    # Dates
    "get_week_bounds",
    "date_range",
    "get_month_bounds",
    "add_business_days",
    "weeks_between",
    "is_weekend",
    "get_quarter",

    # Strings
    "generate_id",
    "normalize_whitespace",
    "remove_accents",
    "camel_to_snake",
    "snake_to_camel",
    "pluralize",
    "mask_sensitive",

    # Stats
    "calculate_average",
    "calculate_median",
    "calculate_variance",
    "calculate_std_dev",
    "calculate_percentile",
    "calculate_mode",
    "calculate_range",
    "moving_average",

    # Food
    "find_or_create_ingredient",
    "batch_find_or_create_ingredients",
    "get_all_ingredients_cached",
    "enrich_with_ingredient_info",
    "validate_stock_level",
    "consolidate_duplicates",
    "format_recipe_summary",
    "format_inventory_summary",
    "calculate_recipe_cost",
    "suggest_ingredient_substitutes"
]