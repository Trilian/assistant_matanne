"""
Routes API pour l'anti-gaspillage.

Score anti-gaspillage, articles bientôt périmés, recettes rescue, suggestions IA.
"""

from datetime import date, timedelta
from typing import Any

from fastapi import APIRouter, Depends, Query

from src.api.dependencies import require_auth
from src.api.schemas.errors import REPONSES_LISTE, REPONSES_CRUD_LECTURE
from src.api.utils import executer_async, executer_avec_session, gerer_exception_api

router = APIRouter(prefix="/api/v1/anti-gaspillage", tags=["Anti-Gaspillage"])


@router.get("", responses=REPONSES_LISTE)
@gerer_exception_api
async def obtenir_anti_gaspillage(
    jours: int = Query(7, ge=1, le=30, description="Horizon en jours pour les alertes"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """
    Retourne le score anti-gaspillage, les articles urgents et des recettes rescue.

    Le score est calculé à partir du ratio d'articles sauvés vs périmés sur le mois.
    """
    from sqlalchemy import func

    def _query():
        with executer_avec_session() as session:
            from src.core.models import ArticleInventaire, Recette

            aujourd_hui = date.today()
            horizon = aujourd_hui + timedelta(days=jours)
            debut_mois = aujourd_hui.replace(day=1)

            # Articles bientôt périmés
            articles_urgents_query = (
                session.query(ArticleInventaire)
                .filter(
                    ArticleInventaire.date_peremption.isnot(None),
                    ArticleInventaire.date_peremption >= aujourd_hui,
                    ArticleInventaire.date_peremption <= horizon,
                )
                .order_by(ArticleInventaire.date_peremption.asc())
                .all()
            )

            articles_urgents = []
            noms_urgents = []
            for a in articles_urgents_query:
                jours_restants = (a.date_peremption - aujourd_hui).days
                articles_urgents.append(
                    {
                        "id": a.id,
                        "nom": a.nom,
                        "date_peremption": a.date_peremption.isoformat(),
                        "jours_restants": jours_restants,
                        "quantite": float(a.quantite) if a.quantite else None,
                        "unite": a.unite,
                    }
                )
                noms_urgents.append(a.nom.lower())

            # Articles périmés ce mois-ci (score)
            articles_perimes_mois = (
                session.query(func.count(ArticleInventaire.id))
                .filter(
                    ArticleInventaire.date_peremption.isnot(None),
                    ArticleInventaire.date_peremption < aujourd_hui,
                    ArticleInventaire.date_peremption >= debut_mois,
                )
                .scalar()
                or 0
            )

            # Score: 100 si aucun périmé, diminue de 10 par article
            articles_sauves = max(0, len(articles_urgents) - articles_perimes_mois)
            score = max(0, 100 - (articles_perimes_mois * 10))

            # Recettes rescue: trouver des recettes dont les ingrédients
            # correspondent à ceux qui sont bientôt périmés
            recettes_rescue = []
            if noms_urgents:
                from src.core.models.recettes import Ingredient, RecetteIngredient

                # Trouver les IDs d'ingrédients correspondant aux articles urgents
                ingredients_urgents = (
                    session.query(Ingredient.id, Ingredient.nom)
                    .filter(
                        func.lower(Ingredient.nom).in_(noms_urgents)
                    )
                    .all()
                )
                ingredient_ids = [i.id for i in ingredients_urgents]
                ingredient_noms = {i.id: i.nom for i in ingredients_urgents}

                if ingredient_ids:
                    # Trouver les recettes qui utilisent ces ingrédients (JOIN proper)
                    from sqlalchemy import distinct

                    recettes_avec_urgents = (
                        session.query(
                            Recette,
                            func.array_agg(distinct(Ingredient.nom)).label("noms_ingredients"),
                        )
                        .join(RecetteIngredient, RecetteIngredient.recette_id == Recette.id)
                        .join(Ingredient, Ingredient.id == RecetteIngredient.ingredient_id)
                        .filter(RecetteIngredient.ingredient_id.in_(ingredient_ids))
                        .group_by(Recette.id)
                        .order_by(func.count(RecetteIngredient.ingredient_id).desc())
                        .limit(5)
                        .all()
                    )

                    for r, noms in recettes_avec_urgents:
                        recettes_rescue.append(
                            {
                                "id": r.id,
                                "nom": r.nom,
                                "ingredients_utilises": [n for n in noms if n],
                                "temps_total": (
                                    (r.temps_preparation or 0) + (r.temps_cuisson or 0)
                                )
                                or None,
                                "difficulte": r.difficulte,
                            }
                        )

            return {
                "score": {
                    "score": score,
                    "articles_perimes_mois": articles_perimes_mois,
                    "articles_sauves_mois": articles_sauves,
                    "economie_estimee": articles_sauves * 3.5,
                },
                "articles_urgents": articles_urgents,
                "recettes_rescue": recettes_rescue,
            }

    return await executer_async(_query)


@router.post("/suggestions-ia", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def suggestions_ia_anti_gaspillage(
    jours: int = Query(7, ge=1, le=14, description="Horizon en jours"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """
    Génère des suggestions IA pour éviter le gaspillage.
    
    Analyse les produits urgents et génère:
    - Recettes créatives utilisant ces produits
    - Conseils de conservation
    - Idées de transformation (congélation, confiture, etc.)
    
    Returns:
        Suggestions IA pour réduire le gaspillage
    """
    import logging
    logger_local = logging.getLogger(__name__)

    from src.services.cuisine.suggestions.anti_gaspillage import obtenir_produits_urgents

    def _get_produits():
        return obtenir_produits_urgents(seuil_jours=jours)

    produits = await executer_async(_get_produits)

    if not produits:
        return {
            "message": "Aucun produit urgent à traiter. Bravo, zéro gaspillage !",
            "produits_urgents": [],
            "suggestions_ia": None,
        }

    produits_data = [
        {
            "nom": p.nom,
            "jours_restants": p.jours_restants,
            "quantite": p.quantite,
            "unite": p.unite,
            "urgence_emoji": p.emoji_urgence,
        }
        for p in produits
    ]

    # Appel IA (async natif)
    from src.core.ai import obtenir_client_ia

    texte_ia = None
    try:
        client = obtenir_client_ia()
        liste_produits = "\n".join(
            f"- {p['nom']} ({p['jours_restants']}j restants, {p['quantite']} {p['unite']})"
            for p in produits_data
        )
        texte_ia = await client.appeler(
            prompt=(
                f"Ces produits sont bientôt périmés:\n\n{liste_produits}\n\n"
                "Propose: 1) 3 recettes créatives utilisant UN MAXIMUM de ces produits "
                "2) 2 conseils de conservation "
                "3) 1 idée de transformation (congélation, confiture, etc.) si applicable. "
                "Format: réponse structurée, concise et pratique."
            ),
            prompt_systeme=(
                "Tu es un expert en cuisine zéro-déchet et en conservation des aliments. "
                "Propose des solutions pratiques et créatives. Réponds en français."
            ),
            max_tokens=800,
        )
    except Exception as e:
        logger_local.warning("Erreur appel IA anti-gaspi: %s", e)

    return {
        "produits_urgents": produits_data,
        "suggestions_ia": texte_ia,
        "nb_produits": len(produits_data),
    }

