"""
Mixin de gestion des tokens et persistance Google Calendar.

Extrait de google_calendar.py pour réduire sa taille.
Gère:
- Rafraîchissement des tokens OAuth2
- Sauvegarde/suppression de la configuration en base
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from uuid import UUID

from src.core.db import obtenir_contexte_db
from src.core.models import CalendrierExterne

from .schemas import ConfigCalendrierExterne

logger = logging.getLogger(__name__)

__all__ = ["GoogleTokensMixin"]


class GoogleTokensMixin:
    """
    Mixin fournissant la gestion des tokens et de la persistance.

    Attend d'être mixé dans une classe possédant:
    - self.http_client: httpx.Client
    """

    def _refresh_google_token(self, config: ConfigCalendrierExterne):
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

    def _save_config_to_db(self, config: ConfigCalendrierExterne):
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
