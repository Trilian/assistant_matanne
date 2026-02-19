"""
Fonctions de scoring et classement des recettes.

Calcule les scores de pertinence des recettes en fonction du contexte,
du profil utilisateur et de l'historique, et génère les raisons de suggestion.
"""

from src.services.cuisine.suggestions.analyse_historique import days_since_last_preparation
from src.services.cuisine.suggestions.constantes_suggestions import (
    SCORE_CATEGORIE_PREFEREE,
    SCORE_DIFFICULTE_ADAPTEE,
    SCORE_INGREDIENT_DISPONIBLE,
    SCORE_INGREDIENT_PRIORITAIRE,
    SCORE_INGREDIENT_SAISON,
    SCORE_JAMAIS_PREPAREE,
    SCORE_TEMPS_ADAPTE,
    SCORE_VARIETE,
)
from src.services.cuisine.suggestions.saisons import get_current_season, is_ingredient_in_season


def calculate_recipe_score(
    recette: dict, contexte: dict, profil: dict | None = None, historique: list[dict] | None = None
) -> float:
    """
    Calcule un score de pertinence pour une recette.

    Args:
        recette: Dict avec infos de la recette (nom, ingredients, categorie, temps_preparation, difficulte)
        contexte: Dict avec (ingredients_disponibles, ingredients_a_utiliser, temps_disponible_minutes, contraintes)
        profil: Dict avec préférences (categories_preferees, difficulte_moyenne, temps_moyen_minutes)
        historique: Historique des préparations

    Returns:
        Score de pertinence (0-100)
    """
    score = 0.0

    # Ingrédients disponibles
    recette_ingredients = recette.get("ingredients", [])
    if isinstance(recette_ingredients, str):
        recette_ingredients = [recette_ingredients]

    ingredients_disponibles = set(i.lower() for i in contexte.get("ingredients_disponibles", []))
    ingredients_prioritaires = set(i.lower() for i in contexte.get("ingredients_a_utiliser", []))

    for ing in recette_ingredients:
        ing_lower = ing.lower() if isinstance(ing, str) else ""
        if ing_lower in ingredients_prioritaires:
            score += SCORE_INGREDIENT_PRIORITAIRE
        elif ing_lower in ingredients_disponibles:
            score += SCORE_INGREDIENT_DISPONIBLE

    # Ingrédient de saison
    saison = contexte.get("saison") or get_current_season()
    for ing in recette_ingredients:
        if is_ingredient_in_season(ing, saison):
            score += SCORE_INGREDIENT_SAISON
            break  # Un seul bonus saison par recette

    # Catégorie préférée
    if profil:
        categories_preferees = profil.get("categories_preferees", [])
        if recette.get("categorie") in categories_preferees:
            score += SCORE_CATEGORIE_PREFEREE

    # Temps adapté
    temps_disponible = contexte.get("temps_disponible_minutes", 60)
    temps_recette = recette.get("temps_preparation", 0) + recette.get("temps_cuisson", 0)

    if temps_recette > 0 and temps_recette <= temps_disponible:
        score += SCORE_TEMPS_ADAPTE
    elif temps_recette > temps_disponible:
        # Pénalité si trop long
        score -= 10

    # Difficulté adaptée
    if profil:
        difficulte_profil = profil.get("difficulte_moyenne", "moyen")
        difficulte_recette = recette.get("difficulte", "moyen")

        if difficulte_recette == difficulte_profil:
            score += SCORE_DIFFICULTE_ADAPTEE

    # Variété (pas préparée récemment)
    if historique:
        jours = days_since_last_preparation(recette.get("id"), historique)
        if jours is None:
            score += SCORE_JAMAIS_PREPAREE
        elif jours >= 14:
            score += SCORE_VARIETE

    # Contraintes alimentaires
    contraintes = contexte.get("contraintes", [])
    if "vegetarien" in contraintes or "végétarien" in contraintes:
        if not recette.get("est_vegetarien", False):
            score -= 50

    if "sans gluten" in contraintes:
        if recette.get("contient_gluten", False):
            score -= 50

    # Normaliser entre 0 et 100
    return max(0.0, min(100.0, score))


def rank_recipes(
    recettes: list[dict],
    contexte: dict,
    profil: dict | None = None,
    historique: list[dict] | None = None,
    limit: int = 5,
) -> list[dict]:
    """
    Classe les recettes par pertinence.

    Args:
        recettes: Liste de recettes à scorer
        contexte: Contexte de suggestion
        profil: Profil culinaire
        historique: Historique des préparations
        limit: Nombre max de résultats

    Returns:
        Liste de recettes avec score, triée par pertinence
    """
    scored = []

    for recette in recettes:
        score = calculate_recipe_score(recette, contexte, profil, historique)
        scored.append(
            {
                **recette,
                "score": score,
            }
        )

    # Trier par score décroissant
    scored.sort(key=lambda r: r["score"], reverse=True)

    return scored[:limit]


def generate_suggestion_reason(recette: dict, contexte: dict) -> str:
    """
    Génère une explication pour la suggestion d'une recette.

    Args:
        recette: Infos de la recette
        contexte: Contexte de suggestion

    Returns:
        Phrase explicative
    """
    raisons = []

    # Ingrédients à utiliser
    ingredients_prioritaires = set(i.lower() for i in contexte.get("ingredients_a_utiliser", []))
    recette_ingredients = recette.get("ingredients", [])

    matching = [ing for ing in recette_ingredients if ing.lower() in ingredients_prioritaires]
    if matching:
        raisons.append(f"Utilise {', '.join(matching[:2])} à consommer rapidement")

    # Saison
    saison = contexte.get("saison") or get_current_season()
    for ing in recette_ingredients:
        if is_ingredient_in_season(ing, saison):
            raisons.append(f"Ingrédient de saison: {ing}")
            break

    # Score
    score = recette.get("score", 0)
    if score >= 80:
        raisons.append("Parfaitement adapté à vos préférences")
    elif score >= 60:
        raisons.append("Correspond à vos habitudes")

    # Jamais préparée
    if recette.get("est_nouvelle"):
        raisons.append("Recette à découvrir")

    if not raisons:
        raisons.append("Suggestion basée sur votre profil")

    return ". ".join(raisons[:2])


__all__ = [
    "calculate_recipe_score",
    "rank_recipes",
    "generate_suggestion_reason",
]
