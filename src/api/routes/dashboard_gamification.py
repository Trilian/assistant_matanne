"""
Routes API pour le tableau de bord — section gamification.

Endpoints : catalogue des badges, badges utilisateur, évaluation et historique des points.
"""

from typing import Any

from fastapi import APIRouter, Depends

from src.api.dependencies import require_auth
from src.api.schemas.errors import REPONSES_LISTE
from src.api.utils import executer_async, gerer_exception_api

router = APIRouter(prefix="/api/v1/dashboard", tags=["Tableau de bord — Gamification"])


@router.get(
    "/badges/catalogue",
    responses=REPONSES_LISTE,
    summary="Catalogue des badges sport + nutrition",
)
@gerer_exception_api
async def obtenir_catalogue_badges(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Retourne le catalogue complet des badges disponibles."""
    from src.services.dashboard.badges_triggers import obtenir_catalogue_badges as catalogue

    return {"items": catalogue(), "total": len(catalogue())}


@router.get(
    "/badges/utilisateur",
    responses=REPONSES_LISTE,
    summary="Badges d'un utilisateur avec progression",
)
@gerer_exception_api
async def obtenir_badges_utilisateur(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Retourne les badges d'un utilisateur avec leur état de progression."""

    def _query():
        from src.services.dashboard.badges_triggers import obtenir_badges_triggers_service

        service = obtenir_badges_triggers_service()
        user_id = user.get("user_id") or user.get("id", 1)
        badges = service.obtenir_badges_utilisateur(user_id=int(user_id))
        obtenus = [b for b in badges if b.get("obtenu")]
        return {
            "items": badges,
            "total": len(badges),
            "obtenus": len(obtenus),
        }

    return await executer_async(_query)


@router.post(
    "/badges/evaluer",
    responses=REPONSES_LISTE,
    summary="Évaluer et attribuer les badges mérités",
)
@gerer_exception_api
async def evaluer_badges(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Évalue les conditions de badges et attribue ceux mérités."""

    def _query():
        from src.services.dashboard.badges_triggers import obtenir_badges_triggers_service

        service = obtenir_badges_triggers_service()
        nouveaux = service.evaluer_et_attribuer()
        return {
            "nouveaux_badges": nouveaux,
            "total_nouveaux": len(nouveaux),
        }

    return await executer_async(_query)


@router.get(
    "/historique-points",
    responses=REPONSES_LISTE,
    summary="Historique des points sur N semaines",
)
@gerer_exception_api
async def obtenir_historique_points(
    nb_semaines: int = 8,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Retourne l'évolution des points sport + nutrition sur N semaines."""

    def _query():
        from src.services.dashboard.badges_triggers import obtenir_badges_triggers_service

        service = obtenir_badges_triggers_service()
        user_id = user.get("user_id") or user.get("id", 1)
        historique = service.obtenir_historique_points(
            user_id=int(user_id), nb_semaines=nb_semaines
        )
        return {"items": historique, "total": len(historique)}

    return await executer_async(_query)
