"""
Formatters - Dates et durées
"""

from datetime import date, datetime


def formater_date(d: date | datetime | None, format: str = "short", locale: str = "fr") -> str:
    """
    Formate une date

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
    Formate une date/heure

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
    Formate une date relativement (hier, aujourd'hui, demain)

    Examples:
        >>> temps_ecoule(date.today())
        "Aujourd'hui"
        >>> temps_ecoule(date.today() - timedelta(days=1))
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
        return formater_date(d, "medium")


def formater_temps(minutes: int | float | None, avec_espace: bool = False) -> str:
    """
    Formate une durée en minutes vers format lisible.

    Args:
        minutes: Durée en minutes
        avec_espace: Ajoute un espace entre le nombre et l'unité (ex: "45 min")

    Examples:
        >>> formater_temps(90)
        "1h30"
        >>> formater_temps(45)
        "45min"
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


def formater_duree(seconds: int | float | None, short: bool = False) -> str:
    """
    Formate une durée en secondes

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
