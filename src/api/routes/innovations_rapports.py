"""Routes d'innovations orientées rapports, résumés et synthèses."""

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
    BilanAnnuelRequest,
    BilanAnnuelResponse,
    CarteVisuellePartageableResponse,
    CarteVisuelleRequest,
    JournalFamilialAutoResponse,
    ModeTabletteMagazineResponse,
    RapportMensuelPdfResponse,
    ResumeMensuelIAResponse,
    ScoreBienEtreResponse,
    ScoreEcoResponsableResponse,
)
from src.api.utils import gerer_exception_api

router = creer_router_innovations()


@router.get(
    "/resume-mensuel",
    response_model=ResumeMensuelIAResponse,
    responses=RESPONSES_IA_TYPED,
    summary="Resume mensuel IA",
)
@gerer_exception_api
async def resume_mensuel(
    user: dict[str, Any] = Depends(require_auth),
    _rate: dict[str, Any] = Depends(verifier_limite_debit_ia),
):
    service = get_innovations_service()
    result = service.generer_resume_mensuel_ia()
    return result or ResumeMensuelIAResponse()


@router.get(
    "/retrospective-annuelle",
    response_model=BilanAnnuelResponse,
    responses=RESPONSES_IA_TYPED,
    summary="Retrospective annuelle IA",
)
@gerer_exception_api
async def retrospective_annuelle(
    annee: int | None = Query(None, ge=2020, le=2100),
    user: dict[str, Any] = Depends(require_auth),
    _rate: dict[str, Any] = Depends(verifier_limite_debit_ia),
):
    service = get_innovations_service()
    result = service.generer_bilan_annuel(annee=annee)
    return result or BilanAnnuelResponse()


@router.get(
    "/journal-familial",
    response_model=JournalFamilialAutoResponse,
    responses=RESPONSES_IA_TYPED,
    summary="Journal familial automatique",
)
@gerer_exception_api
async def journal_familial(
    user: dict[str, Any] = Depends(require_auth),
    _rate: dict[str, Any] = Depends(verifier_limite_debit_ia),
):
    service = get_innovations_service()
    result = service.generer_journal_familial_auto()
    return result or JournalFamilialAutoResponse()


@router.get(
    "/journal-familial/pdf",
    response_model=RapportMensuelPdfResponse,
    responses=RESPONSES_IA_TYPED,
    summary="Export PDF journal familial",
)
@gerer_exception_api
async def journal_familial_pdf(
    user: dict[str, Any] = Depends(require_auth),
):
    service = get_innovations_service()
    result = service.generer_journal_familial_pdf()
    return result or RapportMensuelPdfResponse()


@router.get(
    "/rapport-mensuel/pdf",
    response_model=RapportMensuelPdfResponse,
    responses=RESPONSES_IA_TYPED,
    summary="Rapport mensuel PDF",
)
@gerer_exception_api
async def rapport_mensuel_pdf(
    mois: str | None = Query(None, description="Format YYYY-MM"),
    user: dict[str, Any] = Depends(require_auth),
):
    service = get_innovations_service()
    result = service.generer_rapport_mensuel_pdf(mois=mois)
    return result or RapportMensuelPdfResponse()


@router.post(
    "/bilan-annuel",
    response_model=BilanAnnuelResponse,
    responses=RESPONSES_IA_TYPED,
    summary="Bilan annuel complet IA",
)
@gerer_exception_api
async def bilan_annuel(
    body: BilanAnnuelRequest,
    user: dict[str, Any] = Depends(require_auth),
    _rate: dict[str, Any] = Depends(verifier_limite_debit_ia),
):
    service = get_innovations_service()
    result = service.generer_bilan_annuel(annee=body.annee)
    if result is None:
        return BilanAnnuelResponse()
    return result


@router.get(
    "/score-bien-etre",
    response_model=ScoreBienEtreResponse,
    responses=RESPONSES_IA_TYPED,
    summary="Score bien-etre familial composite",
)
@gerer_exception_api
async def score_bien_etre(
    user: dict[str, Any] = Depends(require_auth),
):
    service = get_innovations_service()
    result = service.calculer_score_bien_etre()
    if result is None:
        return ScoreBienEtreResponse()
    return result


@router.get(
    "/score-eco-responsable",
    response_model=ScoreEcoResponsableResponse,
    responses=RESPONSES_IA_TYPED,
    summary="Score eco-responsable",
)
@gerer_exception_api
async def score_eco_responsable(
    user: dict[str, Any] = Depends(require_auth),
):
    service = get_innovations_service()
    result = service.calculer_score_eco_responsable()
    return result or ScoreEcoResponsableResponse()


@router.post(
    "/carte-visuelle",
    response_model=CarteVisuellePartageableResponse,
    responses=RESPONSES_IA_TYPED,
    summary="Carte visuelle partageable",
)
@gerer_exception_api
async def carte_visuelle(
    body: CarteVisuelleRequest,
    user: dict[str, Any] = Depends(require_auth),
):
    service = get_innovations_service()
    result = service.generer_carte_visuelle_partageable(
        type_carte=body.type_carte,
        titre=body.titre,
    )
    return result or CarteVisuellePartageableResponse(type_carte=body.type_carte)


@router.get(
    "/mode-tablette-magazine",
    response_model=ModeTabletteMagazineResponse,
    responses=RESPONSES_IA_TYPED,
    summary="Mode tablette magazine",
)
@gerer_exception_api
async def mode_tablette_magazine(
    user: dict[str, Any] = Depends(require_auth),
):
    service = get_innovations_service()
    result = service.obtenir_mode_tablette_magazine()
    return result or ModeTabletteMagazineResponse()
