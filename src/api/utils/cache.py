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

    Utilise SHA-256 tronqué (A3: remplacement de MD5 déprécié).

    Args:
        data: Données à hasher (dict, list, ou sérialisable JSON)

    Returns:
        ETag au format W/"<hash>"
    """
    if isinstance(data, dict | list):
        content = json.dumps(data, sort_keys=True, default=str)
    else:
        content = str(data)

    hash_value = hashlib.sha256(content.encode()).hexdigest()[:16]
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
    Middleware pour ajouter automatiquement les ETags et support 304 Not Modified.

    Features:
    - Génère des ETags weak (W/) basés sur le hash SHA-256 tronqué du body
    - Retourne 304 Not Modified si If-None-Match correspond
    - Ajoute Cache-Control headers configurables

    Usage:
        app.add_middleware(ETagMiddleware, cache_seconds=60)

    Note:
        Ce middleware buffurise le body pour calculer l'ETag.
        À utiliser uniquement pour des réponses de taille raisonnable.
    """

    def __init__(self, app: ASGIApp, cache_seconds: int = 60):
        super().__init__(app)
        self.cache_seconds = cache_seconds

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Ne traiter que les GET
        if request.method != "GET":
            return await call_next(request)

        # Capturer le If-None-Match du client
        client_etag = request.headers.get("If-None-Match")

        # Exécuter la requête
        response = await call_next(request)

        # Ne traiter que les réponses JSON 200
        if response.status_code != 200 or not response.headers.get("content-type", "").startswith(
            "application/json"
        ):
            return response

        # Buffuriser le body pour calculer l'ETag
        body_parts: list[bytes] = []
        async for chunk in response.body_iterator:
            body_parts.append(chunk)
        body = b"".join(body_parts)

        # Générer l'ETag à partir du body (SHA-256 tronqué, A3)
        hash_value = hashlib.sha256(body).hexdigest()[:16]
        etag = f'W/"{hash_value}"'

        # Vérifier If-None-Match - retourner 304 si correspondance
        if client_etag:
            client_etags = [e.strip() for e in client_etag.split(",")]
            if etag in client_etags or "*" in client_etags:
                return Response(
                    status_code=304,
                    headers={
                        "ETag": etag,
                        "Cache-Control": f"private, max-age={self.cache_seconds}",
                    },
                )

        # Créer une nouvelle réponse avec le body buffurisé et les headers
        return Response(
            content=body,
            status_code=response.status_code,
            headers={
                **dict(response.headers),
                "ETag": etag,
                "Cache-Control": f"private, max-age={self.cache_seconds}",
            },
            media_type=response.media_type,
        )
