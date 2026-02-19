"""Utilitaires de manipulation de périodes (mois, trimestres, plages)."""

from datetime import date, timedelta


def obtenir_bornes_mois(date_ref: date | None = None) -> tuple[date, date]:
    """
    Retourne premier et dernier jour du mois.

    Args:
        date_ref: Date de référence (défaut: aujourd'hui)

    Returns:
        Tuple (premier jour, dernier jour)

    Examples:
        >>> obtenir_bornes_mois(date(2025, 2, 15))
        (date(2025, 2, 1), date(2025, 2, 28))
    """
    if date_ref is None:
        date_ref = date.today()

    first_day = date_ref.replace(day=1)

    # Dernier jour = premier jour mois suivant - 1
    if date_ref.month == 12:
        next_month = first_day.replace(year=date_ref.year + 1, month=1)
    else:
        next_month = first_day.replace(month=date_ref.month + 1)

    last_day = next_month - timedelta(days=1)
    return first_day, last_day


def obtenir_trimestre(date_ref: date | None = None) -> int:
    """
    Retourne le trimestre (1-4).

    Examples:
        >>> obtenir_trimestre(date(2025, 2, 1))
        1
        >>> obtenir_trimestre(date(2025, 7, 1))
        3
    """
    if date_ref is None:
        date_ref = date.today()
    return (date_ref.month - 1) // 3 + 1


def plage_dates(start: date, end: date) -> list[date]:
    """
    Génère liste de dates entre start et end inclus.

    Examples:
        >>> plage_dates(date(2025, 1, 1), date(2025, 1, 3))
        [date(2025, 1, 1), date(2025, 1, 2), date(2025, 1, 3)]
    """
    delta = end - start
    return [start + timedelta(days=i) for i in range(delta.days + 1)]


def ajouter_jours_ouvres(date_ref: date, days: int) -> date:
    """
    Ajoute X jours ouvrés (skip weekends).

    Examples:
        >>> ajouter_jours_ouvres(date(2025, 1, 6), 5)  # Lundi + 5 jours
        date(2025, 1, 13)  # Lundi suivant
    """
    current = date_ref
    added = 0

    while added < days:
        current += timedelta(days=1)
        # 0=Lundi, 6=Dimanche
        if current.weekday() < 5:
            added += 1

    return current
