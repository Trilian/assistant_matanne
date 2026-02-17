"""
Analyse des fréquences Loto - Statistiques historiques

⚠️ DISCLAIMER: Les tirages sont parfaitement aléatoires et indépendants.
Ces analyses sont à titre informatif uniquement.
"""

import logging
from collections import Counter
from typing import Any

logger = logging.getLogger(__name__)

# Constantes Loto français
NUMERO_MIN = 1
NUMERO_MAX = 49
CHANCE_MIN = 1
CHANCE_MAX = 10


def calculer_frequences_numeros(tirages: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Calcule la fréquence d'apparition de chaque numéro.

    Args:
        tirages: Liste des tirages historiques

    Returns:
        Statistiques de fréquence par numéro
    """
    if not tirages:
        return {"frequences": {}, "frequences_chance": {}, "nb_tirages": 0}

    compteur_numeros = Counter()
    compteur_chance = Counter()
    dernier_tirage = {}

    for tirage in tirages:
        date_t = tirage.get("date_tirage")

        # Compter les 5 numéros principaux
        for i in range(1, 6):
            num = tirage.get(f"numero_{i}")
            if num:
                compteur_numeros[num] += 1
                dernier_tirage[num] = date_t

        # Numéro chance
        chance = tirage.get("numero_chance")
        if chance:
            compteur_chance[chance] += 1

    nb_tirages = len(tirages)

    # Calculer stats par numéro
    frequences = {}
    for num in range(NUMERO_MIN, NUMERO_MAX + 1):
        freq = compteur_numeros.get(num, 0)
        frequences[num] = {
            "frequence": freq,
            "pourcentage": round(freq / nb_tirages * 100, 2) if nb_tirages > 0 else 0,
            "dernier_tirage": dernier_tirage.get(num),
            "ecart": calculer_ecart(tirages, num) if tirages else 0,
        }

    frequences_chance = {}
    for num in range(CHANCE_MIN, CHANCE_MAX + 1):
        freq = compteur_chance.get(num, 0)
        frequences_chance[num] = {
            "frequence": freq,
            "pourcentage": round(freq / nb_tirages * 100, 2) if nb_tirages > 0 else 0,
        }

    return {
        "frequences": frequences,
        "frequences_chance": frequences_chance,
        "nb_tirages": nb_tirages,
    }


def calculer_ecart(tirages: list[dict[str, Any]], numero: int) -> int:
    """
    Calcule l'écart (nombre de tirages depuis la dernière apparition).

    Args:
        tirages: Liste des tirages (du plus ancien au plus récent)
        numero: Numéro à analyser

    Returns:
        Nombre de tirages depuis dernière apparition
    """
    for i, tirage in enumerate(reversed(tirages)):
        numeros = [tirage.get(f"numero_{j}") for j in range(1, 6)]
        if numero in numeros:
            return i
    return len(tirages)  # Jamais sorti


def identifier_numeros_chauds_froids(
    frequences: dict[int, dict], nb_top: int = 10
) -> dict[str, list[int]]:
    """
    Identifie les numéros les plus et moins fréquents.

    Args:
        frequences: Dict des fréquences par numéro
        nb_top: Nombre de numéros à retourner par catégorie

    Returns:
        Numéros chauds et froids
    """
    if not frequences:
        return {"chauds": [], "froids": [], "retard": []}

    # Trier par fréquence
    tries_freq = sorted(frequences.items(), key=lambda x: x[1].get("frequence", 0), reverse=True)

    # Trier par écart (retard)
    tries_ecart = sorted(frequences.items(), key=lambda x: x[1].get("ecart", 0), reverse=True)

    return {
        "chauds": [num for num, _ in tries_freq[:nb_top]],
        "froids": [num for num, _ in tries_freq[-nb_top:]],
        "retard": [num for num, _ in tries_ecart[:nb_top]],
    }


def analyser_patterns_tirages(tirages: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Analyse divers patterns dans les tirages historiques.

    Args:
        tirages: Liste des tirages

    Returns:
        Statistiques sur les patterns
    """
    if not tirages:
        return {}

    sommes = []
    nb_pairs = []
    nb_impairs = []
    ecarts_min_max = []
    paires_frequentes = Counter()

    for tirage in tirages:
        numeros = sorted([tirage.get(f"numero_{i}") for i in range(1, 6)])
        numeros = [n for n in numeros if n]  # Filtrer None

        if len(numeros) != 5:
            continue

        # Somme
        sommes.append(sum(numeros))

        # Parité
        pairs = sum(1 for n in numeros if n % 2 == 0)
        nb_pairs.append(pairs)
        nb_impairs.append(5 - pairs)

        # Écart min-max
        ecarts_min_max.append(numeros[-1] - numeros[0])

        # Paires fréquentes
        for i in range(len(numeros)):
            for j in range(i + 1, len(numeros)):
                paires_frequentes[(numeros[i], numeros[j])] += 1

    if not sommes:
        return {}

    # Top 10 paires les plus fréquentes
    top_paires = paires_frequentes.most_common(10)

    return {
        "somme_moyenne": round(sum(sommes) / len(sommes), 1),
        "somme_min": min(sommes),
        "somme_max": max(sommes),
        "pairs_moyen": round(sum(nb_pairs) / len(nb_pairs), 1),
        "ecart_moyen": round(sum(ecarts_min_max) / len(ecarts_min_max), 1),
        "paires_frequentes": [
            {"paire": list(paire), "frequence": freq} for paire, freq in top_paires
        ],
        "distribution_parite": {f"{i}_pair_{5-i}_impair": nb_pairs.count(i) for i in range(6)},
    }
