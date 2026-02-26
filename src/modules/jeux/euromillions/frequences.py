"""
Analyse des fréquences Euromillions - Statistiques historiques

⚠️ DISCLAIMER: Les tirages sont parfaitement aléatoires et indépendants.
Ces analyses sont à titre informatif uniquement.
"""

import logging
from collections import Counter
from itertools import combinations
from typing import Any

logger = logging.getLogger(__name__)


def calculer_frequences_numeros(tirages: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Calcule les fréquences de chaque numéro (1-50) et étoile (1-12).

    Args:
        tirages: Liste de tirages Euromillions

    Returns:
        Dict avec frequences_numeros et frequences_etoiles
    """
    if not tirages:
        return {"frequences_numeros": {}, "frequences_etoiles": {}}

    freq_numeros: dict[int, dict[str, Any]] = {}
    freq_etoiles: dict[int, dict[str, Any]] = {}

    nb_tirages = len(tirages)

    # Initialiser
    for n in range(1, 51):
        freq_numeros[n] = {"count": 0, "pct": 0.0, "dernier": None, "ecart": nb_tirages}
    for e in range(1, 13):
        freq_etoiles[e] = {"count": 0, "pct": 0.0, "dernier": None, "ecart": nb_tirages}

    # Compter
    for i, tirage in enumerate(tirages):
        numeros = tirage.get("numeros", [])
        etoiles = tirage.get("etoiles", [])
        date_t = tirage.get("date_tirage")

        for n in numeros:
            if n in freq_numeros:
                freq_numeros[n]["count"] += 1
                if freq_numeros[n]["dernier"] is None:
                    freq_numeros[n]["dernier"] = date_t
                    freq_numeros[n]["ecart"] = i

        for e in etoiles:
            if e in freq_etoiles:
                freq_etoiles[e]["count"] += 1
                if freq_etoiles[e]["dernier"] is None:
                    freq_etoiles[e]["dernier"] = date_t
                    freq_etoiles[e]["ecart"] = i

    # Pourcentages
    for n in freq_numeros:
        freq_numeros[n]["pct"] = round(freq_numeros[n]["count"] / nb_tirages * 100, 2)
    for e in freq_etoiles:
        freq_etoiles[e]["pct"] = round(freq_etoiles[e]["count"] / nb_tirages * 100, 2)

    return {
        "frequences_numeros": freq_numeros,
        "frequences_etoiles": freq_etoiles,
        "nb_tirages": nb_tirages,
    }


def calculer_ecart(tirages: list[dict[str, Any]], numero: int, type_num: str = "numero") -> int:
    """
    Calcule l'écart (nombre de tirages) depuis la dernière apparition.

    Args:
        tirages: Liste triée du plus récent au plus ancien
        numero: Le numéro à chercher
        type_num: "numero" ou "etoile"

    Returns:
        Nombre de tirages depuis dernière apparition
    """
    key = "numeros" if type_num == "numero" else "etoiles"
    for i, tirage in enumerate(tirages):
        if numero in tirage.get(key, []):
            return i
    return len(tirages)


def identifier_numeros_chauds_froids(
    frequences: dict[int, dict], nb_top: int = 10
) -> dict[str, list]:
    """
    Identifie les numéros chauds, froids et en retard.

    Args:
        frequences: Fréquences calculées
        nb_top: Nombre de numéros par catégorie

    Returns:
        Dict avec chauds, froids, retard
    """
    if not frequences:
        return {"chauds": [], "froids": [], "retard": []}

    items = list(frequences.items())
    chauds = sorted(items, key=lambda x: x[1]["count"], reverse=True)[:nb_top]
    froids = sorted(items, key=lambda x: x[1]["count"])[:nb_top]
    retard = sorted(items, key=lambda x: x[1]["ecart"], reverse=True)[:nb_top]

    return {
        "chauds": [(n, d["count"], d["pct"]) for n, d in chauds],
        "froids": [(n, d["count"], d["pct"]) for n, d in froids],
        "retard": [(n, d["ecart"]) for n, d in retard],
    }


def analyser_patterns_tirages(tirages: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Analyse les patterns statistiques des tirages Euromillions.

    Args:
        tirages: Liste de tirages

    Returns:
        Patterns identifiés (somme moyenne, parité, paires fréquentes)
    """
    if not tirages:
        return {}

    sommes = []
    ecarts = []
    pairs_impairs = []
    all_pairs: list[tuple[int, int]] = []

    for tirage in tirages:
        numeros = sorted(tirage.get("numeros", []))
        if len(numeros) >= 5:
            sommes.append(sum(numeros))
            ecarts.append(numeros[-1] - numeros[0])
            nb_pairs = sum(1 for n in numeros if n % 2 == 0)
            pairs_impairs.append(nb_pairs)

            for paire in combinations(numeros, 2):
                all_pairs.append(paire)

    paires_counter = Counter(all_pairs)
    top_paires = paires_counter.most_common(10)

    return {
        "somme_moyenne": round(sum(sommes) / len(sommes), 1) if sommes else 0,
        "ecart_moyen": round(sum(ecarts) / len(ecarts), 1) if ecarts else 0,
        "pairs_moyenne": round(sum(pairs_impairs) / len(pairs_impairs), 1) if pairs_impairs else 0,
        "paires_frequentes": [{"paire": list(p), "count": c} for p, c in top_paires],
        "nb_tirages": len(tirages),
    }
