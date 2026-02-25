"""
Mixin d'export d'événements vers Google Calendar.

Extrait de google_calendar.py pour réduire sa taille.
Gère l'export de repas et activités vers Google Calendar:
- Export de repas planifiés
- Export d'activités familiales
- Recherche d'événements existants (déduplication)
"""

from __future__ import annotations

import logging
from datetime import date, datetime, timedelta
from typing import TYPE_CHECKING

from sqlalchemy.orm import joinedload

from src.core.db import obtenir_contexte_db
from src.core.models import ActiviteFamille, Planning, Repas

from .schemas import ConfigCalendrierExterne

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

__all__ = ["GoogleExportMixin"]


class GoogleExportMixin:
    """
    Mixin fournissant l'export vers Google Calendar.

    Attend d'être mixé dans une classe possédant:
    - self.http_client: httpx.Client
    """

    def _export_to_google(self, config: ConfigCalendrierExterne, headers: dict) -> int:
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
                .options(joinedload(Repas.recette))
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
                db.query(ActiviteFamille)
                .filter(
                    ActiviteFamille.date_prevue >= start,
                    ActiviteFamille.date_prevue <= end,
                    ActiviteFamille.statut != "annulé",
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
        self, repas: Repas, config: ConfigCalendrierExterne, headers: dict, db: Session
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
        self, activity: ActiviteFamille, config: ConfigCalendrierExterne, headers: dict, db: Session
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
        except Exception as e:
            logger.debug("Recherche événement échouée: %s", e)
            return None
