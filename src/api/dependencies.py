"""
Dépendances FastAPI centralisées.

Contient les dépendances communes pour l'authentification et l'autorisation.
Utilise le module auth autonome (JWT Bearer tokens).
"""

import ipaddress
import logging
import os
from typing import Any

from fastapi import Depends, HTTPException, Request, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .auth import valider_token
from .security_logs import journaliser_evenement_securite

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# EXTRACTION IP CLIENT 
# ═══════════════════════════════════════════════════════════


def extraire_ip_client(request: Request) -> str | None:
    """Extrait l'IP du client avec validation du format.

    Valide que l'IP extraite de X-Forwarded-For est bien
    une adresse IP valide pour éviter les injections dans les logs
    et le rate limiting.
    """
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        ip_candidate = forwarded.split(",")[0].strip()
        try:
            ipaddress.ip_address(ip_candidate)
            return ip_candidate
        except ValueError:
            logger.warning(
                f"X-Forwarded-For contient une IP invalide: '{ip_candidate}'. "
                "Utilisation de l'IP directe."
            )
    return request.client.host if request.client else None


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


# Environnements explicitement autorisés pour le mode dev (liste blanche stricte)
_ENVIRONNEMENTS_DEV_AUTORISES = frozenset({"development", "dev", "local", "test", "testing"})


def _est_environnement_dev() -> bool:
    """
    Vérifie si l'environnement est EXPLICITEMENT un environnement de développement.

    Utilise une liste blanche stricte : seuls les environnements explicitement
    reconnus comme dev/test autorisent l'auto-auth. Tout environnement non reconnu
    est traité comme production par sécurité (A1: fix bypass dev auto-auth).
    """
    env = os.getenv("ENVIRONMENT", "").lower().strip()

    # Si pas défini du tout, refuser l'auto-auth par sécurité
    if not env:
        logger.warning(
            "ENVIRONMENT non défini. Auto-auth désactivée par sécurité. "
            "Définissez ENVIRONMENT='development' explicitement pour le mode dev."
        )
        return False

    # Liste blanche stricte des environnements de dev
    if env in _ENVIRONNEMENTS_DEV_AUTORISES:
        return True

    # Environnement non reconnu — refuser l'auto-auth par sécurité
    logger.warning(
        f"ENVIRONMENT='{env}' non reconnu (pas dans la liste blanche). "
        "Auto-auth désactivée par sécurité. "
        "Valeurs reconnues : development, dev, local, test, testing."
    )

    return False


async def get_current_user(
    request: Request,
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
        if _est_environnement_dev():
            logger.debug("Mode développement: utilisateur dev auto-authentifié (rôle membre)")
            return {"id": "dev", "email": "dev@local", "role": "membre"}
        client_ip = extraire_ip_client(request)
        journaliser_evenement_securite(
            event_type="auth.missing_token",
            user_id=None,
            ip=client_ip,
            user_agent=request.headers.get("User-Agent"),
            details={"reason": "authorization_header_missing"},
        )
        raise HTTPException(status_code=401, detail="Token requis")

    try:
        utilisateur = valider_token(credentials.credentials)

        if utilisateur:
            return {
                "id": utilisateur.id,
                "email": utilisateur.email,
                "role": utilisateur.role,
            }

        client_ip = extraire_ip_client(request)
        journaliser_evenement_securite(
            event_type="auth.invalid_token",
            user_id=None,
            ip=client_ip,
            user_agent=request.headers.get("User-Agent"),
            details={"reason": "token_validation_failed"},
        )
        raise HTTPException(status_code=401, detail="Token invalide")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur validation token: {e}")
        client_ip = extraire_ip_client(request)
        journaliser_evenement_securite(
            event_type="auth.error",
            user_id=None,
            ip=client_ip,
            user_agent=request.headers.get("User-Agent"),
            details={"reason": "token_exception", "error": str(e)},
        )
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

    def role_checker(
        request: Request,
        user: dict[str, Any] = Depends(require_auth),
    ) -> dict[str, Any]:
        if user.get("role") != required_role:
            client_ip = extraire_ip_client(request)
            journaliser_evenement_securite(
                event_type="auth.role_denied",
                user_id=str(user.get("id")) if user.get("id") else None,
                ip=client_ip,
                user_agent=request.headers.get("User-Agent"),
                details={"required_role": required_role, "actual_role": user.get("role")},
            )
            raise HTTPException(
                status_code=403,
                detail=f"Rôle '{required_role}' requis",
            )
        return user

    return role_checker
