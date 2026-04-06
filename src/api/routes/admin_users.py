"""Routes admin — Utilisateurs (liste, désactivation, impersonation)."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from fastapi import Depends, HTTPException, Query

from src.api.dependencies import require_role
from src.api.schemas.common import MessageResponse
from src.api.schemas.errors import REPONSES_AUTH_ADMIN
from src.api.utils import gerer_exception_api

from .admin_shared import (
    DesactiverUtilisateurRequest,
    UserImpersonationRequest,
    UtilisateurAdminResponse,
    _journaliser_action_admin,
    router,
)

logger = logging.getLogger(__name__)


@router.get(
    "/users",
    response_model=list[UtilisateurAdminResponse],
    responses=REPONSES_AUTH_ADMIN,
    summary="Lister les utilisateurs",
    description="Retourne la liste des comptes utilisateurs. Nécessite le rôle admin.",
)
@gerer_exception_api
async def lister_utilisateurs(
    page: int = Query(1, ge=1),
    par_page: int = Query(50, ge=1, le=200),
    user: dict[str, Any] = Depends(require_role("admin")),
) -> list[dict]:
    """Retourne la liste paginée des profils utilisateurs."""
    from src.api.utils import executer_async, executer_avec_session

    def _query():
        with executer_avec_session() as session:
            from src.core.models.users import ProfilUtilisateur

            offset = (page - 1) * par_page
            profils = (
                session.query(ProfilUtilisateur)
                .order_by(ProfilUtilisateur.id)
                .offset(offset)
                .limit(par_page)
                .all()
            )
            result = []
            for p in profils:
                result.append({
                    "id": str(getattr(p, "username", p.id)),
                    "email": getattr(p, "email", ""),
                    "nom": getattr(p, "nom", None) or getattr(p, "display_name", None),
                    "role": getattr(p, "role", "membre"),
                    "actif": not bool(
                        (getattr(p, "preferences_modules", None) or {}).get("compteDesactive")
                    ),
                    "cree_le": (
                        p.cree_le.isoformat()
                        if hasattr(p, "cree_le") and p.cree_le
                        else None
                    ),
                })
            return result

    return await executer_async(_query)


@router.post(
    "/users/{user_id}/disable",
    response_model=MessageResponse,
    responses=REPONSES_AUTH_ADMIN,
    summary="Désactiver un compte utilisateur",
    description="Marque le compte comme désactivé. Nécessite le rôle admin.",
)
@gerer_exception_api
async def desactiver_utilisateur(
    user_id: str,
    body: DesactiverUtilisateurRequest,
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict:
    """Désactive un compte utilisateur (flag dans preferences_modules)."""
    from src.api.utils import executer_async, executer_avec_session

    def _disable():
        with executer_avec_session() as session:
            from src.core.models.users import ProfilUtilisateur

            profil = (
                session.query(ProfilUtilisateur)
                .filter(ProfilUtilisateur.username == user_id)
                .first()
            )
            if not profil:
                raise HTTPException(status_code=404, detail=f"Utilisateur '{user_id}' introuvable.")

            prefs = dict(profil.preferences_modules or {})
            prefs["compteDesactive"] = True
            if body.raison:
                prefs["raisonDesactivation"] = body.raison
            prefs["desactiveParAdmin"] = str(user.get("id", "admin"))
            prefs["desactiveLe"] = datetime.now().isoformat()
            profil.preferences_modules = prefs
            session.commit()
            return {"status": "ok", "user_id": user_id, "message": f"Compte '{user_id}' désactivé."}

    result = await executer_async(_disable)
    _journaliser_action_admin(
        action="admin.user.disable",
        entite_type="utilisateur",
        utilisateur_id=str(user.get("id", "admin")),
        details={"cible_user_id": user_id, "raison": body.raison},
    )
    return result


@router.post(
    "/users/{user_id}/impersonate",
    responses=REPONSES_AUTH_ADMIN,
    summary="Simuler un utilisateur",
    description="Génère un token temporaire pour naviguer avec le contexte d'un utilisateur cible.",
)
@gerer_exception_api
async def simuler_utilisateur(
    user_id: str,
    body: UserImpersonationRequest,
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    from src.api.auth import creer_token_acces
    from src.api.utils import executer_avec_session
    from src.core.models.users import ProfilUtilisateur

    with executer_avec_session() as session:
        profil = (
            session.query(ProfilUtilisateur)
            .filter(ProfilUtilisateur.username == user_id)
            .first()
        )
        if profil is None:
            raise HTTPException(status_code=404, detail=f"Utilisateur '{user_id}' introuvable.")

        role = str(getattr(profil, "role", "membre") or "membre")
        email = str(getattr(profil, "email", "") or f"{user_id}@local")
        token = creer_token_acces(
            user_id=user_id,
            email=email,
            role=role,
            duree_heures=max(1, min(body.duree_heures, 24)),
        )

    _journaliser_action_admin(
        action="admin.user.impersonate",
        entite_type="utilisateur",
        utilisateur_id=str(user.get("id", "admin")),
        details={"cible_user_id": user_id, "duree_heures": body.duree_heures, "raison": body.raison},
    )
    return {
        "status": "ok",
        "token_type": "bearer",
        "access_token": token,
        "expires_in": max(1, min(body.duree_heures, 24)) * 3600,
        "utilisateur": {
            "id": user_id,
            "email": email,
            "role": role,
        },
    }
