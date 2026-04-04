"""Routes d'innovations transverses : jeux, emploi et partage invité."""

from __future__ import annotations

from typing import Any

from fastapi import Depends, HTTPException, Query

from src.api.dependencies import require_auth
from src.api.rate_limiting import verifier_limite_debit_ia
from src.api.routes.innovations_common import (
    RESPONSES_IA_TYPED,
    creer_router_innovations,
    get_innovations_service,
)
from src.api.schemas.fonctionnalites_avancees import (
    AnalyseTendancesLotoResponse,
    DonneesInviteResponse,
    LienInviteRequest,
    LienInviteResponse,
    VeilleEmploiRequest,
    VeilleEmploiResponse,
)
from src.api.utils import gerer_exception_api

router = creer_router_innovations()


@router.get(
    "/tendances-loto",
    response_model=AnalyseTendancesLotoResponse,
    responses=RESPONSES_IA_TYPED,
    summary="Analyse tendances Loto/EuroMillions",
)
@gerer_exception_api
async def tendances_loto(
    jeu: str = Query("loto", pattern="^(loto|euromillions)$", description="Type de jeu"),
    user: dict[str, Any] = Depends(require_auth),
    _rate: dict[str, Any] = Depends(verifier_limite_debit_ia),
):
    service = get_innovations_service()
    result = service.analyser_tendances_loto(jeu=jeu)
    if result is None:
        return AnalyseTendancesLotoResponse()
    return result


@router.post(
    "/veille-emploi",
    response_model=VeilleEmploiResponse,
    responses=RESPONSES_IA_TYPED,
    summary="Veille emploi multi-sites",
)
@gerer_exception_api
async def veille_emploi(
    body: VeilleEmploiRequest,
    user: dict[str, Any] = Depends(require_auth),
    _rate: dict[str, Any] = Depends(verifier_limite_debit_ia),
):
    from src.services.experimental.types import CriteresVeilleEmploi

    criteres = CriteresVeilleEmploi(
        domaine=body.domaine,
        mots_cles=body.mots_cles,
        type_contrat=body.type_contrat,
        mode_travail=body.mode_travail,
        rayon_km=body.rayon_km,
        frequence=body.frequence,
    )
    service = get_innovations_service()
    result = service.executer_veille_emploi(criteres=criteres)
    if result is None:
        return VeilleEmploiResponse()
    return result


@router.post(
    "/invite/creer",
    response_model=LienInviteResponse,
    summary="Creer un lien invite partageable",
)
@gerer_exception_api
async def creer_lien_invite(
    body: LienInviteRequest,
    user: dict[str, Any] = Depends(require_auth),
):
    modules_valides = {"repas", "routines", "contacts_urgence"}
    modules_demandes = [m for m in body.modules if m in modules_valides]
    if not modules_demandes:
        raise HTTPException(status_code=400, detail="Au moins un module valide requis.")

    service = get_innovations_service()
    return service.creer_lien_invite(
        nom_invite=body.nom_invite,
        modules=modules_demandes,
        duree_heures=body.duree_heures,
    )


@router.get(
    "/invite/{token}",
    response_model=DonneesInviteResponse,
    summary="Acces invite - sans authentification",
)
@gerer_exception_api
async def acceder_donnees_invite(token: str):
    service = get_innovations_service()
    result = service.obtenir_donnees_invite(token=token)
    if result is None:
        raise HTTPException(status_code=404, detail="Lien invite invalide ou expire.")
    return result
