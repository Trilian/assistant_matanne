"""Utilitaires de manipulation de semaines."""

from datetime import date, datetime, timedelta


def obtenir_debut_semaine(date_ref: date | datetime | None = None) -> date:
    """
    Retourne le lundi de la semaine contenant la date.

    Args:
        date_ref: Date de référence (défaut: aujourd'hui)

    Returns:
        Date du lundi de la semaine

    Examples:
        >>> obtenir_debut_semaine(date(2024, 1, 18))  # Jeudi
        date(2024, 1, 15)  # Lundi
    """
    if date_ref is None:
        date_ref = date.today()
    if isinstance(date_ref, datetime):
        date_ref = date_ref.date()
    return date_ref - timedelta(days=date_ref.weekday())


def obtenir_fin_semaine(date_ref: date | None = None) -> date:
    """
    Retourne le dimanche de la semaine contenant la date.

    Args:
        date_ref: Date de référence (défaut: aujourd'hui)

    Returns:
        Date du dimanche de la semaine
    """
    return obtenir_debut_semaine(date_ref) + timedelta(days=6)


def obtenir_bornes_semaine(date_ref: date | None = None) -> tuple[date, date]:
    """
    Retourne (lundi, dimanche) de la semaine.

    Args:
        date_ref: Date de référence (défaut: aujourd'hui)

    Returns:
        Tuple (lundi, dimanche)

    Examples:
        >>> obtenir_bornes_semaine(date(2025, 1, 8))  # Mercredi
        (date(2025, 1, 6), date(2025, 1, 12))  # Lundi -> Dimanche
    """
    lundi = obtenir_debut_semaine(date_ref)
    return lundi, lundi + timedelta(days=6)


def obtenir_jours_semaine(date_ref: date | None = None) -> list[date]:
    """
    Retourne les 7 jours de la semaine (lundi à dimanche).

    Args:
        date_ref: Date de référence (défaut: aujourd'hui)

    Returns:
        Liste des 7 dates de la semaine
    """
    lundi = obtenir_debut_semaine(date_ref)
    return [lundi + timedelta(days=i) for i in range(7)]


def obtenir_semaine_precedente(date_ref: date | None = None) -> date:
    """
    Retourne le lundi de la semaine précédente.

    Args:
        date_ref: Date de référence (défaut: aujourd'hui)

    Returns:
        Date du lundi de la semaine précédente
    """
    return obtenir_debut_semaine(date_ref) - timedelta(days=7)


def obtenir_semaine_suivante(date_ref: date | None = None) -> date:
    """
    Retourne le lundi de la semaine suivante.

    Args:
        date_ref: Date de référence (défaut: aujourd'hui)

    Returns:
        Date du lundi de la semaine suivante
    """
    return obtenir_debut_semaine(date_ref) + timedelta(days=7)


def semaines_entre(start: date, end: date) -> int:
    """
    Nombre de semaines complètes entre deux dates.

    Examples:
        >>> semaines_entre(date(2025, 1, 1), date(2025, 1, 15))
        2
    """
    return (end - start).days // 7
