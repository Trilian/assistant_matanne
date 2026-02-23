"""
Service Calendrier Planning - Chargement et écriture des données de planning.

Centralise toutes les requêtes DB pour le module planning/calendrier,
éliminant les accès directs depuis la couche UI.

Opérations:
- Chargement des données hebdomadaires (repas, batch, activités, events, ménage)
- Chargement des événements pour la timeline
- Création d'événements (activités, events calendrier)
"""

import logging
from datetime import date, datetime, time, timedelta
from typing import Any

from sqlalchemy.orm import Session, joinedload

from src.core.decorators import avec_cache, avec_gestion_erreurs, avec_session_db
from src.core.models import (
    CalendarEvent,
    FamilyActivity,
    Planning,
    Recette,
    Repas,
    SessionBatchCooking,
)
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


class ServiceCalendrierPlanning:
    """Service de données pour le calendrier planning familial.

    Centralise l'accès DB pour le module planning/calendrier,
    remplaçant les requêtes directes dans data.py, components.py
    et timeline_ui.py.
    """

    # ═══════════════════════════════════════════════════════════
    # CHARGEMENT DONNÉES SEMAINE (ex data.py)
    # ═══════════════════════════════════════════════════════════

    @avec_gestion_erreurs(default_return={})
    @avec_cache(ttl=300)
    @avec_session_db
    def charger_donnees_semaine(
        self, date_debut: date, *, db: Session | None = None
    ) -> dict[str, list]:
        """Charge toutes les données nécessaires pour une semaine de calendrier.

        Args:
            date_debut: Date de début (sera alignée au lundi).
            db: Session DB (injectée automatiquement).

        Returns:
            Dict avec clés: repas, sessions_batch, activites, events,
            courses_planifiees, taches_menage.
        """
        if db is None:
            raise ValueError("Session DB requise")

        from src.core.date_utils import obtenir_debut_semaine

        lundi = obtenir_debut_semaine(date_debut)
        dimanche = lundi + timedelta(days=6)

        donnees: dict[str, list] = {
            "repas": [],
            "sessions_batch": [],
            "activites": [],
            "events": [],
            "courses_planifiees": [],
            "taches_menage": [],
        }

        try:
            # Planning actif et ses repas (avec joinedload pour éviter N+1)
            planning = (
                db.query(Planning)
                .filter(
                    Planning.semaine_debut <= dimanche,
                    Planning.semaine_fin >= lundi,
                )
                .first()
            )

            if planning:
                repas = (
                    db.query(Repas)
                    .options(joinedload(Repas.recette))
                    .filter(
                        Repas.planning_id == planning.id,
                        Repas.date_repas >= lundi,
                        Repas.date_repas <= dimanche,
                    )
                    .all()
                )
                donnees["repas"] = repas

            # Sessions batch cooking
            donnees["sessions_batch"] = (
                db.query(SessionBatchCooking)
                .filter(
                    SessionBatchCooking.date_session >= lundi,
                    SessionBatchCooking.date_session <= dimanche,
                )
                .all()
            )

            # Activités famille
            donnees["activites"] = (
                db.query(FamilyActivity)
                .filter(
                    FamilyActivity.date_prevue >= lundi,
                    FamilyActivity.date_prevue <= dimanche,
                )
                .all()
            )

            # Tâches ménage intégrées au planning
            try:
                from src.core.models import MaintenanceTask

                donnees["taches_menage"] = (
                    db.query(MaintenanceTask)
                    .filter(MaintenanceTask.integrer_planning == True)  # noqa: E712
                    .all()
                )
            except Exception as e:
                logger.warning(f"Table maintenance_tasks non disponible: {e}")

            # Événements calendrier
            donnees["events"] = (
                db.query(CalendarEvent)
                .filter(
                    CalendarEvent.date_debut >= datetime.combine(lundi, time.min),
                    CalendarEvent.date_debut <= datetime.combine(dimanche, time.max),
                )
                .all()
            )

        except Exception as e:
            logger.error(f"Erreur chargement données semaine: {e}")

        return donnees

    # ═══════════════════════════════════════════════════════════
    # CHARGEMENT TIMELINE (ex timeline_ui.py)
    # ═══════════════════════════════════════════════════════════

    @avec_gestion_erreurs(default_return=[])
    @avec_cache(ttl=300)
    @avec_session_db
    def charger_events_periode(
        self, date_debut: date, date_fin: date, *, db: Session | None = None
    ) -> list[dict]:
        """Charge tous les événements pour une période donnée (timeline).

        Args:
            date_debut: Date de début de la période.
            date_fin: Date de fin de la période.
            db: Session DB (injectée automatiquement).

        Returns:
            Liste de dicts avec {titre, date_debut, date_fin, type, couleur, lieu}.
        """
        if db is None:
            raise ValueError("Session DB requise")

        events: list[dict] = []
        debut_dt = datetime.combine(date_debut, datetime.min.time())
        fin_dt = datetime.combine(date_fin, datetime.max.time())

        try:
            # CalendarEvent
            calendar_events = (
                db.query(CalendarEvent)
                .filter(
                    CalendarEvent.date_debut >= debut_dt,
                    CalendarEvent.date_debut <= fin_dt,
                )
                .all()
            )

            for e in calendar_events:
                events.append(
                    {
                        "titre": e.titre,
                        "date_debut": e.date_debut,
                        "date_fin": e.date_fin or e.date_debut + timedelta(hours=1),
                        "type": e.type_event or "autre",
                        "couleur": e.couleur if hasattr(e, "couleur") and e.couleur else "#757575",
                        "lieu": e.lieu,
                    }
                )

            # FamilyActivity
            activities = (
                db.query(FamilyActivity)
                .filter(
                    FamilyActivity.date_prevue >= date_debut,
                    FamilyActivity.date_prevue <= date_fin,
                )
                .all()
            )

            for a in activities:
                date_debut_dt = datetime.combine(
                    a.date_prevue, datetime.min.time().replace(hour=10)
                )
                events.append(
                    {
                        "titre": a.titre,
                        "date_debut": date_debut_dt,
                        "date_fin": date_debut_dt + timedelta(hours=2),
                        "type": "activité",
                        "couleur": "#4CAF50",
                        "lieu": a.lieu,
                    }
                )

            # Repas (avec joinedload pour éviter N+1)
            repas = (
                db.query(Repas)
                .options(joinedload(Repas.recette))
                .filter(
                    Repas.date_repas >= date_debut,
                    Repas.date_repas <= date_fin,
                )
                .all()
            )

            for r in repas:
                heures = {"petit_déjeuner": 8, "déjeuner": 12, "goûter": 16, "dîner": 19}
                heure = heures.get(r.type_repas, 12)
                date_debut_dt = datetime.combine(
                    r.date_repas, datetime.min.time().replace(hour=heure)
                )
                recette_nom = r.recette.nom if r.recette else "Non défini"
                events.append(
                    {
                        "titre": f"{r.type_repas.replace('_', ' ').title()}: {recette_nom}",
                        "date_debut": date_debut_dt,
                        "date_fin": date_debut_dt + timedelta(minutes=45),
                        "type": "repas",
                        "couleur": "#2196F3",
                        "lieu": None,
                    }
                )

        except Exception as e:
            logger.error(f"Erreur chargement events période: {e}")

        return events

    # ═══════════════════════════════════════════════════════════
    # CRÉATION D'ÉVÉNEMENTS (ex components.py)
    # ═══════════════════════════════════════════════════════════

    @avec_gestion_erreurs(default_return=None)
    @avec_session_db
    def creer_activite(
        self,
        titre: str,
        date_prevue: date,
        heure_debut: time | None = None,
        lieu: str | None = None,
        notes: str | None = None,
        *,
        db: Session | None = None,
    ) -> FamilyActivity:
        """Crée une activité famille dans le calendrier.

        Args:
            titre: Titre de l'activité.
            date_prevue: Date prévue.
            heure_debut: Heure de début (optionnel).
            lieu: Lieu (optionnel).
            notes: Notes supplémentaires (optionnel).
            db: Session DB (injectée automatiquement).

        Returns:
            L'activité créée.
        """
        if db is None:
            raise ValueError("Session DB requise")

        activite = FamilyActivity(
            titre=titre,
            date_prevue=date_prevue,
            heure_debut=heure_debut,
            lieu=lieu,
            notes=notes,
            type_activite="famille",
            statut="planifié",
        )
        db.add(activite)
        db.commit()
        db.refresh(activite)
        return activite

    @avec_gestion_erreurs(default_return=None)
    @avec_session_db
    def creer_event_calendrier(
        self,
        titre: str,
        date_event: date,
        type_event: str,
        heure: time | None = None,
        lieu: str | None = None,
        description: str | None = None,
        rappel_avant_minutes: int | None = None,
        recurrence_type: str | None = None,
        recurrence_interval: int | None = None,
        recurrence_jours: str | None = None,
        recurrence_fin: date | None = None,
        *,
        db: Session | None = None,
    ) -> CalendarEvent:
        """Crée un événement calendrier.

        Args:
            titre: Titre de l'événement.
            date_event: Date de l'événement.
            type_event: Type (rdv_medical, rdv_autre, courses, autre).
            heure: Heure de l'événement (optionnel).
            lieu: Lieu (optionnel).
            description: Description/notes (optionnel).
            rappel_avant_minutes: Rappel en minutes avant (optionnel).
            recurrence_type: Type de récurrence (optionnel).
            recurrence_interval: Intervalle de récurrence (optionnel).
            recurrence_jours: Jours de récurrence (optionnel).
            recurrence_fin: Date de fin de récurrence (optionnel).
            db: Session DB (injectée automatiquement).

        Returns:
            L'événement calendrier créé.
        """
        if db is None:
            raise ValueError("Session DB requise")

        event = CalendarEvent(
            titre=titre,
            date_debut=datetime.combine(date_event, heure or time(10, 0)),
            type_event=type_event,
            lieu=lieu,
            description=description,
            rappel_avant_minutes=rappel_avant_minutes,
            recurrence_type=recurrence_type,
            recurrence_interval=recurrence_interval,
            recurrence_jours=recurrence_jours,
            recurrence_fin=recurrence_fin,
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        return event


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


@service_factory("calendrier_planning", tags={"planning", "calendrier"})
def _creer_service_calendrier_planning() -> ServiceCalendrierPlanning:
    return ServiceCalendrierPlanning()


def obtenir_service_calendrier_planning() -> ServiceCalendrierPlanning:
    """Factory pour obtenir le service calendrier planning (singleton)."""
    return _creer_service_calendrier_planning()
