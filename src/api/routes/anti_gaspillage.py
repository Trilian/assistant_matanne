"""
Routes API pour l'anti-gaspillage.

Score anti-gaspillage, articles bientôt périmés, recettes rescue.
"""

from datetime import date, timedelta
from typing import Any

from fastapi import APIRouter, Depends, Query

from src.api.dependencies import require_auth
from src.api.schemas.errors import REPONSES_LISTE
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

            # Recettes rescue: trouver des recettes qui utilisent les ingrédients urgents
            recettes_rescue = []
            if noms_urgents:
                recettes = session.query(Recette).limit(100).all()
                for r in recettes:
                    # Vérifie si le nom de la recette ou sa description contient
                    # un ingrédient urgent (recherche simple)
                    nom_lower = (r.nom or "").lower()
                    desc_lower = (r.description or "").lower()
                    ingredients_utilises = [
                        n
                        for n in noms_urgents
                        if n in nom_lower or n in desc_lower
                    ]
                    if ingredients_utilises:
                        recettes_rescue.append(
                            {
                                "id": r.id,
                                "nom": r.nom,
                                "ingredients_utilises": ingredients_utilises,
                                "temps_total": (
                                    (r.temps_preparation or 0) + (r.temps_cuisson or 0)
                                )
                                or None,
                                "difficulte": r.difficulte,
                            }
                        )
                    if len(recettes_rescue) >= 5:
                        break

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
