"""
Validation pour le service de planning.

Contient les fonctions de validation pour:
- Dates du planning
- Sélection de recettes
- Cohérence des plannings
"""

from datetime import date


def validate_planning_dates(semaine_debut: date, semaine_fin: date) -> tuple[bool, str]:
    """
    Valide les dates d'un planning.

    Args:
        semaine_debut: Date de début
        semaine_fin: Date de fin

    Returns:
        Tuple (is_valid, error_message)

    Examples:
        >>> validate_planning_dates(date(2024, 1, 15), date(2024, 1, 21))
        (True, '')
    """
    if semaine_fin < semaine_debut:
        return False, "La date de fin doit être après la date de début"

    diff = (semaine_fin - semaine_debut).days
    if diff != 6:
        return False, f"Un planning doit couvrir exactement 7 jours (trouvé: {diff + 1})"

    # Vérifier que c'est un lundi
    if semaine_debut.weekday() != 0:
        return False, "La semaine doit commencer un lundi"

    return True, ""


def validate_meal_selection(
    selection: dict[str, int], available_recipes: list[int]
) -> tuple[bool, list[str]]:
    """
    Valide la sélection de recettes pour un planning.

    Args:
        selection: Dict {jour_index: recette_id}
        available_recipes: Liste des IDs de recettes disponibles

    Returns:
        Tuple (is_valid, list_of_errors)

    Examples:
        >>> validate_meal_selection({'jour_0': 1, 'jour_1': 2}, [1, 2, 3])
        (True, [])
    """
    errors = []

    for jour_key, recette_id in selection.items():
        if recette_id not in available_recipes:
            errors.append(f"Recette {recette_id} non trouvée pour {jour_key}")

    return len(errors) == 0, errors


__all__ = [
    "validate_planning_dates",
    "validate_meal_selection",
]
