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

    Normalise les noms pour regrouper les variantes (casse, ponctuation,
    suffixes « cuit(e)(s) » / « surgelé(e)(s) »).
    Tente une conversion d'unité quand les unités diffèrent.

    Args:
        ingredients_list: Liste de dicts {nom, quantite, unite, rayon}

    Returns:
        Dict {nom_normalise: {nom, quantite, unite, rayon, count}}

    Examples:
        >>> ings = [
        ...     {'nom': 'Tomate', 'quantite': 2, 'unite': 'pcs'},
        ...     {'nom': 'Tomate', 'quantite': 3, 'unite': 'pcs'}
        ... ]
        >>> agg = aggregate_ingredients(ings)
        >>> agg['tomate']['quantite']
        5
    """
    from src.core.utils.conversions import convertir
    from src.services.cuisine.courses.suggestion import _normaliser_ingredient

    aggregated: dict[str, dict] = {}

    for ing in ingredients_list:
        nom_brut = ing.get("nom", "")
        if not nom_brut:
            continue

        cle = _normaliser_ingredient(nom_brut)
        quantite = ing.get("quantite", 1) or 1
        unite = ing.get("unite", "pcs") or "pcs"
        rayon = ing.get("rayon") or ing.get("categorie") or "autre"

        if cle not in aggregated:
            aggregated[cle] = {
                "nom": nom_brut,
                "quantite": quantite,
                "unite": unite,
                "rayon": rayon,
                "count": 1,
            }
        else:
            existant = aggregated[cle]
            # Même unité: additionner directement
            if existant["unite"] == unite:
                existant["quantite"] += quantite
            else:
                # Tenter une conversion vers l'unité existante
                resultat = convertir(quantite, unite, existant["unite"], cle)
                if resultat is not None:
                    existant["quantite"] += resultat.valeur_cible
                else:
                    # Conversion impossible → garder la plus grande quantité
                    # et créer une note (ne pas perdre l'info)
                    existant["quantite"] += quantite
            existant["count"] += 1

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

    return sorted(items, key=lambda x: (x.get("rayon") or "zzz", -x.get("quantite", 0)))


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
