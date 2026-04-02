"""
Routes API — Services IA Bridges.

Prévision budget, résumé hebdo, diagnostic maison, planificateur adaptatif,
batch cooking intelligent, conseils Jules, checklist voyage, scores écologiques,
analyse nutritionnelle, optimisation énergie.
"""

import logging

from fastapi import APIRouter, Depends, Query

from src.api.dependencies import require_auth
from src.api.rate_limiting import verifier_limite_debit_ia
from src.api.schemas.errors import REPONSES_IA, REPONSES_LISTE
from src.api.schemas.ia_bridges import (
    AnalyseNutritionnelleRequest,
    AnalyseNutritionnelleResponse,
    BatchCookingPlanRequest,
    BatchCookingPlanResponse,
    CategorieDepenseResponse,
    CategoriserDepenseRequest,
    ChecklistVoyageRequest,
    ChecklistVoyageResponse,
    ConseilJulesRequest,
    ConseilJulesResponse,
    DiagnosticPhotoRequest,
    DiagnosticResponse,
    DiagnosticTexteRequest,
    OptimisationEnergieRequest,
    OptimisationEnergieResponse,
    PlanningAdapteResponse,
    PrevisionBudgetResponse,
    ResumeHebdoResponse,
    ScoreEcologiqueRequest,
    ScoreEcologiqueResponse,
)
from src.api.utils import gerer_exception_api

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/ia", tags=["IA Avancée Phase B"])


# ═══════════════════════════════════════════════════════════
# PRÉVISION BUDGET (B1.3)
# ═══════════════════════════════════════════════════════════


@router.get("/budget/prevision", response_model=PrevisionBudgetResponse, responses=REPONSES_LISTE)
@gerer_exception_api
async def prevision_budget(
    mois: int | None = Query(None, ge=1, le=12),
    annee: int | None = Query(None, ge=2020, le=2030),
    user: dict = Depends(require_auth),
):
    """Prévision des dépenses en fin de mois avec analyse de tendances."""
    from src.services.ia.prevision_budget import obtenir_service_prevision_budget

    service = obtenir_service_prevision_budget()
    return service.prevision_fin_de_mois(mois=mois, annee=annee)


@router.get("/budget/anomalies", responses=REPONSES_LISTE)
@gerer_exception_api
async def anomalies_budget(
    seuil: float = Query(80, ge=0, le=200, description="Seuil en % pour alertes"),
    user: dict = Depends(require_auth),
):
    """Détecte les catégories budgétaires dépassant un seuil."""
    from src.services.ia.prevision_budget import obtenir_service_prevision_budget

    service = obtenir_service_prevision_budget()
    return service.detecter_anomalies_budget(seuil_pct=seuil)


@router.post("/budget/categoriser", response_model=CategorieDepenseResponse, responses=REPONSES_IA)
@gerer_exception_api
async def categoriser_depense(
    request: CategoriserDepenseRequest,
    user: dict = Depends(require_auth),
    _rate_check: dict = Depends(verifier_limite_debit_ia),
):
    """Catégorise automatiquement une dépense à partir de sa description."""
    from src.services.ia.prevision_budget import obtenir_service_prevision_budget

    service = obtenir_service_prevision_budget()
    return service.auto_categoriser_depense(request.description)


# ═══════════════════════════════════════════════════════════
# RÉSUMÉ HEBDOMADAIRE (B4.3)
# ═══════════════════════════════════════════════════════════


@router.get("/resume-hebdo", response_model=ResumeHebdoResponse, responses=REPONSES_IA)
@gerer_exception_api
async def resume_hebdomadaire(
    user: dict = Depends(require_auth),
    _rate_check: dict = Depends(verifier_limite_debit_ia),
):
    """Génère un résumé narratif intelligent de la semaine."""
    from src.services.ia.resume_hebdo import obtenir_service_resume_hebdo

    service = obtenir_service_resume_hebdo()
    return service.generer_resume()


# ═══════════════════════════════════════════════════════════
# PLANIFICATEUR ADAPTATIF (B4.2)
# ═══════════════════════════════════════════════════════════


@router.get("/planning-adapte", response_model=PlanningAdapteResponse, responses=REPONSES_IA)
@gerer_exception_api
async def planning_adapte(
    nb_jours: int = Query(7, ge=1, le=14),
    user: dict = Depends(require_auth),
    _rate_check: dict = Depends(verifier_limite_debit_ia),
):
    """Génère un planning de repas adapté au contexte (stocks, saison, météo)."""
    from src.services.ia.planificateur_adaptatif import obtenir_service_planificateur_adaptatif

    service = obtenir_service_planificateur_adaptatif()
    return service.suggerer_planning_adapte(nb_jours=nb_jours)


# ═══════════════════════════════════════════════════════════
# DIAGNOSTIC MAISON (B4.5)
# ═══════════════════════════════════════════════════════════


@router.post("/diagnostic/photo", response_model=DiagnosticResponse, responses=REPONSES_IA)
@gerer_exception_api
async def diagnostic_photo(
    request: DiagnosticPhotoRequest,
    user: dict = Depends(require_auth),
    _rate_check: dict = Depends(verifier_limite_debit_ia),
):
    """Diagnostique un problème maison à partir d'une photo."""
    from src.services.ia.diagnostic_maison import obtenir_service_diagnostic_maison

    service = obtenir_service_diagnostic_maison()
    return service.diagnostiquer_photo(
        image_base64=request.image_base64,
        description=request.description,
    )


@router.post("/diagnostic/texte", response_model=DiagnosticResponse, responses=REPONSES_IA)
@gerer_exception_api
async def diagnostic_texte(
    request: DiagnosticTexteRequest,
    user: dict = Depends(require_auth),
    _rate_check: dict = Depends(verifier_limite_debit_ia),
):
    """Diagnostique un problème maison à partir d'une description texte."""
    from src.services.ia.diagnostic_maison import obtenir_service_diagnostic_maison

    service = obtenir_service_diagnostic_maison()
    return service.diagnostiquer_texte(request.description)


# ═══════════════════════════════════════════════════════════
# BATCH COOKING INTELLIGENT (B4.4)
# ═══════════════════════════════════════════════════════════


@router.post("/batch-cooking-plan", response_model=BatchCookingPlanResponse, responses=REPONSES_IA)
@gerer_exception_api
async def batch_cooking_plan(
    request: BatchCookingPlanRequest,
    user: dict = Depends(require_auth),
    _rate_check: dict = Depends(verifier_limite_debit_ia),
):
    """Génère un plan de batch cooking optimisé avec timeline par appareil."""
    from src.services.ia.suggestions_ia import obtenir_service_suggestions_ia

    service = obtenir_service_suggestions_ia()
    return service.batch_cooking_intelligent(
        recettes=request.recettes,
        nb_personnes=request.nb_personnes,
    )


# ═══════════════════════════════════════════════════════════
# CONSEIL DÉVELOPPEMENT JULES (B4.8)
# ═══════════════════════════════════════════════════════════


@router.post("/conseil-jules", response_model=ConseilJulesResponse, responses=REPONSES_IA)
@gerer_exception_api
async def conseil_jules(
    request: ConseilJulesRequest,
    user: dict = Depends(require_auth),
    _rate_check: dict = Depends(verifier_limite_debit_ia),
):
    """Conseils de développement proactifs pour Jules basés sur l'âge."""
    from src.services.ia.suggestions_ia import obtenir_service_suggestions_ia

    service = obtenir_service_suggestions_ia()
    return service.conseil_developpement_jules(
        age_mois=request.age_mois,
        jalons_atteints=request.jalons_atteints,
    )


# ═══════════════════════════════════════════════════════════
# CHECKLIST VOYAGE (B4.10)
# ═══════════════════════════════════════════════════════════


@router.post("/checklist-voyage", response_model=ChecklistVoyageResponse, responses=REPONSES_IA)
@gerer_exception_api
async def checklist_voyage(
    request: ChecklistVoyageRequest,
    user: dict = Depends(require_auth),
    _rate_check: dict = Depends(verifier_limite_debit_ia),
):
    """Génère une checklist de voyage personnalisée."""
    from src.services.ia.suggestions_ia import obtenir_service_suggestions_ia

    service = obtenir_service_suggestions_ia()
    return service.generer_checklist_voyage(
        destination=request.destination,
        dates=request.dates,
        participants=request.participants,
    )


# ═══════════════════════════════════════════════════════════
# SCORE ÉCOLOGIQUE (B4.11)
# ═══════════════════════════════════════════════════════════


@router.post("/score-ecologique", response_model=ScoreEcologiqueResponse, responses=REPONSES_IA)
@gerer_exception_api
async def score_ecologique(
    request: ScoreEcologiqueRequest,
    user: dict = Depends(require_auth),
    _rate_check: dict = Depends(verifier_limite_debit_ia),
):
    """Évalue le score écologique d'un repas."""
    from src.services.ia.suggestions_ia import obtenir_service_suggestions_ia

    service = obtenir_service_suggestions_ia()
    return service.score_ecologique_repas(
        ingredients=request.ingredients,
        saison=request.saison,
    )


# ═══════════════════════════════════════════════════════════
# ANALYSE NUTRITIONNELLE (B4.7)
# ═══════════════════════════════════════════════════════════


@router.post("/analyse-nutritionnelle", response_model=AnalyseNutritionnelleResponse, responses=REPONSES_IA)
@gerer_exception_api
async def analyse_nutritionnelle(
    request: AnalyseNutritionnelleRequest,
    user: dict = Depends(require_auth),
    _rate_check: dict = Depends(verifier_limite_debit_ia),
):
    """Analyse nutritionnelle d'un repas décrit en texte."""
    from src.services.ia.suggestions_ia import obtenir_service_suggestions_ia

    service = obtenir_service_suggestions_ia()
    return service.analyse_nutritionnelle(request.description_repas)


# ═══════════════════════════════════════════════════════════
# OPTIMISATION ÉNERGIE (B4.6)
# ═══════════════════════════════════════════════════════════


@router.post("/optimisation-energie", response_model=OptimisationEnergieResponse, responses=REPONSES_IA)
@gerer_exception_api
async def optimisation_energie(
    request: OptimisationEnergieRequest,
    user: dict = Depends(require_auth),
    _rate_check: dict = Depends(verifier_limite_debit_ia),
):
    """Analyse les relevés énergie et prédit la prochaine facture."""
    from src.services.ia.suggestions_ia import obtenir_service_suggestions_ia

    service = obtenir_service_suggestions_ia()
    return service.optimisation_energie(
        releves=request.releves,
        meteo=request.meteo,
    )
