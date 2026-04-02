"""
Routes API Famille — Activités familiales et suggestions IA.

Sous-routeur inclus dans famille.py.
"""

from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from src.api.dependencies import require_auth
from src.api.schemas.common import MessageResponse, ReponsePaginee
from src.api.schemas.errors import (
    REPONSES_CRUD_CREATION,
    REPONSES_CRUD_ECRITURE,
    REPONSES_CRUD_LECTURE,
    REPONSES_CRUD_SUPPRESSION,
    REPONSES_LISTE,
)
from src.api.schemas.famille import SuggestionsSoireeRequest, SuggestionsWeekendRequest
from src.api.utils import executer_async, executer_avec_session, gerer_exception_api

import logging
logger = logging.getLogger(__name__)

router = APIRouter(tags=["Famille"])


# ═══════════════════════════════════════════════════════════
# SCHEMAS PYDANTIC LOCAUX
# ═══════════════════════════════════════════════════════════


class ParamsSuggestionsActivites(BaseModel):
    """Paramètres pour suggestions d'activités IA"""

    age_mois: int = Field(..., ge=0, le=72, description="Âge de l'enfant en mois (0-72 mois)")
    meteo: str = Field(
        default="mixte",
        description="Type de météo: pluie, soleil, nuageux, mixte, interieur, exterieur",
    )
    budget_max: float = Field(default=50.0, ge=0, le=500, description="Budget maximum par activité")
    duree_min: int = Field(default=30, ge=5, le=300, description="Durée minimum en minutes")
    duree_max: int = Field(default=120, ge=10, le=360, description="Durée maximum en minutes")
    preferences: list[str] | None = Field(
        default=None, description="Tags de préférences (creatif, sportif, educatif, sensoriel, etc.)"
    )
    nb_suggestions: int = Field(
        default=5, ge=1, le=10, description="Nombre de suggestions souhaitées"
    )

# ═══════════════════════════════════════════════════════════


@router.get("/activites", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_activites(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    type_activite: str | None = Query(None, description="Filtrer par type"),
    statut: str | None = Query(None, description="Filtrer par statut"),
    date_debut: date | None = Query(None, description="Date minimum"),
    date_fin: date | None = Query(None, description="Date maximum"),
    cursor: str | None = Query(None, description="Curseur pour pagination cursor-based"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """
    Liste les activités familiales avec pagination offset ou cursor.

    Supporte deux modes de pagination:
    - Offset: Utiliser page/page_size (défaut)
    - Cursor: Utiliser cursor pour grandes collections
    """
    from src.core.models import ActiviteFamille

    def _query():
        with executer_avec_session() as session:
            query = session.query(ActiviteFamille)

            if type_activite:
                query = query.filter(ActiviteFamille.type_activite == type_activite)
            if statut:
                query = query.filter(ActiviteFamille.statut == statut)
            if date_debut:
                query = query.filter(ActiviteFamille.date_prevue >= date_debut)
            if date_fin:
                query = query.filter(ActiviteFamille.date_prevue <= date_fin)

            query = query.order_by(ActiviteFamille.date_prevue.desc(), ActiviteFamille.id.desc())

            # Pagination cursor-based si cursor fourni
            if cursor:
                cursor_params = decoder_cursor(cursor)
                query = appliquer_cursor_filter(
                    query, 
                    cursor_params, 
                    ActiviteFamille,
                    cursor_field="date_prevue",  # FIX B12: match l'ordre principal
                    secondary_field="id"          # Stable tie-breaker
                )
                items = query.limit(page_size + 1).all()
                return construire_reponse_cursor(
                    items,
                    page_size,
                    cursor_field="date_prevue",   # FIX B12: match l'ordre
                    secondary_field="id",          # FIX B12: ti-breaker unique
                    serializer=None,
                )

            # Pagination offset standard
            total = query.count()
            items = query.offset((page - 1) * page_size).limit(page_size).all()

            return {
                "items": [
                    {
                        "id": a.id,
                        "titre": a.titre,
                        "description": a.description,
                        "type_activite": a.type_activite,
                        "date_prevue": a.date_prevue.isoformat(),
                        "duree_heures": a.duree_heures,
                        "lieu": a.lieu,
                        "statut": a.statut,
                        "cout_estime": a.cout_estime,
                        "cout_reel": a.cout_reel,
                    }
                    for a in items
                ],
                "total": total,
                "page": page,
                "page_size": page_size,
                "pages": (total + page_size - 1) // page_size if total > 0 else 0,
            }

    return await executer_async(_query)


@router.get("/activites/{activite_id}", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def obtenir_activite(activite_id: int, user: dict[str, Any] = Depends(require_auth)):
    """Récupère une activité par son ID."""
    from src.core.models import ActiviteFamille

    def _query():
        with executer_avec_session() as session:
            activite = (
                session.query(ActiviteFamille).filter(ActiviteFamille.id == activite_id).first()
            )
            if not activite:
                raise HTTPException(status_code=404, detail="Activité non trouvée")

            return {
                "id": activite.id,
                "titre": activite.titre,
                "description": activite.description,
                "type_activite": activite.type_activite,
                "date_prevue": activite.date_prevue.isoformat(),
                "duree_heures": activite.duree_heures,
                "lieu": activite.lieu,
                "qui_participe": activite.qui_participe,
                "age_minimal_recommande": activite.age_minimal_recommande,
                "cout_estime": activite.cout_estime,
                "cout_reel": activite.cout_reel,
                "statut": activite.statut,
                "notes": activite.notes,
            }

    return await executer_async(_query)


@router.post("/activites/suggestions-ia", responses=REPONSES_LISTE)
@gerer_exception_api
async def suggerer_activites_ia(
    params: ParamsSuggestionsActivites,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """
    Génère des suggestions d'activités personnalisées via IA.
    
    Utilise JulesAIService avec parsing structuré pour retourner des activités
    adaptées à l'âge de l'enfant, la météo, le budget et les préférences.
    
    **Paramètres**:
    - age_mois: Âge de l'enfant en mois (utilisé pour adapter les suggestions)
    - meteo: Type de météo ou lieu (pluie/soleil/mixte/interieur/exterieur)
    - budget_max: Budget maximum par activité en euros
    - duree_min/duree_max: Fourchette de durée souhaitée
    - preferences: Tags optionnels (creatif, sportif, educatif, sensoriel, etc.)
    - nb_suggestions: Nombre de suggestions (1-10)
    
    **Retour**: Liste structurée d'activités avec nom, description, durée, budget, 
    lieu, compétences, matériel nécessaire, niveau d'effort.
    """
    from src.services.famille.jules_ai import obtenir_jules_ai_service

    def _query():
        service = obtenir_jules_ai_service()
        suggestions = service.suggerer_activites_enrichies(
            age_mois=params.age_mois,
            meteo=params.meteo,
            budget_max=params.budget_max,
            duree_min=params.duree_min,
            duree_max=params.duree_max,
            preferences=params.preferences,
            nb_suggestions=params.nb_suggestions,
        )
        
        # Convertir Pydantic models en dicts pour JSON response
        return {
            "total": len(suggestions),
            "suggestions": [s.model_dump() for s in suggestions],
            "params": params.model_dump(),
        }

    return await executer_async(_query)


@router.post("/activites", status_code=201, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def creer_activite(
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Crée une nouvelle activité familiale."""
    from src.core.models import ActiviteFamille

    def _query():
        with executer_avec_session() as session:
            activite = ActiviteFamille(
                titre=payload["titre"],
                description=payload.get("description"),
                type_activite=payload.get("type_activite", "sortie"),
                date_prevue=payload["date_prevue"],
                duree_heures=payload.get("duree_heures"),
                lieu=payload.get("lieu"),
                qui_participe=payload.get("qui_participe"),
                cout_estime=payload.get("cout_estime"),
                statut=payload.get("statut", "planifié"),
                notes=payload.get("notes"),
            )
            session.add(activite)
            session.commit()
            session.refresh(activite)
            return {
                "id": activite.id,
                "titre": activite.titre,
                "type_activite": activite.type_activite,
                "date_prevue": activite.date_prevue.isoformat(),
                "statut": activite.statut,
            }

    return await executer_async(_query)


@router.patch("/activites/{activite_id}", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def modifier_activite(
    activite_id: int,
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Met à jour une activité familiale."""
    from src.core.models import ActiviteFamille

    def _query():
        with executer_avec_session() as session:
            activite = (
                session.query(ActiviteFamille).filter(ActiviteFamille.id == activite_id).first()
            )
            if not activite:
                raise HTTPException(status_code=404, detail="Activité non trouvée")

            for champ in ("titre", "description", "type_activite", "date_prevue",
                          "duree_heures", "lieu", "qui_participe", "cout_estime",
                          "cout_reel", "statut", "notes"):
                if champ in payload:
                    setattr(activite, champ, payload[champ])

            session.commit()
            session.refresh(activite)
            return {
                "id": activite.id,
                "titre": activite.titre,
                "statut": activite.statut,
                "date_prevue": activite.date_prevue.isoformat(),
            }

    return await executer_async(_query)


@router.delete("/activites/{activite_id}", responses=REPONSES_CRUD_SUPPRESSION)
@gerer_exception_api
async def supprimer_activite(
    activite_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> MessageResponse:
    """Supprime une activité familiale."""
    from src.core.models import ActiviteFamille

    def _query():
        with executer_avec_session() as session:
            activite = (
                session.query(ActiviteFamille).filter(ActiviteFamille.id == activite_id).first()
            )
            if not activite:
                raise HTTPException(status_code=404, detail="Activité non trouvée")
            session.delete(activite)
            session.commit()
            return MessageResponse(message=f"Activité '{activite.titre}' supprimée")

    return await executer_async(_query)


# ═══════════════════════════════════════════════════════════
# SUGGESTIONS IA 
# ═══════════════════════════════════════════════════════════


@router.post("/weekend/suggestions-ia", responses=REPONSES_LISTE)
@gerer_exception_api
async def suggestions_weekend_ia(
    payload: SuggestionsWeekendRequest,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Suggestions d'activités weekend avec météo et âge Jules auto-injectés."""
    from src.services.famille.jules import obtenir_service_jules
    from src.services.famille.weekend_ai import obtenir_weekend_ai_service
    from src.services.integrations.weather.service import obtenir_service_meteo

    async def _query():
        # Auto-inject météo
        meteo_service = obtenir_service_meteo()
        previsions = meteo_service.get_previsions(nb_jours=3)
        meteo_desc = "variable"
        if previsions:
            conditions = [p.condition for p in previsions[:3] if p.condition]
            meteo_desc = ", ".join(conditions[:2]) if conditions else "variable"

        # Auto-inject âge Jules
        jules_service = obtenir_service_jules()
        age_mois = jules_service.get_age_mois(default=19)

        service = obtenir_weekend_ai_service()
        resultat = await service.suggerer_activites(
            meteo=meteo_desc,
            age_enfant_mois=age_mois,
            budget=payload.budget,
            region=payload.region,
            nb_suggestions=payload.nb_suggestions,
        )
        return {"suggestions": resultat}

    return await _query()


@router.post("/soiree/suggestions-ia", responses=REPONSES_LISTE)
@gerer_exception_api
async def suggestions_soiree_ia(
    payload: SuggestionsSoireeRequest,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Suggestions de soirées en couple via IA."""
    from src.services.famille.soiree_ai import obtenir_service_soiree_ai

    async def _query():
        service = obtenir_service_soiree_ai()
        resultat = await service.suggerer_soirees(
            budget=payload.budget,
            duree_heures=payload.duree_heures,
            type_soiree=payload.type_soiree,
            region=payload.region,
        )
        return {"suggestions": resultat}

    return await _query()


# ═══════════════════════════════════════════════════════════
# ACHATS FAMILLE CRUD 
# ═══════════════════════════════════════════════════════════

