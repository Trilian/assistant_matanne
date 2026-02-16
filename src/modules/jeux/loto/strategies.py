"""
Simulation de stratégies Loto - Backtesting et comparaisons

⚠️ DISCLAIMER: Ces simulations démontrent qu'aucune stratégie
ne bat le hasard à long terme.
"""

import logging
from collections import Counter
from decimal import Decimal
from typing import Any

from .calculs import COUT_GRILLE, verifier_grille
from .frequences import analyser_patterns_tirages, calculer_frequences_numeros
from .generation import (
    generer_grille_aleatoire,
    generer_grille_chauds_froids,
    generer_grille_equilibree,
    generer_grille_eviter_populaires,
)

logger = logging.getLogger(__name__)


def simuler_strategie(
    tirages: list[dict[str, Any]],
    strategie: str = "aleatoire",
    nb_grilles_par_tirage: int = 1,
    frequences: dict | None = None,
    patterns: dict | None = None,
) -> dict[str, Any]:
    """
    Simule une stratégie sur l'historique des tirages.

    Args:
        tirages: Historique des tirages
        strategie: "aleatoire", "eviter_populaires", "equilibree", "chauds", "froids"
        nb_grilles_par_tirage: Nombre de grilles jouées par tirage
        frequences: Fréquences pré-calculées
        patterns: Patterns pré-calculés

    Returns:
        Résultats de la simulation
    """
    if not tirages:
        return {"erreur": "Aucun tirage disponible"}

    resultats = []
    mises_totales = Decimal("0.00")
    gains_totaux = Decimal("0.00")

    for tirage in tirages:
        for _ in range(nb_grilles_par_tirage):
            # Générer grille selon stratégie
            if strategie == "aleatoire":
                grille = generer_grille_aleatoire()
            elif strategie == "eviter_populaires":
                grille = generer_grille_eviter_populaires()
            elif strategie == "equilibree" and patterns:
                grille = generer_grille_equilibree(patterns)
            elif strategie in ["chauds", "froids", "mixte"] and frequences:
                grille = generer_grille_chauds_froids(frequences, strategie)
            else:
                grille = generer_grille_aleatoire()

            # Vérifier contre le tirage
            resultat = verifier_grille(grille, tirage)

            mises_totales += COUT_GRILLE
            gains_totaux += resultat.get("gain", Decimal("0.00"))

            resultats.append(
                {"date": tirage.get("date_tirage"), "grille": grille, "resultat": resultat}
            )

    # Statistiques
    nb_gagnants = sum(1 for r in resultats if r["resultat"]["gagnant"])
    rangs = Counter(r["resultat"]["rang"] for r in resultats if r["resultat"]["rang"])

    return {
        "strategie": strategie,
        "nb_tirages": len(tirages),
        "nb_grilles": len(resultats),
        "mises_totales": mises_totales,
        "gains_totaux": gains_totaux,
        "profit": gains_totaux - mises_totales,
        "roi": (
            float((gains_totaux - mises_totales) / mises_totales * 100)
            if mises_totales > 0
            else 0
        ),
        "nb_gagnants": nb_gagnants,
        "taux_gain": round(nb_gagnants / len(resultats) * 100, 2) if resultats else 0,
        "distribution_rangs": dict(rangs),
        "details": resultats[-10:],  # 10 derniers pour affichage
    }


def comparer_strategies(
    tirages: list[dict[str, Any]], nb_simulations: int = 100
) -> dict[str, Any]:
    """
    Compare plusieurs stratégies sur les mêmes tirages.

    Args:
        tirages: Historique des tirages
        nb_simulations: Nombre de simulations par stratégie

    Returns:
        Comparaison des performances
    """
    if not tirages:
        return {"erreur": "Aucun tirage"}

    # Pré-calculer stats
    freq_data = calculer_frequences_numeros(tirages)
    patterns = analyser_patterns_tirages(tirages)

    strategies = ["aleatoire", "eviter_populaires", "equilibree", "chauds", "froids"]
    resultats = {}

    for strat in strategies:
        res = simuler_strategie(
            tirages,
            strategie=strat,
            nb_grilles_par_tirage=1,
            frequences=freq_data.get("frequences"),
            patterns=patterns,
        )
        resultats[strat] = {
            "roi": res.get("roi", 0),
            "taux_gain": res.get("taux_gain", 0),
            "nb_gagnants": res.get("nb_gagnants", 0),
        }

    # Classement par ROI
    classement = sorted(resultats.items(), key=lambda x: x[1]["roi"], reverse=True)

    return {
        "nb_tirages": len(tirages),
        "resultats": resultats,
        "classement": [s[0] for s in classement],
        "meilleure_strategie": classement[0][0] if classement else None,
        "note": "⚠️ Ces résultats varient aléatoirement. Aucune stratégie n'est meilleure à long terme.",
    }
