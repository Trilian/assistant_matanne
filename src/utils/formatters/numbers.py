"""
Formatters - Nombres, quantités, prix, pourcentages
"""
from typing import Union, Optional


def format_quantity(quantity: Union[int, float, None], decimals: int = 2) -> str:
    """
    Formate une quantité en enlevant les décimales inutiles

    Examples:
        >>> format_quantity(2.0)
        "2"
        >>> format_quantity(2.5)
        "2.5"
        >>> format_quantity(2.123)
        "2.12"
    """
    if quantity is None or quantity == 0:
        return "0"

    try:
        rounded = round(float(quantity), decimals)
    except (ValueError, TypeError):
        return "0"

    # Si entier, sans décimales
    if rounded == int(rounded):
        return str(int(rounded))

    # Sinon, avec décimales (sans zéros trailing)
    formatted = f"{rounded:.{decimals}f}"
    formatted = formatted.rstrip("0").rstrip(".")

    return formatted


def format_quantity_with_unit(
        quantity: Union[int, float, None],
        unit: str,
        decimals: int = 2
) -> str:
    """
    Formate quantité + unité

    Examples:
        >>> format_quantity_with_unit(2.5, "kg")
        "2.5 kg"
    """
    qty_formatted = format_quantity(quantity, decimals)
    unit_clean = (unit or "").strip()

    return f"{qty_formatted} {unit_clean}" if unit_clean else qty_formatted


def format_price(price: Union[int, float, None], currency: str = "€") -> str:
    """
    Formate un prix

    Examples:
        >>> format_price(10.0)
        "10€"
        >>> format_price(10.50)
        "10.50€"
    """
    if price is None:
        return f"0{currency}"

    try:
        rounded = round(float(price), 2)
    except (ValueError, TypeError):
        return f"0{currency}"

    # Prix entier sans décimales
    if rounded == int(rounded):
        return f"{int(rounded)}{currency}"

    # Sinon, toujours 2 décimales
    return f"{rounded:.2f}{currency}"


def format_currency(
        amount: Union[int, float, None],
        currency: str = "EUR",
        locale: str = "fr_FR"
) -> str:
    """
    Formate montant avec séparateurs de milliers

    Examples:
        >>> format_currency(1234.56, "EUR")
        "1 234,56 €"
    """
    if amount is None:
        amount = 0

    try:
        amount = float(amount)
    except (ValueError, TypeError):
        amount = 0

    # Format français
    if locale.startswith("fr"):
        formatted = f"{amount:,.2f}".replace(",", " ").replace(".", ",")
        symbols = {"EUR": "€", "USD": "$", "GBP": "£"}
        symbol = symbols.get(currency, currency)
        return f"{formatted} {symbol}"

    # Format anglais
    else:
        formatted = f"{amount:,.2f}"
        symbols = {"EUR": "€", "USD": "$", "GBP": "£"}
        symbol = symbols.get(currency, currency)
        return f"{symbol}{formatted}"


def format_percentage(
        value: Union[int, float, None],
        decimals: int = 1,
        symbol: str = "%"
) -> str:
    """
    Formate un pourcentage

    Examples:
        >>> format_percentage(85.0)
        "85%"
        >>> format_percentage(85.5)
        "85.5%"
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
    formatted = f"{rounded:.{decimals}f}".rstrip("0").rstrip(".")
    return f"{formatted}{symbol}"


def format_number(
        number: Union[int, float, None],
        decimals: int = 0,
        thousands_sep: str = " "
) -> str:
    """
    Formate un nombre avec séparateurs

    Examples:
        >>> format_number(1234567)
        "1 234 567"
        >>> format_number(1234.56, decimals=2)
        "1 234,56"
    """
    if number is None:
        return "0"

    try:
        num = float(number)
    except (ValueError, TypeError):
        return "0"

    if decimals == 0:
        formatted = f"{int(num):,}".replace(",", thousands_sep)
    else:
        formatted = f"{num:,.{decimals}f}".replace(",", thousands_sep).replace(".", ",")

    return formatted


def format_file_size(bytes: Union[int, float, None]) -> str:
    """
    Formate une taille de fichier

    Examples:
        >>> format_file_size(1024)
        "1 Ko"
        >>> format_file_size(1048576)
        "1 Mo"
    """
    if bytes is None or bytes == 0:
        return "0 o"

    try:
        size = float(bytes)
    except (ValueError, TypeError):
        return "0 o"

    units = ["o", "Ko", "Mo", "Go", "To"]
    unit_index = 0

    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1

    return f"{format_quantity(size, 1)} {units[unit_index]}"


def format_range(min_val: float, max_val: float, unit: str = "") -> str:
    """
    Formate une plage de valeurs

    Examples:
        >>> format_range(10, 20, "€")
        "10-20 €"
    """
    min_str = format_quantity(min_val)
    max_str = format_quantity(max_val)

    if unit:
        return f"{min_str}-{max_str} {unit}"
    return f"{min_str}-{max_str}"


def smart_round(value: Union[int, float], precision: int = 2) -> float:
    """
    Arrondi intelligent (évite erreurs de float)

    Examples:
        >>> smart_round(2.5000000001)
        2.5
    """
    if value is None:
        return 0.0

    try:
        return round(float(value), precision)
    except (ValueError, TypeError):
        return 0.0