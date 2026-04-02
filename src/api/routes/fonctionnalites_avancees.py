"""
Routes API pour les Fonctionnalités Avancées.

Endpoints :
- GET  /api/v1/innovations/phase9/*           : Endpoints dedies IA avancee P9
- POST /api/v1/innovations/bilan-annuel        : Bilan annuel IA
- GET  /api/v1/innovations/score-bien-etre      : Score bien-etre familial
- GET  /api/v1/innovations/enrichissement-contacts : Enrichissement contacts IA
- GET  /api/v1/innovations/tendances-loto       : Analyse tendances Loto/EuroMillions
- POST /api/v1/innovations/parcours-magasin     : Optimisation parcours magasin
- POST /api/v1/innovations/veille-emploi        : Veille emploi multi-sites
- POST /api/v1/innovations/invite/creer         : Creer lien invite
- GET  /api/v1/innovations/invite/{token}       : Acces invite (sans auth)
"""

import logging

from typing import Any, cast

from fastapi import APIRouter, Depends, HTTPException, Query

from src.api.dependencies import require_auth
from src.api.rate_limiting import verifier_limite_debit_ia
from src.api.schemas.errors import REPONSES_IA
from src.api.schemas.fonctionnalites_avancees import (
    AlertesContextuellesResponse,
    ApprentissagePreferencesResponse,
    BatchCookingIntelligentResponse,
    CarteVisuellePartageableResponse,
    CarteVisuelleRequest,
    JournalFamilialAutoResponse,
    ModeTabletteMagazineResponse,
    ModePiloteAutomatiqueResponse,
    RapportMensuelPdfResponse,
    ScoreFamilleHebdoResponse,
    AnalyseTendancesLotoResponse,
    AnomaliesEnergieResponse,
    ApprentissageHabitudesResponse,
    BilanAnnuelRequest,
    BilanAnnuelResponse,
    CoachRoutinesResponse,
    ComparateurEnergieRequest,
    ComparateurEnergieResponse,
    ModePiloteConfigurationRequest,
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
    InsightsQuotidiensResponse,
    MeteoContextuelleResponse,
    ModeVacancesConfigurationRequest,
    ModeVacancesResponse,
    PlanificationHebdoCompleteResponse,
)
from src.api.utils import gerer_exception_api

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/innovations", tags=["Innovations"])
RESPONSES_IA_TYPED = cast(dict[int | str, dict[str, Any]], REPONSES_IA)


def _get_service():
    """Lazy-load le service Innovations."""
    from src.services.innovations import get_innovations_service

    return get_innovations_service()


# ===========================================================
# PHASE 9 - IA AVANCEE & INNOVATIONS
# ===========================================================


@router.post(
    "/phase9/mange-ce-soir",
    response_model=SuggestionRepasSoirResponse,
    responses=RESPONSES_IA_TYPED,
    summary="P9-01 Suggestion diner express",
)
@gerer_exception_api
async def p9_mange_ce_soir(
    body: MangeCeSoirRequest,
    user: dict[str, Any] = Depends(require_auth),
    _rate: dict[str, Any] = Depends(verifier_limite_debit_ia),
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
    responses=RESPONSES_IA_TYPED,
    summary="P9-02 Detection patterns alimentaires",
)
@gerer_exception_api
async def p9_patterns_alimentaires(
    periode_jours: int = Query(90, ge=30, le=365),
    user: dict[str, Any] = Depends(require_auth),
):
    service = _get_service()
    result = service.analyser_patterns_alimentaires(periode_jours=periode_jours)
    return result or PatternsAlimentairesResponse()


@router.get(
    "/phase9/coach-routines",
    response_model=CoachRoutinesResponse,
    responses=RESPONSES_IA_TYPED,
    summary="P9-03 Coach routines IA",
)
@gerer_exception_api
async def p9_coach_routines(
    user: dict[str, Any] = Depends(require_auth),
):
    service = _get_service()
    result = service.coach_routines_ia()
    return result or CoachRoutinesResponse()


@router.get(
    "/phase9/anomalies-energie",
    response_model=AnomaliesEnergieResponse,
    responses=RESPONSES_IA_TYPED,
    summary="P9-04 Detection anomalies eau/gaz/elec",
)
@gerer_exception_api
async def p9_anomalies_energie(
    user: dict[str, Any] = Depends(require_auth),
):
    service = _get_service()
    result = service.detecter_anomalies_energie()
    return result or AnomaliesEnergieResponse()


@router.get(
    "/phase9/resume-mensuel",
    response_model=ResumeMensuelIAResponse,
    responses=RESPONSES_IA_TYPED,
    summary="P9-06 Resume mensuel IA",
)
@gerer_exception_api
async def p9_resume_mensuel(
    user: dict[str, Any] = Depends(require_auth),
    _rate: dict[str, Any] = Depends(verifier_limite_debit_ia),
):
    service = _get_service()
    result = service.generer_resume_mensuel_ia()
    return result or ResumeMensuelIAResponse()


@router.get(
    "/phase9/planning-jules-adaptatif",
    response_model=PlanningJulesAdaptatifResponse,
    responses=RESPONSES_IA_TYPED,
    summary="P9-08 Planning Jules adaptatif",
)
@gerer_exception_api
async def p9_planning_jules_adaptatif(
    user: dict[str, Any] = Depends(require_auth),
):
    service = _get_service()
    result = service.generer_planning_jules_adaptatif()
    return result or PlanningJulesAdaptatifResponse()


@router.post(
    "/phase9/comparateur-energie",
    response_model=ComparateurEnergieResponse,
    responses=RESPONSES_IA_TYPED,
    summary="P9-09 Comparateur fournisseurs energie",
)
@gerer_exception_api
async def p9_comparateur_energie(
    body: ComparateurEnergieRequest,
    user: dict[str, Any] = Depends(require_auth),
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
    responses=RESPONSES_IA_TYPED,
    summary="P9-10 Score eco-responsable",
)
@gerer_exception_api
async def p9_score_eco_responsable(
    user: dict[str, Any] = Depends(require_auth),
):
    service = _get_service()
    result = service.calculer_score_eco_responsable()
    return result or ScoreEcoResponsableResponse()


@router.get(
    "/phase9/saisonnalite-intelligente",
    response_model=SaisonnaliteIntelligenteResponse,
    responses=RESPONSES_IA_TYPED,
    summary="P9-11 Saisonnalite intelligente",
)
@gerer_exception_api
async def p9_saisonnalite_intelligente(
    user: dict[str, Any] = Depends(require_auth),
):
    service = _get_service()
    result = service.appliquer_saisonnalite_intelligente()
    return result or SaisonnaliteIntelligenteResponse()


@router.get(
    "/phase9/apprentissage-habitudes",
    response_model=ApprentissageHabitudesResponse,
    responses=RESPONSES_IA_TYPED,
    summary="P9-12 Apprentissage continu habitudes",
)
@gerer_exception_api
async def p9_apprentissage_habitudes(
    user: dict[str, Any] = Depends(require_auth),
):
    service = _get_service()
    result = service.apprendre_habitudes_utilisateur()
    return result or ApprentissageHabitudesResponse()


@router.get(
    "/phase9/retrospective-annuelle",
    response_model=BilanAnnuelResponse,
    responses=RESPONSES_IA_TYPED,
    summary="P9-13 Retrospective annuelle IA",
)
@gerer_exception_api
async def p9_retrospective_annuelle(
    annee: int | None = Query(None, ge=2020, le=2100),
    user: dict[str, Any] = Depends(require_auth),
    _rate: dict[str, Any] = Depends(verifier_limite_debit_ia),
):
    service = _get_service()
    result = service.generer_bilan_annuel(annee=annee)
    return result or BilanAnnuelResponse()


@router.get(
    "/phase9/alertes-contextuelles",
    response_model=AlertesContextuellesResponse,
    responses=RESPONSES_IA_TYPED,
    summary="P9-14 Alertes intelligentes contextuelles",
)
@gerer_exception_api
async def p9_alertes_contextuelles(
    user: dict[str, Any] = Depends(require_auth),
):
    service = _get_service()
    result = service.generer_alertes_contextuelles()
    return result or AlertesContextuellesResponse()


@router.get(
    "/phasee/mode-pilote",
    response_model=ModePiloteAutomatiqueResponse,
    responses=RESPONSES_IA_TYPED,
    summary="E1 Mode pilote automatique",
)
@gerer_exception_api
async def phasee_mode_pilote(
    user: dict[str, Any] = Depends(require_auth),
):
    service = _get_service()
    user_id_raw = user.get("id")
    user_id = int(user_id_raw) if isinstance(user_id_raw, (int, str)) and str(user_id_raw).isdigit() else None
    result = service.obtenir_mode_pilote_automatique(user_id=user_id)
    return result or ModePiloteAutomatiqueResponse()


@router.post(
    "/phasee/mode-pilote/config",
    response_model=ModePiloteAutomatiqueResponse,
    responses=RESPONSES_IA_TYPED,
    summary="E1 Config mode pilote automatique",
)
@gerer_exception_api
async def phasee_configurer_mode_pilote(
    body: ModePiloteConfigurationRequest,
    user: dict[str, Any] = Depends(require_auth),
):
    service = _get_service()
    user_id_raw = user.get("id")
    user_id = int(user_id_raw) if isinstance(user_id_raw, (int, str)) and str(user_id_raw).isdigit() else None
    result = service.configurer_mode_pilote_automatique(
        user_id=user_id,
        actif=body.actif,
        niveau_autonomie=body.niveau_autonomie,
    )
    return result or ModePiloteAutomatiqueResponse(actif=body.actif)


@router.get(
    "/phasee/score-famille-hebdo",
    response_model=ScoreFamilleHebdoResponse,
    responses=RESPONSES_IA_TYPED,
    summary="E3 Score famille hebdomadaire",
)
@gerer_exception_api
async def phasee_score_famille_hebdo(
    user: dict[str, Any] = Depends(require_auth),
):
    service = _get_service()
    result = service.calculer_score_famille_hebdo()
    return result or ScoreFamilleHebdoResponse()


@router.get(
    "/phasee/journal-familial",
    response_model=JournalFamilialAutoResponse,
    responses=RESPONSES_IA_TYPED,
    summary="E8 Journal familial automatique",
)
@gerer_exception_api
async def phasee_journal_familial(
    user: dict[str, Any] = Depends(require_auth),
    _rate: dict[str, Any] = Depends(verifier_limite_debit_ia),
):
    service = _get_service()
    result = service.generer_journal_familial_auto()
    return result or JournalFamilialAutoResponse()


@router.get(
    "/phasee/journal-familial/pdf",
    response_model=RapportMensuelPdfResponse,
    responses=RESPONSES_IA_TYPED,
    summary="E8 Export PDF journal familial",
)
@gerer_exception_api
async def phasee_journal_familial_pdf(
    user: dict[str, Any] = Depends(require_auth),
):
    service = _get_service()
    result = service.generer_journal_familial_pdf()
    return result or RapportMensuelPdfResponse()


@router.get(
    "/phasee/rapport-mensuel/pdf",
    response_model=RapportMensuelPdfResponse,
    responses=RESPONSES_IA_TYPED,
    summary="E9 Rapport mensuel PDF",
)
@gerer_exception_api
async def phasee_rapport_mensuel_pdf(
    mois: str | None = Query(None, description="Format YYYY-MM"),
    user: dict[str, Any] = Depends(require_auth),
):
    service = _get_service()
    result = service.generer_rapport_mensuel_pdf(mois=mois)
    return result or RapportMensuelPdfResponse()


@router.get(
    "/phasee/mode-vacances",
    response_model=ModeVacancesResponse,
    responses=RESPONSES_IA_TYPED,
    summary="S21 IN10 Lecture mode vacances",
)
@gerer_exception_api
async def phasee_lire_mode_vacances(
    user: dict[str, Any] = Depends(require_auth),
):
    service = _get_service()
    user_id = str(user.get("id") or "")
    result = service.obtenir_mode_vacances(user_id=user_id)
    return result or ModeVacancesResponse()


@router.post(
    "/phasee/mode-vacances/config",
    response_model=ModeVacancesResponse,
    responses=RESPONSES_IA_TYPED,
    summary="S21 IN10 Configuration mode vacances",
)
@gerer_exception_api
async def phasee_configurer_mode_vacances(
    body: ModeVacancesConfigurationRequest,
    user: dict[str, Any] = Depends(require_auth),
):
    service = _get_service()
    user_id = str(user.get("id") or "")
    result = service.configurer_mode_vacances(
        user_id=user_id,
        actif=body.actif,
        checklist_voyage_auto=body.checklist_voyage_auto,
    )
    return result or ModeVacancesResponse(actif=body.actif, checklist_voyage_auto=body.checklist_voyage_auto)


@router.get(
    "/phasee/insights-quotidiens",
    response_model=InsightsQuotidiensResponse,
    responses=RESPONSES_IA_TYPED,
    summary="S21 IN11 Insights IA proactifs quotidiens",
)
@gerer_exception_api
async def phasee_insights_quotidiens(
    limite: int = Query(2, ge=1, le=2, description="1 ou 2 insights maximum par jour"),
    user: dict[str, Any] = Depends(require_auth),
):
    service = _get_service()
    result = service.generer_insights_quotidiens(limite=limite)
    return result or InsightsQuotidiensResponse(limite_journaliere=limite)


@router.get(
    "/phasee/meteo-contextuelle",
    response_model=MeteoContextuelleResponse,
    responses=RESPONSES_IA_TYPED,
    summary="S21 IN4 Meteo contextuelle cross-module",
)
@gerer_exception_api
async def phasee_meteo_contextuelle(
    user: dict[str, Any] = Depends(require_auth),
):
    service = _get_service()
    result = service.analyser_meteo_contextuelle()
    return result or MeteoContextuelleResponse()


@router.get(
    "/phasee/garmin-repas-adaptatif",
    response_model=SuggestionRepasSoirResponse,
    responses=RESPONSES_IA_TYPED,
    summary="E4.2 Repas adapte a la depense Garmin",
)
@gerer_exception_api
async def phasee_garmin_repas_adaptatif(
    user: dict[str, Any] = Depends(require_auth),
):
    service = _get_service()
    user_id_raw = user.get("id")
    user_id = int(user_id_raw) if isinstance(user_id_raw, (int, str)) and str(user_id_raw).isdigit() else None
    result = service.proposer_repas_adapte_garmin(user_id=user_id)
    return result or SuggestionRepasSoirResponse()


@router.get(
    "/phasee/s22/preferences-apprises",
    response_model=ApprentissagePreferencesResponse,
    responses=RESPONSES_IA_TYPED,
    summary="S22 IN1 Apprentissage des preferences",
)
@gerer_exception_api
async def phasee_s22_preferences_apprises(
    user: dict[str, Any] = Depends(require_auth),
):
    service = _get_service()
    user_id = str(user.get("id") or "")
    result = service.analyser_preferences_apprises(user_id=user_id)
    return result or ApprentissagePreferencesResponse()


@router.get(
    "/phasee/s22/planification-auto",
    response_model=PlanificationHebdoCompleteResponse,
    responses=RESPONSES_IA_TYPED,
    summary="S22 IN9 Planification hebdo complete automatique",
)
@gerer_exception_api
async def phasee_s22_planification_auto(
    user: dict[str, Any] = Depends(require_auth),
):
    service = _get_service()
    user_id = str(user.get("id") or "")
    result = service.generer_planification_hebdo_complete(user_id=user_id)
    return result or PlanificationHebdoCompleteResponse()


@router.get(
    "/phasee/s22/batch-cooking-intelligent",
    response_model=BatchCookingIntelligentResponse,
    responses=RESPONSES_IA_TYPED,
    summary="S22 IN13 Suggestions batch cooking intelligentes",
)
@gerer_exception_api
async def phasee_s22_batch_cooking_intelligent(
    user: dict[str, Any] = Depends(require_auth),
):
    service = _get_service()
    user_id = str(user.get("id") or "")
    result = service.proposer_batch_cooking_intelligent(user_id=user_id)
    return result or BatchCookingIntelligentResponse()


@router.post(
    "/phasee/s22/carte-visuelle",
    response_model=CarteVisuellePartageableResponse,
    responses=RESPONSES_IA_TYPED,
    summary="S22 IN17 Carte visuelle partageable",
)
@gerer_exception_api
async def phasee_s22_carte_visuelle(
    body: CarteVisuelleRequest,
    user: dict[str, Any] = Depends(require_auth),
):
    service = _get_service()
    result = service.generer_carte_visuelle_partageable(
        type_carte=body.type_carte,
        titre=body.titre,
    )
    return result or CarteVisuellePartageableResponse(type_carte=body.type_carte)


@router.get(
    "/phasee/s22/mode-tablette-magazine",
    response_model=ModeTabletteMagazineResponse,
    responses=RESPONSES_IA_TYPED,
    summary="S22 IN7 Mode tablette magazine",
)
@gerer_exception_api
async def phasee_s22_mode_tablette_magazine(
    user: dict[str, Any] = Depends(require_auth),
):
    service = _get_service()
    result = service.obtenir_mode_tablette_magazine()
    return result or ModeTabletteMagazineResponse()


@router.get(
    "/phase9/tableau-sante-foyer",
    response_model=ScoreBienEtreResponse,
    responses=RESPONSES_IA_TYPED,
    summary="P9-15 Tableau de bord sante foyer",
)
@gerer_exception_api
async def p9_tableau_sante_foyer(
    user: dict[str, Any] = Depends(require_auth),
):
    service = _get_service()
    result = service.calculer_score_bien_etre()
    return result or ScoreBienEtreResponse()


# ===========================================================
# 10.4 - BILAN ANNUEL AUTOMATIQUE IA
# ===========================================================


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
    """Genere un bilan annuel complet : cuisine, budget, maison, Jules, sport."""
    service = _get_service()
    result = service.generer_bilan_annuel(annee=body.annee)
    if result is None:
        return BilanAnnuelResponse()
    return result


# ===========================================================
# 10.5 - SCORE BIEN-ETRE FAMILIAL
# ===========================================================


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
    """Calcule le score bien-etre familial (sport + nutrition + budget + routines)."""
    service = _get_service()
    result = service.calculer_score_bien_etre()
    if result is None:
        return ScoreBienEtreResponse()
    return result


# ===========================================================
# 10.17 - ENRICHISSEMENT CONTACTS IA
# ===========================================================


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
    """Analyse et enrichit les contacts (categorisation, rappels relationnels)."""
    service = _get_service()
    result = service.enrichir_contacts()
    if result is None:
        return EnrichissementContactsResponse()
    return result


# ===========================================================
# 10.18 - ANALYSE TENDANCES LOTO
# ===========================================================


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
    """Analyse statistique des tirages avec numeros chauds/froids et combinaison suggeree."""
    service = _get_service()
    result = service.analyser_tendances_loto(jeu=jeu)
    if result is None:
        return AnalyseTendancesLotoResponse()
    return result


# ===========================================================
# 10.19 - OPTIMISATION PARCOURS MAGASIN
# ===========================================================


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
    """Regroupe les articles de courses par rayon et optimise l'ordre de parcours."""
    service = _get_service()
    result = service.optimiser_parcours_magasin(liste_id=body.liste_id)
    if result is None:
        return ParcoursOptimiseResponse()
    return result


# ===========================================================
# 10.8 - VEILLE EMPLOI
# ===========================================================


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
    """Execute la veille emploi avec criteres configurables."""
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


# ===========================================================
# 10.3 - MODE INVITE
# ===========================================================


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
    """Cree un lien partageable pour un invite (nounou, grands-parents).

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
    summary="Acces invite - sans authentification",
)
@gerer_exception_api
async def acceder_donnees_invite(token: str):
    """Acces aux donnees via lien invite (pas d'authentification requise)."""
    service = _get_service()
    result = service.obtenir_donnees_invite(token=token)
    if result is None:
        raise HTTPException(status_code=404, detail="Lien invite invalide ou expire.")
    return result




