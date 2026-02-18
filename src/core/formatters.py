"""
Formatters centralisés - Dates, nombres, texte, unités.

Ce module consolide les fonctions de formatage précédemment dans:
- utils/formatters/dates.py
- utils/formatters/numbers.py
- utils/formatters/text.py
- utils/formatters/units.py

Usage:
    from src.core.formatters import formater_date, formater_prix, formater_temps
"""

import re
from datetime import date, datetime

# ═══════════════════════════════════════════════════════════
# DATES ET DURÉES
# ═══════════════════════════════════════════════════════════


def formater_date(d: date | datetime | None, format: str = "short", locale: str = "fr") -> str:
    """
    Formate une date.

    Args:
        d: Date à formater
        format: "short" (01/12), "medium" (01/12/2025), "long" (1 décembre 2025)
        locale: "fr" ou "en"

    Examples:
        >>> formater_date(date(2025, 12, 1), "short")
        "01/12"
        >>> formater_date(date(2025, 12, 1), "long")
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
                "janvier",
                "février",
                "mars",
                "avril",
                "mai",
                "juin",
                "juillet",
                "août",
                "septembre",
                "octobre",
                "novembre",
                "décembre",
            ]
            return f"{d.day} {months[d.month - 1]} {d.year}"
        else:
            return d.strftime("%B %d, %Y")
    else:
        return d.strftime("%d/%m/%Y")


def formater_datetime(dt: datetime | None, format: str = "medium", locale: str = "fr") -> str:
    """
    Formate une date/heure.

    Args:
        dt: Datetime à formater
        format: "short" (01/12 14:30), "medium" (01/12/2025 14:30), "long"
        locale: Locale

    Examples:
        >>> formater_datetime(datetime(2025, 12, 1, 14, 30), "medium")
        "01/12/2025 14:30"
    """
    if dt is None:
        return "—"

    if format == "short":
        return dt.strftime("%d/%m %H:%M")
    elif format == "medium":
        return dt.strftime("%d/%m/%Y %H:%M")
    elif format == "long":
        date_part = formater_date(dt.date(), "long", locale)
        time_part = dt.strftime("%H:%M")
        return f"{date_part} à {time_part}"
    else:
        return dt.strftime("%d/%m/%Y %H:%M")


def temps_ecoule(d: date | datetime) -> str:
    """
    Formate une date relativement (hier, aujourd'hui, demain).

    Examples:
        >>> temps_ecoule(date.today())
        "Aujourd'hui"
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
        return formater_date(d, "medium")


def formater_temps(minutes: int | float | None, avec_espace: bool = False) -> str:
    """
    Formate une durée en minutes vers format lisible.

    Args:
        minutes: Durée en minutes
        avec_espace: Ajoute un espace entre le nombre et l'unité

    Examples:
        >>> formater_temps(90)
        "1h30"
        >>> formater_temps(45, avec_espace=True)
        "45 min"
    """
    if minutes is None or minutes == 0:
        return "0 min" if avec_espace else "0min"

    try:
        total_minutes = int(minutes)
    except (ValueError, TypeError):
        return "0 min" if avec_espace else "0min"

    if total_minutes < 60:
        return f"{total_minutes} min" if avec_espace else f"{total_minutes}min"

    hours = total_minutes // 60
    remaining_minutes = total_minutes % 60

    if remaining_minutes == 0:
        return f"{hours}h"

    return f"{hours}h{remaining_minutes:02d}"


def formater_duree(seconds: int | float | None, short: bool = True) -> str:
    """
    Formate une durée en secondes.

    Examples:
        >>> formater_duree(3665)
        "1h 1min 5s"
        >>> formater_duree(3665, short=False)
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


# ═══════════════════════════════════════════════════════════
# NOMBRES ET PRIX
# ═══════════════════════════════════════════════════════════


def formater_quantite(quantity: int | float | None, decimals: int = 2) -> str:
    """
    Formate une quantité en enlevant les décimales inutiles.

    Examples:
        >>> formater_quantite(2.0)
        "2"
        >>> formater_quantite(2.5)
        "2.5"
    """
    if quantity is None or quantity == 0:
        return "0"

    try:
        rounded = round(float(quantity), decimals)
    except (ValueError, TypeError):
        return "0"

    if rounded == int(rounded):
        return str(int(rounded))

    formatted = f"{rounded:.{decimals}f}"
    formatted = formatted.rstrip("0").rstrip(".")

    return formatted


def formater_quantite_unite(quantity: int | float | None, unit: str, decimals: int = 2) -> str:
    """
    Formate quantité + unité.

    Examples:
        >>> formater_quantite_unite(2.5, "kg")
        "2.5 kg"
    """
    qty_formatted = formater_quantite(quantity, decimals)
    unit_clean = (unit or "").strip()

    return f"{qty_formatted} {unit_clean}" if unit_clean else qty_formatted


def formater_prix(price: int | float | None, currency: str = "€") -> str:
    """
    Formate un prix.

    Examples:
        >>> formater_prix(10.0)
        "10€"
        >>> formater_prix(10.50)
        "10.50€"
    """
    if price is None:
        return f"0{currency}"

    try:
        rounded = round(float(price), 2)
    except (ValueError, TypeError):
        return f"0{currency}"

    if rounded == int(rounded):
        return f"{int(rounded)}{currency}"

    return f"{rounded:.2f}{currency}"


def formater_monnaie(
    amount: int | float | None, currency: str = "EUR", locale: str = "fr_FR"
) -> str:
    """
    Formate montant avec séparateurs de milliers.

    Examples:
        >>> formater_monnaie(1234.56, "EUR")
        "1 234,56 €"
    """
    if amount is None:
        amount = 0

    try:
        amount = float(amount)
    except (ValueError, TypeError):
        amount = 0

    symbols = {"EUR": "€", "USD": "$", "GBP": "£"}
    symbol = symbols.get(currency, currency)

    if locale.startswith("fr"):
        formatted = f"{amount:,.2f}".replace(",", " ").replace(".", ",")
        return f"{formatted} {symbol}"
    else:
        formatted = f"{amount:,.2f}"
        return f"{symbol}{formatted}"


def formater_pourcentage(value: int | float | None, decimals: int = 1, symbol: str = "%") -> str:
    """
    Formate un pourcentage.

    Examples:
        >>> formater_pourcentage(85.0)
        "85%"
        >>> formater_pourcentage(85.5)
        "85.5%"
    """
    if value is None:
        return f"0{symbol}"

    try:
        rounded = round(float(value), decimals)
    except (ValueError, TypeError):
        return f"0{symbol}"

    if rounded == int(rounded):
        return f"{int(rounded)}{symbol}"

    formatted = f"{rounded:.{decimals}f}".rstrip("0").rstrip(".")
    return f"{formatted}{symbol}"


def formater_nombre(number: int | float | None, decimals: int = 0, thousands_sep: str = " ") -> str:
    """
    Formate un nombre avec séparateurs.

    Examples:
        >>> formater_nombre(1234567)
        "1 234 567"
        >>> formater_nombre(1234.56, decimals=2)
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


def formater_taille_fichier(bytes: int | float | None) -> str:
    """
    Formate une taille de fichier.

    Examples:
        >>> formater_taille_fichier(1024)
        "1 Ko"
        >>> formater_taille_fichier(1048576)
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

    return f"{formater_quantite(size, 1)} {units[unit_index]}"


def formater_plage(min_val: float, max_val: float, unit: str = "") -> str:
    """
    Formate une plage de valeurs.

    Examples:
        >>> formater_plage(10, 20, "€")
        "10-20 €"
    """
    min_str = formater_quantite(min_val)
    max_str = formater_quantite(max_val)

    if unit:
        return f"{min_str}-{max_str} {unit}"
    return f"{min_str}-{max_str}"


def arrondir_intelligent(value: int | float, precision: int = 2) -> float:
    """
    Arrondi intelligent (évite erreurs de float).

    Examples:
        >>> arrondir_intelligent(2.5000000001)
        2.5
    """
    if value is None:
        return 0.0

    try:
        return round(float(value), precision)
    except (ValueError, TypeError):
        return 0.0


# ═══════════════════════════════════════════════════════════
# TEXTE
# ═══════════════════════════════════════════════════════════


def tronquer(text: str, length: int = 100, suffix: str = "...") -> str:
    """
    Tronque un texte.

    Examples:
        >>> tronquer("Un texte très long...", length=10)
        "Un texte..."
    """
    if len(text) <= length:
        return text
    return text[: length - len(suffix)] + suffix


def nettoyer_texte(text: str) -> str:
    """
    Nettoie texte (évite injection).

    Examples:
        >>> nettoyer_texte("<script>alert('xss')</script>")
        "scriptalert('xss')/script"
    """
    if not text:
        return text
    return re.sub(r"[<>{}]", "", text).strip()


def generer_slug(text: str) -> str:
    """
    Convertit texte en slug.

    Examples:
        >>> generer_slug("Tarte aux Pommes")
        "tarte-aux-pommes"
    """
    text = text.lower()

    replacements = {
        "à": "a",
        "á": "a",
        "â": "a",
        "ä": "a",
        "è": "e",
        "é": "e",
        "ê": "e",
        "ë": "e",
        "ù": "u",
        "ú": "u",
        "û": "u",
        "ü": "u",
        "ç": "c",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def extraire_nombre(text: str) -> float | None:
    """
    Extrait un nombre depuis une string.

    Examples:
        >>> extraire_nombre("2.5 kg")
        2.5
        >>> extraire_nombre("Prix: 10,50€")
        10.5
    """
    if not text:
        return None

    text = str(text).replace(",", ".")
    match = re.search(r"-?\d+\.?\d*", text)

    if match:
        try:
            return float(match.group())
        except ValueError:
            return None

    return None


def capitaliser_premiere(text: str) -> str:
    """
    Capitalise première lettre uniquement.

    Examples:
        >>> capitaliser_premiere("tomate")
        "Tomate"
    """
    if not text:
        return text
    return text[0].upper() + text[1:].lower() if len(text) > 0 else text


def capitaliser_mots(text: str) -> str:
    """
    Capitalise chaque mot.

    Examples:
        >>> capitaliser_mots("bonjour le monde")
        "Bonjour Le Monde"
    """
    if not text:
        return text
    return " ".join(word.capitalize() for word in text.split())


# ═══════════════════════════════════════════════════════════
# UNITÉS (POIDS, VOLUME)
# ═══════════════════════════════════════════════════════════


def formater_poids(grams: int | float | None) -> str:
    """
    Formate un poids en grammes vers kg/g automatique.

    Examples:
        >>> formater_poids(500)
        "500 g"
        >>> formater_poids(1000)
        "1 kg"
    """
    if grams is None or grams == 0:
        return "0 g"

    try:
        g = float(grams)
    except (ValueError, TypeError):
        return "0 g"

    if g >= 1000:
        kg = g / 1000
        return formater_quantite_unite(kg, "kg")

    return formater_quantite_unite(g, "g")


def formater_volume(milliliters: int | float | None) -> str:
    """
    Formate un volume en mL vers L/mL automatique.

    Examples:
        >>> formater_volume(500)
        "500 mL"
        >>> formater_volume(1000)
        "1 L"
    """
    if milliliters is None or milliliters == 0:
        return "0 mL"

    try:
        ml = float(milliliters)
    except (ValueError, TypeError):
        return "0 mL"

    if ml >= 1000:
        liters = ml / 1000
        return formater_quantite_unite(liters, "L")

    return formater_quantite_unite(ml, "mL")


def formater_temperature(celsius: int | float | None, unit: str = "C") -> str:
    """
    Formate une température.

    Examples:
        >>> formater_temperature(20)
        "20°C"
        >>> formater_temperature(68, "F")
        "68°F"
    """
    if celsius is None:
        return "0°C"

    try:
        temp = float(celsius)
    except (ValueError, TypeError):
        return "0°C"

    if unit == "F":
        return f"{int(temp)}°F"
    return f"{int(temp)}°C"


# ═══════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════

__all__ = [
    # Dates
    "formater_date",
    "formater_datetime",
    "temps_ecoule",
    "formater_temps",
    "formater_duree",
    # Nombres
    "formater_quantite",
    "formater_quantite_unite",
    "formater_prix",
    "formater_monnaie",
    "formater_pourcentage",
    "formater_nombre",
    "formater_taille_fichier",
    "formater_plage",
    "arrondir_intelligent",
    # Texte
    "tronquer",
    "nettoyer_texte",
    "generer_slug",
    "extraire_nombre",
    "capitaliser_premiere",
    "capitaliser_mots",
    # Unités
    "formater_poids",
    "formater_volume",
    "formater_temperature",
]
