"""
Imports communs et constantes pour le module courses.
"""

import logging
from datetime import datetime, timedelta

import pandas as pd
import streamlit as st

from src.core.db import obtenir_contexte_db
from src.core.errors_base import ErreurValidation

# Import du module logique métier séparé
from src.modules.cuisine.courses.utils import (
    PRIORITY_EMOJIS,
    PRIORITY_ORDER,
    RAYONS_DEFAULT,
    analyser_historique,
    calculer_statistiques,
    deduper_suggestions,
    filtrer_par_priorite,
    formater_article_label,
    grouper_par_rayon,
    trier_par_priorite,
    valider_article,
)
from src.services.cuisine.courses import get_courses_intelligentes_service, get_courses_service
from src.services.inventaire import get_inventaire_service
from src.services.cuisine.recettes import get_recette_service
from src.services.integrations.web import get_realtime_sync_service

logger = logging.getLogger(__name__)

__all__ = [
    "logging",
    "st",
    "pd",
    "datetime",
    "timedelta",
    "get_courses_service",
    "get_inventaire_service",
    "get_recette_service",
    "get_realtime_sync_service",
    "get_courses_intelligentes_service",
    "ErreurValidation",
    "obtenir_contexte_db",
    "PRIORITY_EMOJIS",
    "PRIORITY_ORDER",
    "RAYONS_DEFAULT",
    "filtrer_par_priorite",
    "trier_par_priorite",
    "grouper_par_rayon",
    "calculer_statistiques",
    "valider_article",
    "formater_article_label",
    "deduper_suggestions",
    "analyser_historique",
    "logger",
]
