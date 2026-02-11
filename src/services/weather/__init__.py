"""
Package d'alertes météo pour le jardin.

Exports:
- ServiceMeteo: Service principal
- WeatherService, WeatherGardenService: Alias pour rétrocompatibilité
- obtenir_service_meteo: Factory (convention française)
- get_weather_service, get_weather_garden_service: Factory (alias anglais)
- Types: TypeAlertMeteo, NiveauAlerte, MeteoJour, AlerteMeteo, ConseilJardin, PlanArrosage
- Utils: Fonctions utilitaires pures
"""

from .utils import (
    # Constantes
    SEUIL_GEL,
    SEUIL_GEL_SEVERE,
    SEUIL_CANICULE,
    SEUIL_CANICULE_SEVERE,
    SEUIL_SECHERESSE_JOURS,
    SEUIL_PLUIE_FORTE,
    SEUIL_PLUIE_VIOLENTE,
    SEUIL_VENT_FORT,
    SEUIL_VENT_TEMPETE,
    SEUIL_UV_ELEVE,
    SEUIL_UV_EXTREME,
    DIRECTIONS_CARDINALES,
    WEATHERCODES,
    # Conversion
    direction_from_degrees,
    degrees_from_direction,
    weathercode_to_condition,
    weathercode_to_icon,
    get_arrosage_factor,
    # Températures
    calculate_average_temperature,
    calculate_temperature_amplitude,
    celsius_to_fahrenheit,
    fahrenheit_to_celsius,
    calculate_feels_like,
    # Alertes
    detect_gel_alert,
    detect_canicule_alert,
    detect_pluie_forte_alert,
    detect_vent_fort_alert,
    detect_uv_alert,
    detect_all_alerts,
    # Arrosage
    calculate_watering_need,
    detect_drought_risk,
    # Conseils
    get_season,
    get_gardening_advice_for_weather,
    format_weather_summary,
    # Parsing API
    parse_open_meteo_daily,
    validate_coordinates,
)

from .service import (
    # Types
    TypeAlertMeteo,
    NiveauAlerte,
    MeteoJour,
    AlerteMeteo,
    ConseilJardin,
    PlanArrosage,
    # Service principal
    ServiceMeteo,
    WeatherGardenService,  # Alias
    WeatherService,  # Alias
    # Factories
    obtenir_service_meteo,
    get_weather_service,
    get_weather_garden_service,
    # UI
    render_weather_garden_ui,
)


__all__ = [
    # Constantes
    "SEUIL_GEL",
    "SEUIL_GEL_SEVERE",
    "SEUIL_CANICULE",
    "SEUIL_CANICULE_SEVERE",
    "SEUIL_SECHERESSE_JOURS",
    "SEUIL_PLUIE_FORTE",
    "SEUIL_PLUIE_VIOLENTE",
    "SEUIL_VENT_FORT",
    "SEUIL_VENT_TEMPETE",
    "SEUIL_UV_ELEVE",
    "SEUIL_UV_EXTREME",
    "DIRECTIONS_CARDINALES",
    "WEATHERCODES",
    # Types
    "TypeAlertMeteo",
    "NiveauAlerte",
    "MeteoJour",
    "AlerteMeteo",
    "ConseilJardin",
    "PlanArrosage",
    # Service
    "ServiceMeteo",
    "WeatherGardenService",
    "WeatherService",
    # Factories
    "obtenir_service_meteo",
    "get_weather_service",
    "get_weather_garden_service",
    # Utils - Conversion
    "direction_from_degrees",
    "degrees_from_direction",
    "weathercode_to_condition",
    "weathercode_to_icon",
    "get_arrosage_factor",
    # Utils - Températures
    "calculate_average_temperature",
    "calculate_temperature_amplitude",
    "celsius_to_fahrenheit",
    "fahrenheit_to_celsius",
    "calculate_feels_like",
    # Utils - Alertes
    "detect_gel_alert",
    "detect_canicule_alert",
    "detect_pluie_forte_alert",
    "detect_vent_fort_alert",
    "detect_uv_alert",
    "detect_all_alerts",
    # Utils - Arrosage
    "calculate_watering_need",
    "detect_drought_risk",
    # Utils - Conseils
    "get_season",
    "get_gardening_advice_for_weather",
    "format_weather_summary",
    # Utils - Parsing
    "parse_open_meteo_daily",
    "validate_coordinates",
    # UI
    "render_weather_garden_ui",
]
