"""
Dashboard - Service de données pour la page d'accueil.

Usage:
    from src.services.dashboard import AccueilDataService, get_accueil_data_service
"""

from .service import AccueilDataService, get_accueil_data_service
from .score_bienetre import ScoreBienEtreService, get_score_bien_etre_service

__all__ = [
    "AccueilDataService",
    "get_accueil_data_service",
    "ScoreBienEtreService",
    "get_score_bien_etre_service",
]
