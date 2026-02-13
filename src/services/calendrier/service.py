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

from src.core.database import obtenir_contexte_db
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
from .schemas import (
    CalendarEventExternal,
    CalendarProvider,
    ExternalCalendarConfig,
    SyncDirection,
    SyncResult,
)

logger = logging.getLogger(__name__)


class CalendarSyncService:
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
    # GOOGLE CALENDAR
    # ═══════════════════════════════════════════════════════════

    def get_google_auth_url(self, user_id: str, redirect_uri: str) -> str:
        """
        Génère l'URL d'autorisation Google Calendar.

        Args:
            user_id: ID de l'utilisateur
            redirect_uri: URL de callback

        Returns:
            URL d'autorisation OAuth2
        """
        from src.core.config import obtenir_parametres

        params = obtenir_parametres()
        client_id = getattr(params, "GOOGLE_CLIENT_ID", "")

        if not client_id:
            raise ValueError("GOOGLE_CLIENT_ID non configuré")

        # Scope pour lecture ET écriture du calendrier
        scope = "https://www.googleapis.com/auth/calendar"

        auth_url = (
            f"https://accounts.google.com/o/oauth2/v2/auth?"
            f"client_id={client_id}&"
            f"redirect_uri={redirect_uri}&"
            f"response_type=code&"
            f"scope={scope}&"
            f"access_type=offline&"
            f"state={user_id}"
        )

        return auth_url

    def handle_google_callback(
        self,
        user_id: str,
        code: str,
        redirect_uri: str,
    ) -> ExternalCalendarConfig | None:
        """
        Gère le callback OAuth2 Google.

        Args:
            user_id: ID de l'utilisateur
            code: Code d'autorisation
            redirect_uri: URL de callback utilisée

        Returns:
            Configuration du calendrier ajouté
        """
        from src.core.config import obtenir_parametres

        params = obtenir_parametres()
        client_id = getattr(params, "GOOGLE_CLIENT_ID", "")
        client_secret = getattr(params, "GOOGLE_CLIENT_SECRET", "")

        if not client_id or not client_secret:
            logger.error("Google OAuth non configuré")
            return None

        try:
            # Échanger le code contre des tokens
            response = self.http_client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code",
                },
            )
            response.raise_for_status()
            tokens = response.json()

            # Créer la configuration
            config = ExternalCalendarConfig(
                user_id=user_id,
                provider=CalendarProvider.GOOGLE,
                name="Google Calendar",
                access_token=tokens["access_token"],
                refresh_token=tokens.get("refresh_token", ""),
                token_expiry=datetime.now() + timedelta(seconds=tokens.get("expires_in", 3600)),
            )

            self.add_calendar(config)
            return config

        except Exception as e:
            logger.error(f"Erreur callback Google: {e}")
            return None

    def sync_google_calendar(self, config: ExternalCalendarConfig) -> SyncResult:
        """
        Synchronise avec Google Calendar (import + export bidirectionnel).

        Args:
            config: Configuration du calendrier Google

        Returns:
            Résultat de la synchronisation
        """
        if config.provider != CalendarProvider.GOOGLE:
            return SyncResult(success=False, message="Pas un calendrier Google")

        # Vérifier/rafraîchir le token
        if config.token_expiry and config.token_expiry < datetime.now():
            self._refresh_google_token(config)

        start_time = datetime.now()
        events_imported = 0
        events_exported = 0
        errors = []

        try:
            headers = {"Authorization": f"Bearer {config.access_token}"}

            # ════════════════════════════════════════════════
            # 1. IMPORT: Google → App (si autorisé)
            # ════════════════════════════════════════════════
            if config.sync_direction in [SyncDirection.IMPORT_ONLY, SyncDirection.BIDIRECTIONAL]:
                events_imported = self._import_from_google(config, headers)

            # ════════════════════════════════════════════════
            # 2. EXPORT: App → Google (si autorisé)
            # ════════════════════════════════════════════════
            if config.sync_direction in [SyncDirection.EXPORT_ONLY, SyncDirection.BIDIRECTIONAL]:
                events_exported = self._export_to_google(config, headers)

            config.last_sync = datetime.now()
            self._save_config_to_db(config)

            duration = (datetime.now() - start_time).total_seconds()

            return SyncResult(
                success=True,
                message=f"Sync Google réussie: {events_imported} importés, {events_exported} exportés",
                events_imported=events_imported,
                events_exported=events_exported,
                duration_seconds=duration,
            )

        except Exception as e:
            logger.error(f"Erreur sync Google: {e}")
            return SyncResult(success=False, message=str(e), errors=[str(e)])

    def _import_from_google(self, config: ExternalCalendarConfig, headers: dict) -> int:
        """Importe les événements depuis Google Calendar."""
        time_min = datetime.now().isoformat() + "Z"
        time_max = (datetime.now() + timedelta(days=30)).isoformat() + "Z"

        response = self.http_client.get(
            "https://www.googleapis.com/calendar/v3/calendars/primary/events",
            headers=headers,
            params={
                "timeMin": time_min,
                "timeMax": time_max,
                "singleEvents": "true",
                "orderBy": "startTime",
            },
        )
        response.raise_for_status()
        data = response.json()

        events = []
        for item in data.get("items", []):
            start = item.get("start", {})
            end = item.get("end", {})

            start_dt = start.get("dateTime") or start.get("date")
            end_dt = end.get("dateTime") or end.get("date")

            if start_dt:
                events.append(
                    CalendarEventExternal(
                        external_id=item["id"],
                        title=item.get("summary", "Sans titre"),
                        description=item.get("description", ""),
                        start_time=datetime.fromisoformat(start_dt.replace("Z", "+00:00")),
                        end_time=datetime.fromisoformat(end_dt.replace("Z", "+00:00"))
                        if end_dt
                        else datetime.now(),
                        all_day="date" in start,
                        location=item.get("location", ""),
                    )
                )

        return self._import_events_to_db(events)

    def _export_to_google(self, config: ExternalCalendarConfig, headers: dict) -> int:
        """
        Exporte les repas et activités vers Google Calendar.

        Crée ou met à jour les événements dans le calendrier Google de l'utilisateur.
        """
        exported_count = 0

        with obtenir_contexte_db() as db:
            # Récupérer les repas des 30 prochains jours
            start = date.today()
            end = date.today() + timedelta(days=30)

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
                try:
                    event_id = self._export_meal_to_google(repas, config, headers, db)
                    if event_id:
                        exported_count += 1
                except Exception as e:
                    logger.warning(f"Erreur export repas {repas.id}: {e}")

            # Récupérer les activités
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
                try:
                    event_id = self._export_activity_to_google(activity, config, headers, db)
                    if event_id:
                        exported_count += 1
                except Exception as e:
                    logger.warning(f"Erreur export activité {activity.id}: {e}")

        logger.info(f"✅ Exporté {exported_count} événements vers Google Calendar")
        return exported_count

    def _export_meal_to_google(
        self, repas: Repas, config: ExternalCalendarConfig, headers: dict, db: Session
    ) -> str | None:
        """Exporte un repas vers Google Calendar."""
        # Déterminer l'heure selon le type de repas
        meal_hours = {
            "petit_déjeuner": 8,
            "déjeuner": 12,
            "goûter": 16,
            "dîner": 19,
        }
        hour = meal_hours.get(repas.type_repas, 12)

        start_time = datetime.combine(repas.date_repas, datetime.min.time().replace(hour=hour))
        end_time = start_time + timedelta(hours=1)

        title = f"🍽️ {repas.type_repas.replace('_', ' ').title()}"
        if repas.recette:
            title += f": {repas.recette.nom}"

        description = repas.notes or ""
        if repas.recette and repas.recette.description:
            description += f"\n\n{repas.recette.description}"

        # ID unique pour éviter les doublons
        matanne_event_id = f"matanne-meal-{repas.id}"

        event_body = {
            "summary": title,
            "description": description,
            "start": {"dateTime": start_time.isoformat(), "timeZone": "Europe/Paris"},
            "end": {"dateTime": end_time.isoformat(), "timeZone": "Europe/Paris"},
            "extendedProperties": {
                "private": {
                    "matanne_type": "meal",
                    "matanne_id": str(repas.id),
                }
            },
        }

        # Vérifier si l'événement existe déjà
        existing = self._find_google_event_by_matanne_id(matanne_event_id, headers)

        if existing:
            # Mettre à jour
            response = self.http_client.patch(
                f"https://www.googleapis.com/calendar/v3/calendars/primary/events/{existing['id']}",
                headers={**headers, "Content-Type": "application/json"},
                json=event_body,
            )
        else:
            # Créer
            response = self.http_client.post(
                "https://www.googleapis.com/calendar/v3/calendars/primary/events",
                headers={**headers, "Content-Type": "application/json"},
                json=event_body,
            )

        response.raise_for_status()
        return response.json().get("id")

    def _export_activity_to_google(
        self, activity: FamilyActivity, config: ExternalCalendarConfig, headers: dict, db: Session
    ) -> str | None:
        """Exporte une activité vers Google Calendar."""
        start_time = datetime.combine(activity.date_prevue, datetime.min.time().replace(hour=10))
        duration_hours = activity.duree_heures or 2
        end_time = start_time + timedelta(hours=duration_hours)

        event_body = {
            "summary": f"👨‍👩‍👧 {activity.titre}",
            "description": activity.description or "",
            "location": activity.lieu or "",
            "start": {"dateTime": start_time.isoformat(), "timeZone": "Europe/Paris"},
            "end": {"dateTime": end_time.isoformat(), "timeZone": "Europe/Paris"},
            "colorId": "9",  # Bleu pour les activités
            "extendedProperties": {
                "private": {
                    "matanne_type": "activity",
                    "matanne_id": str(activity.id),
                }
            },
        }

        matanne_event_id = f"matanne-activity-{activity.id}"
        existing = self._find_google_event_by_matanne_id(matanne_event_id, headers)

        if existing:
            response = self.http_client.patch(
                f"https://www.googleapis.com/calendar/v3/calendars/primary/events/{existing['id']}",
                headers={**headers, "Content-Type": "application/json"},
                json=event_body,
            )
        else:
            response = self.http_client.post(
                "https://www.googleapis.com/calendar/v3/calendars/primary/events",
                headers={**headers, "Content-Type": "application/json"},
                json=event_body,
            )

        response.raise_for_status()
        return response.json().get("id")

    def _find_google_event_by_matanne_id(self, matanne_id: str, headers: dict) -> dict | None:
        """Recherche un événement Google par son ID Matanne."""
        try:
            # Recherche par propriété étendue
            response = self.http_client.get(
                "https://www.googleapis.com/calendar/v3/calendars/primary/events",
                headers=headers,
                params={
                    "privateExtendedProperty": f"matanne_id={matanne_id.split('-')[-1]}",
                    "maxResults": 1,
                },
            )
            response.raise_for_status()
            items = response.json().get("items", [])
            return items[0] if items else None
        except Exception:
            return None

    def export_planning_to_google(
        self,
        user_id: str,
        config: ExternalCalendarConfig,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> SyncResult:
        """
        Export complet du planning vers Google Calendar.

        Args:
            user_id: ID utilisateur
            config: Configuration Google Calendar
            start_date: Date de début (défaut: aujourd'hui)
            end_date: Date de fin (défaut: +30 jours)

        Returns:
            Résultat de l'export
        """
        if config.provider != CalendarProvider.GOOGLE:
            return SyncResult(success=False, message="Pas un calendrier Google")

        # Vérifier/rafraîchir le token
        if config.token_expiry and config.token_expiry < datetime.now():
            self._refresh_google_token(config)

        headers = {"Authorization": f"Bearer {config.access_token}"}

        start_time = datetime.now()
        exported_count = self._export_to_google(config, headers)
        duration = (datetime.now() - start_time).total_seconds()

        return SyncResult(
            success=True,
            message=f"{exported_count} événements exportés vers Google Calendar",
            events_exported=exported_count,
            duration_seconds=duration,
        )

    def _refresh_google_token(self, config: ExternalCalendarConfig):
        """Rafraîchit le token Google."""
        from src.core.config import obtenir_parametres

        params = obtenir_parametres()

        try:
            response = self.http_client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": getattr(params, "GOOGLE_CLIENT_ID", ""),
                    "client_secret": getattr(params, "GOOGLE_CLIENT_SECRET", ""),
                    "refresh_token": config.refresh_token,
                    "grant_type": "refresh_token",
                },
            )
            response.raise_for_status()
            tokens = response.json()

            config.access_token = tokens["access_token"]
            config.token_expiry = datetime.now() + timedelta(seconds=tokens.get("expires_in", 3600))
            self._save_config_to_db(config)

        except Exception as e:
            logger.error(f"Erreur refresh token Google: {e}")

    def _import_events_to_db(self, events: list[CalendarEventExternal]) -> int:
        """Importe les événements dans la base."""
        count = 0

        with obtenir_contexte_db() as db:
            for event in events:
                try:
                    existing = (
                        db.query(CalendarEvent)
                        .filter(CalendarEvent.external_id == event.external_id)
                        .first()
                    )

                    if existing:
                        existing.titre = event.title
                        existing.description = event.description
                    else:
                        cal_event = CalendarEvent(
                            titre=event.title,
                            description=event.description,
                            date_debut=event.start_time.date(),
                            date_fin=event.end_time.date(),
                            external_id=event.external_id,
                        )
                        db.add(cal_event)

                    count += 1
                except Exception as e:
                    logger.warning(f"Erreur import événement: {e}")

            db.commit()

        return count

    # ═══════════════════════════════════════════════════════════
    # PERSISTANCE BASE DE DONNÉES
    # ═══════════════════════════════════════════════════════════

    def _save_config_to_db(self, config: ExternalCalendarConfig):
        """Sauvegarde la configuration en base."""
        with obtenir_contexte_db() as db:
            # Chercher config existante
            existing = (
                db.query(CalendrierExterne)
                .filter(CalendrierExterne.id == int(config.id) if config.id.isdigit() else False)
                .first()
            )

            if existing:
                existing.provider = config.provider.value
                existing.nom = config.name
                existing.url = config.ical_url
                existing.credentials = {
                    "access_token": config.access_token,
                    "refresh_token": config.refresh_token,
                    "token_expiry": config.token_expiry.isoformat()
                    if config.token_expiry
                    else None,
                }
                existing.enabled = config.is_active
                existing.sync_direction = config.sync_direction.value
                existing.last_sync = config.last_sync
            else:
                db_config = CalendrierExterne(
                    provider=config.provider.value,
                    nom=config.name,
                    url=config.ical_url,
                    credentials={
                        "access_token": config.access_token,
                        "refresh_token": config.refresh_token,
                        "token_expiry": config.token_expiry.isoformat()
                        if config.token_expiry
                        else None,
                    },
                    enabled=config.is_active,
                    sync_direction=config.sync_direction.value,
                    user_id=UUID(config.user_id) if config.user_id else None,
                )
                db.add(db_config)

            db.commit()

    def _remove_config_from_db(self, calendar_id: str):
        """Supprime la configuration de la base."""
        with obtenir_contexte_db() as db:
            if calendar_id.isdigit():
                config = (
                    db.query(CalendrierExterne)
                    .filter(CalendrierExterne.id == int(calendar_id))
                    .first()
                )
                if config:
                    db.delete(config)
                    db.commit()

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


_calendar_sync_service: CalendarSyncService | None = None


def get_calendar_sync_service() -> CalendarSyncService:
    """Factory pour le service de synchronisation calendrier."""
    global _calendar_sync_service
    if _calendar_sync_service is None:
        _calendar_sync_service = CalendarSyncService()
    return _calendar_sync_service
