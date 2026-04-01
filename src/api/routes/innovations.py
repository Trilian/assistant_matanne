"""
Routes API pour les Innovations — Phases 9 et 10 du planning.

Endpoints :
- GET  /api/v1/innovations/phase9/*           : Endpoints dédiés IA avancée P9
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
    AlertesContextuellesResponse,
    AnalyseTendancesLotoResponse,
    AnomaliesEnergieResponse,
    ApprentissageHabitudesResponse,
    BilanAnnuelRequest,
    BilanAnnuelResponse,
    CoachRoutinesResponse,
    ComparateurEnergieRequest,
    ComparateurEnergieResponse,
    DonneesInviteResponse,
    EnrichissementContactsResponse,
    LienInviteRequest,
    LienInviteResponse,
    MangeCeSoirRequest,
    PatternsAlimentairesResponse,
    ParcoursOptimiseRequest,
    ParcoursOptimiseResponse,
    PlanningJulesAdaptatifResponse,
    ResumeMensuelIAResponse,
    SaisonnaliteIntelligenteResponse,
    ScoreEcoResponsableResponse,
    ScoreBienEtreResponse,
    SuggestionRepasSoirResponse,
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
# PHASE 9 — IA AVANCÉE & INNOVATIONS
# ═══════════════════════════════════════════════════════════


@router.post(
    "/phase9/mange-ce-soir",
    response_model=SuggestionRepasSoirResponse,
    responses=REPONSES_IA,
    summary="P9-01 Suggestion dîner express",
)
@gerer_exception_api
async def p9_mange_ce_soir(
    body: MangeCeSoirRequest,
    user: dict = Depends(require_auth),
    _rate: dict = Depends(verifier_limite_debit_ia),
):
    service = _get_service()
    result = service.suggerer_repas_ce_soir(
        temps_disponible_min=body.temps_disponible_min,
        humeur=body.humeur,
    )
    return result or SuggestionRepasSoirResponse()


@router.get(
    "/phase9/patterns-alimentaires",
    response_model=PatternsAlimentairesResponse,
    responses=REPONSES_IA,
    summary="P9-02 Détection patterns alimentaires",
)
@gerer_exception_api
async def p9_patterns_alimentaires(
    periode_jours: int = Query(90, ge=30, le=365),
    user: dict = Depends(require_auth),
):
    service = _get_service()
    result = service.analyser_patterns_alimentaires(periode_jours=periode_jours)
    return result or PatternsAlimentairesResponse()


@router.get(
    "/phase9/coach-routines",
    response_model=CoachRoutinesResponse,
    responses=REPONSES_IA,
    summary="P9-03 Coach routines IA",
)
@gerer_exception_api
async def p9_coach_routines(
    user: dict = Depends(require_auth),
):
    service = _get_service()
    result = service.coach_routines_ia()
    return result or CoachRoutinesResponse()


@router.get(
    "/phase9/anomalies-energie",
    response_model=AnomaliesEnergieResponse,
    responses=REPONSES_IA,
    summary="P9-04 Détection anomalies eau/gaz/élec",
)
@gerer_exception_api
async def p9_anomalies_energie(
    user: dict = Depends(require_auth),
):
    service = _get_service()
    result = service.detecter_anomalies_energie()
    return result or AnomaliesEnergieResponse()


@router.get(
    "/phase9/resume-mensuel",
    response_model=ResumeMensuelIAResponse,
    responses=REPONSES_IA,
    summary="P9-06 Résumé mensuel IA",
)
@gerer_exception_api
async def p9_resume_mensuel(
    user: dict = Depends(require_auth),
    _rate: dict = Depends(verifier_limite_debit_ia),
):
    service = _get_service()
    result = service.generer_resume_mensuel_ia()
    return result or ResumeMensuelIAResponse()


@router.get(
    "/phase9/planning-jules-adaptatif",
    response_model=PlanningJulesAdaptatifResponse,
    responses=REPONSES_IA,
    summary="P9-08 Planning Jules adaptatif",
)
@gerer_exception_api
async def p9_planning_jules_adaptatif(
    user: dict = Depends(require_auth),
):
    service = _get_service()
    result = service.generer_planning_jules_adaptatif()
    return result or PlanningJulesAdaptatifResponse()


@router.post(
    "/phase9/comparateur-energie",
    response_model=ComparateurEnergieResponse,
    responses=REPONSES_IA,
    summary="P9-09 Comparateur fournisseurs énergie",
)
@gerer_exception_api
async def p9_comparateur_energie(
    body: ComparateurEnergieRequest,
    user: dict = Depends(require_auth),
):
    service = _get_service()
    result = service.comparer_fournisseurs_energie(
        prix_kwh_actuel_eur=body.prix_kwh_actuel_eur,
        abonnement_mensuel_eur=body.abonnement_mensuel_eur,
    )
    return result or ComparateurEnergieResponse()


@router.get(
    "/phase9/score-eco-responsable",
    response_model=ScoreEcoResponsableResponse,
    responses=REPONSES_IA,
    summary="P9-10 Score éco-responsable",
)
@gerer_exception_api
async def p9_score_eco_responsable(
    user: dict = Depends(require_auth),
):
    service = _get_service()
    result = service.calculer_score_eco_responsable()
    return result or ScoreEcoResponsableResponse()


@router.get(
    "/phase9/saisonnalite-intelligente",
    response_model=SaisonnaliteIntelligenteResponse,
    responses=REPONSES_IA,
    summary="P9-11 Saisonnalité intelligente",
)
@gerer_exception_api
async def p9_saisonnalite_intelligente(
    user: dict = Depends(require_auth),
):
    service = _get_service()
    result = service.appliquer_saisonnalite_intelligente()
    return result or SaisonnaliteIntelligenteResponse()


@router.get(
    "/phase9/apprentissage-habitudes",
    response_model=ApprentissageHabitudesResponse,
    responses=REPONSES_IA,
    summary="P9-12 Apprentissage continu habitudes",
)
@gerer_exception_api
async def p9_apprentissage_habitudes(
    user: dict = Depends(require_auth),
):
    service = _get_service()
    result = service.apprendre_habitudes_utilisateur()
    return result or ApprentissageHabitudesResponse()


@router.get(
    "/phase9/retrospective-annuelle",
    response_model=BilanAnnuelResponse,
    responses=REPONSES_IA,
    summary="P9-13 Rétrospective annuelle IA",
)
@gerer_exception_api
async def p9_retrospective_annuelle(
    annee: int | None = Query(None, ge=2020, le=2100),
    user: dict = Depends(require_auth),
    _rate: dict = Depends(verifier_limite_debit_ia),
):
    service = _get_service()
    result = service.generer_bilan_annuel(annee=annee)
    return result or BilanAnnuelResponse()


@router.get(
    "/phase9/alertes-contextuelles",
    response_model=AlertesContextuellesResponse,
    responses=REPONSES_IA,
    summary="P9-14 Alertes intelligentes contextuelles",
)
@gerer_exception_api
async def p9_alertes_contextuelles(
    user: dict = Depends(require_auth),
):
    service = _get_service()
    result = service.generer_alertes_contextuelles()
    return result or AlertesContextuellesResponse()


@router.get(
    "/phase9/tableau-sante-foyer",
    response_model=ScoreBienEtreResponse,
    responses=REPONSES_IA,
    summary="P9-15 Tableau de bord santé foyer",
)
@gerer_exception_api
async def p9_tableau_sante_foyer(
    user: dict = Depends(require_auth),
):
    service = _get_service()
    result = service.calculer_score_bien_etre()
    return result or ScoreBienEtreResponse()


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
