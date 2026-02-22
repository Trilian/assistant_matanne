"""
Module Calendrier Familial Unifié - Chargement des données.

Facade légère qui délègue au ServiceCalendrierPlanning.
Conserve la signature publique `charger_donnees_semaine(date_debut)`.
"""

import logging
from datetime import date

logger = logging.getLogger(__name__)

# Accesseur lazy pour le service (singleton)
_service = None


def _get_service():
    global _service
    if _service is None:
        from src.services.famille.calendrier_planning import (
            obtenir_service_calendrier_planning,
        )

        _service = obtenir_service_calendrier_planning()
    return _service


def charger_donnees_semaine(date_debut: date) -> dict:
    """Charge toutes les données nécessaires pour une semaine.

    Délègue au ServiceCalendrierPlanning (accès DB centralisé).

    Returns:
        Dict avec repas, sessions_batch, activites, events,
        courses_planifiees, taches_menage.
    """
    try:
        return _get_service().charger_donnees_semaine(date_debut)
    except Exception as e:
        logger.error(f"Erreur chargement données semaine: {e}")
        return {
            "repas": [],
            "sessions_batch": [],
            "activites": [],
            "events": [],
            "courses_planifiees": [],
            "taches_menage": [],
        }
