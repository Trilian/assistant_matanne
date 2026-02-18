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

from .service import (
    AlerteMeteo,
    ConseilJardin,
    MeteoJour,
    NiveauAlerte,
    PlanArrosage,
    # Service principal
    ServiceMeteo,
    # Types
    TypeAlertMeteo,
    WeatherGardenService,  # Alias
    WeatherService,  # Alias
    get_weather_garden_service,
    get_weather_service,
    # Factories
    obtenir_service_meteo,
    # UI (thin wrapper → src.ui.views.meteo)
    render_weather_garden_ui,
)
from .utils import (
    DIRECTIONS_CARDINALES,
    SEUIL_CANICULE,
    SEUIL_CANICULE_SEVERE,
    # Constantes
    SEUIL_GEL,
    SEUIL_GEL_SEVERE,
    SEUIL_PLUIE_FORTE,
    SEUIL_PLUIE_VIOLENTE,
    SEUIL_SECHERESSE_JOURS,
    SEUIL_UV_ELEVE,
    SEUIL_UV_EXTREME,
    SEUIL_VENT_FORT,
    SEUIL_VENT_TEMPETE,
    WEATHERCODES,
    # Températures
    calculate_average_temperature,
    calculate_feels_like,
    calculate_temperature_amplitude,
    # Arrosage
    calculate_watering_need,
    celsius_to_fahrenheit,
    degrees_from_direction,
    detect_all_alerts,
    detect_canicule_alert,
    detect_drought_risk,
    # Alertes
    detect_gel_alert,
    detect_pluie_forte_alert,
    detect_uv_alert,
    detect_vent_fort_alert,
    # Conversion
    direction_from_degrees,
    fahrenheit_to_celsius,
    format_weather_summary,
    get_arrosage_factor,
    get_gardening_advice_for_weather,
    # Conseils
    get_season,
    # Parsing API
    parse_open_meteo_daily,
    validate_coordinates,
    weathercode_to_condition,
    weathercode_to_icon,
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
