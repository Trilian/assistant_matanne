"""
Routes API pour les suggestions IA.

Suggestions de recettes et de plannings de repas gÃ©nÃ©rÃ©es par Mistral AI,
avec limitation de dÃ©bit intÃ©grÃ©e et cache sÃ©mantique.
"""

import logging

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile

from src.api.dependencies import require_auth
from src.api.rate_limiting import verifier_limite_debit_ia
from src.api.schemas import SuggestionsPlanningResponse, SuggestionsRecettesResponse
from src.api.schemas.errors import REPONSES_IA
from src.api.utils import gerer_exception_api

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/suggestions", tags=["IA"])


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# ROUTES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.get("/recettes", response_model=SuggestionsRecettesResponse, responses=REPONSES_IA)
@gerer_exception_api
async def suggest_recettes(
    contexte: str = Query(
        "repas équilibré",
        description="Contexte pour les suggestions (ex: 'rapide', 'vÃ©gÃ©tarien', 'batch cooking')",
    ),
    nombre: int = Query(3, ge=1, le=10, description="Nombre de suggestions Ã  retourner (1-10)"),
    user: dict = Depends(require_auth),
    _rate_check: dict = Depends(verifier_limite_debit_ia),
):
    """
    SuggÃ¨re des recettes via l'IA Mistral.

    GÃ©nÃ¨re des suggestions de recettes personnalisÃ©es en fonction du contexte
    fourni. Soumis Ã  une limitation de dÃ©bit (quota horaire/journalier).

    Args:
        contexte: Description du type de repas souhaitÃ©
        nombre: Nombre de suggestions (dÃ©faut: 3, max: 10)

    Returns:
        Liste de suggestions avec le contexte utilisÃ©

    Raises:
        401: Non authentifiÃ©
        429: Limite de dÃ©bit IA dÃ©passÃ©e
        503: Service IA indisponible

    Example:
        ```
        GET /api/v1/suggestions/recettes?contexte=vÃ©gÃ©tarien&nombre=5
        Authorization: Bearer <token>

        Response:
        {
            "suggestions": [
                {"nom": "Curry de lentilles", "description": "...", "temps_preparation": 30},
                {"nom": "Buddha bowl", "description": "...", "temps_preparation": 20}
            ],
            "contexte": "vÃ©gÃ©tarien",
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


@router.get("/planning", response_model=SuggestionsPlanningResponse, responses=REPONSES_IA)
@gerer_exception_api
async def suggest_planning(
    jours: int = Query(7, ge=1, le=14, description="Nombre de jours Ã  planifier (1-14)"),
    personnes: int = Query(4, ge=1, le=20, description="Nombre de personnes Ã  table"),
    user: dict = Depends(require_auth),
    _rate_check: dict = Depends(verifier_limite_debit_ia),
):
    """
    SuggÃ¨re un planning de repas complet via l'IA Mistral.

    GÃ©nÃ¨re un planning hebdomadaire Ã©quilibrÃ© avec petit-dÃ©jeuner,
    dÃ©jeuner et dÃ®ner pour le nombre de jours et personnes spÃ©cifiÃ©s.

    Args:
        jours: Nombre de jours Ã  planifier (dÃ©faut: 7, max: 14)
        personnes: Nombre de convives (dÃ©faut: 4, max: 20)

    Returns:
        Planning structurÃ© par jour avec recettes suggÃ©rÃ©es

    Raises:
        401: Non authentifiÃ©
        429: Limite de dÃ©bit IA dÃ©passÃ©e
        503: Service IA indisponible

    Example:
        ```
        GET /api/v1/suggestions/planning?jours=7&personnes=4
        Authorization: Bearer <token>

        Response:
        {
            "planning": {
                "lundi": {"dejeuner": "Poulet rÃ´ti", "diner": "Soupe de lÃ©gumes"},
                "mardi": {"dejeuner": "Pasta carbonara", "diner": "Salade compose"}
            },
            "jours": 7,
            "personnes": 4
        }
        ```
    """
    from datetime import date, timedelta

    from src.services.cuisine.planning import obtenir_service_planning

    service = obtenir_service_planning()

    # Calculer le lundi de la semaine courante
    today = date.today()
    semaine_debut = today - timedelta(days=today.weekday())

    planning = service.generer_planning_ia(
        semaine_debut=semaine_debut,
        preferences={"nombre_personnes": personnes, "nombre_jours": jours},
    )

    return {
        "planning": planning,
        "jours": jours,
        "personnes": personnes,
    }


@router.post("/photo-frigo", responses=REPONSES_IA)
@gerer_exception_api
async def analyser_photo_frigo(
    file: UploadFile = File(..., description="Photo du frigo (JPEG/PNG, max 10MB)"),
    zone: str = Query("frigo", pattern="^(frigo|placard|congelateur)$", description="Zone analysÃ©e"),
    zones: list[str] | None = Query(
        None,
        description="Zones Ã  analyser en multi-zone (frigo, placard, congelateur)",
    ),
    user: dict = Depends(require_auth),
    _rate_check: dict = Depends(verifier_limite_debit_ia),
):
    """
    Analyse une photo du frigo et suggÃ¨re des recettes.

    Envoie une photo du frigo pour dÃ©tecter les ingrÃ©dients visibles
    et obtenir des suggestions de recettes rÃ©alisables.
    """
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Le fichier doit Ãªtre une image")

    image_bytes = await file.read()
    if len(image_bytes) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="L'image ne doit pas dÃ©passer 10 MB")

    from src.services.cuisine.photo_frigo import obtenir_photo_frigo_service

    service = obtenir_photo_frigo_service()
    zones_valides = {"frigo", "placard", "congelateur"}

    if zones:
        zones_filtres = [z for z in zones if z in zones_valides]
        if not zones_filtres:
            raise HTTPException(
                status_code=400,
                detail="ParamÃ¨tre zones invalide. Valeurs autorisÃ©es: frigo, placard, congelateur",
            )
        resultat = await service.analyser_photo_frigo_multi_zone(image_bytes, zones_filtres)
    else:
        resultat = await service.analyser_photo_frigo(image_bytes, zone=zone)

    return resultat.model_dump()


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# PRÃ‰DICTIONS ML
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.get("/predictions/courses")
@gerer_exception_api
async def predictions_courses(
    articles: str = Query(
        ...,
        description="Articles Ã  prÃ©dire (sÃ©parÃ©s par virgule)",
    ),
    horizon: int = Query(7, ge=1, le=30, description="Horizon de prÃ©diction en jours"),
    user: dict = Depends(require_auth),
):
    """PrÃ©dit la consommation d'articles sur un horizon donnÃ©."""
    from src.services.cuisine.suggestions.ml_predictions import obtenir_ml_predictions

    service = obtenir_ml_predictions()
    noms = [a.strip() for a in articles.split(",") if a.strip()]

    predictions = []
    for article in noms:
        pred = service.consommation.predire(article, horizon_jours=horizon)
        predictions.append(pred.model_dump() if hasattr(pred, "model_dump") else pred.__dict__)

    return {"predictions": predictions, "horizon_jours": horizon}


@router.get("/predictions/statut")
@gerer_exception_api
async def statut_predictions(
    user: dict = Depends(require_auth),
):
    """Retourne le statut des modÃ¨les ML (entraÃ®nÃ©s ou non)."""
    from src.services.cuisine.suggestions.ml_predictions import obtenir_ml_predictions

    service = obtenir_ml_predictions()
    return {"modeles": service.statut_modeles()}


@router.get("/saison")
@gerer_exception_api
async def produits_de_saison(
    mois: int = Query(0, ge=0, le=12, description="Mois (1-12). 0 = mois courant"),
    user: dict = Depends(require_auth),
):
    """Retourne les fruits et lÃ©gumes de saison pour le mois donnÃ©."""
    import json
    from datetime import date
    from pathlib import Path

    mois_cible = mois if mois > 0 else date.today().month
    fichier = Path(__file__).resolve().parents[3] / "data" / "reference" / "produits_de_saison.json"

    if not fichier.exists():
        raise HTTPException(status_code=404, detail="Catalogue saisonnier introuvable")

    data = json.loads(fichier.read_text(encoding="utf-8"))
    produits = data.get("produits", [])

    fruits = [p["nom"] for p in produits if mois_cible in p.get("mois", []) and p.get("categorie") == "fruit"]
    legumes = [p["nom"] for p in produits if mois_cible in p.get("mois", []) and p.get("categorie") == "legume"]

    return {
        "mois": mois_cible,
        "fruits": sorted(fruits),
        "legumes": sorted(legumes),
        "total": len(fruits) + len(legumes),
    }

