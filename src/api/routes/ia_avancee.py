"""
Routes API pour l'IA avancée — Phase 6 du planning.

14 endpoints IA proactifs et contextuels :
- POST /suggestions-achats : Suggestions achats basées historique
- POST /planning-adaptatif : Planning adapté (météo + budget)
- POST /diagnostic-plante : Diagnostic plante par photo
- GET  /prevision-depenses : Prévision dépenses fin de mois
- POST /idees-cadeaux : Idées cadeaux personnalisées
- POST /analyse-photo : Analyse photo multi-usage (contexte auto)
- GET  /optimisation-routines : Optimisation routines IA
- POST /analyse-document : Analyse document photo (OCR)
- POST /estimation-travaux : Estimation travaux par photo
- POST /planning-voyage : Planning voyage complet
- GET  /recommandations-energie : Économies énergie
- GET  /prediction-pannes : Prédiction pannes équipements
- GET  /suggestions-proactives : Suggestions proactives multi-modules
- POST /adaptations-meteo : Adaptations planning selon météo
"""

import logging

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile

from src.api.dependencies import require_auth
from src.api.rate_limiting import verifier_limite_debit_ia
from src.api.schemas.errors import REPONSES_IA
from src.api.schemas.ia_avancee import (
    AdaptationsMeteoRequest,
    AdaptationsMeteoResponse,
    AnalysePhotoMultiUsage,
    DiagnosticPlante,
    DocumentAnalyse,
    EstimationTravauxPhoto,
    EstimationTravauxRequest,
    IdeesCadeauxRequest,
    IdeesCadeauxResponse,
    OptimisationRoutinesResponse,
    PlanningAdaptatif,
    PlanningAdaptatifRequest,
    PlanningVoyage,
    PlanningVoyageRequest,
    PredictionsPannesResponse,
    PrevisionDepenses,
    RecommandationsEnergieResponse,
    SuggestionsAchatsResponse,
    SuggestionsProactivesResponse,
)
from src.api.utils import gerer_exception_api

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/ia-avancee", tags=["IA Avancée"])

MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10 Mo


def _get_service():
    """Lazy-load le service IA avancée."""
    from src.services.ia_avancee import get_ia_avancee_service

    return get_ia_avancee_service()


def _historiser_suggestion(
    user_id: str,
    type_suggestion: str,
    module: str,
    contenu: dict | None,
) -> None:
    """Persiste une suggestion IA dans l'historique (fire-and-forget)."""
    try:
        from src.core.db import obtenir_contexte_db
        from src.core.models import IASuggestionsHistorique

        with obtenir_contexte_db() as session:
            historique = IASuggestionsHistorique(
                user_id=user_id,
                type_suggestion=type_suggestion,
                module=module,
                contenu=contenu,
            )
            session.add(historique)
            session.commit()
    except Exception:
        logger.debug("Échec historisation suggestion %s (non bloquant)", type_suggestion)


async def _lire_image(file: UploadFile) -> bytes:
    """Lit et valide une image uploadée."""
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Le fichier doit être une image.")
    contenu = await file.read()
    if len(contenu) > MAX_IMAGE_SIZE:
        raise HTTPException(status_code=400, detail="Image trop volumineuse (max 10 Mo).")
    return contenu


# ═══════════════════════════════════════════════════════════
# 6.1 — SUGGESTIONS ACHATS IA
# ═══════════════════════════════════════════════════════════


@router.get(
    "/suggestions-achats",
    response_model=SuggestionsAchatsResponse,
    responses=REPONSES_IA,
    summary="Suggestions achats basées sur l'historique",
)
@gerer_exception_api
async def suggestions_achats(
    jours: int = Query(90, ge=7, le=365, description="Période d'analyse en jours"),
    user: dict = Depends(require_auth),
    _rate: dict = Depends(verifier_limite_debit_ia),
):
    """Suggère des achats à faire basés sur l'historique de consommation."""
    service = _get_service()
    result = service.suggerer_achats(jours=jours)
    if result is None:
        return SuggestionsAchatsResponse()
    _historiser_suggestion(user.get("sub", ""), "suggestions_achats", "cuisine", result.model_dump() if hasattr(result, "model_dump") else None)
    return result


# ═══════════════════════════════════════════════════════════
# 6.2 — PLANNING ADAPTATIF
# ═══════════════════════════════════════════════════════════


@router.post(
    "/planning-adaptatif",
    response_model=PlanningAdaptatif,
    responses=REPONSES_IA,
    summary="Planning adapté selon météo, énergie et budget",
)
@gerer_exception_api
async def planning_adaptatif(
    body: PlanningAdaptatifRequest,
    user: dict = Depends(require_auth),
    _rate: dict = Depends(verifier_limite_debit_ia),
):
    """Génère un planning adapté au contexte (météo + budget)."""
    service = _get_service()
    result = service.generer_planning_adaptatif(
        meteo=body.meteo,
        budget_restant=body.budget_restant,
    )
    if result is None:
        return PlanningAdaptatif()
    _historiser_suggestion(user.get("sub", ""), "planning_adaptatif", "planning", result.model_dump() if hasattr(result, "model_dump") else None)
    return result


# ═══════════════════════════════════════════════════════════
# 6.3 — DIAGNOSTIC PLANTE PHOTO
# ═══════════════════════════════════════════════════════════


@router.post(
    "/diagnostic-plante",
    response_model=DiagnosticPlante,
    responses=REPONSES_IA,
    summary="Diagnostic plante par photo (Pixtral)",
)
@gerer_exception_api
async def diagnostic_plante(
    file: UploadFile = File(..., description="Photo de la plante"),
    user: dict = Depends(require_auth),
    _rate: dict = Depends(verifier_limite_debit_ia),
):
    """Diagnostique l'état d'une plante via analyse photo Pixtral."""
    image_bytes = await _lire_image(file)
    service = _get_service()
    result = service.diagnostiquer_plante_photo(image_bytes)
    if result is None:
        raise HTTPException(status_code=503, detail="Diagnostic plante indisponible.")
    _historiser_suggestion(user.get("sub", ""), "diagnostic_plante", "maison", result.model_dump() if hasattr(result, "model_dump") else None)
    return result


# ═══════════════════════════════════════════════════════════
# 6.4 — PRÉVISION DÉPENSES
# ═══════════════════════════════════════════════════════════


@router.get(
    "/prevision-depenses",
    response_model=PrevisionDepenses,
    responses=REPONSES_IA,
    summary="Prévision dépenses fin de mois",
)
@gerer_exception_api
async def prevision_depenses(
    user: dict = Depends(require_auth),
    _rate: dict = Depends(verifier_limite_debit_ia),
):
    """Prévoit les dépenses jusqu'à la fin du mois."""
    service = _get_service()
    result = service.prevoir_depenses_fin_mois()
    if result is None:
        return PrevisionDepenses()
    _historiser_suggestion(user.get("sub", ""), "prevision_depenses", "finances", result.model_dump() if hasattr(result, "model_dump") else None)
    return result


# ═══════════════════════════════════════════════════════════
# 6.5 — IDÉES CADEAUX IA
# ═══════════════════════════════════════════════════════════


@router.post(
    "/idees-cadeaux",
    response_model=IdeesCadeauxResponse,
    responses=REPONSES_IA,
    summary="Idées cadeaux personnalisées",
)
@gerer_exception_api
async def idees_cadeaux(
    body: IdeesCadeauxRequest,
    user: dict = Depends(require_auth),
    _rate: dict = Depends(verifier_limite_debit_ia),
):
    """Suggère des idées cadeaux personnalisées pour un anniversaire."""
    service = _get_service()
    result = service.suggerer_cadeaux(
        nom=body.nom,
        age=body.age,
        relation=body.relation,
        budget_max=body.budget_max,
        occasion=body.occasion,
    )
    if result is None:
        return IdeesCadeauxResponse()
    _historiser_suggestion(user.get("sub", ""), "idees_cadeaux", "famille", result.model_dump() if hasattr(result, "model_dump") else None)
    return result


# ═══════════════════════════════════════════════════════════
# 6.6 — ANALYSE PHOTO MULTI-USAGE
# ═══════════════════════════════════════════════════════════


@router.post(
    "/analyse-photo",
    response_model=AnalysePhotoMultiUsage,
    responses=REPONSES_IA,
    summary="Analyse photo multi-usage (contexte auto-détecté)",
)
@gerer_exception_api
async def analyse_photo_multi(
    file: UploadFile = File(..., description="Photo à analyser"),
    user: dict = Depends(require_auth),
    _rate: dict = Depends(verifier_limite_debit_ia),
):
    """Analyse une photo en détectant automatiquement le contexte.

    Un seul bouton — l'IA détecte si c'est une recette, plante,
    maison, document, plat, etc.
    """
    image_bytes = await _lire_image(file)
    service = _get_service()
    result = service.analyser_photo_multi_usage(image_bytes)
    if result is None:
        raise HTTPException(status_code=503, detail="Analyse photo indisponible.")
    _historiser_suggestion(user.get("sub", ""), "analyse_photo", "multi", result.model_dump() if hasattr(result, "model_dump") else None)
    return result


# ═══════════════════════════════════════════════════════════
# 6.7 — OPTIMISATION ROUTINES IA
# ═══════════════════════════════════════════════════════════


@router.get(
    "/optimisation-routines",
    response_model=OptimisationRoutinesResponse,
    responses=REPONSES_IA,
    summary="Optimisation routines familiales",
)
@gerer_exception_api
async def optimisation_routines(
    user: dict = Depends(require_auth),
    _rate: dict = Depends(verifier_limite_debit_ia),
):
    """Analyse les routines et suggère des optimisations."""
    service = _get_service()
    result = service.optimiser_routines()
    if result is None:
        return OptimisationRoutinesResponse()
    _historiser_suggestion(user.get("sub", ""), "optimisation_routines", "famille", result.model_dump() if hasattr(result, "model_dump") else None)
    return result


# ═══════════════════════════════════════════════════════════
# 6.8 — ANALYSE DOCUMENT OCR
# ═══════════════════════════════════════════════════════════


@router.post(
    "/analyse-document",
    response_model=DocumentAnalyse,
    responses=REPONSES_IA,
    summary="Analyse document photo (OCR + classement auto)",
)
@gerer_exception_api
async def analyse_document(
    file: UploadFile = File(..., description="Photo du document"),
    user: dict = Depends(require_auth),
    _rate: dict = Depends(verifier_limite_debit_ia),
):
    """Analyse un document photographié via OCR et le classifie."""
    image_bytes = await _lire_image(file)
    service = _get_service()
    result = service.analyser_document_photo(image_bytes)
    if result is None:
        raise HTTPException(status_code=503, detail="Analyse document indisponible.")
    _historiser_suggestion(user.get("sub", ""), "analyse_document", "outils", result.model_dump() if hasattr(result, "model_dump") else None)
    return result


# ═══════════════════════════════════════════════════════════
# 6.9 — ESTIMATION TRAVAUX PHOTO
# ═══════════════════════════════════════════════════════════


@router.post(
    "/estimation-travaux",
    response_model=EstimationTravauxPhoto,
    responses=REPONSES_IA,
    summary="Estimation travaux par photo",
)
@gerer_exception_api
async def estimation_travaux(
    file: UploadFile = File(..., description="Photo des travaux"),
    description: str = Query("", max_length=200, description="Description additionnelle"),
    user: dict = Depends(require_auth),
    _rate: dict = Depends(verifier_limite_debit_ia),
):
    """Estime des travaux à partir d'une photo avec budget et planning."""
    image_bytes = await _lire_image(file)
    service = _get_service()
    result = service.estimer_travaux_photo(image_bytes, description=description)
    if result is None:
        raise HTTPException(status_code=503, detail="Estimation travaux indisponible.")
    _historiser_suggestion(user.get("sub", ""), "estimation_travaux", "maison", result.model_dump() if hasattr(result, "model_dump") else None)
    return result


# ═══════════════════════════════════════════════════════════
# 6.10 — PLANNING VOYAGE IA
# ═══════════════════════════════════════════════════════════


@router.post(
    "/planning-voyage",
    response_model=PlanningVoyage,
    responses=REPONSES_IA,
    summary="Planning voyage complet",
)
@gerer_exception_api
async def planning_voyage(
    body: PlanningVoyageRequest,
    user: dict = Depends(require_auth),
    _rate: dict = Depends(verifier_limite_debit_ia),
):
    """Génère un planning de voyage complet avec itinéraire et budget."""
    service = _get_service()
    result = service.generer_planning_voyage(
        destination=body.destination,
        duree_jours=body.duree_jours,
        budget_total=body.budget_total,
        avec_enfant=body.avec_enfant,
    )
    if result is None:
        raise HTTPException(status_code=503, detail="Génération planning voyage indisponible.")
    _historiser_suggestion(user.get("sub", ""), "planning_voyage", "famille", result.model_dump() if hasattr(result, "model_dump") else None)
    return result


# ═══════════════════════════════════════════════════════════
# 6.11 — RECOMMANDATIONS ÉNERGIE
# ═══════════════════════════════════════════════════════════


@router.get(
    "/recommandations-energie",
    response_model=RecommandationsEnergieResponse,
    responses=REPONSES_IA,
    summary="Recommandations économies énergie",
)
@gerer_exception_api
async def recommandations_energie(
    user: dict = Depends(require_auth),
    _rate: dict = Depends(verifier_limite_debit_ia),
):
    """Recommande des économies d'énergie basées sur la consommation."""
    service = _get_service()
    result = service.recommander_economies_energie()
    if result is None:
        return RecommandationsEnergieResponse()
    _historiser_suggestion(user.get("sub", ""), "recommandations_energie", "maison", result.model_dump() if hasattr(result, "model_dump") else None)
    return result


# ═══════════════════════════════════════════════════════════
# 6.12 — PRÉDICTION PANNES
# ═══════════════════════════════════════════════════════════


@router.get(
    "/prediction-pannes",
    response_model=PredictionsPannesResponse,
    responses=REPONSES_IA,
    summary="Prédiction pannes équipements",
)
@gerer_exception_api
async def prediction_pannes(
    user: dict = Depends(require_auth),
    _rate: dict = Depends(verifier_limite_debit_ia),
):
    """Prédit les risques de panne des équipements."""
    service = _get_service()
    result = service.predire_pannes()
    if result is None:
        return PredictionsPannesResponse()
    _historiser_suggestion(user.get("sub", ""), "prediction_pannes", "maison", result.model_dump() if hasattr(result, "model_dump") else None)
    return result


# ═══════════════════════════════════════════════════════════
# 6.13 — SUGGESTIONS PROACTIVES
# ═══════════════════════════════════════════════════════════


@router.get(
    "/suggestions-proactives",
    response_model=SuggestionsProactivesResponse,
    responses=REPONSES_IA,
    summary="Suggestions proactives multi-modules",
)
@gerer_exception_api
async def suggestions_proactives(
    user: dict = Depends(require_auth),
    _rate: dict = Depends(verifier_limite_debit_ia),
):
    """L'app propose sans qu'on demande, basé sur l'état général."""
    service = _get_service()
    result = service.generer_suggestions_proactives()
    if result is None:
        return SuggestionsProactivesResponse()
    _historiser_suggestion(user.get("sub", ""), "suggestions_proactives", "multi", result.model_dump() if hasattr(result, "model_dump") else None)
    return result


# ═══════════════════════════════════════════════════════════
# 6.14 — ADAPTATIONS MÉTÉO
# ═══════════════════════════════════════════════════════════


@router.post(
    "/adaptations-meteo",
    response_model=AdaptationsMeteoResponse,
    responses=REPONSES_IA,
    summary="Adaptations planning selon météo",
)
@gerer_exception_api
async def adaptations_meteo(
    body: AdaptationsMeteoRequest,
    user: dict = Depends(require_auth),
    _rate: dict = Depends(verifier_limite_debit_ia),
):
    """Adapte le planning familial en fonction des prévisions météo."""
    service = _get_service()
    result = service.adapter_planning_meteo(body.previsions_meteo)
    if result is None:
        return AdaptationsMeteoResponse()
    _historiser_suggestion(user.get("sub", ""), "adaptations_meteo", "planning", result.model_dump() if hasattr(result, "model_dump") else None)
    return result
