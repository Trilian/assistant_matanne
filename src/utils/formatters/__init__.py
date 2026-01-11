"""
Formatters - Point d'entrée unifié
"""

# Numbers
# Dates
from .dates import format_date, format_datetime, format_duration, format_relative_date, format_time
from .numbers import (
    format_currency,
    format_file_size,
    format_number,
    format_percentage,
    format_price,
    format_quantity,
    format_quantity_with_unit,
    format_range,
    smart_round,
)

# Text
from .text import capitalize_first, clean_text, extract_number, slugify, truncate

# Units
from .units import format_volume, format_weight

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
    "capitalize_first",
]
