"""Routes d'innovations historiques consolidées dans un routeur unique.

Le point d'entrée `/api/v1/innovations` est conservé pour la rétrocompatibilité,
mais les implémentations métier vivent désormais dans les routeurs de domaine
et le service `src.services.ia_avancee`.
"""

from __future__ import annotations

from typing import Any, cast

from fastapi import APIRouter, Depends, HTTPException, Query

from src.api.dependencies import require_auth
from src.api.rate_limiting import verifier_limite_debit_ia
from src.api.schemas.errors import REPONSES_IA
from src.api.schemas.ia_transverses import (
    AlertesContextuellesResponse,
    AnalyseTendancesLotoResponse,
    AnomaliesEnergieResponse,
    ApprentissageHabitudesResponse,
    ApprentissagePreferencesResponse,
    BatchCookingIntelligentResponse,
    BilanAnnuelRequest,
    BilanAnnuelResponse,
    CarteVisuellePartageableResponse,
    CarteVisuelleRequest,
    CoachRoutinesResponse,
    ComparateurEnergieRequest,
    ComparateurEnergieResponse,
    ComparateurPrixAutomatiqueResponse,
    DonneesInviteResponse,
    EnergieTempsReelResponse,
    EnrichissementContactsResponse,
    InsightsQuotidiensResponse,
    JournalFamilialAutoResponse,
    LienInviteRequest,
    LienInviteResponse,
    MangeCeSoirRequest,
    MeteoContextuelleResponse,
    ModePiloteAutomatiqueResponse,
    ModePiloteConfigurationRequest,
    ModeTabletteMagazineResponse,
    ModeVacancesConfigurationRequest,
    ModeVacancesResponse,
    ParcoursOptimiseRequest,
    ParcoursOptimiseResponse,
    PatternsAlimentairesResponse,
    PlanificationHebdoCompleteResponse,
    PlanningJulesAdaptatifResponse,
    RapportMensuelPdfResponse,
    ResumeMensuelIAResponse,
    SaisonnaliteIntelligenteResponse,
    ScoreBienEtreResponse,
    ScoreEcoResponsableResponse,
    ScoreFamilleHebdoResponse,
    SuggestionRepasSoirResponse,
    TelegramConversationnelResponse,
    VeilleEmploiRequest,
    VeilleEmploiResponse,
)
from src.api.utils import gerer_exception_api

RESPONSES_IA_TYPED = cast(dict[int | str, dict[str, Any]], REPONSES_IA)

router = APIRouter(prefix="/api/v1/innovations", tags=["Innovations"])


def get_innovations_service():
    """Charge paresseusement le service d'innovations via le namespace stable `ia_avancee`."""
    from src.services.ia_avancee import get_innovations_service as _get_innovations_service

    return _get_innovations_service()


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
    from src.services.ia_avancee.types_transverses import CriteresVeilleEmploi

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


@router.get(
    "/apprentissage-habitudes",
    response_model=ApprentissageHabitudesResponse,
    responses=RESPONSES_IA_TYPED,
    summary="Apprentissage continu habitudes",
)
@gerer_exception_api
async def apprentissage_habitudes(
    user: dict[str, Any] = Depends(require_auth),
):
    service = get_innovations_service()
    result = service.apprendre_habitudes_utilisateur()
    return result or ApprentissageHabitudesResponse()


@router.get(
    "/alertes-contextuelles",
    response_model=AlertesContextuellesResponse,
    responses=RESPONSES_IA_TYPED,
    summary="Alertes intelligentes contextuelles",
)
@gerer_exception_api
async def alertes_contextuelles(
    user: dict[str, Any] = Depends(require_auth),
):
    service = get_innovations_service()
    result = service.generer_alertes_contextuelles()
    return result or AlertesContextuellesResponse()


@router.get(
    "/mode-pilote",
    response_model=ModePiloteAutomatiqueResponse,
    responses=RESPONSES_IA_TYPED,
    summary="Mode pilote automatique",
)
@gerer_exception_api
async def mode_pilote(
    user: dict[str, Any] = Depends(require_auth),
):
    service = get_innovations_service()
    user_id_raw = user.get("id")
    user_id = int(user_id_raw) if isinstance(user_id_raw, (int, str)) and str(user_id_raw).isdigit() else None
    result = service.obtenir_mode_pilote_automatique(user_id=user_id)
    return result or ModePiloteAutomatiqueResponse()


@router.post(
    "/mode-pilote/config",
    response_model=ModePiloteAutomatiqueResponse,
    responses=RESPONSES_IA_TYPED,
    summary="Config mode pilote automatique",
)
@gerer_exception_api
async def configurer_mode_pilote(
    body: ModePiloteConfigurationRequest,
    user: dict[str, Any] = Depends(require_auth),
):
    service = get_innovations_service()
    user_id_raw = user.get("id")
    user_id = int(user_id_raw) if isinstance(user_id_raw, (int, str)) and str(user_id_raw).isdigit() else None
    result = service.configurer_mode_pilote_automatique(
        user_id=user_id,
        actif=body.actif,
        niveau_autonomie=body.niveau_autonomie,
    )
    return result or ModePiloteAutomatiqueResponse(actif=body.actif)


@router.get(
    "/insights-quotidiens",
    response_model=InsightsQuotidiensResponse,
    responses=RESPONSES_IA_TYPED,
    summary="Insights IA proactifs quotidiens",
)
@gerer_exception_api
async def insights_quotidiens(
    limite: int = Query(2, ge=1, le=2, description="1 ou 2 insights maximum par jour"),
    user: dict[str, Any] = Depends(require_auth),
):
    service = get_innovations_service()
    result = service.generer_insights_quotidiens(limite=limite)
    return result or InsightsQuotidiensResponse(limite_journaliere=limite)


@router.get(
    "/meteo-contextuelle",
    response_model=MeteoContextuelleResponse,
    responses=RESPONSES_IA_TYPED,
    summary="Meteo contextuelle cross-module",
)
@gerer_exception_api
async def meteo_contextuelle(
    user: dict[str, Any] = Depends(require_auth),
):
    service = get_innovations_service()
    result = service.analyser_meteo_contextuelle()
    return result or MeteoContextuelleResponse()


@router.get(
    "/preferences-apprises",
    response_model=ApprentissagePreferencesResponse,
    responses=RESPONSES_IA_TYPED,
    summary="Apprentissage des preferences",
)
@gerer_exception_api
async def preferences_apprises(
    user: dict[str, Any] = Depends(require_auth),
):
    service = get_innovations_service()
    user_id = str(user.get("id") or "")
    result = service.analyser_preferences_apprises(user_id=user_id)
    return result or ApprentissagePreferencesResponse()


@router.get(
    "/telegram-conversationnel",
    response_model=TelegramConversationnelResponse,
    responses=RESPONSES_IA_TYPED,
    summary="Telegram conversationnel",
)
@gerer_exception_api
async def telegram_conversationnel(
    user: dict[str, Any] = Depends(require_auth),
):
    service = get_innovations_service()
    result = service.obtenir_capacites_telegram_conversationnelles()
    return result or TelegramConversationnelResponse()
