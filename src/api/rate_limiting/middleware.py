"""
Middleware FastAPI pour la limitation de débit.
"""

import os

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from .limiter import LimiteurDebit, limiteur_debit


class MiddlewareLimitationDebit(BaseHTTPMiddleware):
    """
    Middleware FastAPI pour la limitation de débit automatique.

    Usage:
        app.add_middleware(MiddlewareLimitationDebit)

    Note:
        Désactiver avec RATE_LIMITING_DISABLED=true (pour tests)
    """

    def __init__(self, app, limiteur: LimiteurDebit | None = None):
        super().__init__(app)
        self.limiteur = limiteur or limiteur_debit

    async def dispatch(self, request: Request, call_next) -> Response:
        """Intercepte les requêtes et applique la limitation de débit."""
        # Bypass si désactivé (pour les tests)
        if os.environ.get("RATE_LIMITING_DISABLED", "").lower() == "true":
            return await call_next(request)

        id_utilisateur = None
        auth_header = request.headers.get("Authorization", "")

        if auth_header.startswith("Bearer "):
            try:
                import jwt

                token = auth_header.split(" ")[1]
                payload = jwt.decode(token, options={"verify_signature": False})
                id_utilisateur = payload.get("sub")
            except Exception:
                pass

        est_ia = "/ai/" in request.url.path or "/suggest" in request.url.path

        info_limite = self.limiteur.verifier_limite(
            request,
            id_utilisateur=id_utilisateur,
            est_endpoint_ia=est_ia,
        )

        response = await call_next(request)
        self.limiteur.ajouter_headers(response, info_limite)

        return response
