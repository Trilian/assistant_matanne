"""
Mixin Google Calendar pour CalendarSyncService.

Compose les sous-mixins spécialisés:
- GoogleAuthMixin: Authentification OAuth2
- GoogleExportMixin: Export repas/activités
- GoogleTokensMixin: Gestion tokens et persistance

Ce fichier conserve la synchronisation bidirectionnelle et l'import.
"""

from __future__ import annotations

import logging
from datetime import date, datetime, timedelta
from typing import TYPE_CHECKING

from src.core.db import obtenir_contexte_db
from src.core.decorators import avec_resilience
from src.core.models import EvenementPlanning

from .google_auth import GoogleAuthMixin
from .google_export import GoogleExportMixin
from .google_tokens import GoogleTokensMixin
from .schemas import (
    CalendarEventExternal,
    ConfigCalendrierExterne,
    DirectionSync,
    FournisseurCalendrier,
    SyncResult,
)

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = ["GoogleCalendarMixin"]


class GoogleCalendarMixin(GoogleAuthMixin, GoogleExportMixin, GoogleTokensMixin):
    """
    Mixin fournissant l'intégration Google Calendar.

    Compose:
    - GoogleAuthMixin: OAuth2 (get_google_auth_url, handle_google_callback)
    - GoogleExportMixin: Export (repas, activités, déduplication)
    - GoogleTokensMixin: Tokens et persistance DB

    Attend d'être mixé dans une classe possédant:
    - self.http_client: httpx.Client
    - self._configs: dict[str, ConfigCalendrierExterne]
    - self.add_calendar(config) -> str
    """

    # ═══════════════════════════════════════════════════════════
    # GOOGLE CALENDAR — SYNCHRONISATION
    # ═══════════════════════════════════════════════════════════

    @avec_resilience(
        retry=2, timeout_s=60, fallback=SyncResult(success=False, message="Erreur réseau")
    )
    def sync_google_calendar(self, config: ConfigCalendrierExterne) -> SyncResult:
        """
        Synchronise avec Google Calendar (import + export bidirectionnel).

        Args:
            config: Configuration du calendrier Google

        Returns:
            Résultat de la synchronisation
        """
        if config.provider != FournisseurCalendrier.GOOGLE:
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
            if config.sync_direction in [DirectionSync.IMPORT_ONLY, DirectionSync.BIDIRECTIONAL]:
                events_imported = self._import_from_google(config, headers)

            # ════════════════════════════════════════════════
            # 2. EXPORT: App → Google (si autorisé)
            # ════════════════════════════════════════════════
            if config.sync_direction in [DirectionSync.EXPORT_ONLY, DirectionSync.BIDIRECTIONAL]:
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

    def _import_from_google(self, config: ConfigCalendrierExterne, headers: dict) -> int:
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
                        db.query(EvenementPlanning)
                        .filter(EvenementPlanning.external_id == event.external_id)
                        .first()
                    )

                    if existing:
                        existing.titre = event.title
                        existing.description = event.description
                    else:
                        cal_event = EvenementPlanning(
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
    # GOOGLE CALENDAR — EXPORT PLANNING COMPLET
    # ═══════════════════════════════════════════════════════════

    @avec_resilience(
        retry=2, timeout_s=60, fallback=SyncResult(success=False, message="Erreur réseau export")
    )
    def export_planning_to_google(
        self,
        user_id: str,
        config: ConfigCalendrierExterne,
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
        if config.provider != FournisseurCalendrier.GOOGLE:
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
