"""
Utilitaires de date partages entre tous les modules.

Centralise les fonctions de manipulation de dates/semaines
qui etaient dupliquees dans plusieurs fichiers.
"""

from datetime import date, timedelta

from src.modules.shared.constantes import (
    JOURS_SEMAINE,
    JOURS_SEMAINE_COURT,
    MOIS_FRANCAIS,
)

# ═══════════════════════════════════════════════════════════
# FONCTIONS DE SEMAINE
# ═══════════════════════════════════════════════════════════


def obtenir_debut_semaine(date_ref: date | None = None) -> date:
    """
    Retourne le lundi de la semaine contenant la date.

    Args:
        date_ref: Date de reference (defaut: aujourd'hui)

    Returns:
        Date du lundi de la semaine
    """
    if date_ref is None:
        date_ref = date.today()
    return date_ref - timedelta(days=date_ref.weekday())


def obtenir_fin_semaine(date_ref: date | None = None) -> date:
    """
    Retourne le dimanche de la semaine contenant la date.

    Args:
        date_ref: Date de reference (defaut: aujourd'hui)

    Returns:
        Date du dimanche de la semaine
    """
    return obtenir_debut_semaine(date_ref) + timedelta(days=6)


def obtenir_jours_semaine(date_ref: date | None = None) -> list[date]:
    """
    Retourne les 7 jours de la semaine (lundi à dimanche).

    Args:
        date_ref: Date de reference (defaut: aujourd'hui)

    Returns:
        Liste des 7 dates de la semaine
    """
    lundi = obtenir_debut_semaine(date_ref)
    return [lundi + timedelta(days=i) for i in range(7)]


def obtenir_semaine_precedente(date_ref: date | None = None) -> date:
    """
    Retourne le lundi de la semaine precedente.

    Args:
        date_ref: Date de reference (defaut: aujourd'hui)

    Returns:
        Date du lundi de la semaine precedente
    """
    return obtenir_debut_semaine(date_ref) - timedelta(days=7)


def obtenir_semaine_suivante(date_ref: date | None = None) -> date:
    """
    Retourne le lundi de la semaine suivante.

    Args:
        date_ref: Date de reference (defaut: aujourd'hui)

    Returns:
        Date du lundi de la semaine suivante
    """
    return obtenir_debut_semaine(date_ref) + timedelta(days=7)


# ═══════════════════════════════════════════════════════════
# FORMATAGE DE DATES
# ═══════════════════════════════════════════════════════════


def formater_date_fr(d: date, avec_annee: bool = True) -> str:
    """
    Formate une date en français (ex: "Lundi 15 Janvier 2024").

    Args:
        d: Date à formater
        avec_annee: Inclure l'annee dans le format

    Returns:
        Date formatee en français
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
    from src.modules.shared.constantes import MOIS_FRANCAIS_COURT

    if court:
        return MOIS_FRANCAIS_COURT[d.month - 1]
    return MOIS_FRANCAIS[d.month - 1]


# ═══════════════════════════════════════════════════════════
# ALIAS POUR COMPATIBILITÉ
# (permet migration progressive du code existant)
# ═══════════════════════════════════════════════════════════

# Alias anglais -> français
get_debut_semaine = obtenir_debut_semaine
get_fin_semaine = obtenir_fin_semaine
get_jours_semaine = obtenir_jours_semaine
get_semaine_precedente = obtenir_semaine_precedente
get_semaine_suivante = obtenir_semaine_suivante


# ═══════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════

__all__ = [
    # Fonctions françaises (preferees)
    "obtenir_debut_semaine",
    "obtenir_fin_semaine",
    "obtenir_jours_semaine",
    "obtenir_semaine_precedente",
    "obtenir_semaine_suivante",
    "formater_date_fr",
    "formater_jour_fr",
    "formater_mois_fr",
    # Alias anglais (compatibilite)
    "get_debut_semaine",
    "get_fin_semaine",
    "get_jours_semaine",
    "get_semaine_precedente",
    "get_semaine_suivante",
]
