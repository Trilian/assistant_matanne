"""
Service Google Calendar — Synchronisation planning repas ↔ Google Calendar.

Flux OAuth2 :
1. GET /api/v1/calendrier/google/auth → redirige vers Google consent
2. GET /api/v1/calendrier/google/callback → reçoit le code, échange en token
3. POST /api/v1/calendrier/google/sync → pousse le planning actif vers Google Calendar

Les tokens sont stockés en mémoire (instance) pour le MVP.
En production, il faudra les persister en base.
"""

import logging
from datetime import date, datetime, timedelta

import httpx

from src.core.config import obtenir_parametres

logger = logging.getLogger(__name__)

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_CALENDAR_API = "https://www.googleapis.com/calendar/v3"

# Stockage MVP des tokens (en production → base de données)
_tokens: dict[str, dict] = {}


def construire_url_auth() -> str | None:
    """Construit l'URL d'autorisation Google OAuth2."""
    settings = obtenir_parametres()

    if not settings.GOOGLE_CLIENT_ID:
        return None

    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "https://www.googleapis.com/auth/calendar.events",
        "access_type": "offline",
        "prompt": "consent",
    }
    query = "&".join(f"{k}={v}" for k, v in params.items())
    return f"{GOOGLE_AUTH_URL}?{query}"


async def echanger_code_oauth(code: str) -> dict | None:
    """Échange le code OAuth2 contre un access_token + refresh_token.

    Args:
        code: Code d'autorisation reçu de Google

    Returns:
        Dict avec access_token, refresh_token, expires_in, ou None si échec
    """
    settings = obtenir_parametres()

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            },
        )

        try:
            resp.raise_for_status()
        except Exception:
            logger.error(f"❌ Échec échange OAuth Google : {getattr(resp, 'text', '')}")
            return None

        tokens = resp.json()
        # Stocker les tokens (MVP : mémoire)
        _tokens["google"] = {
            "access_token": tokens["access_token"],
            "refresh_token": tokens.get("refresh_token"),
            "expires_at": datetime.now().timestamp() + tokens.get("expires_in", 3600),
        }
        logger.info("✅ Tokens Google Calendar obtenus")
        return tokens


async def _obtenir_access_token() -> str | None:
    """Retourne un access_token valide, en rafraîchissant si nécessaire."""
    stored = _tokens.get("google")
    if not stored:
        return None

    # Token encore valide ?
    if stored["expires_at"] > datetime.now().timestamp() + 60:
        return stored["access_token"]

    # Rafraîchir
    refresh_token = stored.get("refresh_token")
    if not refresh_token:
        logger.warning("Pas de refresh_token Google — re-auth nécessaire")
        return None

    settings = obtenir_parametres()
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token",
            },
        )

        if resp.status_code != 200:
            logger.error(f"❌ Échec refresh token Google : {resp.text}")
            return None

        tokens = resp.json()
        stored["access_token"] = tokens["access_token"]
        stored["expires_at"] = datetime.now().timestamp() + tokens.get("expires_in", 3600)
        return tokens["access_token"]


async def synchroniser_planning_google(repas_list: list[dict]) -> dict:
    """Pousse les repas du planning actif vers Google Calendar.

    Args:
        repas_list: Liste de dicts {date, type_repas, recette_nom, notes}

    Returns:
        Dict avec created, errors
    """
    token = await _obtenir_access_token()
    if not token:
        return {"created": 0, "errors": ["Non authentifié Google — lancez /google/auth"]}

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    created = 0
    errors = []

    async with httpx.AsyncClient(timeout=15.0) as client:
        for repas in repas_list:
            try:
                repas_date = repas["date"]
                if isinstance(repas_date, str):
                    repas_date = date.fromisoformat(repas_date)

                # Horaires par type de repas
                heures = {"petit_dejeuner": (7, 8), "dejeuner": (12, 13), "gouter": (16, 17), "diner": (19, 20)}
                h_debut, h_fin = heures.get(repas.get("type_repas", "dejeuner"), (12, 13))

                event = {
                    "summary": f"🍽️ {repas.get('recette_nom', repas.get('notes', 'Repas'))}",
                    "description": repas.get("notes", ""),
                    "start": {
                        "dateTime": datetime(repas_date.year, repas_date.month, repas_date.day, h_debut).isoformat(),
                        "timeZone": "Europe/Paris",
                    },
                    "end": {
                        "dateTime": datetime(repas_date.year, repas_date.month, repas_date.day, h_fin).isoformat(),
                        "timeZone": "Europe/Paris",
                    },
                    "colorId": "9",  # Bleuet
                }

                resp = await client.post(
                    f"{GOOGLE_CALENDAR_API}/calendars/primary/events",
                    json=event,
                    headers=headers,
                )

                if resp.status_code in (200, 201):
                    created += 1
                else:
                    errors.append(f"{repas.get('recette_nom', '?')}: {resp.status_code}")

            except Exception as e:
                errors.append(f"{repas.get('recette_nom', '?')}: {e}")

    logger.info(f"📅 Google Calendar sync : {created} créés, {len(errors)} erreurs")
    return {"created": created, "errors": errors}
