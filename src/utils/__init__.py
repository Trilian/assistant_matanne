"""
Utils - Point d'entrée unifié optimisé
Organisation claire : formatters/ validators/ helpers/ media/
"""

# Constants
from .constants import *

# Formatters
from .formatters import (
    capitalize_first,
    clean_text,
    extract_number,
    format_currency,
    # Dates
    format_date,
    format_datetime,
    format_duration,
    format_file_size,
    format_number,
    format_percentage,
    format_price,
    # Numbers
    format_quantity,
    format_quantity_with_unit,
    format_range,
    format_relative_date,
    format_time,
    format_volume,
    # Units
    format_weight,
    slugify,
    smart_round,
    # Text
    truncate,
)

# Helpers
from .helpers import (
    add_business_days,
    # Stats
    calculate_average,
    calculate_median,
    calculate_mode,
    calculate_percentile,
    calculate_range,
    calculate_std_dev,
    calculate_variance,
    camel_vers_snake,
    count_by,
    date_range,
    deduplicate,
    # Food (métier) - 3 fonctions pures
    convertir_unite,
    multiplier_portion,
    extraire_ingredient,
    flatten,
    # Strings
    generer_id,
    get_month_bounds,
    get_quarter,
    # Dates
    get_week_bounds,
    group_by,
    is_weekend,
    masquer_sensible,
    merge_dicts,
    moving_average,
    normaliser_espaces,
    omit,
    partition,
    pick,
    pluraliser,
    retirer_accents,
    # Data
    safe_get,
    snake_vers_camel,
    weeks_between,
)

# Media
from .media import ImageCache, ImageConfig, ImageOptimizer, get_cache_stats, optimize_uploaded_image

# Validators
from .validators import (
    clamp,
    days_until,
    is_future_date,
    is_past_date,
    # Common
    is_valid_email,
    is_valid_phone,
    is_within_days,
    validate_choice,
    # Dates
    validate_date_range,
    validate_expiry_date,
    validate_ingredient,
    validate_inventory_item,
    validate_meal,
    validate_range,
    # Food
    validate_recipe,
    validate_required_fields,
    validate_shopping_item,
    validate_string_length,
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
    "generer_id",
    "normaliser_espaces",
    "retirer_accents",
    "camel_vers_snake",
    "snake_vers_camel",
    "pluraliser",
    "masquer_sensible",
    # Helpers - Stats
    "calculate_average",
    "calculate_median",
    "calculate_variance",
    "calculate_std_dev",
    "calculate_percentile",
    "calculate_mode",
    "calculate_range",
    "moving_average",
    # Helpers - Food (3 fonctions pures)
    "convertir_unite",
    "multiplier_portion",
    "extraire_ingredient",
    # Media
    "ImageOptimizer",
    "ImageCache",
    "ImageConfig",
    "optimize_uploaded_image",
    "get_cache_stats",
]
