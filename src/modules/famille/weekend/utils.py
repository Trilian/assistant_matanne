"""
Module Sorties Weekend - Imports et constantes partages

Planning et suggestions IA:
- 📅 Planning weekend (samedi/dimanche)
- 💡 Idees IA (selon meteo + âge Jules + budget)
- 🗺️ Lieux testes & notes
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
    "st", "date", "timedelta", "Optional",
    # Database
    "obtenir_contexte_db", "WeekendActivity", "ChildProfile",
    # AI
    "BaseAIService", "ClientIA",
    # Constants
    "TYPES_ACTIVITES", "METEO_OPTIONS",
]

