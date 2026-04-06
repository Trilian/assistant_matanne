"""Routes API Garmin santÃ©/sport."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query

from src.api.dependencies import require_auth
from src.api.schemas.errors import REPONSES_CRUD_CREATION, REPONSES_CRUD_LECTURE
from src.api.schemas.garmin import (
    GarminConnectCompleteResponse,
    GarminConnectUrlResponse,
    GarminDisconnectResponse,
    GarminRecommandationDinerResponse,
    GarminStatsResponse,
    GarminStatusResponse,
    GarminSyncResponse,
)
from src.api.utils import executer_async, executer_avec_session, gerer_exception_api

router = APIRouter(prefix="/api/v1/garmin", tags=["Garmin"])


def _resoudre_user_id(session, user: dict[str, Any]) -> int:
    from src.core.models.users import ProfilUtilisateur

    profil = None
    if user.get("email"):
        profil = session.query(ProfilUtilisateur).filter(ProfilUtilisateur.email == user["email"]).first()
    if profil is None:
        profil = session.query(ProfilUtilisateur).order_by(ProfilUtilisateur.id.asc()).first()
    if profil is None:
        raise HTTPException(status_code=404, detail="Aucun profil utilisateur Garmin disponible")
    return profil.id


@router.get("/status", response_model=GarminStatusResponse, responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def obtenir_statut_garmin(user: dict[str, Any] = Depends(require_auth)) -> dict[str, Any]:
    from src.core.models.users import ProfilUtilisateur

    def _query():
        with executer_avec_session() as session:
            user_id = _resoudre_user_id(session, user)
            profil = session.get(ProfilUtilisateur, user_id)
            return {
                "connected": bool(profil and profil.garmin_connected),
                "display_name": profil.display_name if profil else None,
                "objectif_pas": profil.objectif_pas_quotidien if profil else None,
                "objectif_calories": profil.objectif_calories_brulees if profil else None,
            }

    return await executer_async(_query)


@router.post("/connect-url", response_model=GarminConnectUrlResponse, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def creer_url_connexion_garmin(
    callback_url: str = Query("oob"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    from src.services.integrations.garmin.service import obtenir_garmin_service

    service = obtenir_garmin_service()
    authorization_url, request_token = service.get_authorization_url(callback_url=callback_url)
    if not authorization_url:
        raise HTTPException(status_code=503, detail="Garmin n'est pas configurÃ© cÃ´tÃ© serveur")
    return {"authorization_url": authorization_url, "request_token": request_token}


@router.post("/complete", response_model=GarminConnectCompleteResponse, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def terminer_connexion_garmin(
    payload: dict[str, str],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    from src.services.integrations.garmin.service import obtenir_garmin_service

    oauth_verifier = (payload.get("oauth_verifier") or "").strip()
    if not oauth_verifier:
        raise HTTPException(status_code=422, detail="oauth_verifier requis")

    def _query():
        with executer_avec_session() as session:
            user_id = _resoudre_user_id(session, user)
            service = obtenir_garmin_service()
            succes = service.complete_authorization(user_id=user_id, oauth_verifier=oauth_verifier, db=session)
            if not succes:
                raise HTTPException(status_code=400, detail="Impossible de terminer la connexion Garmin")
            return {"connected": True, "message": "Garmin connectÃ©"}

    return await executer_async(_query)


@router.post("/sync", response_model=GarminSyncResponse, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def synchroniser_garmin(
    days_back: int = Query(7, ge=1, le=30),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    from src.services.integrations.garmin.service import obtenir_garmin_service

    def _query():
        with executer_avec_session() as session:
            user_id = _resoudre_user_id(session, user)
            service = obtenir_garmin_service()
            result = service.sync_user_data(user_id=user_id, days_back=days_back, db=session)
            if isinstance(result, dict):
                return {
                    "status": "success" if result.get("synced") else "error",
                    "activities_synced": result.get("activites", result.get("activities_synced", 0)),
                }
            return {"status": "success", "activities_synced": 0}

    return await executer_async(_query)


@router.get("/stats", response_model=GarminStatsResponse, responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def obtenir_stats_garmin(
    days: int = Query(7, ge=1, le=60),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    from src.services.integrations.garmin.service import obtenir_garmin_service

    def _query():
        with executer_avec_session() as session:
            user_id = _resoudre_user_id(session, user)
            service = obtenir_garmin_service()
            return service.get_user_stats(user_id=user_id, days=days, db=session)

    return await executer_async(_query)


@router.post("/disconnect", response_model=GarminDisconnectResponse, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def deconnecter_garmin(user: dict[str, Any] = Depends(require_auth)) -> dict[str, Any]:
    from src.services.integrations.garmin.service import obtenir_garmin_service

    def _query():
        with executer_avec_session() as session:
            user_id = _resoudre_user_id(session, user)
            service = obtenir_garmin_service()
            succes = service.disconnect_user(user_id=user_id, db=session)
            return {"success": succes}

    return await executer_async(_query)


@router.get("/recommandation-diner", response_model=GarminRecommandationDinerResponse, responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def recommander_diner_selon_activite(
    calories_brulees: int = Query(0, ge=0, le=3000),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Propose un dÃ®ner adaptÃ© au niveau de dÃ©pense Ã©nergÃ©tique Garmin."""

    def _query():
        with executer_avec_session() as session:
            from src.core.models import Recette

            if calories_brulees >= 600:
                cible_max = 850
                strategie = "recharge"
            elif calories_brulees >= 350:
                cible_max = 700
                strategie = "equilibre"
            else:
                cible_max = 550
                strategie = "leger"

            recettes = (
                session.query(Recette)
                .filter(Recette.calories.isnot(None), Recette.calories <= cible_max)
                .order_by(Recette.calories.desc())
                .limit(5)
                .all()
            )

            if not recettes:
                return {
                    "strategie": strategie,
                    "calories_brulees": calories_brulees,
                    "message": "Aucune recette calorique adaptÃ©e trouvÃ©e",
                    "items": [],
                }

            return {
                "strategie": strategie,
                "calories_brulees": calories_brulees,
                "message": "Suggestions de dÃ®ner adaptÃ©es Ã  la dÃ©pense du jour",
                "items": [
                    {
                        "id": r.id,
                        "nom": r.nom,
                        "calories": r.calories,
                        "categorie": r.categorie,
                        "temps_preparation": r.temps_preparation,
                    }
                    for r in recettes
                ],
            }

    return await executer_async(_query)
