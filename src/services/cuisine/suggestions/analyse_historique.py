"""
Fonctions d'analyse du profil culinaire et de l'historique.

Analyse les catégories préférées, ingrédients fréquents, difficulté moyenne,
temps moyen, portions et recettes favorites.
"""

from collections import Counter
from datetime import date, datetime


def analyze_categories(historique: list[dict]) -> list[str]:
    """
    Analyse les catégories préférées à partir de l'historique.

    Args:
        historique: Liste de dicts avec clé 'categorie'

    Returns:
        Liste des catégories par ordre de préférence (max 5)

    Examples:
        >>> analyze_categories([{'categorie': 'italien'}, {'categorie': 'italien'}, {'categorie': 'asiatique'}])
        ['italien', 'asiatique']
    """
    categories = [h.get("categorie") for h in historique if h.get("categorie")]
    counter = Counter(categories)
    return [cat for cat, _ in counter.most_common(5)]


def analyze_frequent_ingredients(historique: list[dict]) -> list[str]:
    """
    Identifie les ingrédients fréquemment utilisés.

    Args:
        historique: Liste de dicts avec clé 'ingredients' (liste de noms)

    Returns:
        Liste des ingrédients par fréquence (max 10)
    """
    all_ingredients = []
    for h in historique:
        ingredients = h.get("ingredients", [])
        if isinstance(ingredients, list):
            all_ingredients.extend(ingredients)

    counter = Counter(all_ingredients)
    return [ing for ing, _ in counter.most_common(10)]


def calculate_average_difficulty(historique: list[dict]) -> str:
    """
    Calcule la difficulté moyenne des recettes préparées.

    Args:
        historique: Liste de dicts avec clé 'difficulte'

    Returns:
        Difficulté moyenne (facile, moyen, difficile)
    """
    difficultes = [h.get("difficulte") for h in historique if h.get("difficulte")]

    if not difficultes:
        return "moyen"

    counter = Counter(difficultes)
    return counter.most_common(1)[0][0]


def calculate_average_time(historique: list[dict]) -> int:
    """
    Calcule le temps de préparation moyen.

    Args:
        historique: Liste de dicts avec clé 'temps_preparation' (minutes)

    Returns:
        Temps moyen en minutes
    """
    temps = [h.get("temps_preparation", 0) for h in historique if h.get("temps_preparation")]

    if not temps:
        return 45  # Valeur par défaut

    return int(sum(temps) / len(temps))


def calculate_average_portions(historique: list[dict]) -> int:
    """
    Calcule le nombre de portions moyen.

    Args:
        historique: Liste de dicts avec clé 'portions'

    Returns:
        Nombre de portions moyen
    """
    portions = [h.get("portions", 0) for h in historique if h.get("portions")]

    if not portions:
        return 4  # Valeur par défaut

    return int(sum(portions) / len(portions))


def identify_favorites(historique: list[dict], min_count: int = 3) -> list[int]:
    """
    Identifie les recettes favorites (préparées plusieurs fois).

    Args:
        historique: Liste de dicts avec clé 'recette_id'
        min_count: Nombre minimum de préparations pour être favori

    Returns:
        Liste des IDs de recettes favorites
    """
    recette_ids = [h.get("recette_id") for h in historique if h.get("recette_id")]
    counter = Counter(recette_ids)

    return [rid for rid, count in counter.items() if count >= min_count]


def days_since_last_preparation(
    recette_id: int, historique: list[dict], reference_date: date | None = None
) -> int | None:
    """
    Calcule le nombre de jours depuis la dernière préparation d'une recette.

    Args:
        recette_id: ID de la recette
        historique: Historique avec 'recette_id' et 'date' ou 'date_cuisson'
        reference_date: Date de référence (par défaut: aujourd'hui)

    Returns:
        Nombre de jours, ou None si jamais préparée
    """
    if reference_date is None:
        reference_date = date.today()
    elif isinstance(reference_date, datetime):
        reference_date = reference_date.date()

    dates_preparation = []
    for h in historique:
        if h.get("recette_id") == recette_id:
            d = h.get("date") or h.get("date_cuisson")
            if d:
                if isinstance(d, datetime):
                    d = d.date()
                elif isinstance(d, str):
                    try:
                        d = date.fromisoformat(d[:10])
                    except ValueError:
                        continue
                dates_preparation.append(d)

    if not dates_preparation:
        return None

    derniere = max(dates_preparation)
    return (reference_date - derniere).days


__all__ = [
    "analyze_categories",
    "analyze_frequent_ingredients",
    "calculate_average_difficulty",
    "calculate_average_time",
    "calculate_average_portions",
    "identify_favorites",
    "days_since_last_preparation",
]
