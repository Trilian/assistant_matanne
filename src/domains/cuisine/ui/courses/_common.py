"""
Imports communs et constantes pour le module courses.
"""

import logging
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

from src.services.courses import get_courses_service
from src.services.inventaire import get_inventaire_service
from src.services.recettes import get_recette_service
from src.services.realtime_sync import get_realtime_sync_service
from src.services.courses_intelligentes import get_courses_intelligentes_service
from src.core.errors_base import ErreurValidation
from src.core.database import obtenir_contexte_db

# Import du module logique métier séparé
from src.domains.cuisine.logic.courses_logic import (
    PRIORITY_EMOJIS,
    PRIORITY_ORDER,
    RAYONS_DEFAULT,
    filtrer_par_priorite,
    trier_par_priorite,
    grouper_par_rayon,
    calculer_statistiques,
    valider_article,
    formater_article_label,
    deduper_suggestions,
    analyser_historique,
)

logger = logging.getLogger(__name__)

__all__ = [
    "logging", "st", "pd", "datetime", "timedelta",
    "get_courses_service", "get_inventaire_service", "get_recette_service",
    "get_realtime_sync_service", "get_courses_intelligentes_service",
    "ErreurValidation", "obtenir_contexte_db",
    "PRIORITY_EMOJIS", "PRIORITY_ORDER", "RAYONS_DEFAULT",
    "filtrer_par_priorite", "trier_par_priorite", "grouper_par_rayon",
    "calculer_statistiques", "valider_article", "formater_article_label",
    "deduper_suggestions", "analyser_historique",
    "logger",
]
