"""
Routes API Famille â€” ActivitÃ©s familiales et suggestions IA.

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


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SCHEMAS PYDANTIC LOCAUX
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class ParamsSuggestionsActivites(BaseModel):
    """ParamÃ¨tres pour suggestions d'activitÃ©s IA"""

    age_mois: int = Field(..., ge=0, le=72, description="Ã‚ge de l'enfant en mois (0-72 mois)")
    meteo: str = Field(
        default="mixte",
        description="Type de mÃ©tÃ©o: pluie, soleil, nuageux, mixte, interieur, exterieur",
    )
    budget_max: float = Field(default=50.0, ge=0, le=500, description="Budget maximum par activitÃ©")
    duree_min: int = Field(default=30, ge=5, le=300, description="DurÃ©e minimum en minutes")
    duree_max: int = Field(default=120, ge=10, le=360, description="DurÃ©e maximum en minutes")
    preferences: list[str] | None = Field(
        default=None, description="Tags de prÃ©fÃ©rences (creatif, sportif, educatif, sensoriel, etc.)"
    )
    nb_suggestions: int = Field(
        default=5, ge=1, le=10, description="Nombre de suggestions souhaitÃ©es"
    )

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


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
    Liste les activitÃ©s familiales avec pagination offset ou cursor.

    Supporte deux modes de pagination:
    - Offset: Utiliser page/page_size (dÃ©faut)
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

            query = query.order_by(ActiviteFamille.date_prevue.desc())

            # Pagination cursor-based si cursor fourni
            if cursor:
                cursor_params = decoder_cursor(cursor)
                query = appliquer_cursor_filter(query, cursor_params, ActiviteFamille)
                items = query.limit(page_size + 1).all()
                return construire_reponse_cursor(
                    items,
                    page_size,
                    cursor_field="id",
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
    """RÃ©cupÃ¨re une activitÃ© par son ID."""
    from src.core.models import ActiviteFamille

    def _query():
        with executer_avec_session() as session:
            activite = (
                session.query(ActiviteFamille).filter(ActiviteFamille.id == activite_id).first()
            )
            if not activite:
                raise HTTPException(status_code=404, detail="ActivitÃ© non trouvÃ©e")

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
    GÃ©nÃ¨re des suggestions d'activitÃ©s personnalisÃ©es via IA.
    
    Utilise JulesAIService avec parsing structurÃ© pour retourner des activitÃ©s
    adaptÃ©es Ã  l'Ã¢ge de l'enfant, la mÃ©tÃ©o, le budget et les prÃ©fÃ©rences.
    
    **ParamÃ¨tres**:
    - age_mois: Ã‚ge de l'enfant en mois (utilisÃ© pour adapter les suggestions)
    - meteo: Type de mÃ©tÃ©o ou lieu (pluie/soleil/mixte/interieur/exterieur)
    - budget_max: Budget maximum par activitÃ© en euros
    - duree_min/duree_max: Fourchette de durÃ©e souhaitÃ©e
    - preferences: Tags optionnels (creatif, sportif, educatif, sensoriel, etc.)
    - nb_suggestions: Nombre de suggestions (1-10)
    
    **Retour**: Liste structurÃ©e d'activitÃ©s avec nom, description, durÃ©e, budget, 
    lieu, compÃ©tences, matÃ©riel nÃ©cessaire, niveau d'effort.
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
    """CrÃ©e une nouvelle activitÃ© familiale."""
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
                statut=payload.get("statut", "planifiÃ©"),
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
    """Met Ã  jour une activitÃ© familiale."""
    from src.core.models import ActiviteFamille

    def _query():
        with executer_avec_session() as session:
            activite = (
                session.query(ActiviteFamille).filter(ActiviteFamille.id == activite_id).first()
            )
            if not activite:
                raise HTTPException(status_code=404, detail="ActivitÃ© non trouvÃ©e")

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
    """Supprime une activitÃ© familiale."""
    from src.core.models import ActiviteFamille

    def _query():
        with executer_avec_session() as session:
            activite = (
                session.query(ActiviteFamille).filter(ActiviteFamille.id == activite_id).first()
            )
            if not activite:
                raise HTTPException(status_code=404, detail="ActivitÃ© non trouvÃ©e")
            session.delete(activite)
            session.commit()
            return MessageResponse(message=f"ActivitÃ© '{activite.titre}' supprimÃ©e")

    return await executer_async(_query)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SUGGESTIONS IA (Phase M3)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.post("/weekend/suggestions-ia", responses=REPONSES_LISTE)
@gerer_exception_api
async def suggestions_weekend_ia(
    payload: SuggestionsWeekendRequest,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Suggestions d'activitÃ©s weekend avec mÃ©tÃ©o et Ã¢ge Jules auto-injectÃ©s."""
    from src.services.famille.jules import obtenir_service_jules
    from src.services.famille.weekend_ai import obtenir_weekend_ai_service
    from src.services.integrations.weather.service import obtenir_service_meteo

    async def _query():
        # Auto-inject mÃ©tÃ©o
        meteo_service = obtenir_service_meteo()
        previsions = meteo_service.get_previsions(nb_jours=3)
        meteo_desc = "variable"
        if previsions:
            conditions = [p.condition for p in previsions[:3] if p.condition]
            meteo_desc = ", ".join(conditions[:2]) if conditions else "variable"

        # Auto-inject Ã¢ge Jules
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
    """Suggestions de soirÃ©es en couple via IA."""
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


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# ACHATS FAMILLE CRUD (Phase M4)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

