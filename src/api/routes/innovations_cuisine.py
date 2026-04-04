"""Routes d'innovations orientées cuisine et courses."""

from __future__ import annotations

from typing import Any

from fastapi import Depends, Query

from src.api.dependencies import require_auth
from src.api.rate_limiting import verifier_limite_debit_ia
from src.api.routes.innovations_common import (
    RESPONSES_IA_TYPED,
    creer_router_innovations,
    get_innovations_service,
)
from src.api.schemas.fonctionnalites_avancees import (
    BatchCookingIntelligentResponse,
    ComparateurPrixAutomatiqueResponse,
    MangeCeSoirRequest,
    ParcoursOptimiseRequest,
    ParcoursOptimiseResponse,
    PatternsAlimentairesResponse,
    PlanificationHebdoCompleteResponse,
    SaisonnaliteIntelligenteResponse,
    SuggestionRepasSoirResponse,
)
from src.api.utils import gerer_exception_api

router = creer_router_innovations()


@router.post(
    "/mange-ce-soir",
    response_model=SuggestionRepasSoirResponse,
    responses=RESPONSES_IA_TYPED,
    summary="Suggestion diner express",
)
@gerer_exception_api
async def mange_ce_soir(
    body: MangeCeSoirRequest,
    user: dict[str, Any] = Depends(require_auth),
    _rate: dict[str, Any] = Depends(verifier_limite_debit_ia),
):
    service = get_innovations_service()
    result = service.suggerer_repas_ce_soir(
        temps_disponible_min=body.temps_disponible_min,
        humeur=body.humeur,
    )
    return result or SuggestionRepasSoirResponse()


@router.get(
    "/patterns-alimentaires",
    response_model=PatternsAlimentairesResponse,
    responses=RESPONSES_IA_TYPED,
    summary="Detection patterns alimentaires",
)
@gerer_exception_api
async def patterns_alimentaires(
    periode_jours: int = Query(90, ge=30, le=365),
    user: dict[str, Any] = Depends(require_auth),
):
    service = get_innovations_service()
    result = service.analyser_patterns_alimentaires(periode_jours=periode_jours)
    return result or PatternsAlimentairesResponse()


@router.get(
    "/saisonnalite-intelligente",
    response_model=SaisonnaliteIntelligenteResponse,
    responses=RESPONSES_IA_TYPED,
    summary="Saisonnalite intelligente",
)
@gerer_exception_api
async def saisonnalite_intelligente(
    user: dict[str, Any] = Depends(require_auth),
):
    service = get_innovations_service()
    result = service.appliquer_saisonnalite_intelligente()
    return result or SaisonnaliteIntelligenteResponse()


@router.get(
    "/garmin-repas-adaptatif",
    response_model=SuggestionRepasSoirResponse,
    responses=RESPONSES_IA_TYPED,
    summary="Repas adapte a la depense Garmin",
)
@gerer_exception_api
async def garmin_repas_adaptatif(
    user: dict[str, Any] = Depends(require_auth),
):
    service = get_innovations_service()
    user_id_raw = user.get("id")
    user_id = int(user_id_raw) if isinstance(user_id_raw, (int, str)) and str(user_id_raw).isdigit() else None
    result = service.proposer_repas_adapte_garmin(user_id=user_id)
    return result or SuggestionRepasSoirResponse()


@router.get(
    "/planification-auto",
    response_model=PlanificationHebdoCompleteResponse,
    responses=RESPONSES_IA_TYPED,
    summary="Planification hebdo complete automatique",
)
@gerer_exception_api
async def planification_auto(
    user: dict[str, Any] = Depends(require_auth),
):
    service = get_innovations_service()
    user_id = str(user.get("id") or "")
    result = service.generer_planification_hebdo_complete(user_id=user_id)
    return result or PlanificationHebdoCompleteResponse()


@router.get(
    "/batch-cooking-intelligent",
    response_model=BatchCookingIntelligentResponse,
    responses=RESPONSES_IA_TYPED,
    summary="Suggestions batch cooking intelligentes",
)
@gerer_exception_api
async def batch_cooking_intelligent(
    user: dict[str, Any] = Depends(require_auth),
):
    service = get_innovations_service()
    user_id = str(user.get("id") or "")
    result = service.proposer_batch_cooking_intelligent(user_id=user_id)
    return result or BatchCookingIntelligentResponse()


@router.post(
    "/parcours-magasin",
    response_model=ParcoursOptimiseResponse,
    responses=RESPONSES_IA_TYPED,
    summary="Optimisation parcours magasin",
)
@gerer_exception_api
async def parcours_magasin(
    body: ParcoursOptimiseRequest,
    user: dict[str, Any] = Depends(require_auth),
    _rate: dict[str, Any] = Depends(verifier_limite_debit_ia),
):
    service = get_innovations_service()
    result = service.optimiser_parcours_magasin(liste_id=body.liste_id)
    return result or ParcoursOptimiseResponse()


@router.get(
    "/comparateur-prix-auto",
    response_model=ComparateurPrixAutomatiqueResponse,
    responses=RESPONSES_IA_TYPED,
    summary="Comparateur prix automatique",
)
@gerer_exception_api
async def comparateur_prix_auto(
    top_n: int = Query(20, ge=1, le=20),
    user: dict[str, Any] = Depends(require_auth),
):
    service = get_innovations_service()
    result = service.analyser_comparateur_prix_automatique(top_n=top_n)
    return result or ComparateurPrixAutomatiqueResponse()
