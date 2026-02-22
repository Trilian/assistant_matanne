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

from src.core.decorators import avec_cache
from src.services.jeux import get_loto_crud_service

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


@avec_cache(ttl=1800)
def charger_tirages_db() -> list[dict]:
    """Charge les tirages depuis la base de données avec cache multi-niveaux."""
    service = get_loto_crud_service()
    return service.charger_tirages()


def charger_tirages(limite: int = 100) -> list[dict]:
    """Alias vers charger_tirages_db pour rétrocompatibilité."""
    tirages = charger_tirages_db()
    return tirages[:limite] if limite else tirages


@avec_cache(ttl=1800)
def charger_grilles_utilisateur() -> list[dict]:
    """Charge les grilles enregistrées par l'utilisateur."""
    service = get_loto_crud_service()
    return service.charger_grilles_utilisateur()


def sauvegarder_grille(
    numeros: list[int],
    numero_chance: int,
    strategie: str = "manuel",
    note: str | None = None,
) -> int:
    """Sauvegarde une grille dans la base de données."""
    service = get_loto_crud_service()
    return service.sauvegarder_grille(
        numeros=numeros,
        numero_chance=numero_chance,
        strategie=strategie,
        note=note,
    )


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
    # Standard
    "st",
    "logger",
    "Decimal",
    "date",
    "datetime",
    "timedelta",
]
