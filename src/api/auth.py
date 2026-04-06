"""
Module d'authentification JWT autonome pour l'API FastAPI.

Module d'authentification JWT autonome. Permet:
- Validation de tokens JWT Supabase (avec ou sans vérification de signature)
- Génération de tokens JWT API (pour l'endpoint /auth/login)
- Extraction sécurisée des infos utilisateur depuis le payload JWT

Variables d'environnement:
- API_SECRET_KEY: Clé secrète pour signer les tokens API (obligatoire en production)
- SUPABASE_JWT_SECRET: Secret JWT Supabase pour vérifier les signatures (optionnel)
"""

from __future__ import annotations

import logging
import os
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from pydantic import BaseModel

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════

# Algorithme JWT utilisé pour les tokens API
ALGORITHME = "HS256"

# Durée de vie des tokens API générés (en heures)
DUREE_TOKEN_HEURES = 24

# Clé secrète pour signer/vérifier les tokens API
# En production, DOIT être configurée via variable d'environnement
# Clé par défaut fixe par session — générée UNE SEULE FOIS au
#     chargement du module, partagée par tous les threads/imports du même process.
#     En multi-worker Uvicorn (--workers N), chaque worker a son propre process
#     donc une clé différente. C'est pourquoi API_SECRET_KEY est OBLIGATOIRE
#     en production/staging pour garantir la cohérence inter-workers.
import secrets as _secrets

# Clé générée une seule fois par process — OK en dev single-worker
_API_SECRET_KEY_DEFAULT = _secrets.token_urlsafe(64)

# Vérification au chargement du module — fail-fast en prod/staging
_secret_at_import = os.getenv("API_SECRET_KEY")
_env_at_import = os.getenv("ENVIRONMENT", "").lower().strip()
if not _secret_at_import:
    if _env_at_import in ("production", "prod", "staging", "preview"):
        raise RuntimeError(
            "SÉCURITÉ CRITIQUE: API_SECRET_KEY non configuré "
            f"en environnement '{_env_at_import}'. L'application refuse de démarrer. "
            "Générez une clé sécurisée: "
            "python -c 'import secrets; print(secrets.token_urlsafe(64))'"
        )
    else:
        logger.info(
            "API_SECRET_KEY non configuré — clé aléatoire générée pour cette session. "
            "Configurez API_SECRET_KEY pour la production."
        )
# Cache la clé résolue au démarrage pour cohérence intra-process
_API_SECRET_KEY_RESOLVED: str = _secret_at_import or _API_SECRET_KEY_DEFAULT
del _secret_at_import, _env_at_import

# Clé précédente pour la rotation gracieuse (transition sans déconnexion forcée).
# Procédure de rotation: glisser API_SECRET_KEY vers API_SECRET_KEY_PREVIOUS,
# puis générer un nouveau API_SECRET_KEY. Les anciens tokens restent valides
# pendant la durée de vie maximale d'un token (24h) via la clé précédente.
_API_SECRET_KEY_PREVIOUS: str = os.getenv("API_SECRET_KEY_PREVIOUS", "")


def _est_production() -> bool:
    """Vérifie si l'application tourne en production."""
    return os.getenv("ENVIRONMENT", "development").lower() in ("production", "prod")


def _obtenir_api_secret() -> str:
    """Retourne la clé secrète API courante (cachée au démarrage du module).

    En production, la clé est obligatoirement fournie par variable
    d'environnement (vérifiée au chargement du module — fail-fast).
    """
    return _API_SECRET_KEY_RESOLVED


def _obtenir_api_secret_precedent() -> str:
    """Retourne la clé précédente pour la rotation gracieuse (vide si non configurée)."""
    return _API_SECRET_KEY_PREVIOUS


def _obtenir_supabase_jwt_secret() -> str | None:
    """Retourne le secret JWT Supabase si configuré.

    En production, refuse les tokens non signés.
    ``ALLOW_UNSIGNED_SUPABASE_TOKENS=true`` est interdit en production
    pour éviter toute acceptation de tokens non vérifiés.
    """
    secret = os.getenv("SUPABASE_JWT_SECRET")

    if not secret:
        allow_unsigned = os.getenv("ALLOW_UNSIGNED_SUPABASE_TOKENS", "").lower() == "true"

        if _est_production() and allow_unsigned:
            raise RuntimeError(
                "ERREUR SÉCURITÉ: ALLOW_UNSIGNED_SUPABASE_TOKENS=true "
                "est interdit en production. Configurez SUPABASE_JWT_SECRET."
            )
        elif _est_production():
            logger.error(
                "ERREUR SÉCURITÉ: SUPABASE_JWT_SECRET non configuré en production. "
                "Les tokens Supabase seront REJETÉS. "
                "Configurez SUPABASE_JWT_SECRET."
            )

    return secret


# ═══════════════════════════════════════════════════════════
# SCHÉMAS
# ═══════════════════════════════════════════════════════════


class UtilisateurToken(BaseModel):
    """Informations utilisateur extraites d'un token JWT."""

    id: str
    email: str
    role: str = "membre"


class TokenResponse(BaseModel):
    """Réponse contenant un token JWT."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int = DUREE_TOKEN_HEURES * 3600


# ═══════════════════════════════════════════════════════════
# GÉNÉRATION DE TOKENS
# ═══════════════════════════════════════════════════════════


def creer_token_acces(
    user_id: str,
    email: str,
    role: str = "membre",
    duree_heures: int = DUREE_TOKEN_HEURES,
) -> str:
    """
    Crée un token JWT signé pour l'API.

    Args:
        user_id: Identifiant unique de l'utilisateur
        email: Email de l'utilisateur
        role: Rôle (admin, membre, invite)
        duree_heures: Durée de validité en heures

    Returns:
        Token JWT encodé
    """
    maintenant = datetime.now(UTC)
    expiration = maintenant + timedelta(hours=duree_heures)

    payload = {
        "sub": user_id,
        "email": email,
        "role": role,
        "iat": maintenant,
        "exp": expiration,
        "iss": "assistant-matanne-api",
    }

    return jwt.encode(payload, _obtenir_api_secret(), algorithm=ALGORITHME)


# ═══════════════════════════════════════════════════════════
# VALIDATION DE TOKENS
# ═══════════════════════════════════════════════════════════


def valider_token_api(token: str) -> UtilisateurToken | None:
    """
    Valide un token JWT généré par l'API.

    Args:
        token: Token JWT Bearer

    Returns:
        UtilisateurToken si valide, None sinon
    """
    def _decoder(cle: str) -> dict:
        return jwt.decode(
            token,
            cle,
            algorithms=[ALGORITHME],
            issuer="assistant-matanne-api",
        )

    try:
        payload = _decoder(_obtenir_api_secret())
    except jwt.ExpiredSignatureError:
        logger.warning("Token API expiré")
        return None
    except jwt.InvalidSignatureError:
        # Signature invalide avec la clé courante — essayer la clé précédente (rotation)
        cle_prec = _obtenir_api_secret_precedent()
        if not cle_prec:
            logger.debug("Token API: signature invalide (aucune clé précédente configurée)")
            return None
        try:
            payload = _decoder(cle_prec)
            logger.debug("Token API validé via la clé précédente (rotation en cours)")
        except jwt.ExpiredSignatureError:
            logger.warning("Token API expiré (clé précédente)")
            return None
        except jwt.InvalidTokenError as e:
            logger.debug(f"Token API invalide avec la clé précédente: {e}")
            return None
    except jwt.InvalidTokenError as e:
        logger.debug(f"Token API invalide: {e}")
        return None

    return UtilisateurToken(
        id=payload.get("sub", "unknown"),
        email=payload.get("email", ""),
        role=payload.get("role", "membre"),
    )


def valider_token_supabase(token: str) -> UtilisateurToken | None:
    """
    Valide un token JWT Supabase.

    Si SUPABASE_JWT_SECRET est configuré, vérifie la signature.
    Sinon, décode le payload sans vérification (mode dégradé).

    Args:
        token: Token JWT Supabase

    Returns:
        UtilisateurToken si valide, None sinon
    """
    supabase_secret = _obtenir_supabase_jwt_secret()

    if supabase_secret:
        return _valider_supabase_avec_signature(token, supabase_secret)

    # Sans secret configuré : refuser en production
    if _est_production():
        logger.warning("Token Supabase rejeté: SUPABASE_JWT_SECRET non configuré en production")
        return None

    return _decoder_supabase_sans_signature(token)


def _valider_supabase_avec_signature(token: str, secret: str) -> UtilisateurToken | None:
    """Valide un token Supabase avec vérification de signature."""
    try:
        payload = jwt.decode(
            token,
            secret,
            algorithms=[ALGORITHME],
            audience="authenticated",
            options={"verify_aud": True},
        )
        return _extraire_utilisateur_supabase(payload)
    except jwt.ExpiredSignatureError:
        logger.warning("Token Supabase expiré")
        return None
    except jwt.InvalidTokenError as e:
        logger.debug(f"Token Supabase invalide: {e}")
        return None


def _decoder_supabase_sans_signature(token: str) -> UtilisateurToken | None:
    """
    Décode un token Supabase sans vérification de signature.

    Vérifie manuellement l'expiration. Mode dégradé quand
    SUPABASE_JWT_SECRET n'est pas configuré.
    """
    try:
        payload = jwt.decode(
            token,
            options={
                "verify_signature": False,
                "verify_exp": True,
            },
            algorithms=[ALGORITHME],
        )
        return _extraire_utilisateur_supabase(payload)
    except jwt.ExpiredSignatureError:
        logger.warning("Token Supabase expiré (décodage sans signature)")
        return None
    except Exception as e:
        logger.debug(f"Erreur décodage token Supabase: {e}")
        return None


def _extraire_utilisateur_supabase(payload: dict[str, Any]) -> UtilisateurToken:
    """Extrait les infos utilisateur d'un payload JWT Supabase."""
    metadata = payload.get("user_metadata", {})
    app_metadata = payload.get("app_metadata", {})

    role = metadata.get("role") or app_metadata.get("role") or payload.get("role", "membre")

    return UtilisateurToken(
        id=payload.get("sub", "unknown"),
        email=payload.get("email", ""),
        role=role,
    )


def valider_token(token: str) -> UtilisateurToken | None:
    """
    Valide un token JWT (API ou Supabase).

    Tente d'abord la validation en tant que token API,
    puis en tant que token Supabase.

    Args:
        token: Token JWT Bearer

    Returns:
        UtilisateurToken si valide, None sinon
    """
    # 1. Essayer comme token API (signé par nous)
    utilisateur = valider_token_api(token)
    if utilisateur:
        return utilisateur

    # 2. Essayer comme token Supabase
    utilisateur = valider_token_supabase(token)
    if utilisateur:
        return utilisateur

    logger.warning("Token rejeté: ni API ni Supabase valide")
    return None
