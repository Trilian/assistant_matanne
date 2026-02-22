"""
Module Sorties Weekend - Imports et constantes partages

Planning et suggestions IA:
- 📅 Planning weekend (samedi/dimanche)
- 💡 Idees IA (selon meteo + âge Jules + budget)
- 🗺️ Lieux testes & notes
- 💰 Budget sorties
"""

import logging
from datetime import date, timedelta
from typing import Optional

import streamlit as st

from src.core.ai import ClientIA
from src.core.models import ChildProfile, WeekendActivity
from src.services.core.base import BaseAIService
from src.services.famille.weekend import obtenir_service_weekend
from src.ui import etat_vide

logger = logging.getLogger(__name__)

TYPES_ACTIVITES = {
    "parc": {"emoji": "🌳", "label": "Parc / Nature"},
    "musee": {"emoji": "🏛️", "label": "Musee / Expo"},
    "piscine": {"emoji": "🏊", "label": "Piscine / Aquatique"},
    "zoo": {"emoji": "🦁", "label": "Zoo / Ferme"},
    "restaurant": {"emoji": "🍽️", "label": "Restaurant"},
    "cinema": {"emoji": "🎬", "label": "Cinema"},
    "sport": {"emoji": "⚽", "label": "Sport / Loisir"},
    "shopping": {"emoji": "🛍️", "label": "Shopping"},
    "famille": {"emoji": "👨‍👩‍👧", "label": "Visite famille"},
    "maison": {"emoji": "🏠", "label": "Activite maison"},
    "autre": {"emoji": "✨", "label": "Autre"},
}

METEO_OPTIONS = ["ensoleille", "nuageux", "pluvieux", "interieur"]


__all__ = [
    # Standard libs
    "date",
    "timedelta",
    "Optional",
    # Database
    "WeekendActivity",
    "ChildProfile",
    # AI
    "BaseAIService",
    "ClientIA",
    # Constants
    "TYPES_ACTIVITES",
    "METEO_OPTIONS",
]

# ============================================================
# Fonctions importées depuis utilitaires.py
# ============================================================


def get_next_weekend() -> tuple[date, date]:
    """Retourne les dates du prochain weekend"""
    today = date.today()
    days_until_saturday = (5 - today.weekday()) % 7

    if today.weekday() == 5:  # Samedi
        saturday = today
    elif today.weekday() == 6:  # Dimanche
        saturday = today + timedelta(days=6)  # Prochain samedi
    else:
        if days_until_saturday == 0:
            days_until_saturday = 7
        saturday = today + timedelta(days=days_until_saturday)

    sunday = saturday + timedelta(days=1)
    return saturday, sunday


def get_weekend_activities(saturday: date, sunday: date) -> dict:
    """Recupère les activites du weekend"""
    try:
        return obtenir_service_weekend().lister_activites_weekend(saturday, sunday)
    except Exception as e:
        logger.debug(f"Erreur ignorée: {e}")
        return {"saturday": [], "sunday": []}


def get_budget_weekend(saturday: date, sunday: date) -> dict:
    """Calcule le budget du weekend"""
    try:
        return obtenir_service_weekend().get_budget_weekend(saturday, sunday)
    except Exception as e:
        logger.debug(f"Erreur ignorée: {e}")
        return {"estime": 0, "reel": 0}


def get_lieux_testes() -> list:
    """Recupère les lieux dejà testes"""
    try:
        return obtenir_service_weekend().get_lieux_testes()
    except Exception as e:
        logger.debug(f"Erreur ignorée: {e}")
        return []


def get_age_jules_mois() -> int:
    """Récupère l'âge de Jules en mois (délègue à age_utils)."""
    from src.modules.famille.age_utils import get_age_jules_mois as _get

    return _get()


def mark_activity_done(activity_id: int):
    """Marque une activite comme terminee"""
    try:
        obtenir_service_weekend().marquer_termine(activity_id)
    except Exception as e:
        logger.debug(f"Erreur ignorée: {e}")
