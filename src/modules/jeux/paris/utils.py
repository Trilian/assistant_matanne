"""
Imports communs et constantes pour le module paris sportifs.
"""

import logging
from datetime import date, timedelta
from decimal import Decimal
from typing import Dict

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.services.jeux import get_paris_crud_service

logger = logging.getLogger(__name__)

# Imports directs depuis le service unifié jeux
from src.services.jeux import charger_classement as api_charger_classement
from src.services.jeux import charger_historique_equipe, charger_matchs_termines
from src.services.jeux import charger_matchs_a_venir as api_charger_matchs_a_venir
from src.services.jeux import vider_cache as api_vider_cache

from .constants import CHAMPIONNATS, SEUIL_SERIE_SANS_NUL
from .forme import calculer_forme_equipe, calculer_historique_face_a_face
from .stats import analyser_tendances_championnat, calculer_performance_paris

__all__ = [
    "st",
    "date",
    "timedelta",
    "Decimal",
    "Dict",
    "pd",
    "go",
    "px",
    "logging",
    "logger",
    "CHAMPIONNATS",
    "calculer_forme_equipe",
    "calculer_historique_face_a_face",
    "calculer_performance_paris",
    "analyser_tendances_championnat",
    "SEUIL_SERIE_SANS_NUL",
    "api_charger_classement",
    "api_charger_matchs_a_venir",
    "charger_historique_equipe",
    "charger_matchs_termines",
    "api_vider_cache",
]

# ============================================================
# Fonctions importées depuis utilitaires.py
# ============================================================


def charger_championnats_disponibles():
    """Retourne la liste des championnats disponibles"""
    return CHAMPIONNATS


def charger_equipes(championnat: str = None):
    """Charge les equipes, optionnellement filtrees par championnat"""
    try:
        service = get_paris_crud_service()
        return service.charger_equipes(championnat)
    except Exception as e:
        st.error(f"❌ Erreur chargement equipes: {e}")
        return []


def charger_matchs_a_venir(jours: int = 7, championnat: str = None):
    """Charge les matchs à venir depuis la BD"""
    try:
        service = get_paris_crud_service()
        return service.charger_matchs_a_venir(jours, championnat)
    except Exception as e:
        st.error(f"❌ Erreur chargement matchs: {e}")
        return []


def charger_matchs_recents(equipe_id: int, nb_matchs: int = 10):
    """Charge les derniers matchs joues par une equipe"""
    try:
        service = get_paris_crud_service()
        return service.charger_matchs_recents(equipe_id, nb_matchs)
    except Exception as e:
        st.error(f"❌ Erreur chargement matchs recents: {e}")
        return []


def charger_paris_utilisateur(statut: str = None):
    """Charge les paris de l'utilisateur"""
    try:
        service = get_paris_crud_service()
        return service.charger_paris_utilisateur(statut)
    except Exception as e:
        st.error(f"❌ Erreur chargement paris: {e}")
        return []


__all__ = [
    "charger_championnats_disponibles",
    "charger_equipes",
    "charger_matchs_a_venir",
    "charger_matchs_recents",
    "charger_paris_utilisateur",
]
