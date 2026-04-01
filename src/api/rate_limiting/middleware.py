"""
Middleware FastAPI pour la limitation de débit.
"""

import os

from fastapi import HTTPException
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from src.api.security_logs import journaliser_evenement_securite

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

        # Bypass si mode test admin activé
        try:
            from src.api.routes.admin import est_mode_test_actif

            if est_mode_test_actif():
                return await call_next(request)
        except Exception:
            pass

        id_utilisateur = None
        auth_header = request.headers.get("Authorization", "")

        if auth_header.startswith("Bearer "):
            try:
                from src.api.auth import valider_token

                token = auth_header.split(" ")[1]
                utilisateur = valider_token(token)
                if utilisateur:
                    id_utilisateur = utilisateur.id
            except Exception:
                pass

        est_ia = "/ai/" in request.url.path or "/suggest" in request.url.path

        try:
            info_limite = self.limiteur.verifier_limite(
                request,
                id_utilisateur=id_utilisateur,
                est_endpoint_ia=est_ia,
            )
        except HTTPException as exc:
            if exc.status_code == 429:
                from src.api.dependencies import extraire_ip_client

                client_ip = extraire_ip_client(request)
                journaliser_evenement_securite(
                    event_type="rate_limit.exceeded",
                    user_id=id_utilisateur,
                    ip=client_ip,
                    user_agent=request.headers.get("User-Agent"),
                    details={
                        "path": request.url.path,
                        "method": request.method,
                        "query": str(request.url.query),
                        "is_ai_endpoint": est_ia,
                    },
                )
            raise

        response = await call_next(request)
        self.limiteur.ajouter_headers(response, info_limite)

        return response
