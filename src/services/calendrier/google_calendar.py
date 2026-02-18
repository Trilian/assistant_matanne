"""
Mixin Google Calendar pour CalendarSyncService.

Contient toutes les méthodes d'intégration Google Calendar:
- Authentification OAuth2
- Synchronisation bidirectionnelle
- Export/Import d'événements
- Gestion des tokens et de la persistance
"""

from __future__ import annotations

import logging
from datetime import date, datetime, timedelta
from typing import TYPE_CHECKING
from uuid import UUID

from src.core.database import obtenir_contexte_db
from src.core.models import (
    CalendarEvent,
    CalendrierExterne,
    FamilyActivity,
    Planning,
    Repas,
)

from .schemas import (
    CalendarEventExternal,
    CalendarProvider,
    ExternalCalendarConfig,
    SyncDirection,
    SyncResult,
)

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

__all__ = ["GoogleCalendarMixin"]


class GoogleCalendarMixin:
    """
    Mixin fournissant l'intégration Google Calendar.

    Attend d'être mixé dans une classe possédant:
    - self.http_client: httpx.Client
    - self._configs: dict[str, ExternalCalendarConfig]
    - self.add_calendar(config) -> str
    """

    # ═══════════════════════════════════════════════════════════
    # GOOGLE CALENDAR — AUTHENTIFICATION
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

    # ═══════════════════════════════════════════════════════════
    # GOOGLE CALENDAR — SYNCHRONISATION
    # ═══════════════════════════════════════════════════════════

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

    # ═══════════════════════════════════════════════════════════
    # GOOGLE CALENDAR — IMPORT
    # ═══════════════════════════════════════════════════════════

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
    # GOOGLE CALENDAR — EXPORT
    # ═══════════════════════════════════════════════════════════

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

    # ═══════════════════════════════════════════════════════════
    # GOOGLE CALENDAR — TOKENS & PERSISTANCE
    # ═══════════════════════════════════════════════════════════

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
