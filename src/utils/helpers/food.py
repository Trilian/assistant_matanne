"""
Food Helpers - Utilitaires pour la gestion des recettes et de l'inventaire
"""

import re


def convertir_unite(valeur: float, unite_source: str, unite_cible: str) -> float | None:
    """
    Convertit une unité de mesure vers une autre

    Examples:
        >>> convertir_unite(1000, "ml", "L")
        1.0
        >>> convertir_unite(1, "kg", "g")
        1000.0
    """
    conversions = {
        # Volume
        ("ml", "L"): 0.001,
        ("L", "ml"): 1000,
        ("cl", "ml"): 10,
        ("ml", "cl"): 0.1,
        ("cl", "L"): 0.01,
        ("L", "cl"): 100,
        # Poids
        ("g", "kg"): 0.001,
        ("kg", "g"): 1000,
        ("mg", "g"): 0.001,
        ("g", "mg"): 1000,
    }
    key = (
        unite_source.lower(),
        unite_cible.upper() if unite_cible.upper() in ["L"] else unite_cible.lower(),
    )
    if key in conversions:
        return valeur * conversions[key]
    return None


def multiplier_portion(portion_originale: int, portion_cible: int, ingredients: dict) -> dict:
    """
    Multiplie les quantités d'ingrédients pour adapter une recette

    Examples:
        >>> multiplier_portion(4, 8, {"sucre": 200})
        {"sucre": 400}
    """
    if portion_originale <= 0:
        return ingredients
    multiplicateur = portion_cible / portion_originale
    return {ing: qte * multiplicateur for ing, qte in ingredients.items()}


def extraire_ingredient(texte: str) -> dict | None:
    """
    Extrait les infos d'ingrédient depuis un texte

    Examples:
        >>> extraire_ingredient("200g de farine")
        {"quantite": 200, "unite": "g", "nom": "farine"}
    """
    match = re.match(r"(\d+(?:\.\d+)?)\s*(\w+)?\s*(?:de\s+)?(.+)", texte.strip())
    if match:
        return {
            "quantite": float(match.group(1)),
            "unite": match.group(2) or "",
            "nom": match.group(3).strip(),
        }
    return None
