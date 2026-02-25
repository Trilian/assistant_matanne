"""
Routes API pour les suggestions IA.

Suggestions de recettes et de plannings de repas générées par Mistral AI,
avec limitation de débit intégrée et cache sémantique.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query

from src.api.dependencies import require_auth
from src.api.rate_limiting import verifier_limite_debit_ia
from src.api.schemas import SuggestionsPlanningResponse, SuggestionsRecettesResponse
from src.api.utils import gerer_exception_api

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/suggestions", tags=["IA"])


# ═══════════════════════════════════════════════════════════
# ROUTES
# ═══════════════════════════════════════════════════════════


@router.get("/recettes", response_model=SuggestionsRecettesResponse)
@gerer_exception_api
async def suggest_recettes(
    contexte: str = Query(
        "repas équilibré",
        description="Contexte pour les suggestions (ex: 'rapide', 'végétarien', 'batch cooking')",
    ),
    nombre: int = Query(3, ge=1, le=10, description="Nombre de suggestions à retourner (1-10)"),
    user: dict = Depends(require_auth),
    _rate_check: dict = Depends(verifier_limite_debit_ia),
):
    """
    Suggère des recettes via l'IA Mistral.

    Génère des suggestions de recettes personnalisées en fonction du contexte
    fourni. Soumis à une limitation de débit (quota horaire/journalier).

    Args:
        contexte: Description du type de repas souhaité
        nombre: Nombre de suggestions (défaut: 3, max: 10)

    Returns:
        Liste de suggestions avec le contexte utilisé

    Raises:
        401: Non authentifié
        429: Limite de débit IA dépassée
        503: Service IA indisponible

    Example:
        ```
        GET /api/v1/suggestions/recettes?contexte=végétarien&nombre=5
        Authorization: Bearer <token>

        Response:
        {
            "suggestions": [
                {"nom": "Curry de lentilles", "description": "...", "temps_preparation": 30},
                {"nom": "Buddha bowl", "description": "...", "temps_preparation": 20}
            ],
            "contexte": "végétarien",
            "nombre": 5
        }
        ```
    """
    from src.services.cuisine.recettes import obtenir_service_recettes

    service = obtenir_service_recettes()

    suggestions = service.suggerer_recettes_ia(
        contexte=contexte,
        nombre_suggestions=nombre,
    )

    return {
        "suggestions": suggestions,
        "contexte": contexte,
        "nombre": nombre,
    }


@router.get("/planning", response_model=SuggestionsPlanningResponse)
@gerer_exception_api
async def suggest_planning(
    jours: int = Query(7, ge=1, le=14, description="Nombre de jours à planifier (1-14)"),
    personnes: int = Query(4, ge=1, le=20, description="Nombre de personnes à table"),
    user: dict = Depends(require_auth),
    _rate_check: dict = Depends(verifier_limite_debit_ia),
):
    """
    Suggère un planning de repas complet via l'IA Mistral.

    Génère un planning hebdomadaire équilibré avec petit-déjeuner,
    déjeuner et dîner pour le nombre de jours et personnes spécifiés.

    Args:
        jours: Nombre de jours à planifier (défaut: 7, max: 14)
        personnes: Nombre de convives (défaut: 4, max: 20)

    Returns:
        Planning structuré par jour avec recettes suggérées

    Raises:
        401: Non authentifié
        429: Limite de débit IA dépassée
        503: Service IA indisponible

    Example:
        ```
        GET /api/v1/suggestions/planning?jours=7&personnes=4
        Authorization: Bearer <token>

        Response:
        {
            "planning": {
                "lundi": {"dejeuner": "Poulet rôti", "diner": "Soupe de légumes"},
                "mardi": {"dejeuner": "Pasta carbonara", "diner": "Salade compose"}
            },
            "jours": 7,
            "personnes": 4
        }
        ```
    """
    from src.services.cuisine.planning import obtenir_service_planning

    service = obtenir_service_planning()

    planning = service.generer_planning_ia(
        nombre_jours=jours,
        nombre_personnes=personnes,
    )

    return {
        "planning": planning,
        "jours": jours,
        "personnes": personnes,
    }
