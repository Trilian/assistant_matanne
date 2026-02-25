"""
Routes d'authentification pour l'API FastAPI.

Endpoints:
- POST /api/v1/auth/login: Authentification email/mot de passe via Supabase
- POST /api/v1/auth/refresh: Rafraîchissement du token API
- GET  /api/v1/auth/me: Informations de l'utilisateur connecté

Sécurité:
- Rate limiting sur /login (5 tentatives/minute par IP)
- Tokens JWT signés avec clé sécurisée
"""

from __future__ import annotations

import logging
import time
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request

from src.api.auth import TokenResponse, creer_token_acces
from src.api.dependencies import get_current_user
from src.api.rate_limiting import _stockage
from src.api.schemas import LoginRequest, UserInfoResponse
from src.api.utils import gerer_exception_api

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentification"],
)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Connexion utilisateur",
    description="Authentifie via Supabase et retourne un token JWT API.",
)
@gerer_exception_api
async def connexion(request: LoginRequest, raw_request: Request):
    """
    Authentifie un utilisateur via Supabase Auth.

    Protégé par un rate limiting strict: 5 tentatives/minute par IP
    pour prévenir les attaques par force brute.

    Retourne un token JWT API signé si les identifiants sont valides.
    """
    # Rate limiting anti brute-force (5 tentatives/minute par IP)
    forwarded = raw_request.headers.get("X-Forwarded-For")
    ip = (
        forwarded.split(",")[0].strip()
        if forwarded
        else (raw_request.client.host if raw_request.client else "unknown")
    )
    cle_login = f"login_attempt:ip:{ip}"

    if _stockage.est_bloque(cle_login):
        raise HTTPException(
            status_code=429,
            detail="Trop de tentatives de connexion. Réessayez dans 5 minutes.",
            headers={"Retry-After": "300"},
        )

    compte = _stockage.incrementer(cle_login, fenetre_secondes=60)
    if compte > 5:
        _stockage.bloquer(cle_login, duree_secondes=300)
        logger.warning(f"Brute force détecté sur /login depuis {ip}")
        raise HTTPException(
            status_code=429,
            detail="Trop de tentatives de connexion. Réessayez dans 5 minutes.",
            headers={"Retry-After": "300"},
        )
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
@gerer_exception_api
async def rafraichir_token(user: dict[str, Any] = Depends(get_current_user)):
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
@gerer_exception_api
async def obtenir_profil(user: dict[str, Any] = Depends(get_current_user)):
    """Retourne les informations de l'utilisateur authentifié."""
    if not user:
        raise HTTPException(status_code=401, detail="Authentification requise")

    return UserInfoResponse(
        id=user["id"],
        email=user["email"],
        role=user.get("role", "membre"),
    )
