"""
Utilitaires pour le module Entretien.

Fonctions pures de filtrage, calcul de dates et statistiques
pour les routines et tâches d'entretien.
"""

import logging
from datetime import date, timedelta

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════
# FRÉQUENCES (en jours)
# ═══════════════════════════════════════════════════════════

FREQUENCES_JOURS = {
    "quotidien": 1,
    "tous_2_jours": 2,
    "hebdomadaire": 7,
    "bi_mensuel": 14,
    "mensuel": 30,
    "trimestriel": 90,
    "saisonnier": 120,
    "annuel": 365,
}


def calculer_prochaine_occurrence(
    derniere_date: date | None,
    frequence: str,
) -> date:
    """Calcule la prochaine occurrence d'une tâche récurrente.

    Args:
        derniere_date: Date de dernière exécution (None si jamais fait).
        frequence: Clé de fréquence (quotidien, hebdomadaire, etc.).

    Returns:
        Date de la prochaine occurrence.
    """
    jours = FREQUENCES_JOURS.get(frequence, 7)
    base = derniere_date or date.today()
    return base + timedelta(days=jours)


def calculer_jours_avant_tache(
    derniere_date: date | None,
    frequence: str,
) -> int:
    """Calcule le nombre de jours avant la prochaine tâche.

    Args:
        derniere_date: Date de dernière exécution.
        frequence: Clé de fréquence.

    Returns:
        Nombre de jours restants (négatif si en retard).
    """
    prochaine = calculer_prochaine_occurrence(derniere_date, frequence)
    return (prochaine - date.today()).days


def get_taches_aujourd_hui(taches: list[dict]) -> list[dict]:
    """Filtre les tâches prévues pour aujourd'hui.

    Args:
        taches: Liste de dicts avec clés 'derniere_date' et 'frequence'.

    Returns:
        Liste des tâches dues aujourd'hui ou en retard.
    """
    today = date.today()
    result = []
    for tache in taches:
        prochaine = calculer_prochaine_occurrence(
            tache.get("derniere_date"),
            tache.get("frequence", "quotidien"),
        )
        if prochaine <= today:
            result.append(tache)
    return result


def get_taches_semaine(taches: list[dict]) -> list[dict]:
    """Filtre les tâches prévues pour la semaine courante.

    Args:
        taches: Liste de dicts avec clés 'derniere_date' et 'frequence'.

    Returns:
        Liste des tâches dues dans les 7 prochains jours.
    """
    today = date.today()
    fin_semaine = today + timedelta(days=7)
    result = []
    for tache in taches:
        prochaine = calculer_prochaine_occurrence(
            tache.get("derniere_date"),
            tache.get("frequence", "quotidien"),
        )
        if prochaine <= fin_semaine:
            result.append(tache)
    return result


def get_taches_en_retard(taches: list[dict]) -> list[dict]:
    """Filtre les tâches en retard.

    Args:
        taches: Liste de dicts avec clés 'derniere_date' et 'frequence'.

    Returns:
        Liste des tâches dont la date est dépassée.
    """
    today = date.today()
    result = []
    for tache in taches:
        prochaine = calculer_prochaine_occurrence(
            tache.get("derniere_date"),
            tache.get("frequence", "quotidien"),
        )
        if prochaine < today:
            result.append(tache)
    return result


def filtrer_par_categorie(taches: list[dict], categorie: str) -> list[dict]:
    """Filtre les tâches par catégorie.

    Args:
        taches: Liste de dicts avec clé 'categorie'.
        categorie: La catégorie à filtrer.

    Returns:
        Liste filtrée.
    """
    return [t for t in taches if t.get("categorie") == categorie]


def filtrer_par_piece(taches: list[dict], piece: str) -> list[dict]:
    """Filtre les tâches par pièce.

    Args:
        taches: Liste de dicts avec clé 'piece'.
        piece: La pièce à filtrer.

    Returns:
        Liste filtrée.
    """
    return [t for t in taches if t.get("piece") == piece]


def filtrer_par_frequence(taches: list[dict], frequence: str) -> list[dict]:
    """Filtre les tâches par fréquence.

    Args:
        taches: Liste de dicts avec clé 'frequence'.
        frequence: La fréquence à filtrer.

    Returns:
        Liste filtrée.
    """
    return [t for t in taches if t.get("frequence") == frequence]


def calculer_statistiques_entretien(taches: list[dict]) -> dict:
    """Calcule les statistiques globales d'entretien.

    Args:
        taches: Liste de dicts des tâches planifiées.

    Returns:
        Dict avec total, a_faire, en_retard, completion_rate.
    """
    today = date.today()
    total = len(taches)
    en_retard = len(get_taches_en_retard(taches))
    a_faire = len(get_taches_aujourd_hui(taches))
    faites = total - a_faire if total > 0 else 0

    return {
        "total": total,
        "a_faire": a_faire,
        "en_retard": en_retard,
        "faites": faites,
        "completion_rate": (faites / total * 100) if total > 0 else 0,
    }


def calculer_taux_completion(
    total_taches: int,
    taches_completees: int,
) -> float:
    """Calcule le taux de complétion en pourcentage.

    Args:
        total_taches: Nombre total de tâches.
        taches_completees: Nombre de tâches terminées.

    Returns:
        Taux de complétion (0.0 à 100.0).
    """
    if total_taches <= 0:
        return 0.0
    return min(100.0, (taches_completees / total_taches) * 100)
