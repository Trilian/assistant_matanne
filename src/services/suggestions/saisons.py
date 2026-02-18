"""
Fonctions de gestion des saisons et ingrédients saisonniers.

Détermine la saison courante et vérifie la saisonnalité des ingrédients.
"""

from datetime import date, datetime

from src.services.suggestions.constantes_suggestions import INGREDIENTS_SAISON, SAISONS


def get_current_season(dt: date | datetime | None = None) -> str:
    """
    Détermine la saison pour une date donnée.

    Args:
        dt: Date (par défaut: aujourd'hui)

    Returns:
        Nom de la saison (printemps, été, automne, hiver)

    Examples:
        >>> get_current_season(date(2024, 7, 15))
        'été'
        >>> get_current_season(date(2024, 12, 25))
        'hiver'
    """
    if dt is None:
        dt = date.today()
    elif isinstance(dt, datetime):
        dt = dt.date()

    month = dt.month

    for saison, mois in SAISONS.items():
        if month in mois:
            return saison

    return "hiver"  # Fallback


def get_seasonal_ingredients(saison: str | None = None) -> list[str]:
    """
    Retourne les ingrédients de saison.

    Args:
        saison: Nom de la saison (calcule automatiquement si None)

    Returns:
        Liste des ingrédients de saison

    Examples:
        >>> get_seasonal_ingredients("été")
        ['tomate', 'courgette', ...]
    """
    if saison is None:
        saison = get_current_season()

    saison = saison.lower().replace("é", "e").replace("è", "e")

    # Normaliser les noms
    if saison == "ete":
        saison = "été"

    return INGREDIENTS_SAISON.get(saison, [])


def is_ingredient_in_season(ingredient: str, saison: str | None = None) -> bool:
    """
    Vérifie si un ingrédient est de saison.

    Args:
        ingredient: Nom de l'ingrédient
        saison: Saison (calcule automatiquement si None)

    Returns:
        True si l'ingrédient est de saison
    """
    ingredients_saison = get_seasonal_ingredients(saison)
    ingredient_lower = ingredient.lower()

    return any(ing in ingredient_lower or ingredient_lower in ing for ing in ingredients_saison)


__all__ = [
    "get_current_season",
    "get_seasonal_ingredients",
    "is_ingredient_in_season",
]
