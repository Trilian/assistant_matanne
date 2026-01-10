"""
Validators - Point d'entrée unifié
"""

# Common
from .common import (
    is_valid_email,
    is_valid_phone,
    clamp,
    validate_range,
    validate_string_length,
    validate_required_fields,
    validate_choice
)

# Food
from .food import (
    validate_recipe,
    validate_ingredient,
    validate_inventory_item,
    validate_shopping_item,
    validate_meal
)

# Dates
from .dates import (
    validate_date_range,
    is_future_date,
    is_past_date,
    validate_expiry_date,
    days_until,
    is_within_days
)

__all__ = [
    # Common
    "is_valid_email",
    "is_valid_phone",
    "clamp",
    "validate_range",
    "validate_string_length",
    "validate_required_fields",
    "validate_choice",

    # Food
    "validate_recipe",
    "validate_ingredient",
    "validate_inventory_item",
    "validate_shopping_item",
    "validate_meal",

    # Dates
    "validate_date_range",
    "is_future_date",
    "is_past_date",
    "validate_expiry_date",
    "days_until",
    "is_within_days"
]