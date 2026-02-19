"""
Module Loto - Constantes
"""

from decimal import Decimal

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
