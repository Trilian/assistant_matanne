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


@router.get("/historique", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def obtenir_historique_gaspillage(
    semaines: int = Query(4, ge=1, le=12, description="Nombre de semaines d'historique"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """
    Retourne l'historique anti-gaspillage et les badges de gamification.

    Calcule un score hebdomadaire basé sur les articles périmés détectés
    dans l'inventaire, et attribue des badges selon les performances.
    """

    def _query():
        with executer_avec_session() as session:
            from sqlalchemy import func

            from src.core.models import ArticleInventaire

            aujourd_hui = date.today()
            historique_semaines = []

            for i in range(semaines):
                fin_sem = aujourd_hui - timedelta(days=aujourd_hui.weekday() + 7 * i)
                debut_sem = fin_sem - timedelta(days=7)

                # Articles dont la date de péremption tombe dans cette semaine ET sont déjà périmés
                perimes = (
                    session.query(func.count(ArticleInventaire.id))
                    .filter(
                        ArticleInventaire.date_peremption.isnot(None),
                        ArticleInventaire.date_peremption >= debut_sem,
                        ArticleInventaire.date_peremption < fin_sem,
                        ArticleInventaire.date_peremption < aujourd_hui,
                    )
                    .scalar()
                    or 0
                )

                # Articles dont la péremption tombe dans la fenêtre élargie (+3j) — proches mais sans certitude
                a_utiliser = (
                    session.query(func.count(ArticleInventaire.id))
                    .filter(
                        ArticleInventaire.date_peremption.isnot(None),
                        ArticleInventaire.date_peremption >= debut_sem,
                        ArticleInventaire.date_peremption < fin_sem + timedelta(days=3),
                    )
                    .scalar()
                    or 0
                )
                sauves = max(0, a_utiliser - perimes)
                score_sem = max(0, 100 - (perimes * 10))

                historique_semaines.append({
                    "debut": debut_sem.isoformat(),
                    "fin": fin_sem.isoformat(),
                    "score": score_sem,
                    "articles_perimes": perimes,
                    "articles_sauves": sauves,
                    "economie": round(sauves * 3.5, 2),
                })

            scores = [s["score"] for s in historique_semaines]
            score_moyen = round(sum(scores) / len(scores)) if scores else 0

            tendance: str
            if len(scores) >= 2:
                if scores[0] > scores[-1]:
                    tendance = "hausse"
                elif scores[0] < scores[-1]:
                    tendance = "baisse"
                else:
                    tendance = "stable"
            else:
                tendance = "stable"

            total_sauves = sum(s["articles_sauves"] for s in historique_semaines)
            total_perimes = sum(s["articles_perimes"] for s in historique_semaines)
            semaines_parfaites = sum(1 for s in historique_semaines if s["score"] >= 80)

            badges = [
                {
                    "id": "premier_pas",
                    "nom": "Premier pas",
                    "description": "Commencer à suivre le gaspillage",
                    "emoji": "🌱",
                    "obtenu": True,
                    "condition_valeur": 1,
                    "valeur_actuelle": 1,
                },
                {
                    "id": "sauveur",
                    "nom": "Sauveur",
                    "description": "Sauver 5 articles de la poubelle",
                    "emoji": "🦸",
                    "obtenu": total_sauves >= 5,
                    "condition_valeur": 5,
                    "valeur_actuelle": total_sauves,
                },
                {
                    "id": "guerrier_eco",
                    "nom": "Guerrier Éco",
                    "description": "Sauver 20 articles de la poubelle",
                    "emoji": "♻️",
                    "obtenu": total_sauves >= 20,
                    "condition_valeur": 20,
                    "valeur_actuelle": total_sauves,
                },
                {
                    "id": "semaine_parfaite",
                    "nom": "Semaine parfaite",
                    "description": "Score ≥80 pendant 1 semaine",
                    "emoji": "⭐",
                    "obtenu": semaines_parfaites >= 1,
                    "condition_valeur": 1,
                    "valeur_actuelle": semaines_parfaites,
                },
                {
                    "id": "eco_heros",
                    "nom": "Éco-héros",
                    "description": "Score ≥80 pendant 4 semaines consécutives",
                    "emoji": "🏆",
                    "obtenu": semaines_parfaites >= 4,
                    "condition_valeur": 4,
                    "valeur_actuelle": semaines_parfaites,
                },
                {
                    "id": "zero_dechet",
                    "nom": "Zéro déchet",
                    "description": "Aucun article périmé sur 4 semaines",
                    "emoji": "🌍",
                    "obtenu": total_perimes == 0 and len(historique_semaines) >= 4,
                    "condition_valeur": 0,
                    "valeur_actuelle": total_perimes,
                },
            ]

            return {
                "semaines": historique_semaines,
                "badges": badges,
                "score_moyen_4s": score_moyen,
                "tendance": tendance,
            }

    return await executer_async(_query)

