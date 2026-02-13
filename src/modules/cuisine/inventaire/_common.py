"""
Imports partagés pour le module inventaire UI.
Centralise toutes les dépendances communes.
"""

import logging
from datetime import date, timedelta
from typing import Any

import pandas as pd
import streamlit as st

from src.core.errors_base import ErreurValidation

# Import du module logique métier séparé
from src.modules.cuisine.inventaire.utils import (
    CATEGORIES,
    EMPLACEMENTS,
    STATUS_CONFIG,
    calculer_alertes,
    calculer_statistiques_inventaire,
    calculer_status_peremption,
    calculer_status_stock,
    filtrer_par_categorie,
    filtrer_par_emplacement,
    filtrer_par_status,
    formater_article_inventaire,
    grouper_par_categorie,
    trier_par_urgence,
    valider_article_inventaire,
)
from src.services.inventaire import get_inventaire_service
from src.services.suggestions import obtenir_service_predictions

# Logger pour le module
logger = logging.getLogger(__name__)

__all__ = [
    # Standard
    "logging",
    "logger",
    "st",
    "pd",
    "date",
    "timedelta",
    "Any",
    # Services
    "get_inventaire_service",
    "obtenir_service_predictions",
    "ErreurValidation",
    # Logic
    "EMPLACEMENTS",
    "CATEGORIES",
    "STATUS_CONFIG",
    "calculer_status_stock",
    "calculer_status_peremption",
    "calculer_alertes",
    "calculer_statistiques_inventaire",
    "valider_article_inventaire",
    "formater_article_inventaire",
    "trier_par_urgence",
    "filtrer_par_status",
    "filtrer_par_categorie",
    "filtrer_par_emplacement",
    "grouper_par_categorie",
]
