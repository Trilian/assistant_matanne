"""
Imports communs et constantes pour le module paris sportifs.
"""

import streamlit as st
from datetime import date, timedelta
from decimal import Decimal
from typing import Dict
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import logging

from src.core.database import get_session
from src.core.models import Equipe, Match, PariSportif, HistoriqueJeux

logger = logging.getLogger(__name__)

from src.domains.jeux.logic.paris import (
    CHAMPIONNATS,
    calculer_forme_equipe,
    calculer_historique_face_a_face,
    predire_resultat_match,
    predire_over_under,
    calculer_performance_paris,
    analyser_tendances_championnat,
    generer_conseils_avances,
    generer_analyse_complete,
    generer_resume_parieur,
    SEUIL_SERIE_SANS_NUL
)

from src.domains.jeux.logic.api_football import (
    charger_classement as api_charger_classement,
    charger_matchs_a_venir as api_charger_matchs_a_venir,
    charger_historique_equipe,
    charger_matchs_termines,
    vider_cache as api_vider_cache
)

__all__ = [
    "st", "date", "timedelta", "Decimal", "Dict", "pd", "go", "px", "logging",
    "get_session", "Equipe", "Match", "PariSportif", "HistoriqueJeux", "logger",
    "CHAMPIONNATS", "calculer_forme_equipe", "calculer_historique_face_a_face",
    "predire_resultat_match", "predire_over_under", "calculer_performance_paris",
    "analyser_tendances_championnat", "generer_conseils_avances",
    "generer_analyse_complete", "generer_resume_parieur", "SEUIL_SERIE_SANS_NUL",
    "api_charger_classement", "api_charger_matchs_a_venir",
    "charger_historique_equipe", "charger_matchs_termines", "api_vider_cache",
]
