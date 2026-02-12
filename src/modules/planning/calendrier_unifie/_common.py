"""
Module Calendrier Familial UnifiÃe - Imports et constantes partagÃes

Affiche dans une seule vue:
- ðŸ½ï¸ Repas (midi, soir, goûters)
- ðŸ³ Sessions batch cooking
- ðŸ›’ Courses planifiÃees
- ðŸŽ¨ ActivitÃes famille
- ðŸ¥ RDV mÃedicaux
- ðŸ“… ÉvÃenements divers
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

# Logique mÃetier pure (types et fonctions utilitaires)
from src.modules.planning.calendrier_unifie.utils import (
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
