"""
Middleware de sécurité HTTP pour l'API REST.

Ajoute les headers de sécurité recommandés par OWASP:
- Content-Security-Policy
- Strict-Transport-Security (HSTS)
- X-Content-Type-Options
- X-Frame-Options
- X-XSS-Protection
- Referrer-Policy
- Permissions-Policy
"""

import os

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware qui ajoute les headers de sécurité HTTP à toutes les réponses.

    En production, HSTS est activé automatiquement.
    Les headers CSP sont permissifs pour Swagger UI (/docs, /redoc).

    Usage:
        app.add_middleware(SecurityHeadersMiddleware)
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self._is_production = os.getenv("ENVIRONMENT", "development").lower() in (
            "production",
            "prod",
        )

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)

        # Headers de sécurité universels
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=(), payment=()"
        )

        # HSTS uniquement en production (HTTPS obligatoire)
        if self._is_production:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        # CSP adapté : permissif pour Swagger UI, strict pour les routes API
        path = request.url.path
        if path in ("/docs", "/redoc") or path.startswith("/docs") or path.startswith("/redoc"):
            # Swagger UI nécessite inline styles/scripts
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "img-src 'self' data: https://fastapi.tiangolo.com; "
                "font-src 'self' https://cdn.jsdelivr.net"
            )
        else:
            # CSP strict pour les endpoints API
            response.headers["Content-Security-Policy"] = (
                "default-src 'none'; frame-ancestors 'none'"
            )

        return response
