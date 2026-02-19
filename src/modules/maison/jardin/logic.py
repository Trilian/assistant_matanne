"""
Jardin - Logique métier.

⚠️ Ce fichier est un PROXY vers src/services/maison/jardin_service.py
Il maintient la compatibilité avec l'interface existante tout en
consolidant la logique dans le service.

Usage inchangé pour l'UI:
    from .logic import BADGES_JARDIN, generer_taches_jardin, calculer_autonomie
"""

import logging
from functools import lru_cache

# Importer depuis le service centralisé
from src.services.maison import BADGES_JARDIN, get_jardin_service

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════
# SERVICE SINGLETON (évite recréer à chaque appel)
# ═══════════════════════════════════════════════════════════


@lru_cache(maxsize=1)
def _get_service():
    """Retourne une instance singleton du service jardin."""
    return get_jardin_service()


# ═══════════════════════════════════════════════════════════
# EXPORTS COMPATIBILITÉ - RÉEXPORTÉS DEPUIS LE SERVICE
# ═══════════════════════════════════════════════════════════


def generer_taches_jardin(mes_plantes: list[dict], meteo: dict) -> list[dict]:
    """
    Génère automatiquement les tâches du jardin.

    Proxy vers JardinService.generer_taches()
    """
    return _get_service().generer_taches(mes_plantes, meteo)


def calculer_autonomie(mes_plantes: list[dict], recoltes: list[dict]) -> dict:
    """
    Calcule les métriques d'autonomie alimentaire.

    Proxy vers JardinService.calculer_autonomie()
    """
    return _get_service().calculer_autonomie(mes_plantes, recoltes)


def calculer_streak_jardin(activites: list[dict]) -> int:
    """
    Calcule le nombre de jours consécutifs d'activité jardin.

    Proxy vers JardinService.calculer_streak()
    """
    return _get_service().calculer_streak(activites)


def calculer_stats_jardin(
    mes_plantes: list[dict],
    recoltes: list[dict],
    activites: list[dict] = None,
) -> dict:
    """
    Calcule les statistiques globales pour badges.

    Proxy vers JardinService.calculer_stats()
    """
    return _get_service().calculer_stats(mes_plantes, recoltes, activites)


def obtenir_badges_jardin(stats: dict) -> list[str]:
    """
    Retourne la liste des IDs de badges obtenus.

    Proxy vers JardinService.obtenir_ids_badges()
    """
    return _get_service().obtenir_ids_badges(stats)


def generer_planning_jardin(mes_plantes: list[dict], horizon_mois: int = 6) -> list[dict]:
    """
    Génère le planning prévisionnel des activités jardin.

    Proxy vers JardinService.generer_planning()
    """
    return _get_service().generer_planning(mes_plantes, horizon_mois)


def generer_previsions_recoltes(mes_plantes: list[dict]) -> list[dict]:
    """
    Génère les prévisions de récoltes basées sur les plantes en terre.

    Proxy vers JardinService.generer_previsions_recoltes()
    """
    return _get_service().generer_previsions_recoltes(mes_plantes)


# ═══════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════

__all__ = [
    "BADGES_JARDIN",
    "generer_taches_jardin",
    "calculer_autonomie",
    "calculer_streak_jardin",
    "calculer_stats_jardin",
    "obtenir_badges_jardin",
    "generer_planning_jardin",
    "generer_previsions_recoltes",
]
