"""
Formatters - Helpers d'affichage universels
Gère l'affichage propre des quantités, prix, pourcentages
"""
from typing import Union, Optional
import re


def format_quantity(quantity: Union[int, float, None], decimals: int = 2) -> str:
    """
    Formate une quantité en enlevant les décimales inutiles

    Args:
        quantity: Quantité à formater (int, float, ou None)
        decimals: Nombre max de décimales (défaut: 2)

    Returns:
        String formaté proprement

    Examples:
        >>> format_quantity(2.0)
        "2"
        >>> format_quantity(2.5)
        "2.5"
        >>> format_quantity(2.123)
        "2.12"
        >>> format_quantity(0.5)
        "0.5"
        >>> format_quantity(None)
        "0"
    """
    if quantity is None or quantity == 0:
        return "0"

    # Convertir en float et arrondir
    try:
        rounded = round(float(quantity), decimals)
    except (ValueError, TypeError):
        return "0"

    # Si c'est un entier (ex: 2.0), retourner sans décimales
    if rounded == int(rounded):
        return str(int(rounded))

    # Sinon, formater avec décimales puis enlever les zéros trailing
    formatted = f"{rounded:.{decimals}f}"

    # Enlever les zéros inutiles : "2.50" -> "2.5"
    formatted = formatted.rstrip('0').rstrip('.')

    return formatted


def format_quantity_with_unit(
        quantity: Union[int, float, None],
        unit: str,
        decimals: int = 2
) -> str:
    """
    Formate quantité + unité ensemble

    Args:
        quantity: Quantité
        unit: Unité (kg, L, pcs, etc.)
        decimals: Nombre de décimales max

    Returns:
        String formaté "quantité unité"

    Examples:
        >>> format_quantity_with_unit(2.0, "kg")
        "2 kg"
        >>> format_quantity_with_unit(2.5, "L")
        "2.5 L"
        >>> format_quantity_with_unit(None, "g")
        "0 g"
    """
    qty_formatted = format_quantity(quantity, decimals)
    unit_clean = (unit or "").strip()

    return f"{qty_formatted} {unit_clean}" if unit_clean else qty_formatted


def format_price(price: Union[int, float, None], currency: str = "€") -> str:
    """
    Formate un prix proprement

    Args:
        price: Prix à formater
        currency: Symbole monétaire (défaut: €)

    Returns:
        String formaté avec currency

    Examples:
        >>> format_price(10.0)
        "10€"
        >>> format_price(10.50)
        "10.50€"
        >>> format_price(9.99)
        "9.99€"
        >>> format_price(None)
        "0€"
    """
    if price is None:
        return f"0{currency}"

    try:
        rounded = round(float(price), 2)
    except (ValueError, TypeError):
        return f"0{currency}"

    # Si prix entier, pas de décimales
    if rounded == int(rounded):
        return f"{int(rounded)}{currency}"

    # Sinon, toujours 2 décimales pour les prix
    return f"{rounded:.2f}{currency}"


def format_percentage(
        value: Union[int, float, None],
        decimals: int = 1,
        symbol: str = "%"
) -> str:
    """
    Formate un pourcentage

    Args:
        value: Valeur du pourcentage (0-100)
        decimals: Nombre de décimales
        symbol: Symbole (défaut: %)

    Returns:
        String formaté avec %

    Examples:
        >>> format_percentage(85.0)
        "85%"
        >>> format_percentage(85.5)
        "85.5%"
        >>> format_percentage(85.123, decimals=2)
        "85.12%"
    """
    if value is None:
        return f"0{symbol}"

    try:
        rounded = round(float(value), decimals)
    except (ValueError, TypeError):
        return f"0{symbol}"

    # Si entier, pas de décimales
    if rounded == int(rounded):
        return f"{int(rounded)}{symbol}"

    # Sinon, avec décimales (sans zéros trailing)
    formatted = f"{rounded:.{decimals}f}".rstrip('0').rstrip('.')
    return f"{formatted}{symbol}"


def format_time(minutes: Union[int, float, None]) -> str:
    """
    Formate une durée en minutes vers format lisible

    Args:
        minutes: Durée en minutes

    Returns:
        String formaté (ex: "1h30" ou "45min")

    Examples:
        >>> format_time(90)
        "1h30"
        >>> format_time(45)
        "45min"
        >>> format_time(120)
        "2h"
        >>> format_time(None)
        "0min"
    """
    if minutes is None or minutes == 0:
        return "0min"

    try:
        total_minutes = int(minutes)
    except (ValueError, TypeError):
        return "0min"

    if total_minutes < 60:
        return f"{total_minutes}min"

    hours = total_minutes // 60
    remaining_minutes = total_minutes % 60

    if remaining_minutes == 0:
        return f"{hours}h"

    return f"{hours}h{remaining_minutes:02d}"


def format_weight(grams: Union[int, float, None]) -> str:
    """
    Formate un poids en grammes vers kg/g automatique

    Args:
        grams: Poids en grammes

    Returns:
        String formaté avec unité adaptée

    Examples:
        >>> format_weight(500)
        "500 g"
        >>> format_weight(1000)
        "1 kg"
        >>> format_weight(1500)
        "1.5 kg"
        >>> format_weight(2500)
        "2.5 kg"
    """
    if grams is None or grams == 0:
        return "0 g"

    try:
        g = float(grams)
    except (ValueError, TypeError):
        return "0 g"

    # Si >= 1kg, convertir en kg
    if g >= 1000:
        kg = g / 1000
        return format_quantity_with_unit(kg, "kg")

    return format_quantity_with_unit(g, "g")


def format_volume(milliliters: Union[int, float, None]) -> str:
    """
    Formate un volume en mL vers L/mL automatique

    Args:
        milliliters: Volume en millilitres

    Returns:
        String formaté avec unité adaptée

    Examples:
        >>> format_volume(500)
        "500 mL"
        >>> format_volume(1000)
        "1 L"
        >>> format_volume(1500)
        "1.5 L"
    """
    if milliliters is None or milliliters == 0:
        return "0 mL"

    try:
        ml = float(milliliters)
    except (ValueError, TypeError):
        return "0 mL"

    # Si >= 1L, convertir en litres
    if ml >= 1000:
        liters = ml / 1000
        return format_quantity_with_unit(liters, "L")

    return format_quantity_with_unit(ml, "mL")


# ===================================
# HELPERS AVANCÉS
# ===================================

def clean_number_string(text: str) -> Optional[float]:
    """
    Extrait un nombre depuis une string (même sale)

    Examples:
        >>> clean_number_string("2.5 kg")
        2.5
        >>> clean_number_string("Prix: 10,50€")
        10.5
        >>> clean_number_string("abc")
        None
    """
    if not text:
        return None

    # Remplacer virgules par points
    text = str(text).replace(',', '.')

    # Extraire le nombre
    match = re.search(r'-?\d+\.?\d*', text)

    if match:
        try:
            return float(match.group())
        except ValueError:
            return None

    return None


def smart_round(value: Union[int, float], precision: int = 2) -> float:
    """
    Arrondi intelligent (évite les erreurs de float)

    Examples:
        >>> smart_round(2.5000000001)
        2.5
        >>> smart_round(2.99999999)
        3.0
    """
    if value is None:
        return 0.0

    try:
        return round(float(value), precision)
    except (ValueError, TypeError):
        return 0.0