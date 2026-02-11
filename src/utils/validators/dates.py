"""
Validators - Validation dates
"""

from datetime import date


def valider_plage_dates(start: date, end: date, max_days: int | None = None) -> tuple[bool, str]:
    """
    Valide une plage de dates

    Returns:
        (is_valid, error_message)

    Examples:
        >>> valider_plage_dates(date(2025, 1, 1), date(2025, 1, 10))
        (True, "")
    """
    if start > end:
        return False, "La date de début doit être avant la date de fin"

    if max_days:
        delta = (end - start).days
        if delta > max_days:
            return False, f"Plage maximum de {max_days} jours"

    return True, ""


def est_date_future(d: date) -> bool:
    """
    Vérifie si une date est dans le futur

    Examples:
        >>> est_date_future(date(2030, 1, 1))
        True
    """
    return d > date.today()


def est_date_passee(d: date) -> bool:
    """
    Vérifie si une date est dans le passé

    Examples:
        >>> est_date_passee(date(2020, 1, 1))
        True
    """
    return d < date.today()


def valider_date_peremption(expiry: date, min_days_ahead: int = 1) -> tuple[bool, str]:
    """
    Valide une date de péremption

    Args:
        expiry: Date de péremption
        min_days_ahead: Nombre de jours minimum dans le futur

    Returns:
        (is_valid, error_message)
    """
    today = date.today()

    if expiry < today:
        return False, "Date de péremption déjà passée"

    delta = (expiry - today).days

    if delta < min_days_ahead:
        return (
            False,
            f"Date de péremption doit être au moins {min_days_ahead} jour(s) dans le futur",
        )

    return True, ""


def jours_jusqua(target: date) -> int:
    """
    Calcule nombre de jours jusqu'à une date

    Examples:
        >>> jours_jusqua(date.today() + timedelta(days=7))
        7
    """
    return (target - date.today()).days


def est_dans_x_jours(target: date, days: int) -> bool:
    """
    Vérifie si une date est dans X jours

    Examples:
        >>> est_dans_x_jours(date.today() + timedelta(days=3), 7)
        True
    """
    delta = jours_jusqua(target)
    return 0 <= delta <= days

