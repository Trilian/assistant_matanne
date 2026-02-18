"""
Mixin de chargement de données pour le planning unifié.

Fournit les méthodes de requêtes SQLAlchemy pour charger
tous les types d'événements familiaux :
- Repas planifiés (avec recettes)
- Activités familiales
- Projets domestiques
- Routines quotidiennes
- Événements calendrier
"""

import logging
from datetime import date, datetime

from sqlalchemy.orm import Session

from src.core.models import (
    CalendarEvent,
    FamilyActivity,
    Project,
    Recette,
    Repas,
    Routine,
    RoutineTask,
)

logger = logging.getLogger(__name__)


class PlanningDataLoaderMixin:
    """
    Mixin de chargement des données planning.

    Fournit les méthodes _charger_* pour récupérer les données
    depuis la base via SQLAlchemy. Utilisé par ServicePlanningUnifie.

    Toutes les méthodes reçoivent une session DB en paramètre
    (injectée par le décorateur @avec_session_db du service appelant).
    """

    def _charger_repas(
        self, date_debut: date, date_fin: date, db: Session
    ) -> dict[str, list[dict]]:
        """Charge repas planifiés avec recettes"""
        repas_dict: dict[str, list[dict]] = {}

        repas = (
            db.query(Repas, Recette)
            .outerjoin(Recette, Repas.recette_id == Recette.id)
            .filter(Repas.date_repas >= date_debut, Repas.date_repas <= date_fin)
            .all()
        )

        for meal, recipe in repas:
            jour_str = meal.date_repas.isoformat()
            if jour_str not in repas_dict:
                repas_dict[jour_str] = []

            repas_dict[jour_str].append(
                {
                    "id": meal.id,
                    "type": meal.type_repas,
                    "recette": recipe.nom if recipe else "Non défini",
                    "recette_id": recipe.id if recipe else None,
                    "portions": meal.portion_ajustee or (recipe.portions if recipe else 4),
                    "temps_total": (recipe.temps_preparation + recipe.temps_cuisson)
                    if recipe
                    else 0,
                    "notes": meal.notes,
                }
            )

        return repas_dict

    def _charger_activites(
        self, date_debut: date, date_fin: date, db: Session
    ) -> dict[str, list[dict]]:
        """Charge activités familiales"""
        activites_dict: dict[str, list[dict]] = {}

        activites = (
            db.query(FamilyActivity)
            .filter(
                FamilyActivity.date_prevue
                >= datetime.combine(date_debut, datetime.min.time()).date(),
                FamilyActivity.date_prevue
                <= datetime.combine(date_fin, datetime.max.time()).date(),
            )
            .all()
        )

        for act in activites:
            jour_str = act.date_prevue.isoformat()
            if jour_str not in activites_dict:
                activites_dict[jour_str] = []

            activites_dict[jour_str].append(
                {
                    "id": act.id,
                    "titre": act.titre,
                    "type": act.type_activite,
                    "debut": act.date_prevue,
                    "fin": act.date_prevue,  # FamilyActivity n'a pas de date_fin séparée
                    "lieu": act.lieu,
                    "budget": act.cout_estime or 0,
                    "duree": act.duree_heures or 0,
                }
            )

        return activites_dict

    def _charger_projets(
        self, date_debut: date, date_fin: date, db: Session
    ) -> dict[str, list[dict]]:
        """Charge projets avec tâches"""
        projets_dict: dict[str, list[dict]] = {}

        projets = (
            db.query(Project)
            .filter(
                Project.statut.in_(["à_faire", "en_cours"]),
                (Project.date_fin_prevue == None)  # noqa: E711
                | (Project.date_fin_prevue.between(date_debut, date_fin)),
            )
            .all()
        )

        for projet in projets:
            jour_str = (projet.date_fin_prevue or date_fin).isoformat()
            if jour_str not in projets_dict:
                projets_dict[jour_str] = []

            projets_dict[jour_str].append(
                {
                    "id": projet.id,
                    "nom": projet.nom,
                    "priorite": projet.priorite,
                    "statut": projet.statut,
                    "echéance": projet.date_fin_prevue,
                }
            )

        return projets_dict

    def _charger_routines(self, db: Session) -> dict[str, list[dict]]:
        """Charge routines quotidiennes actives"""
        routines_dict: dict[str, list[dict]] = {}

        routines = (
            db.query(RoutineTask, Routine)
            .join(Routine, RoutineTask.routine_id == Routine.id)
            .filter(Routine.actif == True)  # noqa: E712
            .all()
        )

        for task, routine in routines:
            jour_str = "routine_quotidienne"  # Les routines sont quotidiennes
            if jour_str not in routines_dict:
                routines_dict[jour_str] = []

            routines_dict[jour_str].append(
                {
                    "id": task.id,
                    "nom": task.nom,
                    "routine": routine.nom,
                    "heure": task.heure_prevue,
                    "fait": task.fait_le is not None,
                }
            )

        return routines_dict

    def _charger_events(
        self, date_debut: date, date_fin: date, db: Session
    ) -> dict[str, list[dict]]:
        """Charge événements calendrier"""
        events_dict: dict[str, list[dict]] = {}

        events = (
            db.query(CalendarEvent)
            .filter(
                CalendarEvent.date_debut >= datetime.combine(date_debut, datetime.min.time()),
                CalendarEvent.date_debut <= datetime.combine(date_fin, datetime.max.time()),
            )
            .all()
        )

        for event in events:
            jour_str = event.date_debut.date().isoformat()
            if jour_str not in events_dict:
                events_dict[jour_str] = []

            events_dict[jour_str].append(
                {
                    "id": event.id,
                    "titre": event.titre,
                    "type": event.type_event,
                    "debut": event.date_debut,
                    "fin": event.date_fin,
                    "lieu": event.lieu,
                    "couleur": event.couleur,
                }
            )

        return events_dict


__all__ = ["PlanningDataLoaderMixin"]
