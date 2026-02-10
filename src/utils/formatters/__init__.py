"""
Formatters - Point d'entrée unifié
"""

# Numbers
# Dates
from .dates import (
    format_date, format_datetime, format_duration, format_relative_date, format_time,
    # Alias français
    formater_date, formater_datetime, temps_ecoule, formater_temps, formater_duree
)
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
    # Alias français
    formater_quantite,
    formater_quantite_unite,
    formater_prix,
    formater_monnaie,
    formater_pourcentage,
    formater_entier,
    formater_nombre,
    formater_taille_fichier,
    formater_plage,
    arrondir_intelligent,
)

# Text
from .text import (
    capitalize_first, clean_text, extract_number, slugify, truncate, capitalize_words,
    # Alias français
    tronquer, nettoyer_texte, extraire_nombre, capitaliser_premier, capitaliser_mots
)

# Units
from .units import (
    format_volume, format_weight, format_temperature,
    # Alias français
    formater_poids, formater_volume, formater_temperature
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
    "format_temperature",
    # Text
    "truncate",
    "clean_text",
    "slugify",
    "extract_number",
    "capitalize_first",
    "capitalize_words",
    # Alias français - Dates
    "formater_date",
    "formater_datetime",
    "temps_ecoule",
    "formater_temps",
    "formater_duree",
    # Alias français - Numbers
    "formater_quantite",
    "formater_quantite_unite",
    "formater_prix",
    "formater_monnaie",
    "formater_pourcentage",
    "formater_entier",
    "formater_nombre",
    "formater_taille_fichier",
    "formater_plage",
    "arrondir_intelligent",
    # Alias français - Text
    "tronquer",
    "nettoyer_texte",
    "extraire_nombre",
    "capitaliser_premier",
    "capitaliser_mots",
    # Alias français - Units
    "formater_poids",
    "formater_volume",
    "formater_temperature",
]
