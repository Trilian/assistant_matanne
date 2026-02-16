"""
Génération de grilles Loto - Différentes stratégies

⚠️ DISCLAIMER: Ces stratégies ne modifient PAS vos chances de gagner.
Le Loto reste un jeu de hasard pur.
"""

import logging
import random
from typing import Any

from .frequences import identifier_numeros_chauds_froids

logger = logging.getLogger(__name__)

# Constantes Loto français
NUMERO_MIN = 1
NUMERO_MAX = 49
CHANCE_MIN = 1
CHANCE_MAX = 10
NB_NUMEROS = 5

# Numéros populaires (dates anniversaires, à éviter pour maximiser gains potentiels)
NUMEROS_POPULAIRES = set(range(1, 32))  # 1-31 = dates


def generer_grille_aleatoire() -> dict[str, Any]:
    """
    Génère une grille complètement aléatoire.

    Returns:
        Grille avec 5 numéros + numéro chance
    """
    numeros = sorted(random.sample(range(NUMERO_MIN, NUMERO_MAX + 1), NB_NUMEROS))
    chance = random.randint(CHANCE_MIN, CHANCE_MAX)

    return {"numeros": numeros, "numero_chance": chance, "source": "aleatoire"}


def generer_grille_eviter_populaires() -> dict[str, Any]:
    """
    Génère une grille en évitant les numéros populaires (1-31).

    Stratégie: En cas de gain, partager avec moins de gagnants.

    Returns:
        Grille avec numéros moins populaires
    """
    # Privilégier les numéros 32-49 (moins joués)
    pool_prioritaire = list(range(32, NUMERO_MAX + 1))  # 18 numéros
    pool_secondaire = list(range(NUMERO_MIN, 32))  # 31 numéros

    # Prendre 3-4 numéros du pool prioritaire, 1-2 du secondaire
    nb_prioritaire = random.randint(3, 4)
    nb_secondaire = NB_NUMEROS - nb_prioritaire

    numeros = random.sample(pool_prioritaire, nb_prioritaire) + random.sample(
        pool_secondaire, nb_secondaire
    )
    numeros = sorted(numeros)
    chance = random.randint(CHANCE_MIN, CHANCE_MAX)

    return {
        "numeros": numeros,
        "numero_chance": chance,
        "source": "eviter_populaires",
        "note": "Évite les dates (1-31) pour maximiser gains potentiels",
    }


def generer_grille_equilibree(patterns: dict[str, Any]) -> dict[str, Any]:
    """
    Génère une grille "équilibrée" basée sur les patterns historiques.

    ⚠️ Ceci n'augmente PAS les chances de gagner, mais produit
    une grille statistiquement "typique".

    Args:
        patterns: Résultat de analyser_patterns_tirages()

    Returns:
        Grille équilibrée
    """
    # Viser une somme proche de la moyenne
    somme_cible = patterns.get("somme_moyenne", 125)
    ecart_cible = patterns.get("ecart_moyen", 35)

    # Essayer plusieurs fois pour approcher la cible
    meilleure_grille = None
    meilleur_ecart = float("inf")

    for _ in range(100):
        numeros = sorted(random.sample(range(NUMERO_MIN, NUMERO_MAX + 1), NB_NUMEROS))
        somme = sum(numeros)
        ecart = numeros[-1] - numeros[0]

        # Score = proximité avec les moyennes
        score = abs(somme - somme_cible) + abs(ecart - ecart_cible) * 0.5

        if score < meilleur_ecart:
            meilleur_ecart = score
            meilleure_grille = numeros

    chance = random.randint(CHANCE_MIN, CHANCE_MAX)

    return {
        "numeros": meilleure_grille,
        "numero_chance": chance,
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

    ⚠️ Rappel: Statistiquement inutile, mais psychologiquement satisfaisant.

    Args:
        frequences: Fréquences des numéros
        strategie: "chauds", "froids", ou "mixte"

    Returns:
        Grille basée sur la stratégie
    """
    chauds_froids = identifier_numeros_chauds_froids(frequences)

    if strategie == "chauds":
        pool = chauds_froids["chauds"][:20]
    elif strategie == "froids":
        pool = chauds_froids["froids"][:20]
    else:  # mixte
        pool = chauds_froids["chauds"][:10] + chauds_froids["froids"][:10]

    # Compléter si pas assez
    while len(pool) < NB_NUMEROS:
        pool.append(random.randint(NUMERO_MIN, NUMERO_MAX))
    pool = list(set(pool))

    numeros = sorted(random.sample(pool, min(NB_NUMEROS, len(pool))))

    # Compléter si besoin
    while len(numeros) < NB_NUMEROS:
        n = random.randint(NUMERO_MIN, NUMERO_MAX)
        if n not in numeros:
            numeros.append(n)
    numeros = sorted(numeros[:NB_NUMEROS])

    chance = random.randint(CHANCE_MIN, CHANCE_MAX)

    return {
        "numeros": numeros,
        "numero_chance": chance,
        "source": f"strategie_{strategie}",
        "note": f"Basé sur numéros {strategie}",
    }
