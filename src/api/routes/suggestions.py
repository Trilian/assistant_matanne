"""
Routes API pour les suggestions IA.

Suggestions de recettes et de plannings de repas générées par Mistral AI,
avec limitation de débit intégrée et cache sémantique.
"""

import logging
from datetime import date

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from pydantic import BaseModel, Field

from src.api.dependencies import require_auth
from src.api.rate_limiting import verifier_limite_debit_ia
from src.api.schemas import (
    AdaptationRecetteResponse,
    SuggestionsPlanningResponse,
    SuggestionsRecettesResponse,
)
from src.api.schemas.errors import REPONSES_IA
from src.api.utils import executer_async, executer_avec_session, gerer_exception_api

router = APIRouter(prefix="/api/v1/suggestions", tags=["IA"])


def _verifier_ia_configuree() -> None:
    """Lève HTTP 503 si MISTRAL_API_KEY n'est pas configurée."""
    from src.core.config import obtenir_parametres

    try:
        params = obtenir_parametres()
        _ = params.MISTRAL_API_KEY  # Raises ValueError if not set
    except (ValueError, Exception):
        raise HTTPException(
            status_code=503,
            detail=(
                "Le service IA n'est pas configuré. "
                "Ajoutez MISTRAL_API_KEY dans votre fichier .env.local."
            ),
        )


def _detecter_saison() -> str:
    """Retourne la saison actuelle en français."""
    month = date.today().month
    if month in (3, 4, 5):
        return "printemps"
    elif month in (6, 7, 8):
        return "été"
    elif month in (9, 10, 11):
        return "automne"
    return "hiver"


def _detecter_type_repas(contexte: str) -> str:
    """Déduit le type de repas depuis le contexte libre."""
    c = contexte.lower()
    if any(k in c for k in ("matin", "petit", "breakfast")):
        return "petit_dejeuner"
    if any(k in c for k in ("midi", "dejeuner", "déjeuner", "lunch")):
        return "dejeuner"
    if any(k in c for k in ("goûter", "gouter", "snack", "quatre-heure", "quatre heure")):
        return "gouter"
    if any(
        k in c
        for k in (
            "dessert", "gâteau", "gateau", "tarte", "compote", "mousse",
            "crème", "creme", "flan", "clafoutis", "tiramisu", "brownie",
            "muffin", "cookie", "biscuit", "sorbet", "glace", "fondant",
            "cheesecake", "cake", "yaourt", "charlotte", "île flottante",
            "panna cotta", "crumble", "financier",
        )
    ):
        return "dessert"
    return "diner"


class AdaptationRecetteRequest(BaseModel):
    """Payload pour demander une adaptation rapide d'ingrédient."""

    ingredient_manquant: str = Field(..., min_length=2, max_length=120)
    quantite: float = Field(default=1.0, ge=0)
    unite: str = Field(default="", max_length=30)
    stock_disponible: list[str] = Field(default_factory=list)
    tags_requis: list[str] = Field(default_factory=list)


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

    _verifier_ia_configuree()

    service = obtenir_service_recettes()

    MOTS_FACILE = (
        "rapide", "express", "vite", "simple", "facile",
        # Préparations intrinsèquement simples
        "compote", "salade", "yaourt", "smoothie", "velouté",
        "soupe", "purée", "puree", "omelette",
    )
    difficulte = "facile" if any(k in contexte.lower() for k in MOTS_FACILE) else "moyen"

    suggestions = service.generer_recettes_ia(
        type_repas=_detecter_type_repas(contexte),
        saison=_detecter_saison(),
        difficulte=difficulte,
        nb_recettes=nombre,
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
    from datetime import timedelta

    from src.services.cuisine.planning import obtenir_service_planning

    _verifier_ia_configuree()

    service = obtenir_service_planning()

    # Calculer le lundi de la semaine courante
    today = date.today()
    semaine_debut = today - timedelta(days=today.weekday())

    planning = service.generer_planning_ia(
        semaine_debut=semaine_debut,
        preferences={"nombre_personnes": personnes, "nombre_jours": jours},
    )

    if planning is None:
        raise HTTPException(
            status_code=503,
            detail="La génération du planning a échoué. Vérifiez que MISTRAL_API_KEY est configuré.",
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
    zone: str = Query(
        "frigo", pattern="^(frigo|placard|congelateur)$", description="Zone analysÃ©e"
    ),
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


@router.get("/menu-du-jour", responses=REPONSES_IA)
@gerer_exception_api
async def menu_du_jour(
    repas: str = Query(
        "diner",
        pattern="^(petit_dejeuner|dejeuner|diner)$",
        description="Type de repas (petit_dejeuner, dejeuner, diner)",
    ),
    nombre: int = Query(3, ge=1, le=5, description="Nombre de suggestions (1-5, défaut: 3)"),
    user: dict = Depends(require_auth),
    _rate_check: dict = Depends(verifier_limite_debit_ia),
):
    """
    INNO-5: "Qu'est-ce qu'on mange ?" — 1 bouton = 3 suggestions contextuelles.

    Retourne des suggestions de recettes basées sur:
    - Stock disponible (inventaire + courses)
    - Météo (si possible)
    - Goûts détectés (historique)
    - Derniers repas (éviter la répétition)
    - Adaptations Jules (si applicable)

    Args:
        repas: Type de repas (petit_dejeuner, dejeuner, diner). Défaut: diner
        nombre: Nombre de suggestions. Défaut: 3

    Returns:
        Liste de suggestions avec raison, temps de préparation, et ingrédients manquants
    """
    from src.services.cuisine.suggestions import obtenir_service_suggestions

    service = obtenir_service_suggestions()

    # Générer les suggestions
    suggestions = service.suggerer_recettes(
        contexte=None,  # Utilise le contexte auto-détecté
        nb_suggestions=nombre,
        inclure_decouvertes=True,
    )

    # Formater la réponse
    return {
        "suggestions": [
            {
                "recette_id": s.recette_id,
                "nom": s.nom,
                "raison": s.raison,
                "temps_preparation": s.temps_preparation,
                "difficulte": s.difficulte,
                "ingredients_manquants": s.ingredients_manquants,
                "score": round(s.score, 1),
                "est_nouvelle": s.est_nouvelle,
                "tags": s.tags,
            }
            for s in suggestions[:nombre]
        ],
        "repas": repas,
        "nombre": min(nombre, len(suggestions)) if suggestions else 0,
        "contexte": "Stock + historique personnalisé",
    }


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# PRÃ‰DICTIONS ML
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.post("/adaptation-recette", response_model=AdaptationRecetteResponse, responses=REPONSES_IA)
@gerer_exception_api
async def adaptation_recette(
    body: AdaptationRecetteRequest,
    user: dict = Depends(require_auth),
    _rate_check: dict = Depends(verifier_limite_debit_ia),
):
    """IA4 — Propose des alternatives quand il manque un ingrédient dans une recette."""
    from src.core.db import obtenir_contexte_db
    from src.core.models import ArticleInventaire
    from src.services.cuisine.suggestions.substitutions import suggerer_substitutions_recette

    stock_disponible = list(body.stock_disponible)
    if not stock_disponible:
        try:
            with obtenir_contexte_db() as session:
                stock_disponible = [
                    article.nom
                    for article in session.query(ArticleInventaire)
                    .filter(ArticleInventaire.quantite > 0)
                    .order_by(ArticleInventaire.nom.asc())
                    .limit(80)
                    .all()
                    if article.nom
                ]
        except Exception:
            stock_disponible = []

    resultats = suggerer_substitutions_recette(
        [
            {
                "nom": body.ingredient_manquant,
                "quantite": body.quantite,
                "unite": body.unite,
            }
        ],
        stock_disponible=stock_disponible,
        tags_requis=body.tags_requis,
    )

    adaptation = resultats[0] if resultats else None
    substitutions = []
    meilleure_en_stock = None
    if adaptation is not None:
        substitutions = [
            {
                "ingredient_original": sub.ingredient_original,
                "ingredient_substitut": sub.ingredient_substitut,
                "ratio": sub.ratio,
                "impact_gout": sub.impact_gout,
                "tags": list(sub.tags),
                "note": sub.note,
                "disponible_en_stock": any(
                    sub.ingredient_substitut.lower() in stock.lower()
                    or stock.lower() in sub.ingredient_substitut.lower()
                    for stock in stock_disponible
                ),
            }
            for sub in adaptation.substitutions
        ]
        if adaptation.meilleure_en_stock is not None:
            sub = adaptation.meilleure_en_stock
            meilleure_en_stock = {
                "ingredient_original": sub.ingredient_original,
                "ingredient_substitut": sub.ingredient_substitut,
                "ratio": sub.ratio,
                "impact_gout": sub.impact_gout,
                "tags": list(sub.tags),
                "note": sub.note,
                "disponible_en_stock": True,
            }

    message = (
        f"Utilise {meilleure_en_stock['ingredient_substitut']} à environ {meilleure_en_stock['ratio']}x la quantité habituelle."
        if meilleure_en_stock
        else "Aucune substitution évidente en stock, consulte les alternatives proposées."
    )

    return {
        "ingredient_manquant": body.ingredient_manquant,
        "quantite_requise": body.quantite,
        "unite": body.unite,
        "substitutions": substitutions,
        "meilleure_en_stock": meilleure_en_stock,
        "message": message,
    }


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
    """Retourne le statut des modèles ML (entraînés ou non)."""
    from src.services.cuisine.suggestions.ml_predictions import obtenir_ml_predictions

    service = obtenir_ml_predictions()
    return {"modeles": service.statut_modeles()}


# ══════════════════════════════════════════════════════════════════
# G1 — Recette express depuis le stock actuel
# ══════════════════════════════════════════════════════════════════


@router.get(
    "/depuis-stock",
    responses=REPONSES_IA,
    summary="Suggérer des recettes réalisables avec le stock actuel",
)
@gerer_exception_api
async def suggerer_recettes_depuis_stock(
    max_resultats: int = Query(3, ge=1, le=6, description="Nombre max de suggestions"),
    temps_max_min: int = Query(
        45, ge=10, le=120, description="Temps de préparation maximum (minutes)"
    ),
    user: dict = Depends(require_auth),
    _rate_check: dict = Depends(verifier_limite_debit_ia),
) -> dict:
    """Suggère des recettes réalisables en un tap selon le stock actuel (G1).

    Lit les articles en stock (quantite > quantite_min ou quantite > 0),
    les transmet à Mistral qui propose des recettes faisables sans courses.
    """

    def _query() -> dict:
        from src.core.models.inventaire import ArticleInventaire
        from src.services.cuisine.recettes.service import obtenir_service_recettes

        with executer_avec_session() as session:
            # Récupérer les ingrédients en stock (quantité > 0)
            articles = session.query(ArticleInventaire).filter(ArticleInventaire.quantite > 0).all()
            ingredients_en_stock = [
                {
                    "nom": a.nom or "inconnu",
                    "quantite": a.quantite,
                    "unite": a.unite or "",
                }
                for a in articles
                if a.nom
            ]

        if not ingredients_en_stock:
            return {
                "suggestions": [],
                "nb_ingredients_stock": 0,
                "message": "Aucun ingrédient en stock détecté.",
            }

        service = obtenir_service_recettes()
        suggestions = service.suggerer_depuis_inventaire(
            ingredients_disponibles=ingredients_en_stock,
            temps_max_min=temps_max_min,
            nb_suggestions=max_resultats,
        )
        resultat: dict = {
            "suggestions": [s.model_dump() if hasattr(s, "model_dump") else s for s in suggestions],
            "nb_ingredients_stock": len(ingredients_en_stock),
        }
        if not suggestions:
            resultat["message"] = "L'IA n'a pas pu générer de suggestions. Vérifiez que MISTRAL_API_KEY est configuré."
        return resultat

    return await executer_async(_query)
