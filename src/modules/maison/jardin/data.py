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

    TODO: Intégrer API météo réelle (OpenWeatherMap, etc.)
    """
    # Données simulées basées sur la saison
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
