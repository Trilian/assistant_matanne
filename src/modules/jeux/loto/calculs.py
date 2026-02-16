"""
Calculs mathématiques Loto - Probabilités et espérance

⚠️ DISCLAIMER: Ces calculs démontrent que le Loto est défavorable au joueur.
L'espérance mathématique est toujours négative.
"""

import logging
from decimal import Decimal
from typing import Any

logger = logging.getLogger(__name__)

# Constantes Loto français
COUT_GRILLE = Decimal("2.20")

# Gains par rang (approximatifs, varient selon jackpot et nombre de gagnants)
GAINS_PAR_RANG = {
    1: None,  # Jackpot (variable)
    2: 100_000,  # 5 bons
    3: 1_000,  # 4 bons + chance
    4: 500,  # 4 bons
    5: 50,  # 3 bons + chance
    6: 20,  # 3 bons
    7: 10,  # 2 bons + chance
    8: 5,  # 2 bons
    9: 2.20,  # 1 bon + chance (remboursement)
}

# Probabilité de gagner le jackpot (5 bons + chance)
PROBA_JACKPOT = 1 / 19_068_840  # ~1 sur 19 millions


def verifier_grille(grille: dict[str, Any], tirage: dict[str, Any]) -> dict[str, Any]:
    """
    Vérifie une grille contre un tirage et calcule les gains.

    Args:
        grille: Grille jouée
        tirage: Résultat du tirage

    Returns:
        Résultat avec rang et gain
    """
    # Numéros du tirage
    numeros_tirage = set([tirage.get(f"numero_{i}") for i in range(1, 6)])
    chance_tirage = tirage.get("numero_chance")

    # Numéros de la grille
    numeros_grille = set(grille.get("numeros", []))
    chance_grille = grille.get("numero_chance")

    # Compter les bons numéros
    bons_numeros = len(numeros_tirage & numeros_grille)
    chance_ok = chance_grille == chance_tirage

    # Déterminer le rang
    rang = None
    gain = Decimal("0.00")

    if bons_numeros == 5 and chance_ok:
        rang = 1  # Jackpot!
        gain = Decimal(str(tirage.get("jackpot_euros", 2_000_000)))
    elif bons_numeros == 5:
        rang = 2
        gain = Decimal(str(GAINS_PAR_RANG[2]))
    elif bons_numeros == 4 and chance_ok:
        rang = 3
        gain = Decimal(str(GAINS_PAR_RANG[3]))
    elif bons_numeros == 4:
        rang = 4
        gain = Decimal(str(GAINS_PAR_RANG[4]))
    elif bons_numeros == 3 and chance_ok:
        rang = 5
        gain = Decimal(str(GAINS_PAR_RANG[5]))
    elif bons_numeros == 3:
        rang = 6
        gain = Decimal(str(GAINS_PAR_RANG[6]))
    elif bons_numeros == 2 and chance_ok:
        rang = 7
        gain = Decimal(str(GAINS_PAR_RANG[7]))
    elif bons_numeros == 2:
        rang = 8
        gain = Decimal(str(GAINS_PAR_RANG[8]))
    elif bons_numeros == 1 and chance_ok:
        rang = 9
        gain = Decimal(str(GAINS_PAR_RANG[9]))

    return {
        "bons_numeros": bons_numeros,
        "chance_ok": chance_ok,
        "rang": rang,
        "gain": gain,
        "gagnant": rang is not None,
        "description": f"{bons_numeros} numéros" + (" + chance" if chance_ok else ""),
    }


def calculer_esperance_mathematique() -> dict[str, Any]:
    """
    Calcule l'espérance mathématique du Loto.

    Spoiler: Elle est négative (c'est un jeu d'argent).

    Returns:
        Espérance et probabilités
    """
    # Probabilités exactes du Loto français
    probas = {
        1: 1 / 19_068_840,  # 5 + chance
        2: 1 / 2_118_760,  # 5
        3: 1 / 86_677,  # 4 + chance
        4: 1 / 9_631,  # 4
        5: 1 / 2_016,  # 3 + chance
        6: 1 / 224,  # 3
        7: 1 / 144,  # 2 + chance
        8: 1 / 16,  # 2
        9: 1 / 16,  # 1 + chance
    }

    # Calcul espérance (jackpot moyen estimé à 5M€)
    jackpot_moyen = 5_000_000
    gains_esperes = (
        probas[1] * jackpot_moyen
        + probas[2] * GAINS_PAR_RANG[2]
        + probas[3] * GAINS_PAR_RANG[3]
        + probas[4] * GAINS_PAR_RANG[4]
        + probas[5] * GAINS_PAR_RANG[5]
        + probas[6] * GAINS_PAR_RANG[6]
        + probas[7] * GAINS_PAR_RANG[7]
        + probas[8] * GAINS_PAR_RANG[8]
        + probas[9] * GAINS_PAR_RANG[9]
    )

    esperance = gains_esperes - float(COUT_GRILLE)

    return {
        "cout_grille": float(COUT_GRILLE),
        "gains_esperes": round(gains_esperes, 4),
        "esperance": round(esperance, 4),
        "perte_moyenne_pct": round((1 - gains_esperes / float(COUT_GRILLE)) * 100, 1),
        "probabilites": {rang: f"1/{int(1 / p):,}" for rang, p in probas.items()},
        "conclusion": (
            f"En moyenne, vous perdez {abs(esperance):.2f}€ par grille jouée. "
            f"Le Loto reverse environ {gains_esperes / float(COUT_GRILLE) * 100:.0f}% des mises."
        ),
    }
