"""
Imports partagÃes pour le module inventaire UI.
Centralise toutes les dÃependances communes.
"""

import logging
import streamlit as st
import pandas as pd
from datetime import date, timedelta
from typing import Any

from src.services.inventaire import get_inventaire_service
from src.services.suggestions import obtenir_service_predictions
from src.core.errors_base import ErreurValidation

# Import du module logique mÃetier sÃeparÃe
from src.modules.cuisine.inventaire.utils import (
    EMPLACEMENTS,
    CATEGORIES,
    STATUS_CONFIG,
    calculer_status_stock,
    calculer_status_peremption,
    calculer_alertes,
    calculer_statistiques_inventaire,
    valider_article_inventaire,
    formater_article_inventaire,
    trier_par_urgence,
    filtrer_par_status,
    filtrer_par_categorie,
    filtrer_par_emplacement,
    grouper_par_categorie,
)

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
