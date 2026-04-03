"""Utilitaires de formatage de dates et durées."""

from datetime import date

from ..constants import (
    JOURS_SEMAINE,
    JOURS_SEMAINE_COURT,
    MOIS_FRANCAIS,
    MOIS_FRANCAIS_COURT,
)


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


def formater_label_semaine(semaine_debut: date, semaine_fin: date | None = None) -> str:
    """
    Formate un label pour afficher la semaine.

    Args:
        semaine_debut: Date du lundi
        semaine_fin: Date du dimanche (optionnel, non utilisé)

    Returns:
        Label formaté "Semaine du DD/MM/YYYY"
    """
    return f"Semaine du {semaine_debut.strftime('%d/%m/%Y')}"


# Alias rétrocompatibilité
format_week_label = formater_label_semaine


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
