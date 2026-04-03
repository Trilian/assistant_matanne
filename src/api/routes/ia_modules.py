"""Routes API pour les services IA modulaires."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from src.api.dependencies import require_auth
from src.api.rate_limiting import verifier_limite_debit_ia
from src.api.schemas.errors import REPONSES_IA
from src.api.schemas.ia_modules import (
    AnalyseHabitudeRequest,
    AnalyseImpactsMeteoRequest,
    AnalyseNutritionPersonneRequest,
    AnalyseVarietePlanningRequest,
    BilanMensuelNarratifResponse,
    DiagnosticPlanteJardinRequest,
    DiagnosticPlanteJardinResponse,
    EstimationProjetMaisonRequest,
    PredictionConsommationRequest,
)
from src.api.utils import gerer_exception_api
from src.services.cuisine.nutrition_famille_ia import DonneesNutritionnelles
from src.services.integrations.habitudes_ia import AnalyseHabitude
from src.services.integrations.meteo_impact_ai import MeteoContexte
from src.services.inventaire.ia_service import PredictionConsommation
from src.services.maison.projets_ia_service import EstimationProjet
from src.services.planning.ia_service import AnalyseVariete

router = APIRouter(prefix="/api/v1/ia/modules", tags=["IA"])


def _get_inventaire_ai_service():
    from src.services.inventaire.ia_service import get_inventaire_ai_service

    return get_inventaire_ai_service()


def _get_planning_ai_service():
    from src.services.planning.ia_service import get_planning_ai_service

    return get_planning_ai_service()


def _get_meteo_impact_ai_service():
    from src.services.integrations.meteo_impact_ai import get_meteo_impact_ai_service

    return get_meteo_impact_ai_service()


def _get_habitudes_ai_service():
    from src.services.integrations.habitudes_ia import get_habitudes_ai_service

    return get_habitudes_ai_service()


def _get_projets_maison_ai_service():
    from src.services.maison.projets_ia_service import get_projets_maison_ai_service

    return get_projets_maison_ai_service()


def _get_nutrition_famille_ai_service():
    from src.services.cuisine.nutrition_famille_ia import get_nutrition_famille_ai_service

    return get_nutrition_famille_ai_service()


@router.post(
    "/inventaire/prediction-consommation",
    response_model=PredictionConsommation,
    responses=REPONSES_IA,
    summary="Prédire la consommation d'un article d'inventaire",
)
@gerer_exception_api
async def predire_consommation_inventaire(
    body: PredictionConsommationRequest,
    user: dict = Depends(require_auth),
    _rate: dict = Depends(verifier_limite_debit_ia),
) -> PredictionConsommation:
    service = _get_inventaire_ai_service()
    return service.predire_consommation(
        ingredient_nom=body.ingredient_nom,
        stock_actuel_kg=body.stock_actuel_kg,
        historique_achat_mensuel=body.historique_achat_mensuel,
    )


@router.post(
    "/planning/analyse-variete",
    response_model=AnalyseVariete,
    responses=REPONSES_IA,
    summary="Analyser la variété d'un planning de repas",
)
@gerer_exception_api
async def analyser_variete_planning(
    body: AnalyseVarietePlanningRequest,
    user: dict = Depends(require_auth),
    _rate: dict = Depends(verifier_limite_debit_ia),
) -> AnalyseVariete:
    service = _get_planning_ai_service()
    return service.analyser_variete_semaine(body.planning_repas)


@router.post(
    "/meteo/impacts",
    response_model=list[MeteoContexte],
    responses=REPONSES_IA,
    summary="Analyser les impacts météo cross-modules",
)
@gerer_exception_api
async def analyser_impacts_meteo(
    body: AnalyseImpactsMeteoRequest,
    user: dict = Depends(require_auth),
    _rate: dict = Depends(verifier_limite_debit_ia),
) -> list[MeteoContexte]:
    service = _get_meteo_impact_ai_service()
    return await service.analyser_impacts(
        previsions_7j=body.previsions_7j,
        saison=body.saison,
    )


@router.post(
    "/habitudes/analyse",
    response_model=AnalyseHabitude,
    responses=REPONSES_IA,
    summary="Analyser une routine familiale",
)
@gerer_exception_api
async def analyser_habitude(
    body: AnalyseHabitudeRequest,
    user: dict = Depends(require_auth),
    _rate: dict = Depends(verifier_limite_debit_ia),
) -> AnalyseHabitude:
    service = _get_habitudes_ai_service()
    return await service.analyser_habitude(
        habitude_nom=body.habitude_nom,
        historique_7j=body.historique_7j,
        description_contexte=body.description_contexte,
    )


@router.post(
    "/maison/projets/estimation",
    response_model=EstimationProjet,
    responses=REPONSES_IA,
    summary="Estimer un projet maison",
)
@gerer_exception_api
async def estimer_projet_maison(
    body: EstimationProjetMaisonRequest,
    user: dict = Depends(require_auth),
    _rate: dict = Depends(verifier_limite_debit_ia),
) -> EstimationProjet:
    service = _get_projets_maison_ai_service()
    return await service.estimer_projet(
        projet_description=body.projet_description,
        surface_m2=body.surface_m2,
        type_maison=body.type_maison,
        contraintes=body.contraintes,
    )


@router.post(
    "/nutrition/personne",
    response_model=DonneesNutritionnelles,
    responses=REPONSES_IA,
    summary="Analyser la nutrition d'une personne",
)
@gerer_exception_api
async def analyser_nutrition_personne(
    body: AnalyseNutritionPersonneRequest,
    user: dict = Depends(require_auth),
    _rate: dict = Depends(verifier_limite_debit_ia),
) -> DonneesNutritionnelles:
    service = _get_nutrition_famille_ai_service()
    return await service.analyser_nutrition_personne(
        personne_nom=body.personne_nom,
        age_ans=body.age_ans,
        sexe=body.sexe,
        activite_niveau=body.activite_niveau,
        donnees_garmin_semaine=body.donnees_garmin_semaine,
        recettes_semaine=body.recettes_semaine,
        objectif_sante=body.objectif_sante,
    )


@router.post(
    "/jardin/diagnostic-plante",
    response_model=DiagnosticPlanteJardinResponse,
    responses=REPONSES_IA,
    summary="Diagnostiquer une plante à partir d'une photo",
)
@gerer_exception_api
async def diagnostiquer_plante_jardin(
    body: DiagnosticPlanteJardinRequest,
    user: dict = Depends(require_auth),
    _rate: dict = Depends(verifier_limite_debit_ia),
) -> DiagnosticPlanteJardinResponse:
    from src.services.maison.jardin_service import obtenir_jardin_service

    service = obtenir_jardin_service()
    diagnostic = await service.diagnostiquer_plante(
        image_base64=body.image_base64,
        description=body.description,
    )
    return DiagnosticPlanteJardinResponse(
        plante_identifiee=diagnostic.plante_identifiee,
        etat=diagnostic.etat.value if hasattr(diagnostic.etat, "value") else str(diagnostic.etat),
        problemes_detectes=list(diagnostic.problemes_detectes or []),
        traitements_suggeres=list(diagnostic.traitements_suggeres or []),
        confiance=float(diagnostic.confiance or 0.0),
    )


@router.get(
    "/rapports/bilan-mensuel",
    response_model=BilanMensuelNarratifResponse,
    responses=REPONSES_IA,
    summary="Générer le bilan mensuel narratif multi-modules",
)
@gerer_exception_api
async def generer_bilan_mensuel_narratif(
    mois: str | None = None,
    user: dict = Depends(require_auth),
    _rate: dict = Depends(verifier_limite_debit_ia),
) -> BilanMensuelNarratifResponse:
    from src.services.rapports.bilan_mensuel import obtenir_bilan_mensuel_service

    service = obtenir_bilan_mensuel_service()
    bilan = await service.generer_bilan(mois=mois)
    return BilanMensuelNarratifResponse(**bilan)
