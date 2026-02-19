"""
Fonctions d'équilibre protéique et de variété des recettes.

Détecte le type de protéine, calcule l'équilibre hebdomadaire,
et mesure la variété de la sélection de recettes.
"""

from collections import Counter
from datetime import date, datetime

from src.services.cuisine.suggestions.constantes_suggestions import (
    PROTEINES_POISSON,
    PROTEINES_VEGETARIEN,
    PROTEINES_VIANDE_ROUGE,
    PROTEINES_VOLAILLE,
)


def detect_protein_type(recette: dict) -> str:
    """
    Détecte le type de protéine principal d'une recette.

    Args:
        recette: Dict avec 'type_proteines', 'description', 'nom' ou 'ingredients'

    Returns:
        Type de protéine (poisson, viande_rouge, volaille, vegetarien, autre)
    """
    # Champ explicite
    type_proteines = recette.get("type_proteines", "").lower()
    if type_proteines:
        if any(p in type_proteines for p in PROTEINES_POISSON):
            return "poisson"
        if any(p in type_proteines for p in PROTEINES_VIANDE_ROUGE):
            return "viande_rouge"
        if any(p in type_proteines for p in PROTEINES_VOLAILLE):
            return "volaille"
        if any(p in type_proteines for p in PROTEINES_VEGETARIEN):
            return "vegetarien"

    # Recette explicitement végétarienne
    if recette.get("est_vegetarien"):
        return "vegetarien"

    # Analyse du nom et de la description
    text = f"{recette.get('nom', '')} {recette.get('description', '')}".lower()

    if any(p in text for p in PROTEINES_POISSON):
        return "poisson"
    if any(p in text for p in PROTEINES_VIANDE_ROUGE):
        return "viande_rouge"
    if any(p in text for p in PROTEINES_VOLAILLE):
        return "volaille"

    # Analyse des ingrédients
    ingredients = recette.get("ingredients", [])
    ingredients_text = " ".join(i.lower() if isinstance(i, str) else "" for i in ingredients)

    if any(p in ingredients_text for p in PROTEINES_POISSON):
        return "poisson"
    if any(p in ingredients_text for p in PROTEINES_VIANDE_ROUGE):
        return "viande_rouge"
    if any(p in ingredients_text for p in PROTEINES_VOLAILLE):
        return "volaille"
    if any(p in ingredients_text for p in PROTEINES_VEGETARIEN):
        return "vegetarien"

    return "autre"


def calculate_week_protein_balance(repas: list[dict]) -> dict:
    """
    Calcule l'équilibre protéique sur une semaine.

    Args:
        repas: Liste de repas avec infos recette

    Returns:
        Dict avec comptage par type de protéine
    """
    balance = {
        "poisson": 0,
        "viande_rouge": 0,
        "volaille": 0,
        "vegetarien": 0,
        "autre": 0,
    }

    for r in repas:
        protein_type = detect_protein_type(r)
        balance[protein_type] = balance.get(protein_type, 0) + 1

    return balance


def is_week_balanced(repas: list[dict]) -> tuple[bool, list[str]]:
    """
    Vérifie si une semaine est équilibrée nutritionnellement.

    Recommandations:
    - Au moins 2 repas de poisson
    - Maximum 2 repas de viande rouge
    - Au moins 1 repas végétarien

    Args:
        repas: Liste de repas de la semaine

    Returns:
        Tuple (est_equilibre, liste_problemes)
    """
    balance = calculate_week_protein_balance(repas)
    problemes = []

    if balance["poisson"] < 2:
        problemes.append(f"Pas assez de poisson ({balance['poisson']}/2 minimum)")

    if balance["viande_rouge"] > 2:
        problemes.append(f"Trop de viande rouge ({balance['viande_rouge']}/2 maximum)")

    if balance["vegetarien"] < 1:
        problemes.append("Aucun repas végétarien")

    return len(problemes) == 0, problemes


def calculate_variety_score(
    recettes_selectionnees: list[dict], historique: list[dict], jours_reference: int = 14
) -> float:
    """
    Calcule un score de variété pour une sélection de recettes.

    Args:
        recettes_selectionnees: Recettes proposées
        historique: Historique des préparations
        jours_reference: Période de référence

    Returns:
        Score de variété (0-100)
    """
    if not recettes_selectionnees:
        return 100.0

    # Recettes récentes
    reference_date = date.today()
    recettes_recentes = set()

    for h in historique:
        d = h.get("date") or h.get("date_cuisson")
        if d:
            if isinstance(d, datetime):
                d = d.date()
            elif isinstance(d, str):
                try:
                    d = date.fromisoformat(d[:10])
                except ValueError:
                    continue

            if (reference_date - d).days <= jours_reference:
                recettes_recentes.add(h.get("recette_id"))

    # Compter les répétitions
    repetitions = sum(1 for r in recettes_selectionnees if r.get("id") in recettes_recentes)

    # Score
    ratio_nouveau = (len(recettes_selectionnees) - repetitions) / len(recettes_selectionnees)

    return round(ratio_nouveau * 100, 1)


def get_least_prepared_recipes(
    recettes: list[dict], historique: list[dict], limit: int = 5
) -> list[dict]:
    """
    Retourne les recettes les moins préparées (pour découverte).

    Args:
        recettes: Pool de recettes disponibles
        historique: Historique des préparations
        limit: Nombre de résultats

    Returns:
        Liste des recettes rarement préparées
    """
    preparation_count = Counter(h.get("recette_id") for h in historique)

    scored = []
    for r in recettes:
        rid = r.get("id")
        count = preparation_count.get(rid, 0)
        scored.append((r, count))

    # Trier par nombre de préparations (croissant)
    scored.sort(key=lambda x: x[1])

    return [r for r, _ in scored[:limit]]


__all__ = [
    "detect_protein_type",
    "calculate_week_protein_balance",
    "is_week_balanced",
    "calculate_variety_score",
    "get_least_prepared_recipes",
]
