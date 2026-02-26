"""
Logique metier du Planificateur de Repas Intelligent

Hub de re-exports: les implementations sont dans helpers.py, calculs.py et prompts.py
"""

# Re-export depuis helpers (constantes, dataclasses)
# Re-export JOURS_SEMAINE pour compatibilite
from src.core.constants import JOURS_SEMAINE

# Re-export depuis schemas (pour compatibilite)
from src.modules.cuisine.schemas import FeedbackRecette, PreferencesUtilisateur

# Re-export depuis calculs (scoring, filtrage, validation, equilibre)
from .calculs import (
    calculer_score_recette,
    filtrer_recettes_eligibles,
    generer_suggestions_alternatives,
    suggerer_ajustements_equilibre,
    valider_equilibre_semaine,
)
from .helpers import (
    EQUILIBRE_DEFAUT,
    PROTEINES,
    ROBOTS_CUISINE,
    TEMPS_CATEGORIES,
    TYPES_REPAS,
    PlanningSemaine,
    RecetteSuggestion,
    RepasPlannifie,
)

# Re-export depuis prompts (generation de prompts IA)
from .prompts import generer_prompt_alternative, generer_prompt_semaine

__all__ = [
    # Constantes
    "EQUILIBRE_DEFAUT",
    "JOURS_SEMAINE",
    "PROTEINES",
    "ROBOTS_CUISINE",
    "TEMPS_CATEGORIES",
    "TYPES_REPAS",
    # Dataclasses
    "PlanningSemaine",
    "RecetteSuggestion",
    "RepasPlannifie",
    # Schemas
    "FeedbackRecette",
    "PreferencesUtilisateur",
    # Calculs
    "calculer_score_recette",
    "filtrer_recettes_eligibles",
    "generer_suggestions_alternatives",
    "suggerer_ajustements_equilibre",
    "valider_equilibre_semaine",
    # Prompts
    "generer_prompt_alternative",
    "generer_prompt_semaine",
]
