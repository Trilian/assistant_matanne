"""Utilitaires de vérification et noms de jours/mois."""

from datetime import date

from src.core.constants import JOURS_SEMAINE, JOURS_SEMAINE_LOWER


def est_weekend(date_ref: date) -> bool:
    """
    Vérifie si la date est un weekend.

    Examples:
        >>> est_weekend(date(2025, 1, 11))  # Samedi
        True
    """
    return date_ref.weekday() >= 5


def est_aujourd_hui(date_ref: date) -> bool:
    """
    Vérifie si une date est aujourd'hui.

    Examples:
        >>> est_aujourd_hui(date.today())
        True
    """
    return date_ref == date.today()


def obtenir_noms_jours_semaine() -> list[str]:
    """
    Retourne la liste des noms de jours de la semaine.

    Returns:
        Liste des jours en français avec majuscule ['Lundi', ..., 'Dimanche']
    """
    return JOURS_SEMAINE.copy()


# Alias rétrocompatibilité
get_weekday_names = obtenir_noms_jours_semaine


def obtenir_nom_jour_semaine(day_index: int) -> str:
    """
    Retourne le nom du jour pour un index donné.

    Args:
        day_index: Index du jour (0=Lundi, 6=Dimanche)

    Returns:
        Nom du jour ou chaîne vide si invalide
    """
    if 0 <= day_index <= 6:
        return JOURS_SEMAINE[day_index]
    return ""


# Alias rétrocompatibilité
get_weekday_name = obtenir_nom_jour_semaine


def obtenir_index_jour_semaine(day_name: str) -> int:
    """
    Retourne l'index d'un jour de la semaine.

    Args:
        day_name: Nom du jour (insensible à la casse)

    Returns:
        Index (0-6) ou -1 si non trouvé
    """
    try:
        return JOURS_SEMAINE_LOWER.index(day_name.lower())
    except ValueError:
        return -1


# Alias rétrocompatibilité
get_weekday_index = obtenir_index_jour_semaine
