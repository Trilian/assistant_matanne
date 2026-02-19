"""
Utilitaires de date centralisés.

Ce module consolide toutes les fonctions de manipulation de dates/semaines
précédemment dispersées dans:
- modules/shared/date_utils.py
- utils/helpers/dates.py
- services/planning/utils.py (section dates)

Usage:
    from src.core.date_utils import obtenir_debut_semaine, formater_date_fr
"""

from datetime import date, datetime, timedelta

from src.core.constants import (
    JOURS_SEMAINE,
    JOURS_SEMAINE_COURT,
    JOURS_SEMAINE_LOWER,
    MOIS_FRANCAIS,
    MOIS_FRANCAIS_COURT,
)

# ═══════════════════════════════════════════════════════════
# MANIPULATION DE SEMAINES
# ═══════════════════════════════════════════════════════════


def obtenir_debut_semaine(date_ref: date | datetime | None = None) -> date:
    """
    Retourne le lundi de la semaine contenant la date.

    Args:
        date_ref: Date de référence (défaut: aujourd'hui)

    Returns:
        Date du lundi de la semaine

    Examples:
        >>> obtenir_debut_semaine(date(2024, 1, 18))  # Jeudi
        date(2024, 1, 15)  # Lundi
    """
    if date_ref is None:
        date_ref = date.today()
    if isinstance(date_ref, datetime):
        date_ref = date_ref.date()
    return date_ref - timedelta(days=date_ref.weekday())


def obtenir_fin_semaine(date_ref: date | None = None) -> date:
    """
    Retourne le dimanche de la semaine contenant la date.

    Args:
        date_ref: Date de référence (défaut: aujourd'hui)

    Returns:
        Date du dimanche de la semaine
    """
    return obtenir_debut_semaine(date_ref) + timedelta(days=6)


def obtenir_bornes_semaine(date_ref: date | None = None) -> tuple[date, date]:
    """
    Retourne (lundi, dimanche) de la semaine.

    Args:
        date_ref: Date de référence (défaut: aujourd'hui)

    Returns:
        Tuple (lundi, dimanche)

    Examples:
        >>> obtenir_bornes_semaine(date(2025, 1, 8))  # Mercredi
        (date(2025, 1, 6), date(2025, 1, 12))  # Lundi -> Dimanche
    """
    lundi = obtenir_debut_semaine(date_ref)
    return lundi, lundi + timedelta(days=6)


def obtenir_jours_semaine(date_ref: date | None = None) -> list[date]:
    """
    Retourne les 7 jours de la semaine (lundi à dimanche).

    Args:
        date_ref: Date de référence (défaut: aujourd'hui)

    Returns:
        Liste des 7 dates de la semaine
    """
    lundi = obtenir_debut_semaine(date_ref)
    return [lundi + timedelta(days=i) for i in range(7)]


def obtenir_semaine_precedente(date_ref: date | None = None) -> date:
    """
    Retourne le lundi de la semaine précédente.

    Args:
        date_ref: Date de référence (défaut: aujourd'hui)

    Returns:
        Date du lundi de la semaine précédente
    """
    return obtenir_debut_semaine(date_ref) - timedelta(days=7)


def obtenir_semaine_suivante(date_ref: date | None = None) -> date:
    """
    Retourne le lundi de la semaine suivante.

    Args:
        date_ref: Date de référence (défaut: aujourd'hui)

    Returns:
        Date du lundi de la semaine suivante
    """
    return obtenir_debut_semaine(date_ref) + timedelta(days=7)


def semaines_entre(start: date, end: date) -> int:
    """
    Nombre de semaines complètes entre deux dates.

    Examples:
        >>> semaines_entre(date(2025, 1, 1), date(2025, 1, 15))
        2
    """
    return (end - start).days // 7


# ═══════════════════════════════════════════════════════════
# MANIPULATION DE MOIS
# ═══════════════════════════════════════════════════════════


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


# ═══════════════════════════════════════════════════════════
# PLAGES DE DATES
# ═══════════════════════════════════════════════════════════


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


# ═══════════════════════════════════════════════════════════
# VÉRIFICATIONS
# ═══════════════════════════════════════════════════════════


def est_weekend(date_ref: date) -> bool:
    """
    Vérifie si la date est un weekend.

    Examples:
        >>> est_weekend(date(2025, 1, 11))  # Samedi
        True
    """
    return date_ref.weekday() >= 5


def est_aujourd_hui(date_ref: date) -> bool:
    """
    Vérifie si une date est aujourd'hui.

    Examples:
        >>> est_aujourd_hui(date.today())
        True
    """
    return date_ref == date.today()


# ═══════════════════════════════════════════════════════════
# NOMS DE JOURS/MOIS
# ═══════════════════════════════════════════════════════════


def get_weekday_names() -> list[str]:
    """
    Retourne la liste des noms de jours de la semaine.

    Returns:
        Liste des jours en français avec majuscule ['Lundi', ..., 'Dimanche']
    """
    return JOURS_SEMAINE.copy()


def get_weekday_name(day_index: int) -> str:
    """
    Retourne le nom du jour pour un index donné.

    Args:
        day_index: Index du jour (0=Lundi, 6=Dimanche)

    Returns:
        Nom du jour ou chaîne vide si invalide
    """
    if 0 <= day_index <= 6:
        return JOURS_SEMAINE[day_index]
    return ""


def get_weekday_index(day_name: str) -> int:
    """
    Retourne l'index d'un jour de la semaine.

    Args:
        day_name: Nom du jour (insensible à la casse)

    Returns:
        Index (0-6) ou -1 si non trouvé
    """
    try:
        return JOURS_SEMAINE_LOWER.index(day_name.lower())
    except ValueError:
        return -1


# ═══════════════════════════════════════════════════════════
# FORMATAGE DE DATES
# ═══════════════════════════════════════════════════════════


def formater_date_fr(d: date, avec_annee: bool = True) -> str:
    """
    Formate une date en français (ex: "Lundi 15 Janvier 2024").

    Args:
        d: Date à formater
        avec_annee: Inclure l'année dans le format

    Returns:
        Date formatée en français
    """
    jour = JOURS_SEMAINE[d.weekday()]
    mois = MOIS_FRANCAIS[d.month - 1]

    if avec_annee:
        return f"{jour} {d.day} {mois} {d.year}"
    return f"{jour} {d.day} {mois}"


def formater_jour_fr(d: date, court: bool = False) -> str:
    """
    Retourne le nom du jour de la semaine en français.

    Args:
        d: Date
        court: Utiliser le format court (Lun, Mar, etc.)

    Returns:
        Nom du jour en français
    """
    if court:
        return JOURS_SEMAINE_COURT[d.weekday()]
    return JOURS_SEMAINE[d.weekday()]


def formater_mois_fr(d: date, court: bool = False) -> str:
    """
    Retourne le nom du mois en français.

    Args:
        d: Date
        court: Utiliser le format court

    Returns:
        Nom du mois en français
    """
    if court:
        return MOIS_FRANCAIS_COURT[d.month - 1]
    return MOIS_FRANCAIS[d.month - 1]


def format_week_label(semaine_debut: date, semaine_fin: date | None = None) -> str:
    """
    Formate un label pour afficher la semaine.

    Args:
        semaine_debut: Date du lundi
        semaine_fin: Date du dimanche (optionnel, non utilisé)

    Returns:
        Label formaté "Semaine du DD/MM/YYYY"
    """
    return f"Semaine du {semaine_debut.strftime('%d/%m/%Y')}"


# ═══════════════════════════════════════════════════════════
# FORMATAGE DURÉES
# ═══════════════════════════════════════════════════════════


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


# ═══════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════

__all__ = [
    # Fonctions principales (préférées)
    "obtenir_debut_semaine",
    "obtenir_fin_semaine",
    "obtenir_bornes_semaine",
    "obtenir_jours_semaine",
    "obtenir_semaine_precedente",
    "obtenir_semaine_suivante",
    "semaines_entre",
    "obtenir_bornes_mois",
    "obtenir_trimestre",
    "plage_dates",
    "ajouter_jours_ouvres",
    "est_weekend",
    "est_aujourd_hui",
    "get_weekday_names",
    "get_weekday_name",
    "get_weekday_index",
    "formater_date_fr",
    "formater_jour_fr",
    "formater_mois_fr",
    "format_week_label",
    # Formatage durées
    "formater_temps",
]
