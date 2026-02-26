"""
Module Euromillions - Constantes

Euromillions: 5 numéros (1-50) + 2 étoiles (1-12)
Tirages: mardi et vendredi soir
"""

from decimal import Decimal

NUMERO_MIN = 1
NUMERO_MAX = 50
ETOILE_MIN = 1
ETOILE_MAX = 12
NB_NUMEROS = 5
NB_ETOILES = 2
COUT_GRILLE = Decimal("2.50")
PROBA_JACKPOT = 1 / 139_838_160

# Gains par rang (approximatifs, varient selon jackpot et nombre de gagnants)
# 13 rangs au total pour Euromillions
GAINS_PAR_RANG = {
    1: None,  # 5+2★ Jackpot (variable, min 17M€)
    2: 300_000,  # 5+1★
    3: 50_000,  # 5+0★
    4: 3_000,  # 4+2★
    5: 200,  # 4+1★
    6: 100,  # 3+2★
    7: 50,  # 4+0★
    8: 20,  # 2+2★
    9: 15,  # 3+1★
    10: 10,  # 3+0★
    11: 8,  # 1+2★
    12: 6,  # 2+1★
    13: 4,  # 2+0★
}

NUMEROS_POPULAIRES = set(range(1, 32))  # Dates = 1-31

# Jours de tirage
JOURS_TIRAGE = ["mardi", "vendredi"]
