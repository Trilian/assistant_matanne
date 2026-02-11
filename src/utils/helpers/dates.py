"""
Helpers - Manipulation de dates
"""

from datetime import date, timedelta


def obtenir_bornes_semaine(d: date) -> tuple[date, date]:
    """
    Retourne (lundi, dimanche) de la semaine

    Examples:
        >>> obtenir_bornes_semaine(date(2025, 1, 8))  # Mercredi
        (date(2025, 1, 6), date(2025, 1, 12))  # Lundi -> Dimanche
    """
    monday = d - timedelta(days=d.weekday())
    sunday = monday + timedelta(days=6)
    return monday, sunday


def plage_dates(start: date, end: date) -> list[date]:
    """
    Génère liste de dates

    Examples:
        >>> plage_dates(date(2025, 1, 1), date(2025, 1, 3))
        [date(2025, 1, 1), date(2025, 1, 2), date(2025, 1, 3)]
    """
    delta = end - start
    return [start + timedelta(days=i) for i in range(delta.days + 1)]


def obtenir_bornes_mois(d: date) -> tuple[date, date]:
    """
    Retourne premier et dernier jour du mois

    Examples:
        >>> obtenir_bornes_mois(date(2025, 2, 15))
        (date(2025, 2, 1), date(2025, 2, 28))
    """
    first_day = d.replace(day=1)

    # Dernier jour = premier jour mois suivant - 1
    if d.month == 12:
        next_month = first_day.replace(year=d.year + 1, month=1)
    else:
        next_month = first_day.replace(month=d.month + 1)

    last_day = next_month - timedelta(days=1)

    return first_day, last_day


def ajouter_jours_ouvres(d: date, days: int) -> date:
    """
    Ajoute X jours ouvrés (skip weekends)

    Examples:
        >>> ajouter_jours_ouvres(date(2025, 1, 6), 5)  # Lundi + 5 jours
        date(2025, 1, 13)  # Lundi suivant
    """
    current = d
    added = 0

    while added < days:
        current += timedelta(days=1)
        # 0=Lundi, 6=Dimanche
        if current.weekday() < 5:
            added += 1

    return current


def semaines_entre(start: date, end: date) -> int:
    """
    Nombre de semaines entre deux dates

    Examples:
        >>> semaines_entre(date(2025, 1, 1), date(2025, 1, 15))
        2
    """
    return (end - start).days // 7


def est_weekend(d: date) -> bool:
    """
    Vérifie si weekend

    Examples:
        >>> est_weekend(date(2025, 1, 11))  # Samedi
        True
    """
    return d.weekday() >= 5


def obtenir_trimestre(d: date) -> int:
    """
    Retourne le trimestre (1-4)

    Examples:
        >>> obtenir_trimestre(date(2025, 2, 1))
        1
        >>> obtenir_trimestre(date(2025, 7, 1))
        3
    """
    return (d.month - 1) // 3 + 1


def est_aujourd_hui(d: date) -> bool:
    """
    Vérifie si une date est aujourd'hui

    Examples:
        >>> from datetime import date
        >>> est_aujourd_hui(date.today())
        True
    """
    return d == date.today()


def obtenir_debut_semaine(d: date) -> date:
    """Retourne le lundi de la semaine"""
    return obtenir_bornes_semaine(d)[0]


def obtenir_fin_semaine(d: date) -> date:
    """Retourne le dimanche de la semaine"""
    return obtenir_bornes_semaine(d)[1]
