"""
Validators - Validation dates
"""
from datetime import date, datetime, timedelta
from typing import Tuple, Optional


def validate_date_range(
        start: date,
        end: date,
        max_days: Optional[int] = None
) -> Tuple[bool, str]:
    """
    Valide une plage de dates

    Returns:
        (is_valid, error_message)

    Examples:
        >>> validate_date_range(date(2025, 1, 1), date(2025, 1, 10))
        (True, "")
    """
    if start > end:
        return False, "La date de début doit être avant la date de fin"

    if max_days:
        delta = (end - start).days
        if delta > max_days:
            return False, f"Plage maximum de {max_days} jours"

    return True, ""


def is_future_date(d: date) -> bool:
    """
    Vérifie si une date est dans le futur

    Examples:
        >>> is_future_date(date(2030, 1, 1))
        True
    """
    return d > date.today()


def is_past_date(d: date) -> bool:
    """
    Vérifie si une date est dans le passé

    Examples:
        >>> is_past_date(date(2020, 1, 1))
        True
    """
    return d < date.today()


def validate_expiry_date(
        expiry: date,
        min_days_ahead: int = 1
) -> Tuple[bool, str]:
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
        return False, f"Date de péremption doit être au moins {min_days_ahead} jour(s) dans le futur"

    return True, ""


def days_until(target: date) -> int:
    """
    Calcule nombre de jours jusqu'à une date

    Examples:
        >>> days_until(date.today() + timedelta(days=7))
        7
    """
    return (target - date.today()).days


def is_within_days(target: date, days: int) -> bool:
    """
    Vérifie si une date est dans X jours

    Examples:
        >>> is_within_days(date.today() + timedelta(days=3), 7)
        True
    """
    delta = days_until(target)
    return 0 <= delta <= days