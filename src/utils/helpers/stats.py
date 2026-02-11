"""
Helpers - Calculs statistiques
"""

import statistics
from typing import Any


def calculer_moyenne(values: list[float]) -> float:
    """
    Calcule moyenne

    Examples:
        >>> calculer_moyenne([1, 2, 3, 4, 5])
        3.0
    """
    return sum(values) / len(values) if values else 0.0


def calculer_mediane(values: list[float]) -> float:
    """
    Calcule médiane

    Examples:
        >>> calculer_mediane([1, 2, 3, 4, 5])
        3.0
    """
    if not values:
        return 0.0

    sorted_values = sorted(values)
    n = len(sorted_values)

    if n % 2 == 0:
        return (sorted_values[n // 2 - 1] + sorted_values[n // 2]) / 2
    else:
        return sorted_values[n // 2]


def calculer_variance(values: list[float]) -> float:
    """
    Calcule variance

    Examples:
        >>> calculer_variance([1, 2, 3, 4, 5])
        2.0
    """
    if not values or len(values) < 2:
        return 0.0

    return statistics.variance(values)


def calculer_ecart_type(values: list[float]) -> float:
    """
    Calcule écart-type

    Examples:
        >>> calculer_ecart_type([1, 2, 3, 4, 5])
        1.4142135623730951
    """
    if not values or len(values) < 2:
        return 0.0

    return statistics.stdev(values)


def calculer_percentile(values: list[float], percentile: int) -> float:
    """
    Calcule un percentile

    Args:
        values: Liste de valeurs
        percentile: 0-100

    Examples:
        >>> calculer_percentile([1, 2, 3, 4, 5], 50)
        3.0
    """
    if not values:
        return 0.0

    sorted_values = sorted(values)
    index = (len(sorted_values) - 1) * percentile / 100

    # Interpolation linéaire
    lower = int(index)
    upper = min(lower + 1, len(sorted_values) - 1)
    weight = index - lower

    return sorted_values[lower] * (1 - weight) + sorted_values[upper] * weight


def calculer_mode(values: list) -> Any:
    """
    Calcule le mode (valeur la plus fréquente)

    Examples:
        >>> calculer_mode([1, 2, 2, 3, 3, 3])
        3
    """
    if not values:
        return None

    try:
        return statistics.mode(values)
    except statistics.StatisticsError:
        # Pas de mode unique
        return None


def calculer_etendue(values: list[float]) -> float:
    """
    Calcule l'étendue (max - min)

    Examples:
        >>> calculer_etendue([1, 2, 3, 4, 5])
        4.0
    """
    if not values:
        return 0.0

    return max(values) - min(values)


def moyenne_mobile(values: list[float], window: int) -> list[float]:
    """
    Calcule moyenne mobile

    Examples:
        >>> moyenne_mobile([1, 2, 3, 4, 5], 3)
        [2.0, 3.0, 4.0]
    """
    if len(values) < window:
        return []

    result = []
    for i in range(len(values) - window + 1):
        window_values = values[i : i + window]
        result.append(sum(window_values) / window)

    return result

