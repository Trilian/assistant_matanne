"""
Formatters - Unités (poids, volume, température).
"""

from .numbers import formater_quantite_unite


def formater_poids(grams: int | float | None) -> str:
    """
    Formate un poids en grammes vers kg/g automatique.

    Examples:
        >>> formater_poids(500)
        "500 g"
        >>> formater_poids(1000)
        "1 kg"
    """
    if grams is None or grams == 0:
        return "0 g"

    try:
        g = float(grams)
    except (ValueError, TypeError):
        return "0 g"

    if g >= 1000:
        kg = g / 1000
        return formater_quantite_unite(kg, "kg")

    return formater_quantite_unite(g, "g")


def formater_volume(milliliters: int | float | None) -> str:
    """
    Formate un volume en mL vers L/mL automatique.

    Examples:
        >>> formater_volume(500)
        "500 mL"
        >>> formater_volume(1000)
        "1 L"
    """
    if milliliters is None or milliliters == 0:
        return "0 mL"

    try:
        ml = float(milliliters)
    except (ValueError, TypeError):
        return "0 mL"

    if ml >= 1000:
        liters = ml / 1000
        return formater_quantite_unite(liters, "L")

    return formater_quantite_unite(ml, "mL")


def formater_temperature(celsius: int | float | None, unit: str = "C") -> str:
    """
    Formate une température.

    Examples:
        >>> formater_temperature(20)
        "20°C"
        >>> formater_temperature(68, "F")
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


__all__ = [
    "formater_poids",
    "formater_volume",
    "formater_temperature",
]
