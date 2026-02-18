"""
Module Loto - Imports communs centralisés

Ce fichier centralise les imports pour éviter les dépendances circulaires
entre les différents modules du package Loto.
"""

import logging
import random
from datetime import date, datetime, timedelta
from decimal import Decimal

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.core.db import obtenir_contexte_db
from src.core.models import GrilleLoto, TirageLoto
from src.modules.jeux.scraper_loto import charger_tirages_loto

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════
# CONSTANTES LOTO
# ═══════════════════════════════════════════════════════════════════

NUMERO_MIN = 1
NUMERO_MAX = 49
CHANCE_MIN = 1
CHANCE_MAX = 10
NB_NUMEROS = 5
COUT_GRILLE = Decimal("2.20")
PROBA_JACKPOT = 1 / 19_068_840

GAINS_PAR_RANG = {
    1: None,
    2: 100_000,
    3: 1_000,
    4: 500,
    5: 50,
    6: 20,
    7: 10,
    8: 5,
    9: 2.20,
}

NUMEROS_POPULAIRES = set(range(1, 32))

# ═══════════════════════════════════════════════════════════════════
# RÉEXPORTS DEPUIS LES MODULES SPÉCIALISÉS
# ═══════════════════════════════════════════════════════════════════

from .calculs import (
    calculer_esperance_mathematique,
    verifier_grille,
)
from .frequences import (
    analyser_patterns_tirages,
    calculer_ecart,
    calculer_frequences_numeros,
    identifier_numeros_chauds_froids,
)
from .generation import (
    generer_grille_aleatoire,
    generer_grille_chauds_froids,
    generer_grille_equilibree,
    generer_grille_eviter_populaires,
)
from .strategies import (
    comparer_strategies,
    simuler_strategie,
)

__all__ = [
    # Streamlit
    "st",
    # Standard lib
    "date",
    "datetime",
    "timedelta",
    "random",
    "Decimal",
    "logger",
    # Third party
    "pd",
    "go",
    # Core
    "obtenir_contexte_db",
    "TirageLoto",
    "GrilleLoto",
    "charger_tirages_loto",
    # Constantes
    "NUMERO_MIN",
    "NUMERO_MAX",
    "CHANCE_MIN",
    "CHANCE_MAX",
    "NB_NUMEROS",
    "COUT_GRILLE",
    "PROBA_JACKPOT",
    "GAINS_PAR_RANG",
    "NUMEROS_POPULAIRES",
    # Calculs
    "calculer_esperance_mathematique",
    "verifier_grille",
    # Frequences
    "analyser_patterns_tirages",
    "calculer_ecart",
    "calculer_frequences_numeros",
    "identifier_numeros_chauds_froids",
    # Generation
    "generer_grille_aleatoire",
    "generer_grille_chauds_froids",
    "generer_grille_equilibree",
    "generer_grille_eviter_populaires",
    # Strategies
    "comparer_strategies",
    "simuler_strategie",
]
