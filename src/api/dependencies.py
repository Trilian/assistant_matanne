"""
Dépendances FastAPI centralisées.

Contient les dépendances communes pour l'authentification et l'autorisation.
Utilise le module auth autonome (sans dépendance Streamlit).
"""

import logging
import os
from typing import Any

from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .auth import valider_token

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
) -> dict[str, Any] | None:
    """
    Valide le token JWT (API ou Supabase) et retourne l'utilisateur.

    Utilise le module auth autonome basé sur PyJWT.
    En mode développement, retourne un utilisateur dev si pas de token.

    Returns:
        Dict avec id, email, role de l'utilisateur
    """
    if not credentials:
        env = os.getenv("ENVIRONMENT", "development").lower()
        if env not in ("production", "prod"):
            logger.debug("Mode développement: utilisateur dev auto-authentifié")
            return {"id": "dev", "email": "dev@local", "role": "admin"}
        raise HTTPException(status_code=401, detail="Token requis")

    try:
        utilisateur = valider_token(credentials.credentials)

        if utilisateur:
            return {
                "id": utilisateur.id,
                "email": utilisateur.email,
                "role": utilisateur.role,
            }

        raise HTTPException(status_code=401, detail="Token invalide")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur validation token: {e}")
        raise HTTPException(status_code=401, detail="Token invalide ou expiré") from e


def require_auth(user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
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

    def role_checker(user: dict[str, Any] = Depends(require_auth)) -> dict[str, Any]:
        if user.get("role") != required_role:
            raise HTTPException(
                status_code=403,
                detail=f"Rôle '{required_role}' requis",
            )
        return user

    return role_checker
