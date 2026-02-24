"""
Module Suivi Perso - Imports et constantes partages

Dashboard sante/sport pour Anne et Mathieu:
- Switch utilisateur (Anne / Mathieu)
- Dashboard perso (stats Garmin, streak, objectifs)
- Routines sport
- Log alimentation
- Progression (graphiques)
- Sync Garmin
"""

import logging
from datetime import date, datetime, timedelta

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

logger = logging.getLogger(__name__)

from src.core.constants import OBJECTIF_PAS_QUOTIDIEN_DEFAUT
from src.core.models import (
    ActiviteGarmin,
    GarminToken,
    JournalAlimentaire,
    ProfilUtilisateur,
    ResumeQuotidienGarmin,
    RoutineSante,
)
from src.core.session_keys import SK
from src.services.famille.suivi_perso import obtenir_service_suivi_perso
from src.services.integrations.garmin import (
    ServiceGarmin,
    get_garmin_service,
    get_or_create_user,
    get_user_by_username,
)

__all__ = [
    # Standard libs
    "date",
    "datetime",
    "timedelta",
    "go",
    "px",
    # Database
    # Models
    "ProfilUtilisateur",
    "GarminToken",
    "ActiviteGarmin",
    "ResumeQuotidienGarmin",
    "JournalAlimentaire",
    "RoutineSante",
    # Services
    "ServiceGarmin",
    "get_garmin_service",
    "get_or_create_user",
    "get_user_by_username",
]

# ============================================================
# Fonctions importées depuis utilitaires.py
# ============================================================


def get_current_user() -> str:
    """Recupère l'utilisateur courant"""
    return st.session_state.get(SK.SUIVI_USER, "anne")


def set_current_user(username: str):
    """Definit l'utilisateur courant"""
    st.session_state[SK.SUIVI_USER] = username


def get_user_data(username: str) -> dict:
    """Récupère les données complètes de l'utilisateur"""
    try:
        return obtenir_service_suivi_perso().get_user_data(username)
    except Exception as e:
        logger.debug(f"Erreur ignorée: {e}")
        return {}


def get_food_logs_today(username: str) -> list:
    """Récupère les logs alimentation du jour"""
    try:
        return obtenir_service_suivi_perso().get_food_logs_today(username)
    except Exception as e:
        logger.debug(f"Erreur ignorée: {e}")
        return []
