"""
Calculs mathématiques Euromillions - Probabilités et espérance

⚠️ DISCLAIMER: Ces calculs démontrent que l'Euromillions est défavorable au joueur.
L'espérance mathématique est toujours négative.
"""

import logging
from decimal import Decimal
from typing import Any

logger = logging.getLogger(__name__)

COUT_GRILLE = Decimal("2.50")

GAINS_PAR_RANG = {
    1: None,  # 5+2★ Jackpot
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

PROBA_JACKPOT = 1 / 139_838_160


def verifier_grille(grille: dict[str, Any], tirage: dict[str, Any]) -> dict[str, Any]:
    """
    Vérifie une grille Euromillions contre un tirage.

    Args:
        grille: Grille jouée (numeros: list[int], etoiles: list[int])
        tirage: Résultat du tirage

    Returns:
        Résultat avec rang et gain
    """
    numeros_tirage = set(tirage.get(f"numero_{i}") for i in range(1, 6))
    etoiles_tirage = set(tirage.get(f"etoile_{i}") for i in range(1, 3))

    numeros_grille = set(grille.get("numeros", []))
    etoiles_grille = set(grille.get("etoiles", []))

    bons_numeros = len(numeros_tirage & numeros_grille)
    bonnes_etoiles = len(etoiles_tirage & etoiles_grille)

    rang = None
    gain = Decimal("0.00")

    # Tableau des rangs Euromillions
    tableau_rangs = {
        (5, 2): 1,  # Jackpot
        (5, 1): 2,
        (5, 0): 3,
        (4, 2): 4,
        (4, 1): 5,
        (3, 2): 6,
        (4, 0): 7,
        (2, 2): 8,
        (3, 1): 9,
        (3, 0): 10,
        (1, 2): 11,
        (2, 1): 12,
        (2, 0): 13,
    }

    combo = (bons_numeros, bonnes_etoiles)
    if combo in tableau_rangs:
        rang = tableau_rangs[combo]
        if rang == 1:
            gain = Decimal(str(tirage.get("jackpot_euros", 17_000_000)))
        else:
            gain = Decimal(str(GAINS_PAR_RANG[rang]))

    return {
        "bons_numeros": bons_numeros,
        "bonnes_etoiles": bonnes_etoiles,
        "rang": rang,
        "gain": gain,
        "gagnant": rang is not None,
        "description": f"{bons_numeros} numéros + {bonnes_etoiles} étoile(s)",
    }


def calculer_esperance_mathematique() -> dict[str, Any]:
    """
    Calcule l'espérance mathématique de l'Euromillions.

    Returns:
        Espérance et probabilités détaillées
    """
    # Probabilités exactes Euromillions
    probas = {
        1: 1 / 139_838_160,  # 5+2★
        2: 1 / 6_991_908,  # 5+1★
        3: 1 / 3_107_515,  # 5+0★
        4: 1 / 621_503,  # 4+2★
        5: 1 / 31_075,  # 4+1★
        6: 1 / 14_125,  # 3+2★
        7: 1 / 13_811,  # 4+0★
        8: 1 / 985,  # 2+2★
        9: 1 / 706,  # 3+1★
        10: 1 / 314,  # 3+0★
        11: 1 / 188,  # 1+2★
        12: 1 / 49,  # 2+1★
        13: 1 / 22,  # 2+0★
    }

    # Jackpot moyen de 40M€
    jackpot_moyen = 40_000_000

    gains_esperes = Decimal("0.00")
    tableau = []

    for rang_num, proba in probas.items():
        gain_rang = jackpot_moyen if rang_num == 1 else GAINS_PAR_RANG[rang_num]
        contribution = Decimal(str(proba)) * Decimal(str(gain_rang))
        gains_esperes += contribution

        tableau.append(
            {
                "rang": rang_num,
                "description": _description_rang(rang_num),
                "probabilite": proba,
                "gain": gain_rang,
                "contribution": float(contribution),
            }
        )

    esperance = gains_esperes - COUT_GRILLE
    perte_pct = float(abs(esperance) / COUT_GRILLE * 100)

    return {
        "esperance": float(esperance),
        "gains_esperes": float(gains_esperes),
        "cout_grille": float(COUT_GRILLE),
        "perte_moyenne_pct": perte_pct,
        "tableau": tableau,
        "conclusion": (
            f"Pour chaque grille à {COUT_GRILLE}€, vous perdez en moyenne "
            f"{abs(float(esperance)):.2f}€ ({perte_pct:.1f}%). "
            f"C'est ~7× pire que le Loto français."
        ),
    }


def _description_rang(rang: int) -> str:
    """Description humaine d'un rang Euromillions"""
    descriptions = {
        1: "5 numéros + 2 étoiles (Jackpot)",
        2: "5 numéros + 1 étoile",
        3: "5 numéros",
        4: "4 numéros + 2 étoiles",
        5: "4 numéros + 1 étoile",
        6: "3 numéros + 2 étoiles",
        7: "4 numéros",
        8: "2 numéros + 2 étoiles",
        9: "3 numéros + 1 étoile",
        10: "3 numéros",
        11: "1 numéro + 2 étoiles",
        12: "2 numéros + 1 étoile",
        13: "2 numéros",
    }
    return descriptions.get(rang, f"Rang {rang}")
