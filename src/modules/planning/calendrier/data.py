"""
Module Calendrier Familial Unifié - Chargement des données
"""

import logging
from datetime import date, datetime, time, timedelta

from src.core.db import obtenir_contexte_db
from src.core.models import (
    CalendarEvent,
    FamilyActivity,
    Planning,
    Recette,
    Repas,
    SessionBatchCooking,
)
from .utils import get_debut_semaine

logger = logging.getLogger(__name__)


def charger_donnees_semaine(date_debut: date) -> dict:
    """
    Charge toutes les données nécessaires pour une semaine.

    Returns:
        Dict avec repas, sessions_batch, activites, events, taches_menage
    """
    lundi = get_debut_semaine(date_debut)
    dimanche = lundi + timedelta(days=6)

    donnees = {
        "repas": [],
        "sessions_batch": [],
        "activites": [],
        "events": [],
        "courses_planifiees": [],
        "taches_menage": [],  # Tâches ménage intégrées au planning
    }

    try:
        with obtenir_contexte_db() as db:
            # Charger le planning actif et ses repas
            planning = (
                db.query(Planning)
                .filter(Planning.semaine_debut <= dimanche, Planning.semaine_fin >= lundi)
                .first()
            )

            if planning:
                repas = (
                    db.query(Repas)
                    .filter(
                        Repas.planning_id == planning.id,
                        Repas.date_repas >= lundi,
                        Repas.date_repas <= dimanche,
                    )
                    .all()
                )

                # Charger les recettes associées
                for r in repas:
                    if r.recette_id:
                        r.recette = db.query(Recette).filter_by(id=r.recette_id).first()

                donnees["repas"] = repas

            # Sessions batch cooking
            sessions = (
                db.query(SessionBatchCooking)
                .filter(
                    SessionBatchCooking.date_session >= lundi,
                    SessionBatchCooking.date_session <= dimanche,
                )
                .all()
            )
            donnees["sessions_batch"] = sessions

            # Activités famille
            activites = (
                db.query(FamilyActivity)
                .filter(FamilyActivity.date_prevue >= lundi, FamilyActivity.date_prevue <= dimanche)
                .all()
            )
            donnees["activites"] = activites

            # Tâches ménage intégrées au planning
            try:
                from src.core.models import MaintenanceTask

                taches = (
                    db.query(MaintenanceTask)
                    .filter(MaintenanceTask.integrer_planning == True)
                    .all()
                )
                donnees["taches_menage"] = taches
            except Exception as e:
                logger.warning(f"Table maintenance_tasks non disponible: {e}")

            # Événements calendrier
            events = (
                db.query(CalendarEvent)
                .filter(
                    CalendarEvent.date_debut >= datetime.combine(lundi, time.min),
                    CalendarEvent.date_debut <= datetime.combine(dimanche, time.max),
                )
                .all()
            )
            donnees["events"] = events

    except Exception as e:
        logger.error(f"Erreur chargement données semaine: {e}")

    return donnees
