"""
Fonctions de formatage et filtrage des suggestions de recettes.

Formate les suggestions pour l'affichage UI, résume le profil culinaire,
et filtre les recettes selon les contraintes alimentaires.
"""

from src.services.cuisine.suggestions.equilibre import detect_protein_type


def format_suggestion(recette: dict, raison: str = "") -> dict:
    """
    Formate une suggestion de recette pour l'affichage.

    Args:
        recette: Données de la recette
        raison: Raison de la suggestion

    Returns:
        Dict formaté pour l'UI
    """
    temps_total = (recette.get("temps_preparation", 0) or 0) + (
        recette.get("temps_cuisson", 0) or 0
    )

    return {
        "id": recette.get("id"),
        "nom": recette.get("nom", "Sans nom"),
        "raison": raison,
        "score": recette.get("score", 0),
        "temps_total": temps_total,
        "temps_display": f"{temps_total} min" if temps_total > 0 else "Non spécifié",
        "difficulte": recette.get("difficulte", "moyen"),
        "categorie": recette.get("categorie", ""),
        "est_nouvelle": recette.get("est_nouvelle", False),
        "protein_type": detect_protein_type(recette),
    }


def format_profile_summary(profil: dict) -> str:
    """
    Formate un résumé du profil culinaire.

    Args:
        profil: Dict avec les données du profil

    Returns:
        Résumé textuel
    """
    parts = []

    categories = profil.get("categories_preferees", [])
    if categories:
        parts.append(f"Cuisines préférées: {', '.join(categories[:3])}")

    ingredients = profil.get("ingredients_frequents", [])
    if ingredients:
        parts.append(f"Ingrédients favoris: {', '.join(ingredients[:5])}")

    temps = profil.get("temps_moyen_minutes", 0)
    if temps:
        parts.append(f"Temps moyen de préparation: {temps} min")

    nb_favorites = len(profil.get("recettes_favorites", []))
    if nb_favorites:
        parts.append(f"{nb_favorites} recettes favorites")

    return ". ".join(parts) if parts else "Profil en cours de construction"


def filter_by_constraints(recettes: list[dict], contraintes: list[str]) -> list[dict]:
    """
    Filtre les recettes selon les contraintes alimentaires.

    Args:
        recettes: Liste de recettes
        contraintes: Liste de contraintes (vegetarien, sans gluten, etc.)

    Returns:
        Liste filtrée
    """
    if not contraintes:
        return recettes

    contraintes_lower = [c.lower() for c in contraintes]
    filtered = []

    for r in recettes:
        keep = True

        if "vegetarien" in contraintes_lower or "végétarien" in contraintes_lower:
            if not r.get("est_vegetarien", False):
                protein = detect_protein_type(r)
                if protein not in ["vegetarien", "autre"]:
                    keep = False

        if "vegan" in contraintes_lower or "végétalien" in contraintes_lower:
            if not r.get("est_vegan", False):
                keep = False

        if "sans gluten" in contraintes_lower:
            if r.get("contient_gluten", False):
                keep = False

        if "sans lactose" in contraintes_lower:
            if r.get("contient_lactose", False):
                keep = False

        if keep:
            filtered.append(r)

    return filtered


__all__ = [
    "format_suggestion",
    "format_profile_summary",
    "filter_by_constraints",
]
