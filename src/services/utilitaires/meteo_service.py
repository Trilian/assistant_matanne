"""
Service météo via Open-Meteo API (gratuit, sans clé).

Fournit la météo actuelle et prévisions 7 jours.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import httpx

from src.core.decorators import avec_cache
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)

# Coordonnées par défaut (Paris — configurable)
DEFAULT_LAT = 48.8566
DEFAULT_LON = 2.3522
DEFAULT_VILLE = "Paris"

# URL de l'API Open-Meteo
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

# Mapping codes météo WMO → emojis/descriptions
WMO_CODES: dict[int, tuple[str, str]] = {
    0: ("☀️", "Ciel dégagé"),
    1: ("🌤️", "Principalement dégagé"),
    2: ("⛅", "Partiellement nuageux"),
    3: ("☁️", "Couvert"),
    45: ("🌫️", "Brouillard"),
    48: ("🌫️", "Brouillard givrant"),
    51: ("🌦️", "Bruine légère"),
    53: ("🌦️", "Bruine modérée"),
    55: ("🌧️", "Bruine forte"),
    61: ("🌧️", "Pluie légère"),
    63: ("🌧️", "Pluie modérée"),
    65: ("🌧️", "Pluie forte"),
    66: ("🌧️", "Pluie verglaçante légère"),
    67: ("🌧️", "Pluie verglaçante forte"),
    71: ("🌨️", "Neige légère"),
    73: ("🌨️", "Neige modérée"),
    75: ("❄️", "Neige forte"),
    77: ("🌨️", "Grains de neige"),
    80: ("🌦️", "Averses légères"),
    81: ("🌧️", "Averses modérées"),
    82: ("⛈️", "Averses violentes"),
    85: ("🌨️", "Averses de neige légères"),
    86: ("❄️", "Averses de neige fortes"),
    95: ("⛈️", "Orage"),
    96: ("⛈️", "Orage avec grêle légère"),
    99: ("⛈️", "Orage avec grêle forte"),
}


@dataclass
class MeteoActuelle:
    """Données météo actuelles."""

    temperature: float
    temperature_ressentie: float
    humidite: int
    vent_kmh: float
    direction_vent: int
    code_meteo: int
    precip_mm: float = 0.0
    uv_index: float = 0.0
    pression_hpa: float = 0.0
    visibilite_km: float = 0.0

    @property
    def emoji(self) -> str:
        return WMO_CODES.get(self.code_meteo, ("❓", "Inconnu"))[0]

    @property
    def description(self) -> str:
        return WMO_CODES.get(self.code_meteo, ("❓", "Inconnu"))[1]


@dataclass
class PrevisionJour:
    """Prévision pour un jour."""

    date: str
    temp_max: float
    temp_min: float
    code_meteo: int
    precip_mm: float
    precip_proba: int
    vent_max_kmh: float
    uv_max: float = 0.0
    lever_soleil: str = ""
    coucher_soleil: str = ""

    @property
    def emoji(self) -> str:
        return WMO_CODES.get(self.code_meteo, ("❓", "Inconnu"))[0]

    @property
    def description(self) -> str:
        return WMO_CODES.get(self.code_meteo, ("❓", "Inconnu"))[1]


@dataclass
class DonneesMeteo:
    """Données météo complètes."""

    ville: str
    actuelle: MeteoActuelle | None = None
    previsions: list[PrevisionJour] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)


class MeteoService:
    """Service météo via Open-Meteo API."""

    def __init__(
        self, lat: float = DEFAULT_LAT, lon: float = DEFAULT_LON, ville: str = DEFAULT_VILLE
    ):
        self.lat = lat
        self.lon = lon
        self.ville = ville

    @avec_cache(ttl=1800)  # Cache 30 min
    def obtenir_meteo(self) -> DonneesMeteo:
        """Obtient la météo actuelle + prévisions 7 jours."""
        try:
            params = {
                "latitude": self.lat,
                "longitude": self.lon,
                "current": "temperature_2m,relative_humidity_2m,apparent_temperature,"
                "precipitation,weather_code,wind_speed_10m,wind_direction_10m,"
                "surface_pressure,uv_index",
                "daily": "weather_code,temperature_2m_max,temperature_2m_min,"
                "precipitation_sum,precipitation_probability_max,"
                "wind_speed_10m_max,uv_index_max,sunrise,sunset",
                "timezone": "Europe/Paris",
                "forecast_days": 7,
            }

            response = httpx.get(OPEN_METEO_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Parser données actuelles
            current = data.get("current", {})
            actuelle = MeteoActuelle(
                temperature=current.get("temperature_2m", 0),
                temperature_ressentie=current.get("apparent_temperature", 0),
                humidite=current.get("relative_humidity_2m", 0),
                vent_kmh=current.get("wind_speed_10m", 0),
                direction_vent=current.get("wind_direction_10m", 0),
                code_meteo=current.get("weather_code", 0),
                precip_mm=current.get("precipitation", 0),
                uv_index=current.get("uv_index", 0),
                pression_hpa=current.get("surface_pressure", 0),
            )

            # Parser prévisions
            daily = data.get("daily", {})
            previsions = []
            dates = daily.get("time", [])
            for i, d in enumerate(dates):
                previsions.append(
                    PrevisionJour(
                        date=d,
                        temp_max=daily.get("temperature_2m_max", [0])[i],
                        temp_min=daily.get("temperature_2m_min", [0])[i],
                        code_meteo=daily.get("weather_code", [0])[i],
                        precip_mm=daily.get("precipitation_sum", [0])[i],
                        precip_proba=daily.get("precipitation_probability_max", [0])[i],
                        vent_max_kmh=daily.get("wind_speed_10m_max", [0])[i],
                        uv_max=daily.get("uv_index_max", [0])[i],
                        lever_soleil=daily.get("sunrise", [""])[i],
                        coucher_soleil=daily.get("sunset", [""])[i],
                    )
                )

            # Suggestions contextuelles
            suggestions = self._generer_suggestions(actuelle, previsions)

            return DonneesMeteo(
                ville=self.ville,
                actuelle=actuelle,
                previsions=previsions,
                suggestions=suggestions,
            )

        except Exception as e:
            logger.error(f"Erreur API Open-Meteo: {e}")
            return DonneesMeteo(ville=self.ville)

    def _generer_suggestions(
        self, actuelle: MeteoActuelle, previsions: list[PrevisionJour]
    ) -> list[str]:
        """Génère des suggestions contextuelles."""
        suggestions = []

        if actuelle.temperature >= 20 and actuelle.code_meteo <= 2:
            suggestions.append("☀️ Beau temps — idéal pour le jardin ou une promenade avec Jules !")
        if actuelle.temperature < 5:
            suggestions.append("🧣 Temps froid — pensez à bien couvrir Jules pour la sortie.")
        if actuelle.precip_mm > 0 or actuelle.code_meteo >= 61:
            suggestions.append("☂️ Pluie prévue — prévoir des activités d'intérieur pour Jules.")
        if actuelle.uv_index >= 6:
            suggestions.append("🧴 UV élevé — crème solaire et chapeau pour Jules !")
        if actuelle.vent_kmh > 40:
            suggestions.append("💨 Vent fort — éviter les activités extérieures.")

        # Vérifier les prochains jours
        for prev in previsions[1:3]:
            if prev.precip_proba > 70:
                suggestions.append(
                    f"🌧️ Forte probabilité de pluie {prev.date} — prévoir les courses aujourd'hui."
                )
                break

        return suggestions


@service_factory("meteo_service", tags={"utilitaires", "api"})
def obtenir_meteo_service() -> MeteoService:
    """Factory singleton MeteoService."""
    return MeteoService()



