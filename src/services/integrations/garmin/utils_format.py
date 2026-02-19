"""
Fonctions de formatage pour les données Garmin.

Formatage des durées, distances, allures et vitesses
pour l'affichage dans l'interface utilisateur.
"""


# ═══════════════════════════════════════════════════════════
# FORMATAGE POUR L'AFFICHAGE
# ═══════════════════════════════════════════════════════════


def format_duration(seconds: int | float) -> str:
    """
    Formate une durée en secondes pour l'affichage.

    Args:
        seconds: Durée en secondes

    Returns:
        Chaîne formatée (ex: "1h 30m" ou "45m")

    Examples:
        >>> format_duration(5400)
        '1h 30m'
        >>> format_duration(1800)
        '30m'
    """
    if not seconds or seconds <= 0:
        return "0m"

    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60

    if hours > 0:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"


def format_distance(meters: float | None) -> str:
    """
    Formate une distance en mètres pour l'affichage.

    Args:
        meters: Distance en mètres

    Returns:
        Chaîne formatée (km ou m selon la valeur)

    Examples:
        >>> format_distance(5000)
        '5.00 km'
        >>> format_distance(500)
        '500 m'
    """
    if not meters:
        return "0 m"

    if meters >= 1000:
        return f"{meters / 1000:.2f} km"
    return f"{int(meters)} m"


def format_pace(seconds_per_meter: float | None) -> str:
    """
    Formate une allure en min/km.

    Args:
        seconds_per_meter: Vitesse en secondes par mètre

    Returns:
        Allure formatée (min:sec /km)
    """
    if not seconds_per_meter or seconds_per_meter <= 0:
        return "N/A"

    # Convertir en secondes par km
    seconds_per_km = seconds_per_meter * 1000

    minutes = int(seconds_per_km // 60)
    seconds = int(seconds_per_km % 60)

    return f"{minutes}:{seconds:02d} /km"


def format_speed(meters_per_second: float | None) -> str:
    """
    Formate une vitesse en km/h.

    Args:
        meters_per_second: Vitesse en m/s

    Returns:
        Vitesse formatée en km/h
    """
    if not meters_per_second or meters_per_second <= 0:
        return "0 km/h"

    kmh = meters_per_second * 3.6
    return f"{kmh:.1f} km/h"
