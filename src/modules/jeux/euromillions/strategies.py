"""
Simulation et backtesting de stratégies Euromillions

⚠️ DISCLAIMER: Aucune stratégie n'améliore vos chances. L'EuroMillions est un jeu de hasard pur.
"""

import logging
from decimal import Decimal
from typing import Any

from .calculs import COUT_GRILLE, verifier_grille
from .frequences import analyser_patterns_tirages, calculer_frequences_numeros
from .generation import (
    generer_grille_aleatoire,
    generer_grille_chauds_froids,
    generer_grille_ecart,
    generer_grille_equilibree,
    generer_grille_eviter_populaires,
)

logger = logging.getLogger(__name__)


def simuler_strategie(
    tirages: list[dict[str, Any]],
    strategie: str = "aleatoire",
    nb_grilles_par_tirage: int = 1,
) -> dict[str, Any]:
    """
    Simule une stratégie sur les tirages historiques.

    Args:
        tirages: Tirages historiques (du plus ancien au plus récent)
        strategie: Nom de la stratégie
        nb_grilles_par_tirage: Grilles jouées par tirage

    Returns:
        Résultats de simulation
    """
    if len(tirages) < 10:
        return {"erreur": "Pas assez de tirages (minimum 10)"}

    patterns = analyser_patterns_tirages(tirages[:50])
    frequences_data = calculer_frequences_numeros(tirages[:50])
    freq_numeros = frequences_data.get("frequences_numeros", {})

    total_mise = Decimal("0.00")
    total_gains = Decimal("0.00")
    distribution_rangs: dict[int, int] = {}
    nb_gagnants = 0

    for i in range(50, len(tirages)):
        tirage = tirages[i]

        for _ in range(nb_grilles_par_tirage):
            grille = _generer_par_strategie(strategie, patterns, freq_numeros)
            resultat = verifier_grille(grille, tirage)

            total_mise += COUT_GRILLE
            total_gains += resultat["gain"]

            if resultat["gagnant"]:
                nb_gagnants += 1
                rang = resultat["rang"]
                distribution_rangs[rang] = distribution_rangs.get(rang, 0) + 1

    profit = total_gains - total_mise
    roi = float(profit / total_mise * 100) if total_mise > 0 else 0.0
    nb_total = (len(tirages) - 50) * nb_grilles_par_tirage
    taux_gain = nb_gagnants / nb_total * 100 if nb_total > 0 else 0.0

    return {
        "strategie": strategie,
        "nb_grilles": nb_total,
        "mise_totale": float(total_mise),
        "gains_totaux": float(total_gains),
        "profit": float(profit),
        "roi": roi,
        "nb_gagnants": nb_gagnants,
        "taux_gain": taux_gain,
        "distribution_rangs": distribution_rangs,
    }


def comparer_strategies(tirages: list[dict[str, Any]], nb_grilles: int = 1) -> list[dict[str, Any]]:
    """Compare toutes les stratégies sur le même historique."""
    strategies = ["aleatoire", "eviter_populaires", "equilibree", "chauds", "froids", "ecart"]
    resultats = []

    for strat in strategies:
        res = simuler_strategie(tirages, strat, nb_grilles)
        resultats.append(res)

    return sorted(resultats, key=lambda r: r.get("roi", 0), reverse=True)


def _generer_par_strategie(
    strategie: str,
    patterns: dict[str, Any],
    frequences: dict[int, dict],
) -> dict[str, Any]:
    """Génère une grille selon la stratégie choisie."""
    if strategie == "eviter_populaires":
        return generer_grille_eviter_populaires()
    elif strategie == "equilibree":
        return generer_grille_equilibree(patterns)
    elif strategie == "chauds":
        return generer_grille_chauds_froids(frequences, "chauds")
    elif strategie == "froids":
        return generer_grille_chauds_froids(frequences, "froids")
    elif strategie == "ecart":
        return generer_grille_ecart(frequences)
    else:
        return generer_grille_aleatoire()
