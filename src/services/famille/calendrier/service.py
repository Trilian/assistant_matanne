"""
Service de synchronisation avec calendriers externes.

Fonctionnalités:
- Import/Export Google Calendar
- Import/Export Apple Calendar (iCal)
- Synchronisation bidirectionnelle
- Mapping des événements planning → calendrier
- Gestion des conflits
"""

import logging
from datetime import date, datetime, timedelta
from uuid import UUID, uuid4

import httpx
from sqlalchemy.orm import Session

from src.core.db import obtenir_contexte_db
from src.core.decorators import avec_gestion_erreurs, avec_session_db
from src.core.models import (
    CalendarEvent,
    CalendrierExterne,
    EvenementCalendrier,
    FamilyActivity,
    Planning,
    Repas,
)

from .generateur import ICalGenerator
from .google_calendar import GoogleCalendarMixin
from .schemas import (
    CalendarEventExternal,
    CalendarProvider,
    ExternalCalendarConfig,
    SyncDirection,
    SyncResult,
)

logger = logging.getLogger(__name__)


class CalendarSyncService(GoogleCalendarMixin):
    """
    Service de synchronisation avec les calendriers externes.

    Supporte:
    - Google Calendar (OAuth2)
    - Apple iCloud Calendar (via URL iCal)
    - Outlook Calendar (OAuth2)
    - URLs iCal génériques
    """

    def __init__(self):
        """Initialise le service."""
        self._configs: dict[str, ExternalCalendarConfig] = {}
        self.http_client = httpx.Client(timeout=30.0)

    # ═══════════════════════════════════════════════════════════
    # CONFIGURATION
    # ═══════════════════════════════════════════════════════════

    def add_calendar(self, config: ExternalCalendarConfig) -> str:
        """
        Ajoute un calendrier externe à synchroniser.

        Args:
            config: Configuration du calendrier

        Returns:
            ID du calendrier ajouté
        """
        self._configs[config.id] = config
        self._save_config_to_db(config)
        logger.info(f"Calendrier ajouté: {config.name} ({config.provider.value})")
        return config.id

    def remove_calendar(self, calendar_id: str):
        """Supprime un calendrier."""
        if calendar_id in self._configs:
            del self._configs[calendar_id]
        self._remove_config_from_db(calendar_id)

    def get_user_calendars(self, user_id: str) -> list[ExternalCalendarConfig]:
        """Récupère les calendriers d'un utilisateur."""
        return [c for c in self._configs.values() if c.user_id == user_id]

    # ═══════════════════════════════════════════════════════════
    # EXPORT VERS CALENDRIER EXTERNE
    # ═══════════════════════════════════════════════════════════

    @avec_gestion_erreurs(default_return=None, afficher_erreur=True)
    def export_to_ical(
        self,
        user_id: str,
        start_date: date | None = None,
        end_date: date | None = None,
        include_meals: bool = True,
        include_activities: bool = True,
    ) -> str | None:
        """
        Exporte les événements vers un fichier iCal.

        Args:
            user_id: ID de l'utilisateur
            start_date: Date de début (défaut: aujourd'hui)
            end_date: Date de fin (défaut: +30 jours)
            include_meals: Inclure les repas du planning
            include_activities: Inclure les activités familiales

        Returns:
            Contenu du fichier .ics
        """
        start = start_date or date.today()
        end = end_date or (date.today() + timedelta(days=30))

        events = []

        with obtenir_contexte_db() as db:
            # Repas du planning
            if include_meals:
                repas_list = (
                    db.query(Repas)
                    .join(Planning)
                    .filter(
                        Repas.date_repas >= start,
                        Repas.date_repas <= end,
                    )
                    .all()
                )

                for repas in repas_list:
                    # Déterminer l'heure selon le type de repas
                    if repas.type_repas == "petit_déjeuner":
                        hour = 8
                    elif repas.type_repas == "déjeuner":
                        hour = 12
                    elif repas.type_repas == "goûter":
                        hour = 16
                    else:  # dîner
                        hour = 19

                    start_time = datetime.combine(
                        repas.date_repas, datetime.min.time().replace(hour=hour)
                    )
                    end_time = start_time + timedelta(hours=1)

                    title = f"🍽️ {repas.type_repas.title()}"
                    if repas.recette:
                        title += f": {repas.recette.nom}"

                    events.append(
                        CalendarEventExternal(
                            external_id=f"meal-{repas.id}",
                            title=title,
                            description=repas.notes or "",
                            start_time=start_time,
                            end_time=end_time,
                            source_type="meal",
                            source_id=repas.id,
                        )
                    )

            # Activités familiales
            if include_activities:
                activities = (
                    db.query(FamilyActivity)
                    .filter(
                        FamilyActivity.date_prevue >= start,
                        FamilyActivity.date_prevue <= end,
                        FamilyActivity.statut != "annulé",
                    )
                    .all()
                )

                for activity in activities:
                    start_time = datetime.combine(
                        activity.date_prevue, datetime.min.time().replace(hour=10)
                    )
                    duration_hours = activity.duree_heures or 2
                    end_time = start_time + timedelta(hours=duration_hours)

                    events.append(
                        CalendarEventExternal(
                            external_id=f"activity-{activity.id}",
                            title=f"👨‍👩‍👧 {activity.titre}",
                            description=activity.description or "",
                            start_time=start_time,
                            end_time=end_time,
                            location=activity.lieu or "",
                            source_type="activity",
                            source_id=activity.id,
                        )
                    )

            # Événements du calendrier interne
            calendar_events = (
                db.query(CalendarEvent)
                .filter(
                    CalendarEvent.date_debut >= start,
                    CalendarEvent.date_debut <= end,
                )
                .all()
            )

            for event in calendar_events:
                events.append(
                    CalendarEventExternal(
                        external_id=f"event-{event.id}",
                        title=event.titre,
                        description=event.description or "",
                        start_time=datetime.combine(
                            event.date_debut, datetime.min.time().replace(hour=9)
                        ),
                        end_time=datetime.combine(
                            event.date_fin or event.date_debut, datetime.min.time().replace(hour=10)
                        ),
                        all_day=event.journee_entiere
                        if hasattr(event, "journee_entiere")
                        else False,
                        source_type="event",
                        source_id=event.id,
                    )
                )

        logger.info(f"Export iCal: {len(events)} événements")
        return ICalGenerator.generate_ical(events)

    # ═══════════════════════════════════════════════════════════
    # IMPORT DEPUIS CALENDRIER EXTERNE
    # ═══════════════════════════════════════════════════════════

    @avec_gestion_erreurs(default_return=None, afficher_erreur=True)
    def import_from_ical_url(
        self,
        user_id: str,
        ical_url: str,
        calendar_name: str = "Calendrier importé",
    ) -> SyncResult:
        """
        Importe les événements depuis une URL iCal.

        Args:
            user_id: ID de l'utilisateur
            ical_url: URL du calendrier iCal
            calendar_name: Nom à donner au calendrier

        Returns:
            Résultat de l'import
        """
        start_time = datetime.now()

        try:
            response = self.http_client.get(ical_url)
            response.raise_for_status()
            ical_content = response.text
        except Exception as e:
            return SyncResult(
                success=False,
                message=f"Impossible de télécharger le calendrier: {e}",
                errors=[str(e)],
            )

        # Parser le contenu iCal
        events = ICalGenerator.parse_ical(ical_content)

        if not events:
            return SyncResult(success=False, message="Aucun événement trouvé dans le calendrier")

        # Sauvegarder les événements
        imported_count = 0
        errors = []

        with obtenir_contexte_db() as db:
            for event in events:
                try:
                    # Créer un CalendarEvent dans la base
                    cal_event = CalendarEvent(
                        titre=event.title,
                        description=event.description,
                        date_debut=event.start_time.date(),
                        date_fin=event.end_time.date() if event.end_time else None,
                        source_externe=f"ical:{ical_url}",
                        external_id=event.external_id,
                    )

                    # Vérifier si existe déjà (par external_id)
                    existing = (
                        db.query(CalendarEvent)
                        .filter(CalendarEvent.external_id == event.external_id)
                        .first()
                    )

                    if existing:
                        # Mettre à jour
                        existing.titre = event.title
                        existing.description = event.description
                        existing.date_debut = event.start_time.date()
                    else:
                        db.add(cal_event)

                    imported_count += 1
                except Exception as e:
                    errors.append(f"Erreur import '{event.title}': {e}")

            db.commit()

        duration = (datetime.now() - start_time).total_seconds()

        return SyncResult(
            success=len(errors) == 0,
            message=f"{imported_count} événements importés",
            events_imported=imported_count,
            errors=errors,
            duration_seconds=duration,
        )

    # ═══════════════════════════════════════════════════════════
    # NOTE: Méthodes Google Calendar déléguées via GoogleCalendarMixin
    # (voir google_calendar.py)
    #
    # Méthodes héritées: get_google_auth_url, handle_google_callback,
    # sync_google_calendar, export_planning_to_google, _import_from_google,
    # _export_to_google, _export_meal_to_google, _export_activity_to_google,
    # _find_google_event_by_matanne_id, _refresh_google_token,
    # _import_events_to_db, _save_config_to_db, _remove_config_from_db
    # ═══════════════════════════════════════════════════════════

    @avec_session_db
    def ajouter_calendrier_externe(
        self,
        user_id: UUID | str,
        provider: str,
        nom: str,
        url: str | None = None,
        credentials: dict | None = None,
        db: Session = None,
    ) -> CalendrierExterne:
        """
        Ajoute un calendrier externe dans la DB.

        Args:
            user_id: UUID de l'utilisateur
            provider: google, apple, outlook, ical
            nom: Nom du calendrier
            url: URL iCal (optionnel)
            credentials: Tokens OAuth (optionnel)
            db: Session SQLAlchemy

        Returns:
            Calendrier créé
        """
        calendrier = CalendrierExterne(
            provider=provider,
            nom=nom,
            url=url,
            credentials=credentials or {},
            user_id=UUID(str(user_id)),
        )
        db.add(calendrier)
        db.commit()
        db.refresh(calendrier)
        return calendrier

    @avec_session_db
    def lister_calendriers_utilisateur(
        self,
        user_id: UUID | str,
        db: Session = None,
    ) -> list[CalendrierExterne]:
        """
        Liste les calendriers externes d'un utilisateur.

        Args:
            user_id: UUID de l'utilisateur
            db: Session SQLAlchemy

        Returns:
            Liste des calendriers
        """
        return (
            db.query(CalendrierExterne)
            .filter(
                CalendrierExterne.user_id == UUID(str(user_id)),
                CalendrierExterne.enabled == True,
            )
            .all()
        )

    @avec_session_db
    def sauvegarder_evenement_calendrier(
        self,
        calendrier_id: int,
        event: CalendarEventExternal,
        user_id: UUID | str | None = None,
        db: Session = None,
    ) -> EvenementCalendrier:
        """
        Sauvegarde un événement de calendrier externe.

        Args:
            calendrier_id: ID du calendrier source
            event: Événement Pydantic
            user_id: UUID de l'utilisateur
            db: Session SQLAlchemy

        Returns:
            Événement créé
        """
        # Chercher si l'événement existe déjà
        existing = (
            db.query(EvenementCalendrier)
            .filter(
                EvenementCalendrier.uid == event.external_id,
                EvenementCalendrier.user_id == UUID(str(user_id)) if user_id else True,
            )
            .first()
        )

        if existing:
            existing.titre = event.title
            existing.description = event.description
            existing.date_debut = event.start_time
            existing.date_fin = event.end_time
            existing.lieu = event.location
            existing.all_day = event.all_day
            db.commit()
            db.refresh(existing)
            return existing

        db_event = EvenementCalendrier(
            uid=event.external_id or str(uuid4()),
            titre=event.title,
            description=event.description,
            date_debut=event.start_time,
            date_fin=event.end_time,
            lieu=event.location,
            all_day=event.all_day,
            source_calendrier_id=calendrier_id,
            user_id=UUID(str(user_id)) if user_id else None,
        )
        db.add(db_event)
        db.commit()
        db.refresh(db_event)
        return db_event

    @avec_session_db
    def lister_evenements_calendrier(
        self,
        user_id: UUID | str,
        date_debut: date | None = None,
        date_fin: date | None = None,
        calendrier_id: int | None = None,
        db: Session = None,
    ) -> list[EvenementCalendrier]:
        """
        Liste les événements de calendrier.

        Args:
            user_id: UUID de l'utilisateur
            date_debut: Date de début (filtre)
            date_fin: Date de fin (filtre)
            calendrier_id: ID du calendrier source (filtre)
            db: Session SQLAlchemy

        Returns:
            Liste des événements
        """
        query = db.query(EvenementCalendrier).filter(
            EvenementCalendrier.user_id == UUID(str(user_id))
        )

        if date_debut:
            query = query.filter(
                EvenementCalendrier.date_debut >= datetime.combine(date_debut, datetime.min.time())
            )
        if date_fin:
            query = query.filter(
                EvenementCalendrier.date_debut <= datetime.combine(date_fin, datetime.max.time())
            )
        if calendrier_id:
            query = query.filter(EvenementCalendrier.source_calendrier_id == calendrier_id)

        return query.order_by(EvenementCalendrier.date_debut).all()


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


from src.services.core.registry import service_factory


@service_factory("calendrier", tags={"famille", "integration"})
def obtenir_service_synchronisation_calendrier() -> CalendarSyncService:
    """Factory pour le service de synchronisation calendrier (thread-safe via registre)."""
    return CalendarSyncService()


def get_calendar_sync_service() -> CalendarSyncService:
    """Factory pour le service de synchronisation calendrier (alias anglais)."""
    return obtenir_service_synchronisation_calendrier()
