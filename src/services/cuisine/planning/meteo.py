"""
Service météo pour le planning cuisine.

Interroge OpenWeatherMap pour adapter les suggestions de repas :
- Temps chaud → salades, gaspacho, grillades
- Temps froid → soupes, raclette, plats mijotés
- Temps pluvieux → comfort food, gratins

Utilise le plan gratuit OpenWeatherMap (< 1000 req/jour).
"""

import logging
from dataclasses import dataclass
from datetime import date

import httpx

from src.core.config import obtenir_parametres

logger = logging.getLogger(__name__)


@dataclass
class MeteoJour:
    """Données météo pour une journée."""

    date: date
    temperature: float  # °C
    temperature_ressentie: float
    description: str  # ex: "ciel dégagé", "pluie légère"
    icone: str  # code icône OpenWeather (ex: "01d")
    humidite: int  # %
    vent_kmh: float

    @property
    def ambiance(self) -> str:
        """Détermine l'ambiance culinaire selon la météo."""
        if self.temperature >= 28:
            return "chaud"
        elif self.temperature >= 20:
            return "doux"
        elif self.temperature >= 10:
            return "frais"
        else:
            return "froid"

    @property
    def suggestion_type_repas(self) -> list[str]:
        """Retourne les types de repas suggérés pour cette météo."""
        suggestions = {
            "chaud": ["salade", "gaspacho", "grillade", "ceviche", "smoothie bowl"],
            "doux": ["poisson grillé", "wok", "tarte salée", "buddha bowl"],
            "frais": ["soupe", "gratin", "risotto", "plat mijoté", "quiche"],
            "froid": ["raclette", "fondue", "pot-au-feu", "blanquette", "cassoulet"],
        }
        types = suggestions.get(self.ambiance, [])

        # Pluie → comfort food
        mots_pluie = ["pluie", "averse", "bruine", "orage"]
        if any(mot in self.description.lower() for mot in mots_pluie):
            types.extend(["gratin", "crumble", "soupe"])

        return list(dict.fromkeys(types))  # Dédupliqué, ordre préservé


async def obtenir_meteo_jour(jour: date | None = None) -> MeteoJour | None:
    """Récupère la météo pour un jour donné via OpenWeatherMap.

    Args:
        jour: Date cible (défaut: aujourd'hui). Supporte J à J+4 via forecast.

    Returns:
        MeteoJour ou None si l'API n'est pas configurée / erreur.
    """
    settings = obtenir_parametres()
    api_key = settings.OPENWEATHER_API_KEY

    if not api_key:
        logger.debug("OPENWEATHER_API_KEY non configurée — météo désactivée")
        return None

    city = settings.OPENWEATHER_CITY or "Bordeaux"
    jour = jour or date.today()

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            if jour == date.today():
                # API current weather
                url = "https://api.openweathermap.org/data/2.5/weather"
                params = {
                    "q": city,
                    "appid": api_key,
                    "units": "metric",
                    "lang": "fr",
                }
                resp = await client.get(url, params=params)
                resp.raise_for_status()
                data = resp.json()

                return MeteoJour(
                    date=jour,
                    temperature=data["main"]["temp"],
                    temperature_ressentie=data["main"]["feels_like"],
                    description=data["weather"][0]["description"],
                    icone=data["weather"][0]["icon"],
                    humidite=data["main"]["humidity"],
                    vent_kmh=round(data["wind"]["speed"] * 3.6, 1),
                )
            else:
                # API 5-day forecast (gratuit)
                url = "https://api.openweathermap.org/data/2.5/forecast"
                params = {
                    "q": city,
                    "appid": api_key,
                    "units": "metric",
                    "lang": "fr",
                }
                resp = await client.get(url, params=params)
                resp.raise_for_status()
                data = resp.json()

                # Chercher le créneau 12h du jour demandé
                jour_str = jour.isoformat()
                for item in data.get("list", []):
                    if jour_str in item["dt_txt"] and "12:00" in item["dt_txt"]:
                        return MeteoJour(
                            date=jour,
                            temperature=item["main"]["temp"],
                            temperature_ressentie=item["main"]["feels_like"],
                            description=item["weather"][0]["description"],
                            icone=item["weather"][0]["icon"],
                            humidite=item["main"]["humidity"],
                            vent_kmh=round(item["wind"]["speed"] * 3.6, 1),
                        )

                logger.warning(f"Pas de données forecast pour {jour}")
                return None

    except httpx.HTTPStatusError as e:
        logger.error(f"Erreur OpenWeatherMap HTTP {e.response.status_code}: {e}")
        return None
    except Exception as e:
        logger.error(f"Erreur météo : {e}")
        return None


def construire_contexte_meteo_prompt(meteo: MeteoJour) -> str:
    """Construit un fragment de prompt IA avec le contexte météo.

    Utilisé par le planning IA pour adapter les suggestions de recettes.
    """
    return (
        f"Météo du {meteo.date.strftime('%A %d %B')} : {meteo.description}, "
        f"{meteo.temperature}°C (ressenti {meteo.temperature_ressentie}°C). "
        f"Ambiance : {meteo.ambiance}. "
        f"Types de repas suggérés : {', '.join(meteo.suggestion_type_repas)}. "
        "Adapte les suggestions en conséquence."
    )
