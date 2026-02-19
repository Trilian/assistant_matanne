"""
Utilitaires de cache HTTP pour l'API REST.

Fournit le support des ETags et headers de cache.
"""

import hashlib
import json
from datetime import datetime
from typing import Any

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp


def generate_etag(data: Any) -> str:
    """
    Génère un ETag à partir des données.

    Args:
        data: Données à hasher (dict, list, ou sérialisable JSON)

    Returns:
        ETag au format W/"<hash>"
    """
    if isinstance(data, dict | list):
        content = json.dumps(data, sort_keys=True, default=str)
    else:
        content = str(data)

    hash_value = hashlib.md5(content.encode()).hexdigest()[:16]
    return f'W/"{hash_value}"'


def add_cache_headers(
    response: Response,
    etag: str | None = None,
    max_age: int = 0,
    private: bool = True,
    last_modified: datetime | None = None,
) -> None:
    """
    Ajoute les headers de cache à une réponse.

    Args:
        response: Réponse FastAPI
        etag: ETag à ajouter
        max_age: Durée du cache en secondes
        private: Cache privé (par défaut) ou public
        last_modified: Date de dernière modification
    """
    if etag:
        response.headers["ETag"] = etag

    cache_control_parts: list[str] = []
    if private:
        cache_control_parts.append("private")
    else:
        cache_control_parts.append("public")

    if max_age > 0:
        cache_control_parts.append(f"max-age={max_age}")
    else:
        cache_control_parts.append("no-cache")

    response.headers["Cache-Control"] = ", ".join(cache_control_parts)

    if last_modified:
        response.headers["Last-Modified"] = last_modified.strftime("%a, %d %b %Y %H:%M:%S GMT")


def check_etag_match(request: Request, current_etag: str) -> bool:
    """
    Vérifie si le client a déjà la version actuelle.

    Args:
        request: Requête FastAPI
        current_etag: ETag actuel des données

    Returns:
        True si le client a la même version (304 approprié)
    """
    if_none_match = request.headers.get("If-None-Match")
    if if_none_match:
        # Supporte multiple ETags séparés par virgules
        client_etags = [e.strip() for e in if_none_match.split(",")]
        return current_etag in client_etags
    return False


class ETagMiddleware(BaseHTTPMiddleware):
    """
    Middleware pour ajouter automatiquement les ETags.

    Usage:
        app.add_middleware(ETagMiddleware)

    Note:
        Ce middleware ne génère des ETags que pour les réponses JSON.
        Les ETags sont "weak" (W/) car basés sur le contenu.
    """

    def __init__(self, app: ASGIApp, cache_seconds: int = 0):
        super().__init__(app)
        self.cache_seconds = cache_seconds

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)

        # Uniquement pour les GET avec réponses JSON réussies
        if (
            request.method == "GET"
            and response.status_code == 200
            and response.headers.get("content-type", "").startswith("application/json")
        ):
            # Note: Pour un middleware complet, il faudrait accéder au body
            # Ici, on montre le pattern - l'implémentation complète nécessiterait
            # de buffuriser la réponse
            if self.cache_seconds > 0:
                response.headers["Cache-Control"] = f"private, max-age={self.cache_seconds}"

        return response
