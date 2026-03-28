"""Routes API pour les automations simples type 'Si -> Alors'."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from src.api.dependencies import require_auth
from src.api.schemas.errors import REPONSES_CRUD_CREATION, REPONSES_CRUD_LECTURE, REPONSES_LISTE
from src.api.utils import executer_async, executer_avec_session, gerer_exception_api

router = APIRouter(prefix="/api/v1/automations", tags=["Automations"])


def _charger_automations(session, user: dict[str, Any]):
    from src.core.models.users import ProfilUtilisateur

    profil = None
    if user.get("email"):
        profil = session.query(ProfilUtilisateur).filter(ProfilUtilisateur.email == user["email"]).first()
    if profil is None:
        profil = session.query(ProfilUtilisateur).order_by(ProfilUtilisateur.id.asc()).first()
    if profil is None:
        raise HTTPException(status_code=404, detail="Profil utilisateur introuvable")

    preferences_modules = profil.preferences_modules or {}
    automations = preferences_modules.get("automations", [])
    return profil, preferences_modules, automations


@router.get("", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_automations(user: dict[str, Any] = Depends(require_auth)) -> dict[str, Any]:
    def _query():
        with executer_avec_session() as session:
            _, _, automations = _charger_automations(session, user)
            return {"items": automations, "total": len(automations)}

    return await executer_async(_query)


@router.post("", responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def creer_automation(payload: dict[str, Any], user: dict[str, Any] = Depends(require_auth)) -> dict[str, Any]:
    def _query():
        with executer_avec_session() as session:
            profil, preferences_modules, automations = _charger_automations(session, user)
            automation = {
                "id": len(automations) + 1,
                "nom": payload.get("nom") or "Nouvelle automation",
                "declencheur": payload.get("declencheur") or {"type": "stock_bas", "seuil": 2},
                "action": payload.get("action") or {"type": "ajouter_courses", "quantite": 1},
                "active": bool(payload.get("active", True)),
            }
            automations.append(automation)
            preferences_modules["automations"] = automations
            profil.preferences_modules = preferences_modules
            session.commit()
            return {"message": "Automation créée", "item": automation}

    return await executer_async(_query)


@router.put("/{automation_id}", responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def modifier_automation(
    automation_id: int,
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    def _query():
        with executer_avec_session() as session:
            profil, preferences_modules, automations = _charger_automations(session, user)
            for index, automation in enumerate(automations):
                if int(automation.get("id", -1)) == automation_id:
                    updated = {**automation, **payload, "id": automation_id}
                    automations[index] = updated
                    preferences_modules["automations"] = automations
                    profil.preferences_modules = preferences_modules
                    session.commit()
                    return {"message": "Automation mise à jour", "item": updated}
            raise HTTPException(status_code=404, detail="Automation introuvable")

    return await executer_async(_query)


@router.post("/{automation_id}/simuler", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def simuler_automation(
    automation_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    def _query():
        with executer_avec_session() as session:
            _, _, automations = _charger_automations(session, user)
            automation = next((a for a in automations if int(a.get("id", -1)) == automation_id), None)
            if automation is None:
                raise HTTPException(status_code=404, detail="Automation introuvable")
            declencheur = automation.get("declencheur", {})
            action = automation.get("action", {})
            return {
                "success": True,
                "resume": f"Si {declencheur.get('type', 'événement')} alors {action.get('type', 'action')}",
                "item": automation,
            }

    return await executer_async(_query)