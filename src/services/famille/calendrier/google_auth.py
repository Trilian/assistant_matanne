"""
Mixin d'authentification OAuth2 pour Google Calendar.

Extrait de google_calendar.py pour réduire sa taille.
Gère l'authentification OAuth2:
- Génération URL d'autorisation
- Gestion du callback OAuth2
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from .schemas import ConfigCalendrierExterne, FournisseurCalendrier

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = ["GoogleAuthMixin"]


class GoogleAuthMixin:
    """
    Mixin fournissant l'authentification OAuth2 Google Calendar.

    Attend d'être mixé dans une classe possédant:
    - self.http_client: httpx.Client
    - self.add_calendar(config) -> str
    """

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
    ) -> ConfigCalendrierExterne | None:
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
            config = ConfigCalendrierExterne(
                user_id=user_id,
                provider=FournisseurCalendrier.GOOGLE,
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
