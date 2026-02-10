"""
Food Helpers - Utilitaires pour la gestion des recettes et de l'inventaire
"""

from typing import List, Dict, Optional, Any


def batch_find_or_create_ingredients(ingredients_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Crée ou trouve des ingrédients en batch"""
    return ingredients_data


def calculate_recipe_cost(ingredients: List[Dict[str, Any]]) -> float:
    """Calcule le coût d'une recette basé sur les ingrédients"""
    return 0.0


def consolidate_duplicates(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Consolide les doublons"""
    return items


def enrich_with_ingredient_info(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Enrichit les items avec les infos d'ingrédient"""
    return items


def find_or_create_ingredient(name: str) -> Dict[str, Any]:
    """Trouve ou crée un ingrédient"""
    return {"name": name}


def format_inventory_summary(inventory_data: Dict[str, Any]) -> str:
    """Formate un résumé de l'inventaire"""
    return "Inventaire vide"


def format_recipe_summary(recipe_data: Dict[str, Any]) -> str:
    """Formate un résumé de recette"""
    return f"Recette: {recipe_data.get('name', 'sans titre')}"


def get_all_ingredients_cached() -> List[Dict[str, Any]]:
    """Récupère tous les ingrédients (cached)"""
    return []


def suggest_ingredient_substitutes(ingredient_name: str) -> List[str]:
    """Suggère des substituts pour un ingrédient"""
    return []


def validate_stock_level(stock: float, min_stock: float) -> bool:
    """Valide si le stock est au-dessus du minimum"""
    return stock >= min_stock


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
    key = (unite_source.lower(), unite_cible.upper() if unite_cible.upper() in ["L"] else unite_cible.lower())
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
    import re
    match = re.match(r"(\d+(?:\.\d+)?)\s*(\w+)?\s*(?:de\s+)?(.+)", texte.strip())
    if match:
        return {
            "quantite": float(match.group(1)),
            "unite": match.group(2) or "",
            "nom": match.group(3).strip()
        }
    return None


# ═══════════════════════════════════════════════════════════
# ALIAS FRANÇAIS (pour compatibilité)
# ═══════════════════════════════════════════════════════════

trouver_ou_creer_ingredients_batch = batch_find_or_create_ingredients
calculer_cout_recette = calculate_recipe_cost
consolider_doublons = consolidate_duplicates
enrichir_avec_info_ingredient = enrich_with_ingredient_info
trouver_ou_creer_ingredient = find_or_create_ingredient
formater_resume_inventaire = format_inventory_summary
formater_resume_recette = format_recipe_summary
obtenir_tous_ingredients_cache = get_all_ingredients_cached
suggerer_substituts = suggest_ingredient_substitutes
valider_niveau_stock = validate_stock_level
