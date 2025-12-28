"""
Formatters - Formatage Universel Amélioré
Gestion du formatage de quantités, prix, dates, pourcentages, etc.
"""
from typing import Union, Optional
from datetime import date, datetime, timedelta
import re


# ═══════════════════════════════════════════════════════════════
# QUANTITÉS
# ═══════════════════════════════════════════════════════════════

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
    formatted = formatted.rstrip("0").rstrip(".")

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


# ═══════════════════════════════════════════════════════════════
# PRIX & MONNAIE
# ═══════════════════════════════════════════════════════════════

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


def format_currency(
        amount: Union[int, float, None],
        currency: str = "EUR",
        locale: str = "fr_FR"
) -> str:
    """
    Formate une somme avec séparateurs de milliers

    Args:
        amount: Montant
        currency: Code devise (EUR, USD, etc.)
        locale: Locale (fr_FR, en_US)

    Returns:
        String formaté

    Examples:
        >>> format_currency(1234.56, "EUR")
        "1 234,56 €"
        >>> format_currency(1000000, "USD", "en_US")
        "1,000,000.00 $"
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


# ═══════════════════════════════════════════════════════════════
# POURCENTAGES
# ═══════════════════════════════════════════════════════════════

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
    formatted = f"{rounded:.{decimals}f}".rstrip("0").rstrip(".")
    return f"{formatted}{symbol}"


# ═══════════════════════════════════════════════════════════════
# TEMPS & DURÉES
# ═══════════════════════════════════════════════════════════════

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


def format_duration(seconds: Union[int, float, None], short: bool = False) -> str:
    """
    Formate une durée en secondes

    Args:
        seconds: Durée en secondes
        short: Format court (1h 30m) ou long (1 heure 30 minutes)

    Returns:
        String formaté

    Examples:
        >>> format_duration(3665)
        "1h 1min 5s"
        >>> format_duration(3665, short=False)
        "1 heure 1 minute 5 secondes"
    """
    if seconds is None or seconds == 0:
        return "0s" if short else "0 seconde"

    try:
        sec = int(seconds)
    except (ValueError, TypeError):
        return "0s"

    hours = sec // 3600
    minutes = (sec % 3600) // 60
    remaining_seconds = sec % 60

    parts = []

    if short:
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}min")
        if remaining_seconds > 0:
            parts.append(f"{remaining_seconds}s")
    else:
        if hours > 0:
            parts.append(f"{hours} heure" + ("s" if hours > 1 else ""))
        if minutes > 0:
            parts.append(f"{minutes} minute" + ("s" if minutes > 1 else ""))
        if remaining_seconds > 0:
            parts.append(f"{remaining_seconds} seconde" + ("s" if remaining_seconds > 1 else ""))

    return " ".join(parts) if parts else ("0s" if short else "0 seconde")


# ═══════════════════════════════════════════════════════════════
# DATES
# ═══════════════════════════════════════════════════════════════

def format_date(
        d: Union[date, datetime, None],
        format: str = "short",
        locale: str = "fr"
) -> str:
    """
    Formate une date

    Args:
        d: Date à formater
        format: "short" (01/12), "medium" (01/12/2025), "long" (1 décembre 2025)
        locale: Locale (fr, en)

    Returns:
        String formaté

    Examples:
        >>> format_date(date(2025, 12, 1), "short")
        "01/12"
        >>> format_date(date(2025, 12, 1), "long")
        "1 décembre 2025"
    """
    if d is None:
        return "—"

    if isinstance(d, datetime):
        d = d.date()

    if format == "short":
        return d.strftime("%d/%m")
    elif format == "medium":
        return d.strftime("%d/%m/%Y")
    elif format == "long":
        if locale == "fr":
            months = [
                "janvier", "février", "mars", "avril", "mai", "juin",
                "juillet", "août", "septembre", "octobre", "novembre", "décembre"
            ]
            return f"{d.day} {months[d.month - 1]} {d.year}"
        else:
            return d.strftime("%B %d, %Y")
    else:
        return d.strftime("%d/%m/%Y")


def format_datetime(
        dt: Union[datetime, None],
        format: str = "medium",
        locale: str = "fr"
) -> str:
    """
    Formate une date/heure

    Args:
        dt: Datetime à formater
        format: "short" (01/12 14:30), "medium" (01/12/2025 14:30), "long"
        locale: Locale

    Returns:
        String formaté
    """
    if dt is None:
        return "—"

    if format == "short":
        return dt.strftime("%d/%m %H:%M")
    elif format == "medium":
        return dt.strftime("%d/%m/%Y %H:%M")
    elif format == "long":
        date_part = format_date(dt.date(), "long", locale)
        time_part = dt.strftime("%H:%M")
        return f"{date_part} à {time_part}"
    else:
        return dt.strftime("%d/%m/%Y %H:%M")


def format_relative_date(d: Union[date, datetime]) -> str:
    """
    Formate une date relativement (hier, aujourd'hui, demain)

    Args:
        d: Date

    Returns:
        String relatif

    Examples:
        >>> format_relative_date(date.today())
        "Aujourd'hui"
        >>> format_relative_date(date.today() - timedelta(days=1))
        "Hier"
    """
    if isinstance(d, datetime):
        d = d.date()

    today = date.today()
    delta = (d - today).days

    if delta == 0:
        return "Aujourd'hui"
    elif delta == 1:
        return "Demain"
    elif delta == -1:
        return "Hier"
    elif 2 <= delta <= 7:
        return f"Dans {delta} jours"
    elif -7 <= delta <= -2:
        return f"Il y a {abs(delta)} jours"
    else:
        return format_date(d, "medium")


# ═══════════════════════════════════════════════════════════════
# NOMBRES
# ═══════════════════════════════════════════════════════════════

def format_number(
        number: Union[int, float, None],
        decimals: int = 0,
        thousands_sep: str = " "
) -> str:
    """
    Formate un nombre avec séparateurs

    Args:
        number: Nombre
        decimals: Décimales
        thousands_sep: Séparateur de milliers

    Returns:
        String formaté

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

    Args:
        bytes: Taille en bytes

    Returns:
        String formaté (Ko, Mo, Go)

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


# ═══════════════════════════════════════════════════════════════
# HELPERS AVANCÉS
# ═══════════════════════════════════════════════════════════════

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
    text = str(text).replace(",", ".")

    # Extraire le nombre
    match = re.search(r"-?\d+\.?\d*", text)

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


def format_range(min_val: float, max_val: float, unit: str = "") -> str:
    """
    Formate une plage de valeurs

    Args:
        min_val: Valeur min
        max_val: Valeur max
        unit: Unité

    Returns:
        String formaté

    Examples:
        >>> format_range(10, 20, "€")
        "10-20 €"
        >>> format_range(1.5, 2.5, "kg")
        "1.5-2.5 kg"
    """
    min_str = format_quantity(min_val)
    max_str = format_quantity(max_val)

    if unit:
        return f"{min_str}-{max_str} {unit}"
    return f"{min_str}-{max_str}"