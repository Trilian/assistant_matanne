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

security = HTTPBearer(
    auto_error=False,
    description="Token JWT Bearer. Obtenu via POST /api/v1/auth/login",
)


# ═══════════════════════════════════════════════════════════
# AUTHENTIFICATION
# ═══════════════════════════════════════════════════════════


def _est_environnement_production() -> bool:
    """
    Vérifie si l'environnement est la production.

    Vérifie plusieurs indicateurs pour éviter un bypass accidentel
    de l'authentification en production.
    """
    env = os.getenv("ENVIRONMENT", "development").lower().strip()

    # Liste noire stricte des valeurs de production
    if env in ("production", "prod", "prd", "live"):
        return True

    # Indicateurs supplémentaires de production
    # (présence de secrets réels, etc.)
    api_secret = os.getenv("API_SECRET_KEY", "")
    if api_secret and api_secret != "dev-secret-key-change-in-production":
        # Si une vraie clé API est configurée, on considère que c'est la prod
        if env not in ("development", "dev", "local", "test", "testing"):
            logger.warning(
                f"ENVIRONMENT='{env}' non reconnu avec API_SECRET_KEY configurée. "
                "Traité comme production par sécurité."
            )
            return True

    return False


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
        if not _est_environnement_production():
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
