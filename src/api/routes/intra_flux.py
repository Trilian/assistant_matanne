"""
Routes Phase B.6/B.7 — Améliorations intra-modules & flux utilisateur simplifiés.

Endpoints :
- GET /api/v1/intra/routines-streak → Streak tracking routines (B6.5)
- GET /api/v1/intra/energie-comparaison → Comparaison énergie N vs N-1 (B6.6)
- GET /api/v1/intra/suggestions-entretien-age → Suggestions entretien par âge (B6.7)
- GET /api/v1/flux/cuisine-3-clics → État du flux cuisine simplifié (B7.1)
- GET /api/v1/flux/digest-quotidien → Digest famille du jour (B7.2)
- POST /api/v1/flux/marquer-fait/{tache_id} → Marquer tâche + auto next date (B7.3)
- POST /api/v1/flux/feedback-semaine → Feedback fin de semaine (B7.5)
"""

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from src.api.dependencies import require_auth
from src.api.utils import executer_async, gerer_exception_api

router = APIRouter(tags=["Phase B — Intra-modules & Flux"])


# ── Schemas ──────────────────────────────────────────


class StreakRoutine(BaseModel):
    nom: str
    streak: int = 0
    meilleur_streak: int = 0
    taux_completion: float = 0.0


class ComparaisonEnergieMois(BaseModel):
    mois: int
    mois_nom: str
    annee_n: float
    annee_n1: float
    ecart_pct: float
    tendance: str


class ComparaisonEnergieResponse(BaseModel):
    type_energie: str
    annee_n: int
    annee_n1: int
    mois: list[ComparaisonEnergieMois]
    total_n: float
    total_n1: float
    ecart_total_pct: float


class SuggestionEntretien(BaseModel):
    equipement: str
    categorie: str | None = None
    age_annees: float
    seuil_revision: int
    suggestion: str
    priorite: str


class FluxCuisineResponse(BaseModel):
    etape_actuelle: str
    planning: dict | None = None
    courses: dict | None = None
    actions_suivantes: list[dict] = []


class DigestQuotidienResponse(BaseModel):
    date: str
    jour: str
    repas: list[dict] = []
    routines: list[dict] = []
    entretien: list[dict] = []
    nb_sections: int = 0


class FeedbackItem(BaseModel):
    recette_id: int
    note: int = Field(ge=1, le=5, default=3)
    commentaire: str = ""
    mange: bool = True


class FeedbackSemaineRequest(BaseModel):
    feedbacks: list[FeedbackItem]


class MarquerFaitResponse(BaseModel):
    tache_id: int
    nom: str = ""
    fait: bool = True
    prochaine_fois: str = ""
    frequence: str = ""


# ── Routes ──────────────────────────────────────────


@router.get("/api/v1/intra/routines-streak", response_model=dict[str, StreakRoutine])
@gerer_exception_api
async def get_routines_streak(user: dict = Depends(require_auth)):
    """B6.5: Streak tracking pour les routines actives."""
    from src.services.ia.intra_modules import calculer_streak_routines

    def _query():
        raw = calculer_streak_routines()
        return {str(k): v for k, v in raw.items()}
    return await executer_async(_query)


@router.get("/api/v1/intra/energie-comparaison", response_model=ComparaisonEnergieResponse)
@gerer_exception_api
async def get_energie_comparaison(
    type_energie: str = Query("electricite", description="Type d'énergie (electricite, gaz, eau)"),
    user: dict = Depends(require_auth),
):
    """B6.6: Comparaison consommation énergie N vs N-1."""
    from src.services.ia.intra_modules import comparaison_energie_n_vs_n1

    def _query():
        return comparaison_energie_n_vs_n1(type_energie=type_energie)
    return await executer_async(_query)


@router.get("/api/v1/intra/suggestions-entretien-age", response_model=list[SuggestionEntretien])
@gerer_exception_api
async def get_suggestions_entretien_age(user: dict = Depends(require_auth)):
    """B6.7: Suggestions entretien basées sur l'âge des équipements."""
    from src.services.ia.intra_modules import suggestions_entretien_par_age_equipement

    def _query():
        return suggestions_entretien_par_age_equipement()
    return await executer_async(_query)


@router.get("/api/v1/flux/cuisine-3-clics", response_model=FluxCuisineResponse)
@gerer_exception_api
async def get_flux_cuisine(
    planning_id: int | None = Query(None),
    user: dict = Depends(require_auth),
):
    """B7.1: État du flux cuisine simplifié (planning → courses → checkout)."""
    from src.services.ia.flux_utilisateur import flux_cuisine_3_clics

    def _query():
        return flux_cuisine_3_clics(planning_id=planning_id)
    return await executer_async(_query)


@router.get("/api/v1/flux/digest-quotidien", response_model=DigestQuotidienResponse)
@gerer_exception_api
async def get_digest_quotidien(user: dict = Depends(require_auth)):
    """B7.2: Digest famille du jour (repas, routines, entretien)."""
    from src.services.ia.flux_utilisateur import generer_digest_quotidien

    def _query():
        return generer_digest_quotidien()
    return await executer_async(_query)


@router.post("/api/v1/flux/marquer-fait/{tache_id}", response_model=MarquerFaitResponse)
@gerer_exception_api
async def post_marquer_fait(tache_id: int, user: dict = Depends(require_auth)):
    """B7.3: Marquer tâche entretien comme faite + calcul auto prochaine date."""
    from src.services.ia.flux_utilisateur import marquer_tache_fait_avec_prochaine

    def _query():
        return marquer_tache_fait_avec_prochaine(tache_id=tache_id)
    return await executer_async(_query)


@router.post("/api/v1/flux/feedback-semaine")
@gerer_exception_api
async def post_feedback_semaine(
    request: FeedbackSemaineRequest,
    user: dict = Depends(require_auth),
):
    """B7.5: Enregistrer les feedbacks de fin de semaine sur les repas."""
    from src.services.ia.flux_utilisateur import enregistrer_feedback_semaine

    def _query():
        return enregistrer_feedback_semaine(
            feedbacks=[fb.model_dump() for fb in request.feedbacks]
        )
    return await executer_async(_query)
