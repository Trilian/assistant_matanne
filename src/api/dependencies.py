"""
Dépendances FastAPI centralisées.

Contient les dépendances communes pour l'authentification et l'autorisation.
"""

import logging
import os

from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# SÉCURITÉ
# ═══════════════════════════════════════════════════════════

security = HTTPBearer(auto_error=False)


# ═══════════════════════════════════════════════════════════
# AUTHENTIFICATION
# ═══════════════════════════════════════════════════════════


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> dict | None:
    """
    Valide le token JWT Supabase et retourne l'utilisateur.

    En mode développement, retourne un utilisateur dev si pas de token.

    Returns:
        Dict avec id, email, role de l'utilisateur
    """
    if not credentials:
        if os.getenv("ENVIRONMENT", "development") == "development":
            return {"id": "dev", "email": "dev@local", "role": "admin"}
        raise HTTPException(status_code=401, detail="Token requis")

    try:
        from src.services.core.utilisateur import get_auth_service

        auth = get_auth_service()
        user = auth.validate_token(credentials.credentials)

        if user:
            return {
                "id": user.id,
                "email": user.email,
                "role": user.role.value,
            }

        payload = auth.decode_jwt_payload(credentials.credentials)
        if payload:
            return {
                "id": payload.get("sub", "unknown"),
                "email": payload.get("email", ""),
                "role": payload.get("user_metadata", {}).get("role", "membre"),
            }

        raise HTTPException(status_code=401, detail="Token invalide")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur validation token: {e}")
        raise HTTPException(status_code=401, detail="Token invalide ou expiré") from e


def require_auth(user: dict = Depends(get_current_user)) -> dict:
    """
    Dependency qui exige une authentification.

    Usage:
        @app.get("/protected")
        async def protected_route(user: dict = Depends(require_auth)):
            ...
    """
    if not user:
        raise HTTPException(status_code=401, detail="Authentification requise")
    return user


def require_role(required_role: str):
    """
    Dependency factory qui exige un rôle spécifique.

    Usage:
        @app.get("/admin-only")
        async def admin_route(user: dict = Depends(require_role("admin"))):
            ...
    """

    def role_checker(user: dict = Depends(require_auth)) -> dict:
        if user.get("role") != required_role:
            raise HTTPException(
                status_code=403,
                detail=f"Rôle '{required_role}' requis",
            )
        return user

    return role_checker


# Alias anglais
get_user = get_current_user
auth_required = require_auth
role_required = require_role
