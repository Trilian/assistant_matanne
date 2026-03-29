"""Service léger de partage public de recettes via token temporaire."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from secrets import token_urlsafe
from threading import Lock
from typing import Any


_tokens_partage: dict[str, dict[str, Any]] = {}
_verrou_tokens = Lock()


def creer_lien_partage_recette(recette_id: int, duree_heures: int = 48) -> tuple[str, datetime]:
    """Crée un token de partage temporaire pour une recette."""
    expires_at = datetime.now(UTC) + timedelta(hours=max(1, duree_heures))
    token = token_urlsafe(24)

    with _verrou_tokens:
        _tokens_partage[token] = {
            "recette_id": recette_id,
            "expires_at": expires_at,
        }

    return token, expires_at


def obtenir_recette_partagee(token: str) -> int | None:
    """Retourne l'ID de recette si le token est valide, sinon None."""
    with _verrou_tokens:
        payload = _tokens_partage.get(token)
        if not payload:
            return None

        expires_at = payload.get("expires_at")
        if not isinstance(expires_at, datetime) or expires_at < datetime.now(UTC):
            _tokens_partage.pop(token, None)
            return None

        recette_id = payload.get("recette_id")
        return int(recette_id) if recette_id is not None else None
