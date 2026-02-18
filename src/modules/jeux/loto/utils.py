"""
Module Loto - Utilitaires et réexports

Ce module fournit un point d'accès unifié aux fonctionnalités Loto.
La logique a été éclatée en modules spécialisés pour une meilleure maintenabilité.

⚠️ DISCLAIMER: Le Loto est un jeu de hasard pur.
Aucune stratégie ne peut prédire les résultats.
"""

import logging
from datetime import date, datetime, timedelta
from decimal import Decimal

import streamlit as st

from src.core.db import obtenir_contexte_db
from src.core.models import GrilleLoto, TirageLoto

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════
# CONSTANTES (maintenues ici pour rétrocompatibilité)
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

# ═══════════════════════════════════════════════════════════════════
# FONCTIONS UTILITAIRES DB
# ═══════════════════════════════════════════════════════════════════


@st.cache_data(ttl=1800)
def charger_tirages_db() -> list[dict]:
    """Charge les tirages depuis la base de données avec cache Streamlit."""
    with obtenir_contexte_db() as session:
        tirages = session.query(TirageLoto).order_by(TirageLoto.date_tirage.desc()).all()
        return [
            {
                "id": t.id,
                "date_tirage": t.date_tirage,
                "numero_1": t.numero_1,
                "numero_2": t.numero_2,
                "numero_3": t.numero_3,
                "numero_4": t.numero_4,
                "numero_5": t.numero_5,
                "numero_chance": t.numero_chance,
                "jackpot_euros": t.jackpot_euros,
            }
            for t in tirages
        ]


def charger_tirages(limite: int = 100) -> list[dict]:
    """Alias vers charger_tirages_db pour rétrocompatibilité."""
    tirages = charger_tirages_db()
    return tirages[:limite] if limite else tirages


@st.cache_data(ttl=1800)
def charger_grilles_utilisateur() -> list[dict]:
    """Charge les grilles enregistrées par l'utilisateur."""
    with obtenir_contexte_db() as session:
        grilles = session.query(GrilleLoto).order_by(GrilleLoto.date_creation.desc()).all()
        return [
            {
                "id": g.id,
                "numeros": [g.numero_1, g.numero_2, g.numero_3, g.numero_4, g.numero_5],
                "numero_chance": g.numero_chance,
                "date_creation": g.date_creation,
                "strategie": g.strategie,
                "note": g.note,
            }
            for g in grilles
        ]


def sauvegarder_grille(
    numeros: list[int],
    numero_chance: int,
    strategie: str = "manuel",
    note: str | None = None,
) -> int:
    """Sauvegarde une grille dans la base de données."""
    with obtenir_contexte_db() as session:
        grille = GrilleLoto(
            numero_1=numeros[0],
            numero_2=numeros[1],
            numero_3=numeros[2],
            numero_4=numeros[3],
            numero_5=numeros[4],
            numero_chance=numero_chance,
            strategie=strategie,
            note=note,
        )
        session.add(grille)
        session.commit()
        return grille.id


# ═══════════════════════════════════════════════════════════════════
# EXPORTS PUBLICS
# ═══════════════════════════════════════════════════════════════════

__all__ = [
    # Constantes
    "NUMERO_MIN",
    "NUMERO_MAX",
    "CHANCE_MIN",
    "CHANCE_MAX",
    "NB_NUMEROS",
    "COUT_GRILLE",
    "GAINS_PAR_RANG",
    "PROBA_JACKPOT",
    "NUMEROS_POPULAIRES",
    # Fréquences
    "calculer_frequences_numeros",
    "calculer_ecart",
    "identifier_numeros_chauds_froids",
    "analyser_patterns_tirages",
    # Génération
    "generer_grille_aleatoire",
    "generer_grille_eviter_populaires",
    "generer_grille_equilibree",
    "generer_grille_chauds_froids",
    # Calculs
    "verifier_grille",
    "calculer_esperance_mathematique",
    # Simulation
    "simuler_strategie",
    "comparer_strategies",
    # Utilitaires DB
    "charger_tirages_db",
    "charger_tirages",
    "charger_grilles_utilisateur",
    "sauvegarder_grille",
    # Database
    "obtenir_contexte_db",
    "TirageLoto",
    "GrilleLoto",
    # Standard
    "st",
    "logger",
    "Decimal",
    "date",
    "datetime",
    "timedelta",
]
