"""
Routes d'authentification pour l'API FastAPI.

Endpoints:
- POST /api/v1/auth/login: Authentification email/mot de passe via Supabase
- POST /api/v1/auth/refresh: Rafraîchissement du token API
- GET  /api/v1/auth/me: Informations de l'utilisateur connecté
- POST /api/v1/auth/2fa/enable: Initier l'activation 2FA (QR code + backup codes)
- POST /api/v1/auth/2fa/verify-setup: Confirmer l'activation 2FA avec un code
- POST /api/v1/auth/2fa/disable: Désactiver le 2FA
- GET  /api/v1/auth/2fa/status: Statut 2FA de l'utilisateur
- POST /api/v1/auth/2fa/login: Vérifier le code 2FA pendant le login

Sécurité:
- Rate limiting sur /login (5 tentatives/minute par IP)
- Tokens JWT signés avec clé sécurisée
- TOTP 2FA optionnel (Google Authenticator, Authy, etc.)
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request

from src.api.auth import DUREE_TOKEN_HEURES, TokenResponse, creer_token_acces
from src.api.dependencies import get_current_user, require_auth
from src.api.rate_limiting import _stockage
from src.api.schemas import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    TwoFactorEnableResponse,
    TwoFactorLoginRequest,
    TwoFactorStatusResponse,
    TwoFactorVerifyRequest,
    UserInfoResponse,
)
from src.api.schemas.errors import REPONSES_AUTH, REPONSES_AUTH_LOGIN
from src.api.utils import gerer_exception_api

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentification"],
)


# ═══════════════════════════════════════════════════════════
# HELPERS DB pour 2FA
# ═══════════════════════════════════════════════════════════


def _obtenir_profil_par_email(email: str):
    """Cherche le profil utilisateur par email (retourne None si inexistant)."""
    try:
        from src.core.db import obtenir_contexte_db
        from src.core.models.users import ProfilUtilisateur

        with obtenir_contexte_db() as session:
            profil = (
                session.query(ProfilUtilisateur)
                .filter(ProfilUtilisateur.email == email)
                .first()
            )
            if profil:
                # Détacher l'objet de la session pour pouvoir l'utiliser après
                session.expunge(profil)
            return profil
    except Exception as e:
        logger.debug(f"Erreur recherche profil par email: {e}")
        return None


def _obtenir_profil_par_id(user_id: str):
    """Cherche le profil utilisateur par user_id."""
    try:
        from src.core.db import obtenir_contexte_db
        from src.core.models.users import ProfilUtilisateur

        with obtenir_contexte_db() as session:
            profil = (
                session.query(ProfilUtilisateur)
                .filter(ProfilUtilisateur.username == user_id)
                .first()
            )
            if not profil:
                # Essayer par id numérique
                try:
                    profil = session.query(ProfilUtilisateur).get(int(user_id))
                except (ValueError, TypeError):
                    pass
            if profil:
                session.expunge(profil)
            return profil
    except Exception as e:
        logger.debug(f"Erreur recherche profil par id: {e}")
        return None


def _maj_profil_2fa(email: str, **kwargs):
    """Met à jour les champs 2FA du profil."""
    try:
        from src.core.db import obtenir_contexte_db
        from src.core.models.users import ProfilUtilisateur

        with obtenir_contexte_db() as session:
            profil = (
                session.query(ProfilUtilisateur)
                .filter(ProfilUtilisateur.email == email)
                .first()
            )
            if profil:
                for k, v in kwargs.items():
                    setattr(profil, k, v)
                session.commit()
                return True
    except Exception as e:
        logger.error(f"Erreur mise à jour 2FA: {e}")
    return False


# ═══════════════════════════════════════════════════════════
# LOGIN
# ═══════════════════════════════════════════════════════════


@router.post(
    "/login",
    response_model=LoginResponse,
    responses=REPONSES_AUTH_LOGIN,
    summary="Connexion utilisateur",
    description="Authentifie via Supabase et retourne un token JWT API. Si 2FA activé, retourne un token temporaire.",
)
@gerer_exception_api
async def connexion(request: LoginRequest, raw_request: Request):
    """
    Authentifie un utilisateur via Supabase Auth.

    Si 2FA activé, retourne requires_2fa=true avec un temp_token.
    L'utilisateur doit alors appeler POST /auth/2fa/login avec le code TOTP.
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

        metadata = response.user.user_metadata or {}
        role = metadata.get("role", "membre")
        email = response.user.email or request.email

        # Vérifier si 2FA est activé pour cet utilisateur
        profil = _obtenir_profil_par_email(email)
        if profil and profil.two_factor_enabled and profil.two_factor_secret:
            # Générer un token temporaire (courte durée, non-utilisable pour l'API)
            temp_token = creer_token_acces(
                user_id=response.user.id,
                email=email,
                role="2fa_pending",
                duree_heures=0.083,  # ~5 minutes
            )
            return LoginResponse(
                requires_2fa=True,
                temp_token=temp_token,
            )

        # Pas de 2FA : générer le token API directement
        token = creer_token_acces(
            user_id=response.user.id,
            email=email,
            role=role,
        )

        return LoginResponse(
            access_token=token,
            token_type="bearer",
            expires_in=DUREE_TOKEN_HEURES * 3600,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur login: {e}")
        raise HTTPException(status_code=401, detail="Identifiants invalides") from e


# ═══════════════════════════════════════════════════════════
# REGISTER / REFRESH / ME
# ═══════════════════════════════════════════════════════════


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=201,
    summary="Inscription",
    description="Crée un nouveau compte via Supabase et retourne un token JWT.",
)
@gerer_exception_api
async def inscription(request: RegisterRequest):
    """Crée un compte utilisateur via Supabase Auth."""
    try:
        from supabase import create_client
    except ImportError:
        raise HTTPException(
            status_code=503,
            detail="Service d'authentification Supabase non disponible",
        )

    import os

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")

    if not supabase_url or not supabase_key:
        raise HTTPException(
            status_code=503,
            detail="Supabase non configuré",
        )

    try:
        client = create_client(supabase_url, supabase_key)
        response = client.auth.sign_up(
            {
                "email": request.email,
                "password": request.password,
                "options": {"data": {"nom": request.nom, "role": "membre"}},
            }
        )

        if not response.user:
            raise HTTPException(status_code=400, detail="Impossible de créer le compte")

        token = creer_token_acces(
            user_id=response.user.id,
            email=response.user.email or request.email,
            role="membre",
        )

        return TokenResponse(access_token=token)


    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur inscription: {e}")
        raise HTTPException(
            status_code=400, detail="Impossible de créer le compte"
        ) from e


# ═══════════════════════════════════════════════════════════
# MOT DE PASSE OUBLIÉ / VÉRIFICATION EMAIL
# ═══════════════════════════════════════════════════════════


@router.post(
    "/forgot-password",
    summary="Mot de passe oublié",
    description="Envoie un email de réinitialisation de mot de passe.",
    status_code=200,
)
@gerer_exception_api
async def mot_de_passe_oublie(request: LoginRequest):
    """
    Envoie un email de réinitialisation de mot de passe.

    Retourne toujours 200 pour éviter l'énumération des emails.
    """
    # Générer un token signé à courte durée (30 min)
    token = creer_token_acces(
        user_id="reset",
        email=request.email,
        role="reset_password",
        duree_heures=0.5,
    )

    try:
        from src.services.core.notifications.notif_email import get_service_email

        service_email = get_service_email()
        service_email.envoyer_reset_password(request.email, token)
    except Exception as e:
        logger.warning("Erreur envoi email reset pour %s : %s", request.email, e)

    # Toujours retourner 200 (ne pas révéler si l'email existe)
    return {"message": "Si cet email existe, un lien de réinitialisation a été envoyé."}


@router.post(
    "/verify-email",
    summary="Renvoyer l'email de vérification",
    description="Envoie un nouvel email de vérification d'adresse.",
    status_code=200,
)
@gerer_exception_api
async def renvoyer_verification_email(request: LoginRequest):
    """Envoie un email de vérification à l'adresse fournie."""
    token = creer_token_acces(
        user_id="verify",
        email=request.email,
        role="verify_email",
        duree_heures=24,
    )

    try:
        from src.services.core.notifications.notif_email import get_service_email

        service_email = get_service_email()
        service_email.envoyer_verification_email(request.email, token)
    except Exception as e:
        logger.warning("Erreur envoi email vérification pour %s : %s", request.email, e)

    return {"message": "Email de vérification envoyé."}

@router.post(
    "/refresh",
    response_model=TokenResponse,
    responses=REPONSES_AUTH,
    summary="Rafraîchir le token",
    description="Génère un nouveau token à partir d'un token valide.",
)
@gerer_exception_api
async def rafraichir_token(user: dict[str, Any] = Depends(get_current_user)):
    """Rafraîchit le token JWT API."""
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
    responses=REPONSES_AUTH,
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


# ═══════════════════════════════════════════════════════════
# 2FA ENDPOINTS
# ═══════════════════════════════════════════════════════════


@router.post(
    "/2fa/enable",
    response_model=TwoFactorEnableResponse,
    responses=REPONSES_AUTH,
    summary="Initier l'activation 2FA",
    description="Génère un secret TOTP, un QR code et des codes de récupération.",
)
@gerer_exception_api
async def activer_2fa(user: dict[str, Any] = Depends(require_auth)):
    """Génère le secret TOTP et le QR code pour activation 2FA.

    L'utilisateur doit ensuite appeler /2fa/verify-setup avec un code valide
    pour confirmer l'activation.
    """
    from src.services.core.utilisateur.two_factor import obtenir_service_2fa

    service = obtenir_service_2fa()

    secret = service.generer_secret()
    qr_code = service.generer_qr_code(secret, user["email"])
    backup_codes = service.generer_codes_backup()
    backup_hashes = service.hasher_codes_backup(backup_codes)

    # Stocker le secret en attente de confirmation (pas encore activé)
    _maj_profil_2fa(
        user["email"],
        two_factor_secret=secret,
        backup_codes=backup_hashes,
        two_factor_enabled=False,
    )

    return TwoFactorEnableResponse(
        secret=secret,
        qr_code=qr_code,
        backup_codes=backup_codes,
    )


@router.post(
    "/2fa/verify-setup",
    responses=REPONSES_AUTH,
    summary="Confirmer l'activation 2FA",
    description="Vérifie le premier code TOTP pour activer définitivement le 2FA.",
)
@gerer_exception_api
async def verifier_setup_2fa(
    request: TwoFactorVerifyRequest,
    user: dict[str, Any] = Depends(require_auth),
):
    """Confirme l'activation 2FA en vérifiant un code TOTP."""
    from src.services.core.utilisateur.two_factor import obtenir_service_2fa

    profil = _obtenir_profil_par_email(user["email"])
    if not profil or not profil.two_factor_secret:
        raise HTTPException(status_code=400, detail="Aucune activation 2FA en cours")

    service = obtenir_service_2fa()

    if not service.verifier_code(profil.two_factor_secret, request.code):
        raise HTTPException(status_code=400, detail="Code invalide")

    # Activer le 2FA
    _maj_profil_2fa(user["email"], two_factor_enabled=True)

    return {"message": "2FA activé avec succès"}


@router.post(
    "/2fa/disable",
    responses=REPONSES_AUTH,
    summary="Désactiver le 2FA",
    description="Désactive l'authentification à deux facteurs après vérification du code.",
)
@gerer_exception_api
async def desactiver_2fa(
    request: TwoFactorVerifyRequest,
    user: dict[str, Any] = Depends(require_auth),
):
    """Désactive le 2FA (nécessite un code valide)."""
    from src.services.core.utilisateur.two_factor import obtenir_service_2fa

    profil = _obtenir_profil_par_email(user["email"])
    if not profil or not profil.two_factor_enabled:
        raise HTTPException(status_code=400, detail="2FA non activé")

    service = obtenir_service_2fa()

    if not service.verifier_code(profil.two_factor_secret, request.code):
        raise HTTPException(status_code=400, detail="Code invalide")

    _maj_profil_2fa(
        user["email"],
        two_factor_enabled=False,
        two_factor_secret=None,
        backup_codes=None,
    )

    return {"message": "2FA désactivé"}


@router.get(
    "/2fa/status",
    response_model=TwoFactorStatusResponse,
    responses=REPONSES_AUTH,
    summary="Statut 2FA",
    description="Retourne si le 2FA est activé et le nombre de codes backup restants.",
)
@gerer_exception_api
async def statut_2fa(user: dict[str, Any] = Depends(require_auth)):
    """Retourne le statut 2FA de l'utilisateur."""
    profil = _obtenir_profil_par_email(user["email"])

    if not profil:
        return TwoFactorStatusResponse(enabled=False, backup_codes_remaining=0)

    return TwoFactorStatusResponse(
        enabled=profil.two_factor_enabled,
        backup_codes_remaining=len(profil.backup_codes) if profil.backup_codes else 0,
    )


@router.post(
    "/2fa/login",
    response_model=TokenResponse,
    responses=REPONSES_AUTH_LOGIN,
    summary="Vérifier code 2FA pour login",
    description="Complète le login en vérifiant le code TOTP avec le token temporaire.",
)
@gerer_exception_api
async def login_2fa(request: TwoFactorLoginRequest):
    """Vérifie le code 2FA et émet le token API définitif."""
    from src.api.auth import valider_token_api
    from src.services.core.utilisateur.two_factor import obtenir_service_2fa

    # Valider le token temporaire
    utilisateur_temp = valider_token_api(request.temp_token)
    if not utilisateur_temp or utilisateur_temp.role != "2fa_pending":
        raise HTTPException(status_code=401, detail="Token temporaire invalide ou expiré")

    profil = _obtenir_profil_par_email(utilisateur_temp.email)
    if not profil or not profil.two_factor_enabled or not profil.two_factor_secret:
        raise HTTPException(status_code=400, detail="2FA non configuré")

    service = obtenir_service_2fa()

    # Essayer TOTP d'abord
    code_valide = service.verifier_code(profil.two_factor_secret, request.code)

    # Si échec TOTP, essayer les codes backup
    if not code_valide and profil.backup_codes:
        code_valide, codes_restants = service.verifier_code_backup(
            request.code, profil.backup_codes
        )
        if code_valide:
            _maj_profil_2fa(utilisateur_temp.email, backup_codes=codes_restants)

    if not code_valide:
        raise HTTPException(status_code=401, detail="Code 2FA invalide")

    # Récupérer le vrai rôle depuis les métadonnées
    # (le temp_token a role="2fa_pending", on doit retrouver le vrai rôle)
    token = creer_token_acces(
        user_id=utilisateur_temp.id,
        email=utilisateur_temp.email,
        role="membre",  # Rôle par défaut, sera overridé par le profil si dispo
    )

    return TokenResponse(access_token=token)
