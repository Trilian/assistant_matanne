"""
Agrégation des courses et ingrédients pour le planning.

Contient les fonctions pour:
- Agrégation des quantités d'ingrédients identiques
- Tri par rayon de supermarché
- Organisation de la liste de courses
"""


def aggregate_ingredients(ingredients_list: list[dict]) -> dict[str, dict]:
    """
    Agrège les quantités d'ingrédients identiques.

    Args:
        ingredients_list: Liste de dicts {nom, quantite, unite, rayon}

    Returns:
        Dict {nom: {quantite, unite, rayon, count}}

    Examples:
        >>> ings = [
        ...     {'nom': 'Tomate', 'quantite': 2, 'unite': 'pcs'},
        ...     {'nom': 'Tomate', 'quantite': 3, 'unite': 'pcs'}
        ... ]
        >>> agg = aggregate_ingredients(ings)
        >>> agg['Tomate']['quantite']
        5
    """
    aggregated = {}

    for ing in ingredients_list:
        nom = ing.get("nom", "")
        if not nom:
            continue

        quantite = ing.get("quantite", 1) or 1
        unite = ing.get("unite", "pcs")
        rayon = ing.get("rayon", ing.get("categorie", "autre"))

        if nom not in aggregated:
            aggregated[nom] = {
                "nom": nom,
                "quantite": quantite,
                "unite": unite,
                "rayon": rayon,
                "count": 1,
            }
        else:
            # Même unité: additionner
            if aggregated[nom]["unite"] == unite:
                aggregated[nom]["quantite"] += quantite
            aggregated[nom]["count"] += 1

    return aggregated


def sort_ingredients_by_rayon(ingredients: dict[str, dict] | list[dict]) -> list[dict]:
    """
    Trie les ingrédients par rayon puis par quantité.

    Args:
        ingredients: Dict ou liste d'ingrédients

    Returns:
        Liste triée

    Examples:
        >>> ings = {'Tomate': {'rayon': 'legumes', 'quantite': 5}}
        >>> sorted_ings = sort_ingredients_by_rayon(ings)
        >>> sorted_ings[0]['nom']
        'Tomate'
    """
    if isinstance(ingredients, dict):
        items = list(ingredients.values())
    else:
        items = ingredients

    return sorted(items, key=lambda x: (x.get("rayon", "zzz"), -x.get("quantite", 0)))


def get_rayon_order() -> list[str]:
    """
    Retourne l'ordre des rayons en supermarché.

    Returns:
        Liste ordonnée des rayons
    """
    return [
        "fruits_legumes",
        "legumes",
        "fruits",
        "boucherie",
        "poissonnerie",
        "charcuterie",
        "cremerie",
        "epicerie",
        "conserves",
        "surgeles",
        "boissons",
        "hygiene",
        "autre",
    ]


__all__ = [
    "aggregate_ingredients",
    "sort_ingredients_by_rayon",
    "get_rayon_order",
]
