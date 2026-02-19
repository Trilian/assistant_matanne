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
from src.services.cuisine.courses import (
    obtenir_service_courses,
    obtenir_service_courses_intelligentes,
)
from src.services.cuisine.recettes import obtenir_service_recettes
from src.services.integrations.web import get_realtime_sync_service
from src.services.inventaire import obtenir_service_inventaire
from src.ui.components.atoms import etat_vide

logger = logging.getLogger(__name__)


def get_current_user_id() -> str | None:
    """Retourne l'ID de l'utilisateur courant ou None si non authentifié."""
    try:
        from src.services.core.utilisateur import get_auth_service

        auth = get_auth_service()
        user = auth.get_current_user()
        return user.id if user else None
    except Exception:
        return None


__all__ = [
    "logging",
    "st",
    "pd",
    "datetime",
    "timedelta",
    "obtenir_service_courses",
    "obtenir_service_inventaire",
    "obtenir_service_recettes",
    "get_realtime_sync_service",
    "obtenir_service_courses_intelligentes",
    "get_current_user_id",
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
