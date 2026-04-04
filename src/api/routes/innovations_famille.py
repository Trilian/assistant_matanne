"""Routes d'innovations orientées famille, routines et vacances."""

from __future__ import annotations

from typing import Any

from fastapi import Depends

from src.api.dependencies import require_auth
from src.api.rate_limiting import verifier_limite_debit_ia
from src.api.routes.innovations_common import (
    RESPONSES_IA_TYPED,
    creer_router_innovations,
    get_innovations_service,
)
from src.api.schemas.fonctionnalites_avancees import (
    CoachRoutinesResponse,
    EnrichissementContactsResponse,
    ModeVacancesConfigurationRequest,
    ModeVacancesResponse,
    PlanningJulesAdaptatifResponse,
    ScoreFamilleHebdoResponse,
    ScoreBienEtreResponse,
)
from src.api.utils import gerer_exception_api

router = creer_router_innovations()


@router.get(
    "/coach-routines",
    response_model=CoachRoutinesResponse,
    responses=RESPONSES_IA_TYPED,
    summary="Coach routines IA",
)
@gerer_exception_api
async def coach_routines(
    user: dict[str, Any] = Depends(require_auth),
):
    service = get_innovations_service()
    result = service.coach_routines_ia()
    return result or CoachRoutinesResponse()


@router.get(
    "/planning-jules-adaptatif",
    response_model=PlanningJulesAdaptatifResponse,
    responses=RESPONSES_IA_TYPED,
    summary="Planning Jules adaptatif",
)
@gerer_exception_api
async def planning_jules_adaptatif(
    user: dict[str, Any] = Depends(require_auth),
):
    service = get_innovations_service()
    result = service.generer_planning_jules_adaptatif()
    return result or PlanningJulesAdaptatifResponse()


@router.get(
    "/score-famille-hebdo",
    response_model=ScoreFamilleHebdoResponse,
    responses=RESPONSES_IA_TYPED,
    summary="Score famille hebdomadaire",
)
@gerer_exception_api
async def score_famille_hebdo(
    user: dict[str, Any] = Depends(require_auth),
):
    service = get_innovations_service()
    result = service.calculer_score_famille_hebdo()
    return result or ScoreFamilleHebdoResponse()


@router.get(
    "/mode-vacances",
    response_model=ModeVacancesResponse,
    responses=RESPONSES_IA_TYPED,
    summary="Lecture mode vacances",
)
@gerer_exception_api
async def lire_mode_vacances(
    user: dict[str, Any] = Depends(require_auth),
):
    service = get_innovations_service()
    user_id = str(user.get("id") or "")
    result = service.obtenir_mode_vacances(user_id=user_id)
    return result or ModeVacancesResponse()


@router.post(
    "/mode-vacances/config",
    response_model=ModeVacancesResponse,
    responses=RESPONSES_IA_TYPED,
    summary="Configuration mode vacances",
)
@gerer_exception_api
async def configurer_mode_vacances(
    body: ModeVacancesConfigurationRequest,
    user: dict[str, Any] = Depends(require_auth),
):
    service = get_innovations_service()
    user_id = str(user.get("id") or "")
    result = service.configurer_mode_vacances(
        user_id=user_id,
        actif=body.actif,
        checklist_voyage_auto=body.checklist_voyage_auto,
    )
    return result or ModeVacancesResponse(actif=body.actif, checklist_voyage_auto=body.checklist_voyage_auto)


@router.get(
    "/tableau-sante-foyer",
    response_model=ScoreBienEtreResponse,
    responses=RESPONSES_IA_TYPED,
    summary="Tableau de bord sante foyer",
)
@gerer_exception_api
async def tableau_sante_foyer(
    user: dict[str, Any] = Depends(require_auth),
):
    service = get_innovations_service()
    result = service.calculer_score_bien_etre()
    return result or ScoreBienEtreResponse()


@router.get(
    "/enrichissement-contacts",
    response_model=EnrichissementContactsResponse,
    responses=RESPONSES_IA_TYPED,
    summary="Enrichissement contacts IA",
)
@gerer_exception_api
async def enrichissement_contacts(
    user: dict[str, Any] = Depends(require_auth),
    _rate: dict[str, Any] = Depends(verifier_limite_debit_ia),
):
    service = get_innovations_service()
    result = service.enrichir_contacts()
    return result or EnrichissementContactsResponse()
