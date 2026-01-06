"""
Formatters - Point d'entrée unifié
"""

# Numbers
from .numbers import (
    format_quantity,
    format_quantity_with_unit,
    format_price,
    format_currency,
    format_percentage,
    format_number,
    format_file_size,
    format_range,
    smart_round
)

# Dates
from .dates import (
    format_date,
    format_datetime,
    format_relative_date,
    format_time,
    format_duration
)

# Units
from .units import (
    format_weight,
    format_volume
)

# Text
from .text import (
    truncate,
    clean_text,
    slugify,
    extract_number,
    capitalize_first
)

__all__ = [
    # Numbers
    "format_quantity",
    "format_quantity_with_unit",
    "format_price",
    "format_currency",
    "format_percentage",
    "format_number",
    "format_file_size",
    "format_range",
    "smart_round",

    # Dates
    "format_date",
    "format_datetime",
    "format_relative_date",
    "format_time",
    "format_duration",

    # Units
    "format_weight",
    "format_volume",

    # Text
    "truncate",
    "clean_text",
    "slugify",
    "extract_number",
    "capitalize_first"
]