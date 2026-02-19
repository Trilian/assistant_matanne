"""
Routes API pour les suggestions IA.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException

from src.api.dependencies import get_current_user
from src.api.rate_limiting import verifier_limite_debit_ia

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/suggestions", tags=["IA"])


# ═══════════════════════════════════════════════════════════
# ROUTES
# ═══════════════════════════════════════════════════════════


@router.get("/recettes")
async def suggest_recettes(
    contexte: str = "repas équilibré",
    nombre: int = 3,
    user: dict = Depends(get_current_user),
    _rate_check: dict = Depends(verifier_limite_debit_ia),
):
    """
    Suggère des recettes via IA.

    Args:
        contexte: Contexte pour les suggestions (ex: "repas équilibré", "rapide", "végétarien")
        nombre: Nombre de suggestions à retourner (1-10)
        user: Utilisateur authentifié

    Returns:
        Liste de suggestions de recettes
    """
    try:
        from src.services.cuisine.recettes import get_recette_service

        service = get_recette_service()

        suggestions = service.suggerer_recettes_ia(
            contexte=contexte,
            nombre_suggestions=nombre,
        )

        return {
            "suggestions": suggestions,
            "contexte": contexte,
            "nombre": nombre,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur suggestions IA: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/planning")
async def suggest_planning(
    jours: int = 7,
    personnes: int = 4,
    user: dict = Depends(get_current_user),
    _rate_check: dict = Depends(verifier_limite_debit_ia),
):
    """
    Suggère un planning de repas via IA.

    Args:
        jours: Nombre de jours à planifier (1-14)
        personnes: Nombre de personnes
        user: Utilisateur authentifié

    Returns:
        Suggestion de planning hebdomadaire
    """
    try:
        from src.services.cuisine.planning import get_planning_service

        service = get_planning_service()

        planning = service.generer_planning_ia(
            nombre_jours=jours,
            nombre_personnes=personnes,
        )

        return {
            "planning": planning,
            "jours": jours,
            "personnes": personnes,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur suggestions planning: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e
