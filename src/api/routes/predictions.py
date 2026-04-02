"""
Routes API — Prédiction courses IA (B4.1 / B5.4).

Prédiction intelligente des courses basée sur l'historique d'achats.
"""

import logging

from fastapi import APIRouter, Depends, Query

from src.api.dependencies import require_auth
from src.api.rate_limiting import verifier_limite_debit_ia
from src.api.schemas.errors import REPONSES_IA, REPONSES_LISTE
from src.api.schemas.ia_bridges import (
    EnregistrerAchatRequest,
    HabitudesAchatResponse,
    PredictionCoursesResponse,
)
from src.api.utils import gerer_exception_api

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/predictions/courses", tags=["Prédictions Courses"])


@router.get("", response_model=PredictionCoursesResponse, responses=REPONSES_LISTE)
@gerer_exception_api
async def predire_courses(
    limite: int = Query(30, ge=1, le=100, description="Nombre max d'articles prédits"),
    user: dict = Depends(require_auth),
):
    """Prédit la prochaine liste de courses basée sur l'historique d'achats.

    Analyse les fréquences d'achat pour pré-remplir automatiquement
    la liste avec les articles habituels.
    """
    from src.services.ia.prediction_courses import obtenir_service_prediction_courses

    service = obtenir_service_prediction_courses()
    predictions = service.predire_prochaine_liste(limite=limite)

    return {
        "predictions": predictions,
        "nb_total": len(predictions),
    }


@router.get("/habitudes", response_model=HabitudesAchatResponse, responses=REPONSES_LISTE)
@gerer_exception_api
async def habitudes_achat(user: dict = Depends(require_auth)):
    """Analyse les habitudes d'achat (fréquences, catégories)."""
    from src.services.ia.prediction_courses import obtenir_service_prediction_courses

    service = obtenir_service_prediction_courses()
    return service.analyser_habitudes()


@router.post("/enregistrer-achat", responses=REPONSES_LISTE)
@gerer_exception_api
async def enregistrer_achat(
    request: EnregistrerAchatRequest,
    user: dict = Depends(require_auth),
):
    """Enregistre un achat et met à jour l'historique de fréquence."""
    from src.services.ia.prediction_courses import obtenir_service_prediction_courses

    service = obtenir_service_prediction_courses()
    return service.enregistrer_achat(
        article_nom=request.article_nom,
        categorie=request.categorie,
        rayon=request.rayon,
    )
