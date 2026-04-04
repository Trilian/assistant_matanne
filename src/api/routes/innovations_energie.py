"""Routes d'innovations orientées énergie et consommation."""

from __future__ import annotations

from typing import Any

from fastapi import Depends

from src.api.dependencies import require_auth
from src.api.routes.innovations_common import (
    RESPONSES_IA_TYPED,
    creer_router_innovations,
    get_innovations_service,
)
from src.api.schemas.fonctionnalites_avancees import (
    AnomaliesEnergieResponse,
    ComparateurEnergieRequest,
    ComparateurEnergieResponse,
    EnergieTempsReelResponse,
)
from src.api.utils import gerer_exception_api

router = creer_router_innovations()


@router.get(
    "/anomalies-energie",
    response_model=AnomaliesEnergieResponse,
    responses=RESPONSES_IA_TYPED,
    summary="Detection anomalies eau/gaz/elec",
)
@gerer_exception_api
async def anomalies_energie(
    user: dict[str, Any] = Depends(require_auth),
):
    service = get_innovations_service()
    result = service.detecter_anomalies_energie()
    return result or AnomaliesEnergieResponse()


@router.post(
    "/comparateur-energie",
    response_model=ComparateurEnergieResponse,
    responses=RESPONSES_IA_TYPED,
    summary="Comparateur fournisseurs energie",
)
@gerer_exception_api
async def comparateur_energie(
    body: ComparateurEnergieRequest,
    user: dict[str, Any] = Depends(require_auth),
):
    service = get_innovations_service()
    result = service.comparer_fournisseurs_energie(
        prix_kwh_actuel_eur=body.prix_kwh_actuel_eur,
        abonnement_mensuel_eur=body.abonnement_mensuel_eur,
    )
    return result or ComparateurEnergieResponse()


@router.get(
    "/energie-temps-reel",
    response_model=EnergieTempsReelResponse,
    responses=RESPONSES_IA_TYPED,
    summary="Tableau énergie temps-réel",
)
@gerer_exception_api
async def energie_temps_reel(
    user: dict[str, Any] = Depends(require_auth),
):
    service = get_innovations_service()
    result = service.obtenir_tableau_bord_energie_temps_reel()
    return result or EnergieTempsReelResponse()
