"""Routes API pour les automations simples type 'Si -> Alors'."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from src.api.dependencies import require_auth
from src.api.schemas.errors import REPONSES_CRUD_CREATION, REPONSES_CRUD_LECTURE, REPONSES_LISTE
from src.api.utils import executer_async, executer_avec_session, gerer_exception_api

router = APIRouter(prefix="/api/v1/automations", tags=["Automations"])


def _charger_automations(session, user: dict[str, Any]):
    from src.core.models import AutomationRegle
    from src.core.models.users import ProfilUtilisateur

    profil = None
    if user.get("email"):
        profil = session.query(ProfilUtilisateur).filter(ProfilUtilisateur.email == user["email"]).first()
    if profil is None:
        profil = session.query(ProfilUtilisateur).order_by(ProfilUtilisateur.id.asc()).first()
    if profil is None:
        raise HTTPException(status_code=404, detail="Profil utilisateur introuvable")

    automations = (
        session.query(AutomationRegle)
        .filter(AutomationRegle.user_id == profil.id)
        .order_by(AutomationRegle.id.asc())
        .all()
    )

    return profil, automations


def _migrer_automations_depuis_preferences(session, profil) -> list:
    """Migration douce préférences → AutomationRegle (POST /init uniquement, pas dans GET)."""
    from src.core.models import AutomationRegle

    preferences_modules = profil.preferences_modules or {}
    automations_pref = preferences_modules.get("automations", [])
    if not automations_pref:
        return []

    for item in automations_pref:
        session.add(
            AutomationRegle(
                user_id=profil.id,
                nom=item.get("nom") or "Nouvelle automation",
                declencheur=item.get("declencheur") or {"type": "stock_bas", "seuil": 2},
                action=item.get("action") or {"type": "ajouter_courses", "quantite": 1},
                active=bool(item.get("active", True)),
            )
        )
    session.commit()
    return (
        session.query(AutomationRegle)
        .filter(AutomationRegle.user_id == profil.id)
        .order_by(AutomationRegle.id.asc())
        .all()
    )


def _serialiser_automation(item) -> dict[str, Any]:
    return {
        "id": item.id,
        "nom": item.nom,
        "declencheur": item.declencheur or {},
        "action": item.action or {},
        "active": bool(item.active),
        "derniere_execution": item.derniere_execution.isoformat() if item.derniere_execution else None,
        "execution_count": int(item.execution_count or 0),
    }


@router.get("", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_automations(user: dict[str, Any] = Depends(require_auth)) -> dict[str, Any]:
    def _query():
        with executer_avec_session() as session:
            _, automations = _charger_automations(session, user)
            items = [_serialiser_automation(item) for item in automations]
            return {"items": items, "total": len(items)}

    return await executer_async(_query)


@router.post("/init", responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def initialiser_automations(user: dict[str, Any] = Depends(require_auth)) -> dict[str, Any]:
    """Initialise les automations depuis les préférences legacy (migration unique, idempotent)."""
    def _query():
        with executer_avec_session() as session:
            profil, automations = _charger_automations(session, user)
            if automations:
                return {"message": "Automations déjà initialisées", "total": len(automations)}
            migrees = _migrer_automations_depuis_preferences(session, profil)
            return {"message": f"{len(migrees)} automation(s) importée(s)", "total": len(migrees)}

    return await executer_async(_query)


@router.post("", responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def creer_automation(payload: dict[str, Any], user: dict[str, Any] = Depends(require_auth)) -> dict[str, Any]:
    from src.core.models import AutomationRegle

    def _query():
        with executer_avec_session() as session:
            profil, _ = _charger_automations(session, user)
            automation = AutomationRegle(
                user_id=profil.id,
                nom=payload.get("nom") or "Nouvelle automation",
                declencheur=payload.get("declencheur") or {"type": "stock_bas", "seuil": 2},
                action=payload.get("action") or {"type": "ajouter_courses", "quantite": 1},
                active=bool(payload.get("active", True)),
            )
            session.add(automation)
            session.commit()
            session.refresh(automation)
            return {"message": "Automation créée", "item": _serialiser_automation(automation)}

    return await executer_async(_query)


@router.put("/{automation_id}", responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def modifier_automation(
    automation_id: int,
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    from src.core.models import AutomationRegle

    def _query():
        with executer_avec_session() as session:
            profil, _ = _charger_automations(session, user)
            automation = (
                session.query(AutomationRegle)
                .filter(
                    AutomationRegle.id == automation_id,
                    AutomationRegle.user_id == profil.id,
                )
                .first()
            )
            if automation is None:
                raise HTTPException(status_code=404, detail="Automation introuvable")

            if "nom" in payload:
                automation.nom = payload["nom"]
            if "declencheur" in payload:
                automation.declencheur = payload["declencheur"]
            if "action" in payload:
                automation.action = payload["action"]
            if "active" in payload:
                automation.active = bool(payload["active"])

            session.commit()
            return {"message": "Automation mise à jour", "item": _serialiser_automation(automation)}

    return await executer_async(_query)


@router.post("/{automation_id}/simuler", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def simuler_automation(
    automation_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    from src.core.models import AutomationRegle

    def _query():
        with executer_avec_session() as session:
            profil, _ = _charger_automations(session, user)
            automation = (
                session.query(AutomationRegle)
                .filter(
                    AutomationRegle.id == automation_id,
                    AutomationRegle.user_id == profil.id,
                )
                .first()
            )
            if not automation:
                raise HTTPException(status_code=404, detail="Automation introuvable")
            declencheur = automation.declencheur or {}
            action = automation.action or {}
            return {
                "success": True,
                "resume": f"Si {declencheur.get('type', 'événement')} alors {action.get('type', 'action')}",
                "item": _serialiser_automation(automation),
            }

    return await executer_async(_query)


@router.post("/{automation_id}/executer-maintenant", responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def executer_automation_maintenant(
    automation_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Déclenche manuellement une automation (LT-04)."""
    from src.services.utilitaires.automations_engine import get_moteur_automations_service

    def _query():
        with executer_avec_session() as session:
            profil, _ = _charger_automations(session, user)
            service = get_moteur_automations_service()
            result = service.executer_automation_par_id(automation_id, db=session)
            if not result.get("success"):
                raise HTTPException(status_code=404, detail=result.get("message", "Automation introuvable"))
            return {"message": "Automation exécutée", "resultat": result, "user_id": profil.id}

    return await executer_async(_query)