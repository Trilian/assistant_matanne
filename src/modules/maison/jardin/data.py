"""
Jardin - Chargement des données.

⚠️ charger_catalogue_plantes est maintenant un PROXY vers le service.
obtenir_meteo_jardin reste local (données simulées pour l'UI).
"""

import logging
from datetime import datetime
from functools import lru_cache

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# CHARGEMENT DONNÉES - PROXY VERS SERVICE
# ═══════════════════════════════════════════════════════════


@lru_cache(maxsize=1)
def _get_service():
    """Retourne une instance singleton du service jardin."""
    from src.services.maison import get_jardin_service

    return get_jardin_service()


def charger_catalogue_plantes() -> dict:
    """
    Charge le catalogue des plantes.

    Proxy vers JardinService.charger_catalogue_plantes()
    """
    return _get_service().charger_catalogue_plantes()


def obtenir_meteo_jardin() -> dict:
    """
    Obtient les données météo pour le jardin.

    Utilise ServiceMeteo avec Open-Meteo API, fallback vers données saisonnières.
    """
    try:
        from src.services.integrations.weather import obtenir_service_meteo

        service = obtenir_service_meteo()
        previsions = service.get_previsions(nb_jours=1)

        if previsions and len(previsions) > 0:
            aujourdhui = previsions[0]
            temp_moy = aujourdhui.temperature_moyenne
            pluie_prevue = aujourdhui.probabilite_pluie > 50 or aujourdhui.precipitation_mm > 0
            gel_risque = aujourdhui.temperature_min < 2

            # Conseil basé sur les conditions réelles
            if gel_risque:
                conseil = "Risque de gel ! Protégez vos cultures sensibles."
            elif temp_moy > 30:
                conseil = "Canicule prévue. Arrosez tôt le matin et paillez."
            elif pluie_prevue:
                conseil = f"Pluie prévue ({aujourdhui.precipitation_mm:.1f}mm). Pas d'arrosage nécessaire."
            else:
                conseil = f"Conditions favorables. Température: {temp_moy:.0f}°C"

            return {
                "temperature": round(temp_moy),
                "pluie_prevue": pluie_prevue,
                "gel_risque": gel_risque,
                "vent": "fort"
                if aujourdhui.vent_km_h > 30
                else "modéré"
                if aujourdhui.vent_km_h > 15
                else "faible",
                "conseil": conseil,
                "source": "api",
            }
    except Exception as e:
        logger.debug(f"Fallback météo saisonnière: {e}")

    # Fallback: données saisonnières simulées
    mois = datetime.now().month

    if mois in [12, 1, 2]:  # Hiver
        return {
            "temperature": 5,
            "pluie_prevue": True,
            "gel_risque": True,
            "vent": "modéré",
            "conseil": "Protégez vos cultures du gel. Évitez d'arroser.",
        }
    elif mois in [3, 4, 5]:  # Printemps
        return {
            "temperature": 15,
            "pluie_prevue": False,
            "gel_risque": mois == 3,
            "vent": "faible",
            "conseil": "Période idéale pour les semis et plantations.",
        }
    elif mois in [6, 7, 8]:  # Été
        return {
            "temperature": 25,
            "pluie_prevue": False,
            "gel_risque": False,
            "vent": "faible",
            "conseil": "Arrosez tôt le matin ou tard le soir. Paillez pour garder l'humidité.",
        }
    else:  # Automne
        return {
            "temperature": 12,
            "pluie_prevue": True,
            "gel_risque": mois == 11,
            "vent": "modéré",
            "conseil": "Récoltez les derniers légumes. Préparez le jardin pour l'hiver.",
        }
