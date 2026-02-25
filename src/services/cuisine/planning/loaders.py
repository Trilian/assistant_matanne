"""
Chargement optimisé des données pour le planning unifié.

Extrait du service principal pour réduire sa taille.
Contient les loaders de données:
- Repas planifiés
- Activités familiales
- Projets domestiques
- Routines quotidiennes
- Événements calendrier
"""

import logging
from datetime import date, datetime

from sqlalchemy.orm import Session

from src.core.models import (
    ActiviteFamille,
    EvenementPlanning,
    Projet,
    Recette,
    Repas,
    Routine,
    TacheRoutine,
)

logger = logging.getLogger(__name__)


class PlanningLoadersMixin:
    """
    Mixin fournissant le chargement optimisé des données.

    Charge repas, activités, projets, routines et événements
    en un seul pass optimisé.
    """

    def _charger_repas(
        self, date_debut: date, date_fin: date, db: Session
    ) -> dict[str, list[dict]]:
        """Charge repas planifiés avec recettes"""
        repas_dict = {}

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
        activites_dict = {}

        activites = (
            db.query(ActiviteFamille)
            .filter(
                ActiviteFamille.date_prevue
                >= datetime.combine(date_debut, datetime.min.time()).date(),
                ActiviteFamille.date_prevue
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
                    "fin": act.date_prevue,  # ActiviteFamille n'a pas de date_fin séparée
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
        projets_dict = {}

        projets = (
            db.query(Projet)
            .filter(
                Projet.statut.in_(["à_faire", "en_cours"]),
                (Projet.date_fin_prevue == None)
                | (Projet.date_fin_prevue.between(date_debut, date_fin)),
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
        routines_dict = {}

        routines = (
            db.query(TacheRoutine, Routine)
            .join(Routine, TacheRoutine.routine_id == Routine.id)
            .filter(Routine.actif == True)
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
        events_dict = {}

        events = (
            db.query(EvenementPlanning)
            .filter(
                EvenementPlanning.date_debut >= datetime.combine(date_debut, datetime.min.time()),
                EvenementPlanning.date_debut <= datetime.combine(date_fin, datetime.max.time()),
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


__all__ = ["PlanningLoadersMixin"]
