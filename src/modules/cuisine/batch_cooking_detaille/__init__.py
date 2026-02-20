"""
Module Batch Cooking Détaillé - UI Streamlit

Interface pour les sessions de batch cooking:
- Planning visuel avec timeline
- Instructions détaillées (découpes, robots, quantités)
- Moments Jules intégrés
- Génération liste de courses
- Export/impression
"""

from .app import app
from .components import (
    afficher_etape_batch,
    afficher_finition_jour_j,
    afficher_ingredient_detaille,
    afficher_instruction_robot,
    afficher_liste_courses_batch,
    afficher_moments_jules,
    afficher_planning_semaine_preview,
    afficher_selecteur_session,
    afficher_timeline_session,
)
from .constants import TYPES_DECOUPE, TYPES_SESSION
from .generation import generer_batch_ia

__all__ = [
    "app",
    "TYPES_DECOUPE",
    "TYPES_SESSION",
    "afficher_selecteur_session",
    "afficher_planning_semaine_preview",
    "afficher_ingredient_detaille",
    "afficher_etape_batch",
    "afficher_instruction_robot",
    "afficher_timeline_session",
    "afficher_moments_jules",
    "afficher_liste_courses_batch",
    "afficher_finition_jour_j",
    "generer_batch_ia",
]
