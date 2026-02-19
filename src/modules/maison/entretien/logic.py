"""
Entretien - Logique métier.

⚠️ Ce fichier est un PROXY vers src/services/maison/entretien_service.py
Il maintient la compatibilité avec l'interface existante tout en
consolidant la logique dans le service.

Usage inchangé pour l'UI:
    from .logic import BADGES_ENTRETIEN, generer_taches_entretien, calculer_score_proprete
"""

import logging
from functools import lru_cache

# Importer depuis le service centralisé
from src.services.maison import BADGES_ENTRETIEN, get_entretien_service

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════
# SERVICE SINGLETON (évite recréer à chaque appel)
# ═══════════════════════════════════════════════════════════


@lru_cache(maxsize=1)
def _get_service():
    """Retourne une instance singleton du service entretien."""
    return get_entretien_service()


# ═══════════════════════════════════════════════════════════
# EXPORTS COMPATIBILITÉ - RÉEXPORTÉS DEPUIS LE SERVICE
# ═══════════════════════════════════════════════════════════


def generer_taches_entretien(mes_objets: list[dict], historique: list[dict]) -> list[dict]:
    """
    Génère automatiquement les tâches d'entretien.

    Proxy vers EntretienService.generer_taches()
    """
    return _get_service().generer_taches(mes_objets, historique)


def calculer_score_proprete(mes_objets: list[dict], historique: list[dict]) -> dict:
    """
    Calcule un score de propreté/entretien global.

    Proxy vers EntretienService.calculer_score_proprete()
    """
    return _get_service().calculer_score_proprete(mes_objets, historique)


def calculer_streak(historique: list[dict]) -> int:
    """
    Calcule le nombre de jours consécutifs avec des tâches accomplies.

    Proxy vers EntretienService.calculer_streak()
    """
    return _get_service().calculer_streak(historique)


def calculer_stats_globales(mes_objets: list[dict], historique: list[dict]) -> dict:
    """
    Calcule les statistiques globales pour l'attribution des badges.

    Proxy vers EntretienService.calculer_stats_globales()
    """
    return _get_service().calculer_stats_globales(mes_objets, historique)


def obtenir_badges_obtenus(stats: dict) -> list[str]:
    """
    Retourne la liste des IDs de badges obtenus.

    Proxy vers EntretienService.obtenir_ids_badges()
    """
    return _get_service().obtenir_ids_badges(stats)


def generer_planning_previsionnel(
    mes_objets: list[dict], historique: list[dict], horizon_jours: int = 60
) -> list[dict]:
    """
    Génère le planning prévisionnel des tâches.

    Proxy vers EntretienService.generer_planning_previsionnel()
    """
    return _get_service().generer_planning_previsionnel(mes_objets, historique, horizon_jours)


def generer_alertes_predictives(mes_objets: list[dict], historique: list[dict]) -> list[dict]:
    """
    Génère les alertes pour les tâches arrivant bientôt.

    Proxy vers EntretienService.generer_alertes_predictives()
    """
    return _get_service().generer_alertes_predictives(mes_objets, historique)


# ═══════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════

__all__ = [
    "BADGES_ENTRETIEN",
    "generer_taches_entretien",
    "calculer_score_proprete",
    "calculer_streak",
    "calculer_stats_globales",
    "obtenir_badges_obtenus",
    "generer_planning_previsionnel",
    "generer_alertes_predictives",
]
