"""
Dashboard - Service de données pour la page d'accueil.

Usage:
    from src.services.dashboard import AccueilDataService, obtenir_accueil_data_service
"""

from .service import AccueilDataService, obtenir_accueil_data_service
from .score_bienetre import ScoreBienEtreService, obtenir_score_bien_etre_service
from .score_foyer import ScoreFoyerService, obtenir_score_foyer_service
from .resume_famille_ia import ResumeFamilleIAService, obtenir_service_resume_famille_ia
from .anomalies_financieres import ServiceAnomaliesFinancieres, obtenir_service_anomalies_financieres

__all__ = [
    "AccueilDataService",
    "obtenir_accueil_data_service",
    "ScoreBienEtreService",
    "obtenir_score_bien_etre_service",
    "ScoreFoyerService",
    "obtenir_score_foyer_service",
    "ResumeFamilleIAService",
    "obtenir_service_resume_famille_ia",
    "ServiceAnomaliesFinancieres",
    "obtenir_service_anomalies_financieres",
]
