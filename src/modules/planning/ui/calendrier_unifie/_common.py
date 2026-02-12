"""
Module Calendrier Familial Unifié - Imports et constantes partagés

Affiche dans une seule vue:
- 🍽️ Repas (midi, soir, goûters)
- 🍳 Sessions batch cooking
- 🛒 Courses planifiées
- 🎨 Activités famille
- 🏥 RDV médicaux
- 📅 Événements divers
"""

import streamlit as st
from datetime import date, datetime, time, timedelta
import logging

from src.core.database import obtenir_contexte_db
from src.core.models import (
    Planning, Repas, Recette,
    SessionBatchCooking,
    FamilyActivity,
    CalendarEvent,
)

# Logique métier pure (types et fonctions utilitaires)
from src.domains.planning.logic.calendrier_unifie_logic import (
    TypeEvenement,
    EvenementCalendrier,
    JourCalendrier,
    SemaineCalendrier,
    JOURS_SEMAINE,
    EMOJI_TYPE,
    COULEUR_TYPE,
    get_debut_semaine,
    get_semaine_precedente,
    get_semaine_suivante,
    construire_semaine_calendrier,
    generer_texte_semaine_pour_impression,
)

logger = logging.getLogger(__name__)


__all__ = [
    # Standard libs
    "st", "date", "datetime", "time", "timedelta", "logging", "logger",
    # Database
    "obtenir_contexte_db",
    "Planning", "Repas", "Recette", "SessionBatchCooking", "FamilyActivity", "CalendarEvent",
    # Logic
    "TypeEvenement", "EvenementCalendrier", "JourCalendrier", "SemaineCalendrier",
    "JOURS_SEMAINE", "EMOJI_TYPE", "COULEUR_TYPE",
    "get_debut_semaine", "get_semaine_precedente", "get_semaine_suivante",
    "construire_semaine_calendrier", "generer_texte_semaine_pour_impression",
]
