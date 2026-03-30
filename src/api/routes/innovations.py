"""
Routes API pour les Innovations — Phase 10 du planning.

Endpoints :
- POST /api/v1/innovations/bilan-annuel        : Bilan annuel IA
- GET  /api/v1/innovations/score-bien-etre      : Score bien-être familial
- GET  /api/v1/innovations/enrichissement-contacts : Enrichissement contacts IA
- GET  /api/v1/innovations/tendances-loto       : Analyse tendances Loto/EuroMillions
- POST /api/v1/innovations/parcours-magasin     : Optimisation parcours magasin
- POST /api/v1/innovations/veille-emploi        : Veille emploi multi-sites
- POST /api/v1/innovations/invite/creer         : Créer lien invité
- GET  /api/v1/innovations/invite/{token}       : Accès invité (sans auth)
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query

from src.api.dependencies import require_auth
from src.api.rate_limiting import verifier_limite_debit_ia
from src.api.schemas.errors import REPONSES_IA
from src.api.schemas.innovations import (
    AnalyseTendancesLotoResponse,
    BilanAnnuelRequest,
    BilanAnnuelResponse,
    DonneesInviteResponse,
    EnrichissementContactsResponse,
    LienInviteRequest,
    LienInviteResponse,
    ParcoursOptimiseRequest,
    ParcoursOptimiseResponse,
    ScoreBienEtreResponse,
    VeilleEmploiRequest,
    VeilleEmploiResponse,
)
from src.api.utils import gerer_exception_api

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/innovations", tags=["Innovations"])


def _get_service():
    """Lazy-load le service Innovations."""
    from src.services.innovations import get_innovations_service

    return get_innovations_service()


# ═══════════════════════════════════════════════════════════
# 10.4 — BILAN ANNUEL AUTOMATIQUE IA
# ═══════════════════════════════════════════════════════════


@router.post(
    "/bilan-annuel",
    response_model=BilanAnnuelResponse,
    responses=REPONSES_IA,
    summary="Bilan annuel complet IA",
)
@gerer_exception_api
async def bilan_annuel(
    body: BilanAnnuelRequest,
    user: dict = Depends(require_auth),
    _rate: dict = Depends(verifier_limite_debit_ia),
):
    """Génère un bilan annuel complet : cuisine, budget, maison, Jules, sport."""
    service = _get_service()
    result = service.generer_bilan_annuel(annee=body.annee)
    if result is None:
        return BilanAnnuelResponse()
    return result


# ═══════════════════════════════════════════════════════════
# 10.5 — SCORE BIEN-ÊTRE FAMILIAL
# ═══════════════════════════════════════════════════════════


@router.get(
    "/score-bien-etre",
    response_model=ScoreBienEtreResponse,
    responses=REPONSES_IA,
    summary="Score bien-être familial composite",
)
@gerer_exception_api
async def score_bien_etre(
    user: dict = Depends(require_auth),
):
    """Calcule le score bien-être familial (sport + nutrition + budget + routines)."""
    service = _get_service()
    result = service.calculer_score_bien_etre()
    if result is None:
        return ScoreBienEtreResponse()
    return result


# ═══════════════════════════════════════════════════════════
# 10.17 — ENRICHISSEMENT CONTACTS IA
# ═══════════════════════════════════════════════════════════


@router.get(
    "/enrichissement-contacts",
    response_model=EnrichissementContactsResponse,
    responses=REPONSES_IA,
    summary="Enrichissement contacts IA",
)
@gerer_exception_api
async def enrichissement_contacts(
    user: dict = Depends(require_auth),
    _rate: dict = Depends(verifier_limite_debit_ia),
):
    """Analyse et enrichit les contacts (catégorisation, rappels relationnels)."""
    service = _get_service()
    result = service.enrichir_contacts()
    if result is None:
        return EnrichissementContactsResponse()
    return result


# ═══════════════════════════════════════════════════════════
# 10.18 — ANALYSE TENDANCES LOTO
# ═══════════════════════════════════════════════════════════


@router.get(
    "/tendances-loto",
    response_model=AnalyseTendancesLotoResponse,
    responses=REPONSES_IA,
    summary="Analyse tendances Loto/EuroMillions",
)
@gerer_exception_api
async def tendances_loto(
    jeu: str = Query("loto", regex="^(loto|euromillions)$", description="Type de jeu"),
    user: dict = Depends(require_auth),
    _rate: dict = Depends(verifier_limite_debit_ia),
):
    """Analyse statistique des tirages avec numéros chauds/froids et combinaison suggérée."""
    service = _get_service()
    result = service.analyser_tendances_loto(jeu=jeu)
    if result is None:
        return AnalyseTendancesLotoResponse()
    return result


# ═══════════════════════════════════════════════════════════
# 10.19 — OPTIMISATION PARCOURS MAGASIN
# ═══════════════════════════════════════════════════════════


@router.post(
    "/parcours-magasin",
    response_model=ParcoursOptimiseResponse,
    responses=REPONSES_IA,
    summary="Optimisation parcours magasin",
)
@gerer_exception_api
async def parcours_magasin(
    body: ParcoursOptimiseRequest,
    user: dict = Depends(require_auth),
    _rate: dict = Depends(verifier_limite_debit_ia),
):
    """Regroupe les articles de courses par rayon et optimise l'ordre de parcours."""
    service = _get_service()
    result = service.optimiser_parcours_magasin(liste_id=body.liste_id)
    if result is None:
        return ParcoursOptimiseResponse()
    return result


# ═══════════════════════════════════════════════════════════
# 10.8 — VEILLE EMPLOI
# ═══════════════════════════════════════════════════════════


@router.post(
    "/veille-emploi",
    response_model=VeilleEmploiResponse,
    responses=REPONSES_IA,
    summary="Veille emploi multi-sites",
)
@gerer_exception_api
async def veille_emploi(
    body: VeilleEmploiRequest,
    user: dict = Depends(require_auth),
    _rate: dict = Depends(verifier_limite_debit_ia),
):
    """Exécute la veille emploi avec critères configurables."""
    from src.services.innovations.types import CriteresVeilleEmploi

    criteres = CriteresVeilleEmploi(
        domaine=body.domaine,
        mots_cles=body.mots_cles,
        type_contrat=body.type_contrat,
        mode_travail=body.mode_travail,
        rayon_km=body.rayon_km,
        frequence=body.frequence,
    )
    service = _get_service()
    result = service.executer_veille_emploi(criteres=criteres)
    if result is None:
        return VeilleEmploiResponse()
    return result


# ═══════════════════════════════════════════════════════════
# 10.3 — MODE INVITÉ
# ═══════════════════════════════════════════════════════════


@router.post(
    "/invite/creer",
    response_model=LienInviteResponse,
    summary="Créer un lien invité partageable",
)
@gerer_exception_api
async def creer_lien_invite(
    body: LienInviteRequest,
    user: dict = Depends(require_auth),
):
    """Crée un lien partageable pour un invité (nounou, grands-parents).

    Modules accessibles : repas, routines, contacts_urgence.
    """
    modules_valides = {"repas", "routines", "contacts_urgence"}
    modules_demandes = [m for m in body.modules if m in modules_valides]
    if not modules_demandes:
        raise HTTPException(status_code=400, detail="Au moins un module valide requis.")

    service = _get_service()
    return service.creer_lien_invite(
        nom_invite=body.nom_invite,
        modules=modules_demandes,
        duree_heures=body.duree_heures,
    )


@router.get(
    "/invite/{token}",
    response_model=DonneesInviteResponse,
    summary="Accès invité — sans authentification",
)
@gerer_exception_api
async def acceder_donnees_invite(token: str):
    """Accès aux données via lien invité (pas d'authentification requise)."""
    service = _get_service()
    result = service.obtenir_donnees_invite(token=token)
    if result is None:
        raise HTTPException(status_code=404, detail="Lien invité invalide ou expiré.")
    return result
