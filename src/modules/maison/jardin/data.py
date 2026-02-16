"""
Jardin - Chargement des données.

Fonctions de récupération du catalogue plantes et données météo.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

import streamlit as st

logger = logging.getLogger(__name__)


# =============================================================================
# CHARGEMENT DONNÉES
# =============================================================================


@st.cache_data(ttl=3600)
def charger_catalogue_plantes() -> dict:
    """Charge le catalogue des plantes depuis le fichier JSON."""
    try:
        catalogue_path = (
            Path(__file__).parent.parent.parent.parent.parent / "data" / "catalogue_jardin.json"
        )
        if catalogue_path.exists():
            with open(catalogue_path, encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Erreur chargement catalogue: {e}")

    # Catalogue minimal par défaut
    return {
        "plantes": {
            "tomate": {
                "nom": "Tomate",
                "emoji": "🍅",
                "categorie": "légume-fruit",
                "semis_interieur": [2, 3],
                "plantation_exterieur": [5, 6],
                "recolte": [7, 8, 9],
                "rendement_kg_m2": 4,
                "besoin_eau": "moyen",
                "exposition": "soleil",
                "compagnons_positifs": ["basilic", "carotte", "persil"],
                "compagnons_negatifs": ["fenouil", "chou"],
            },
            "courgette": {
                "nom": "Courgette",
                "emoji": "🥒",
                "categorie": "légume-fruit",
                "semis_interieur": [3, 4],
                "plantation_exterieur": [5, 6],
                "recolte": [6, 7, 8, 9],
                "rendement_kg_m2": 5,
                "besoin_eau": "élevé",
                "exposition": "soleil",
            },
            "carotte": {
                "nom": "Carotte",
                "emoji": "🥕",
                "categorie": "légume-racine",
                "semis_direct": [3, 4, 5, 6],
                "recolte": [6, 7, 8, 9, 10],
                "rendement_kg_m2": 3,
                "besoin_eau": "faible",
                "exposition": "mi-ombre",
            },
            "salade": {
                "nom": "Salade",
                "emoji": "🥬",
                "categorie": "légume-feuille",
                "semis_direct": [3, 4, 5, 6, 7, 8],
                "recolte": [4, 5, 6, 7, 8, 9, 10],
                "rendement_kg_m2": 2,
                "besoin_eau": "moyen",
                "exposition": "mi-ombre",
            },
            "basilic": {
                "nom": "Basilic",
                "emoji": "🌿",
                "categorie": "aromatique",
                "semis_interieur": [3, 4],
                "plantation_exterieur": [5, 6],
                "recolte": [6, 7, 8, 9],
                "rendement_kg_m2": 0.5,
                "besoin_eau": "moyen",
                "exposition": "soleil",
            },
        },
        "calendrier_lunaire": {},
        "objectifs_autonomie": {
            "legumes_fruits_kg": 150,
            "legumes_feuilles_kg": 50,
            "legumes_racines_kg": 60,
            "aromatiques_kg": 5,
        },
    }


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
