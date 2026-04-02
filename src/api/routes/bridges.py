"""
Routes API — Bridges inter-modules (B5).

Documents expirés, planning unifié, alertes météo→entretien.
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends, Query

from src.api.dependencies import require_auth
from src.api.schemas.errors import REPONSES_LISTE
from src.api.schemas.ia_bridges import (
    DocumentsExpiresResponse,
    PlanningUnifieResponse,
)
from src.api.utils import gerer_exception_api

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/bridges", tags=["Bridges Inter-Modules"])


@router.get("/documents-expires", response_model=DocumentsExpiresResponse, responses=REPONSES_LISTE)
@gerer_exception_api
async def documents_expires(
    jours_avant: int = Query(30, ge=1, le=365, description="Horizon en jours"),
    user: dict = Depends(require_auth),
):
    """Liste les documents expirés ou expirant bientôt (B5.3)."""
    from src.services.ia.bridges import obtenir_service_bridges

    service = obtenir_service_bridges()
    alertes = service.documents_expires_alertes(jours_avant=jours_avant)

    nb_expires = sum(1 for a in alertes if a.get("est_expire"))
    nb_bientot = len(alertes) - nb_expires

    return {
        "alertes": alertes,
        "nb_expires": nb_expires,
        "nb_bientot": nb_bientot,
    }


@router.get("/planning-unifie", response_model=PlanningUnifieResponse, responses=REPONSES_LISTE)
@gerer_exception_api
async def planning_unifie(
    nb_jours: int = Query(7, ge=1, le=30, description="Nombre de jours à afficher"),
    user: dict = Depends(require_auth),
):
    """Planning unifié multi-modules: entretien + activités (B5.5 / B2.8)."""
    from src.services.ia.bridges import obtenir_service_bridges

    service = obtenir_service_bridges()
    taches = service.entretien_planning_unifie(nb_jours=nb_jours)

    nb_en_retard = sum(1 for t in taches if t.get("en_retard"))

    return {
        "taches": taches,
        "nb_total": len(taches),
        "nb_en_retard": nb_en_retard,
    }


@router.get("/recolte-recettes", responses=REPONSES_LISTE)
@gerer_exception_api
async def recolte_recettes(
    ingredient: str = Query(..., min_length=2, description="Ingrédient récolté"),
    user: dict = Depends(require_auth),
):
    """Trouve des recettes utilisant un ingrédient récolté au jardin (B5.1)."""
    from src.services.ia.bridges import obtenir_service_bridges

    service = obtenir_service_bridges()
    recettes = service.recolte_vers_recettes(ingredient)

    return {
        "ingredient": ingredient,
        "recettes": recettes,
        "nb_recettes": len(recettes),
    }


@router.post("/meteo-entretien", responses=REPONSES_LISTE)
@gerer_exception_api
async def meteo_entretien(
    conditions: dict[str, Any],
    user: dict = Depends(require_auth),
):
    """Génère des alertes entretien basées sur les conditions météo (B5.8)."""
    from src.services.ia.bridges import obtenir_service_bridges

    service = obtenir_service_bridges()
    alertes = service.meteo_vers_entretien(conditions)

    return {"alertes": alertes, "nb_alertes": len(alertes)}
