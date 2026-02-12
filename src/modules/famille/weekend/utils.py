"""
Module Sorties Weekend - Imports et constantes partagés

Planning et suggestions IA:
- 📅 Planning weekend (samedi/dimanche)
- 💡 Idées IA (selon météo + âge Jules + budget)
- 🗺️ Lieux testés & notés
- 💰 Budget sorties
"""

import streamlit as st
from datetime import date, timedelta
from typing import Optional

from src.core.database import obtenir_contexte_db
from src.core.models import WeekendActivity, ChildProfile
from src.services.base import BaseAIService
from src.core.ai import ClientIA


TYPES_ACTIVITES = {
    "parc": {"emoji": "🌳", "label": "Parc / Nature"},
    "musee": {"emoji": "🏛️", "label": "Musée / Expo"},
    "piscine": {"emoji": "🏊", "label": "Piscine / Aquatique"},
    "zoo": {"emoji": "🦁", "label": "Zoo / Ferme"},
    "restaurant": {"emoji": "🍽️", "label": "Restaurant"},
    "cinema": {"emoji": "🎬", "label": "Cinéma"},
    "sport": {"emoji": "⚽", "label": "Sport / Loisir"},
    "shopping": {"emoji": "🛍️", "label": "Shopping"},
    "famille": {"emoji": "👨‍👩‍👧", "label": "Visite famille"},
    "maison": {"emoji": "🏠", "label": "Activité maison"},
    "autre": {"emoji": "✨", "label": "Autre"},
}

METEO_OPTIONS = ["ensoleillé", "nuageux", "pluvieux", "intérieur"]


__all__ = [
    # Standard libs
    "st", "date", "timedelta", "Optional",
    # Database
    "obtenir_contexte_db", "WeekendActivity", "ChildProfile",
    # AI
    "BaseAIService", "ClientIA",
    # Constants
    "TYPES_ACTIVITES", "METEO_OPTIONS",
]

