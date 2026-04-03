"""
Parsing des données API Open-Meteo et validation de coordonnées.

Contient les fonctions de transformation des réponses API brutes
en structures de données exploitables par l'application.
"""

from typing import Any

from .alertes_meteo import calculate_average_temperature
from .weather_codes import direction_from_degrees, weathercode_to_condition, weathercode_to_icon

__all__ = [
    "parse_open_meteo_daily",
    "_safe_get_index",
    "validate_coordinates",
]


# ═══════════════════════════════════════════════════════════
# PARSING DE DONNÉES API
# ═══════════════════════════════════════════════════════════


def parse_open_meteo_daily(data: dict) -> list[dict]:
    """
    Parse les données daily de l'API Open-Meteo.

    Args:
        data: Réponse JSON de l'API

    Returns:
        Liste de dict avec les données formatées
    """
    daily = data.get("daily", {})
    dates = daily.get("time", [])

    previsions = []

    for i, date_str in enumerate(dates):
        temp_min = _safe_get_index(daily, "temperature_2m_min", i)
        temp_max = _safe_get_index(daily, "temperature_2m_max", i)

        prev = {
            "date": date_str,
            "temperature_min": temp_min,
            "temperature_max": temp_max,
            "temperature_moyenne": calculate_average_temperature(temp_min or 15, temp_max or 25),
            "precipitation_mm": _safe_get_index(daily, "precipitation_sum", i) or 0,
            "probabilite_pluie": _safe_get_index(daily, "precipitation_probability_max", i) or 0,
            "vent_km_h": _safe_get_index(daily, "wind_speed_10m_max", i) or 0,
            "direction_vent": direction_from_degrees(
                _safe_get_index(daily, "wind_direction_10m_dominant", i)
            ),
            "uv_index": _safe_get_index(daily, "uv_index_max", i) or 0,
            "weathercode": _safe_get_index(daily, "weathercode", i),
        }

        # Ajouter condition et icône
        prev["condition"] = weathercode_to_condition(prev["weathercode"])
        prev["icone"] = weathercode_to_icon(prev["weathercode"])

        # Lever/coucher du soleil
        sunrise = _safe_get_index(daily, "sunrise", i)
        sunset = _safe_get_index(daily, "sunset", i)

        if sunrise and "T" in sunrise:
            prev["lever_soleil"] = sunrise.split("T")[1]
        if sunset and "T" in sunset:
            prev["coucher_soleil"] = sunset.split("T")[1]

        previsions.append(prev)

    return previsions


def _safe_get_index(data: dict, key: str, index: int, default=None) -> Any:
    """
    Récupère une valeur à un index de façon sécurisée.

    Args:
        data: Dictionnaire contenant les listes
        key: Clé de la liste
        index: Index à récupérer
        default: Valeur par défaut

    Returns:
        Valeur à l'index ou default
    """
    lst = data.get(key, [])
    if lst and 0 <= index < len(lst):
        return lst[index]
    return default


def validate_coordinates(latitude: float, longitude: float) -> tuple[bool, str]:
    """
    Valide des coordonnées GPS.

    Args:
        latitude: Latitude (-90 à 90)
        longitude: Longitude (-180 à 180)

    Returns:
        Tuple (valide, message_erreur)
    """
    if not isinstance(latitude, int | float):
        return False, "La latitude doit être un nombre"

    if not isinstance(longitude, int | float):
        return False, "La longitude doit être un nombre"

    if latitude < -90 or latitude > 90:
        return False, f"Latitude invalide: {latitude} (doit être entre -90 et 90)"

    if longitude < -180 or longitude > 180:
        return False, f"Longitude invalide: {longitude} (doit être entre -180 et 180)"

    return True, ""
