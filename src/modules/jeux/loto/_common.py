"""
Module Loto - Imports et constantes partages

⚠️ DISCLAIMER: Le Loto est un jeu de hasard pur.
Aucune strategie ne peut predire les resultats.
Ce module est à but educatif et de divertissement.
"""

import logging
import random
from datetime import date, datetime, timedelta
from decimal import Decimal

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

logger = logging.getLogger(__name__)

from src.core.database import obtenir_contexte_db
from src.core.models import GrilleLoto, StatistiquesLoto, TirageLoto
from src.modules.jeux.loto.utils import (
    CHANCE_MAX,
    CHANCE_MIN,
    COUT_GRILLE,
    GAINS_PAR_RANG,
    NB_NUMEROS,
    NUMERO_MAX,
    NUMERO_MIN,
    PROBA_JACKPOT,
    analyser_patterns_tirages,
    calculer_esperance_mathematique,
    calculer_frequences_numeros,
    comparer_strategies,
    generer_grille_aleatoire,
    generer_grille_chauds_froids,
    generer_grille_equilibree,
    generer_grille_eviter_populaires,
    identifier_numeros_chauds_froids,
    simuler_strategie,
    verifier_grille,
)
from src.modules.jeux.scraper_loto import charger_tirages_loto

__all__ = [
    # Standard libs
    "st",
    "date",
    "timedelta",
    "datetime",
    "Decimal",
    "pd",
    "go",
    "px",
    "random",
    "logger",
    # Database
    "obtenir_contexte_db",
    "TirageLoto",
    "GrilleLoto",
    "StatistiquesLoto",
    # Logic - constants
    "NUMERO_MIN",
    "NUMERO_MAX",
    "CHANCE_MIN",
    "CHANCE_MAX",
    "NB_NUMEROS",
    "COUT_GRILLE",
    "GAINS_PAR_RANG",
    "PROBA_JACKPOT",
    # Logic - functions
    "calculer_frequences_numeros",
    "identifier_numeros_chauds_froids",
    "analyser_patterns_tirages",
    "generer_grille_aleatoire",
    "generer_grille_eviter_populaires",
    "generer_grille_equilibree",
    "generer_grille_chauds_froids",
    "verifier_grille",
    "simuler_strategie",
    "calculer_esperance_mathematique",
    "comparer_strategies",
    # Scraper
    "charger_tirages_loto",
]
