"""
Module Planificateur de Repas - Imports et constantes partagÃes

Interface style Jow:
- GÃenÃerateur IA de menus ÃequilibrÃes
- Apprentissage des goûts (ðŸ‘/ðŸ‘Ž) persistant en DB
- Versions Jules intÃegrÃees
- Suggestions alternatives
"""

import streamlit as st
from datetime import date, datetime, time, timedelta
from io import BytesIO
import logging
import json

logger = logging.getLogger(__name__)

from src.core.database import obtenir_contexte_db
from src.core.models import (
    Recette, Planning, Repas,
    SessionBatchCooking,
)
from src.core.ai import obtenir_client_ia
from src.services.recettes import get_recette_service
from src.services.planning import get_planning_service
from src.services.utilisateur import get_user_preference_service

# Logique mÃetier pure
from src.modules.cuisine.planificateur_repas.utils import (
    JOURS_SEMAINE,
    PROTEINES,
    ROBOTS_CUISINE,
    TEMPS_CATEGORIES,
    PreferencesUtilisateur,
    FeedbackRecette,
    RecetteSuggestion,
    RepasPlannifie,
    PlanningSemaine,
    calculer_score_recette,
    filtrer_recettes_eligibles,
    generer_suggestions_alternatives,
    generer_prompt_semaine,
    generer_prompt_alternative,
    valider_equilibre_semaine,
    suggerer_ajustements_equilibre,
)


__all__ = [
    # Standard libs
    "st", "date", "datetime", "time", "timedelta", "BytesIO", "json", "logger",
    # Database / Services
    "obtenir_contexte_db", "Recette", "Planning", "Repas", "SessionBatchCooking",
    "obtenir_client_ia", "get_recette_service", "get_planning_service", 
    "get_user_preference_service",
    # Logic - constants
    "JOURS_SEMAINE", "PROTEINES", "ROBOTS_CUISINE", "TEMPS_CATEGORIES",
    # Logic - dataclasses
    "PreferencesUtilisateur", "FeedbackRecette", "RecetteSuggestion",
    "RepasPlannifie", "PlanningSemaine",
    # Logic - functions
    "calculer_score_recette", "filtrer_recettes_eligibles",
    "generer_suggestions_alternatives", "generer_prompt_semaine",
    "generer_prompt_alternative", "valider_equilibre_semaine",
    "suggerer_ajustements_equilibre",
]
