"""
Module météo transversal - Service météo pour jardin et activités familiales.

Ce module est placé dans integrations/ car il est utilisé par plusieurs domaines:
- maison/jardin: conseils d'arrosage, alertes gel
- famille/activités: suggestions d'activités selon météo
"""

# Ré-export depuis le service weather (à renommer en meteo plus tard)
from src.services.weather.service import (
    AlerteMeteo,
    ConseilJardin,
    # Types
    MeteoJour,
    NiveauAlerte,
    PlanArrosage,
    ServiceMeteo,
    TypeAlertMeteo,
    get_weather_garden_service,
    get_weather_service,
    obtenir_service_meteo,
)

# Alias
WeatherService = ServiceMeteo
obtenir_service = obtenir_service_meteo

__all__ = [
    # Services
    "ServiceMeteo",
    "WeatherService",
    "get_weather_service",
    "obtenir_service_meteo",
    "get_weather_garden_service",
    "obtenir_service",
    # Types
    "MeteoJour",
    "AlerteMeteo",
    "ConseilJardin",
    "PlanArrosage",
    "TypeAlertMeteo",
    "NiveauAlerte",
]
