"""
Formatters - Unités (poids, volume)
"""

from .numbers import format_quantity_with_unit


def format_weight(grams: int | float | None) -> str:
    """
    Formate un poids en grammes vers kg/g automatique

    Examples:
        >>> format_weight(500)
        "500 g"
        >>> format_weight(1000)
        "1 kg"
        >>> format_weight(1500)
        "1.5 kg"
    """
    if grams is None or grams == 0:
        return "0 g"

    try:
        g = float(grams)
    except (ValueError, TypeError):
        return "0 g"

    # Si >= 1kg, convertir en kg
    if g >= 1000:
        kg = g / 1000
        return format_quantity_with_unit(kg, "kg")

    return format_quantity_with_unit(g, "g")


def format_volume(milliliters: int | float | None) -> str:
    """
    Formate un volume en mL vers L/mL automatique

    Examples:
        >>> format_volume(500)
        "500 mL"
        >>> format_volume(1000)
        "1 L"
        >>> format_volume(1500)
        "1.5 L"
    """
    if milliliters is None or milliliters == 0:
        return "0 mL"

    try:
        ml = float(milliliters)
    except (ValueError, TypeError):
        return "0 mL"

    # Si >= 1L, convertir en litres
    if ml >= 1000:
        liters = ml / 1000
        return format_quantity_with_unit(liters, "L")

    return format_quantity_with_unit(ml, "mL")


def format_temperature(celsius: int | float | None, unit: str = "C") -> str:
    """
    Formate une température

    Examples:
        >>> format_temperature(20)
        "20°C"
        >>> format_temperature(68, "F")
        "68°F"
    """
    if celsius is None:
        return "0°C"

    try:
        temp = float(celsius)
    except (ValueError, TypeError):
        return "0°C"

    if unit == "F":
        return f"{int(temp)}°F"
    return f"{int(temp)}°C"


# ═══════════════════════════════════════════════════════════
# ALIAS FRANÇAIS (pour compatibilité)
# ═══════════════════════════════════════════════════════════

formater_poids = format_weight
formater_volume = format_volume
formater_temperature = format_temperature
