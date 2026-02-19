"""
Routes d'authentification pour l'API FastAPI.

Endpoints:
- POST /api/v1/auth/login: Authentification email/mot de passe via Supabase
- POST /api/v1/auth/refresh: Rafraîchissement du token API
- GET  /api/v1/auth/me: Informations de l'utilisateur connecté
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from src.api.auth import TokenResponse, creer_token_acces, valider_token
from src.api.dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentification"],
)


# ═══════════════════════════════════════════════════════════
# SCHÉMAS
# ═══════════════════════════════════════════════════════════


class LoginRequest(BaseModel):
    """Requête de connexion."""

    email: str = Field(..., description="Adresse email de l'utilisateur")
    password: str = Field(..., description="Mot de passe")


class UserInfoResponse(BaseModel):
    """Réponse avec les infos utilisateur."""

    id: str
    email: str
    role: str


# ═══════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Connexion utilisateur",
    description="Authentifie via Supabase et retourne un token JWT API.",
)
async def login(request: LoginRequest):
    """
    Authentifie un utilisateur via Supabase Auth.

    Retourne un token JWT API signé si les identifiants sont valides.
    """
    try:
        # Import lazy pour éviter la dépendance directe à Supabase
        # au chargement du module
        from supabase import create_client
    except ImportError:
        raise HTTPException(
            status_code=503,
            detail="Service d'authentification Supabase non disponible",
        )

    try:
        import os

        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_ANON_KEY")

        if not supabase_url or not supabase_key:
            raise HTTPException(
                status_code=503,
                detail="Supabase non configuré (SUPABASE_URL, SUPABASE_ANON_KEY)",
            )

        client = create_client(supabase_url, supabase_key)
        response = client.auth.sign_in_with_password(
            {"email": request.email, "password": request.password}
        )

        if not response.user:
            raise HTTPException(status_code=401, detail="Identifiants invalides")

        # Extraire les métadonnées utilisateur
        metadata = response.user.user_metadata or {}
        role = metadata.get("role", "membre")

        # Générer un token API signé
        token = creer_token_acces(
            user_id=response.user.id,
            email=response.user.email or request.email,
            role=role,
        )

        return TokenResponse(access_token=token)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur login: {e}")
        raise HTTPException(status_code=401, detail="Identifiants invalides") from e


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Rafraîchir le token",
    description="Génère un nouveau token à partir d'un token valide.",
)
async def refresh_token(user: dict = Depends(get_current_user)):
    """
    Rafraîchit le token JWT API.

    Nécessite un token valide (API ou Supabase) dans le header Authorization.
    Retourne un nouveau token API avec une expiration prolongée.
    """
    if not user:
        raise HTTPException(status_code=401, detail="Authentification requise")

    token = creer_token_acces(
        user_id=user["id"],
        email=user["email"],
        role=user.get("role", "membre"),
    )

    return TokenResponse(access_token=token)


@router.get(
    "/me",
    response_model=UserInfoResponse,
    summary="Profil utilisateur",
    description="Retourne les informations de l'utilisateur connecté.",
)
async def get_me(user: dict = Depends(get_current_user)):
    """Retourne les informations de l'utilisateur authentifié."""
    if not user:
        raise HTTPException(status_code=401, detail="Authentification requise")

    return UserInfoResponse(
        id=user["id"],
        email=user["email"],
        role=user.get("role", "membre"),
    )
