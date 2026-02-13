"""
Module Calendrier Familial Unifié - Imports et constantes partagés

Affiche dans une seule vue:
- ðŸ½ï¸ Repas (midi, soir, goûters)
- ðŸ³ Sessions batch cooking
- ðŸ›’ Courses planifiées
- ðŸŽ¨ Activités famille
- ðŸ¥ RDV médicaux
- ðŸ“… Événements divers
"""

import logging
from datetime import date, datetime, time, timedelta

import streamlit as st

from src.core.database import obtenir_contexte_db
from src.core.models import (
    CalendarEvent,
    FamilyActivity,
    Planning,
    Recette,
    Repas,
    SessionBatchCooking,
)

# Logique métier pure (types et fonctions utilitaires)
from src.modules.planning.calendrier_unifie.utils import (
    COULEUR_TYPE,
    EMOJI_TYPE,
    JOURS_SEMAINE,
    EvenementCalendrier,
    JourCalendrier,
    SemaineCalendrier,
    TypeEvenement,
    construire_semaine_calendrier,
    generer_texte_semaine_pour_impression,
    get_debut_semaine,
    get_semaine_precedente,
    get_semaine_suivante,
)

logger = logging.getLogger(__name__)


__all__ = [
    # Standard libs
    "st",
    "date",
    "datetime",
    "time",
    "timedelta",
    "logging",
    "logger",
    # Database
    "obtenir_contexte_db",
    "Planning",
    "Repas",
    "Recette",
    "SessionBatchCooking",
    "FamilyActivity",
    "CalendarEvent",
    # Logic
    "TypeEvenement",
    "EvenementCalendrier",
    "JourCalendrier",
    "SemaineCalendrier",
    "JOURS_SEMAINE",
    "EMOJI_TYPE",
    "COULEUR_TYPE",
    "get_debut_semaine",
    "get_semaine_precedente",
    "get_semaine_suivante",
    "construire_semaine_calendrier",
    "generer_texte_semaine_pour_impression",
]
