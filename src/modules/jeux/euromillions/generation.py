"""
Génération de grilles Euromillions - Différentes stratégies

⚠️ DISCLAIMER: Ces stratégies ne modifient PAS vos chances de gagner.
L'Euromillions reste un jeu de hasard pur.
"""

import logging
import random
from typing import Any

from .frequences import identifier_numeros_chauds_froids

logger = logging.getLogger(__name__)

NUMERO_MIN = 1
NUMERO_MAX = 50
ETOILE_MIN = 1
ETOILE_MAX = 12
NB_NUMEROS = 5
NB_ETOILES = 2
NUMEROS_POPULAIRES = set(range(1, 32))


def generer_grille_aleatoire() -> dict[str, Any]:
    """Génère une grille Euromillions complètement aléatoire."""
    numeros = sorted(random.sample(range(NUMERO_MIN, NUMERO_MAX + 1), NB_NUMEROS))
    etoiles = sorted(random.sample(range(ETOILE_MIN, ETOILE_MAX + 1), NB_ETOILES))
    return {"numeros": numeros, "etoiles": etoiles, "source": "aleatoire"}


def generer_grille_eviter_populaires() -> dict[str, Any]:
    """Génère une grille en évitant les numéros populaires (1-31)."""
    pool_prioritaire = list(range(32, NUMERO_MAX + 1))  # 19 numéros
    pool_secondaire = list(range(NUMERO_MIN, 32))

    nb_prioritaire = random.randint(3, 4)
    nb_secondaire = NB_NUMEROS - nb_prioritaire

    numeros = sorted(
        random.sample(pool_prioritaire, nb_prioritaire)
        + random.sample(pool_secondaire, nb_secondaire)
    )
    etoiles = sorted(random.sample(range(ETOILE_MIN, ETOILE_MAX + 1), NB_ETOILES))

    return {
        "numeros": numeros,
        "etoiles": etoiles,
        "source": "eviter_populaires",
        "note": "Évite les dates (1-31) pour maximiser gains potentiels",
    }


def generer_grille_equilibree(patterns: dict[str, Any]) -> dict[str, Any]:
    """
    Génère une grille statistiquement typique basée sur l'historique.

    ⚠️ N'augmente PAS les chances de gagner.
    """
    somme_cible = patterns.get("somme_moyenne", 130)
    ecart_cible = patterns.get("ecart_moyen", 38)

    meilleure_grille = None
    meilleur_score = float("inf")

    for _ in range(100):
        numeros = sorted(random.sample(range(NUMERO_MIN, NUMERO_MAX + 1), NB_NUMEROS))
        somme = sum(numeros)
        ecart = numeros[-1] - numeros[0]
        score = abs(somme - somme_cible) + abs(ecart - ecart_cible) * 0.5

        if score < meilleur_score:
            meilleur_score = score
            meilleure_grille = numeros

    etoiles = sorted(random.sample(range(ETOILE_MIN, ETOILE_MAX + 1), NB_ETOILES))

    return {
        "numeros": meilleure_grille,
        "etoiles": etoiles,
        "source": "equilibree",
        "somme": sum(meilleure_grille),
        "ecart": meilleure_grille[-1] - meilleure_grille[0],
        "note": f"Somme proche de la moyenne ({somme_cible})",
    }


def generer_grille_chauds_froids(
    frequences: dict[int, dict], strategie: str = "mixte"
) -> dict[str, Any]:
    """
    Génère une grille basée sur les numéros chauds ou froids.

    Args:
        frequences: Fréquences des numéros
        strategie: "chauds", "froids", ou "mixte"
    """
    analyse = identifier_numeros_chauds_froids(frequences, nb_top=15)

    if strategie == "chauds":
        pool = [n for n, _, _ in analyse["chauds"]]
    elif strategie == "froids":
        pool = [n for n, _, _ in analyse["froids"]]
    else:  # mixte
        chauds = [n for n, _, _ in analyse["chauds"][:8]]
        froids = [n for n, _, _ in analyse["froids"][:8]]
        pool = list(set(chauds + froids))

    if len(pool) < NB_NUMEROS:
        pool = list(range(NUMERO_MIN, NUMERO_MAX + 1))

    numeros = sorted(random.sample(pool, NB_NUMEROS))
    etoiles = sorted(random.sample(range(ETOILE_MIN, ETOILE_MAX + 1), NB_ETOILES))

    return {
        "numeros": numeros,
        "etoiles": etoiles,
        "source": f"chauds_froids_{strategie}",
        "strategie": strategie,
        "note": f"Basé sur numéros {strategie}",
    }


def generer_grille_ecart(frequences: dict[int, dict]) -> dict[str, Any]:
    """
    Génère une grille en ciblant les numéros les plus en retard.

    ⚠️ Rappel: Un numéro en retard n'a PAS plus de chances de sortir.
    """
    analyse = identifier_numeros_chauds_froids(frequences, nb_top=15)
    pool = [n for n, _ in analyse["retard"]]

    if len(pool) < NB_NUMEROS:
        pool = list(range(NUMERO_MIN, NUMERO_MAX + 1))

    numeros = sorted(random.sample(pool[:15], NB_NUMEROS))
    etoiles = sorted(random.sample(range(ETOILE_MIN, ETOILE_MAX + 1), NB_ETOILES))

    return {
        "numeros": numeros,
        "etoiles": etoiles,
        "source": "ecart",
        "note": "Basé sur les numéros les plus en retard (⚠️ ne change rien aux probabilités)",
    }
