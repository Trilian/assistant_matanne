"""
Service inter-modules : Inventaire/Batch/Nutrition/Feedback -> Planning recettes.

Bridge inter-modules :
- P5-01/P5-09: prioriser les recettes selon le stock disponible
- P5-10: exclure les articles en surplus des courses
- P5-11: bloquer les jours batch cooking dans le planning
- P5-12: alerter sur le desequilibre nutritionnel hebdomadaire
- P5-13: exclure les recettes mal notees des suggestions
"""

from __future__ import annotations

import logging
from collections import Counter
from datetime import date as date_type, timedelta
from typing import Any

from sqlalchemy import func

from src.core.decorators import avec_gestion_erreurs, avec_session_db
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


class InventairePlanningInteractionService:
    """Interactions intra-cuisine autour du planning hebdomadaire."""

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def suggerer_recettes_selon_stock(
        self,
        *,
        limite: int = 10,
        db=None,
    ) -> dict[str, Any]:
        """P5-01/P5-09: suggere les recettes maximisant l'usage du stock."""
        from src.core.models import ArticleInventaire, Ingredient, Recette
        from src.core.models.recettes import RecetteIngredient

        articles = (
            db.query(ArticleInventaire)
            .join(Ingredient, Ingredient.id == ArticleInventaire.ingredient_id)
            .filter(ArticleInventaire.quantite > 0)
            .all()
        )
        noms_stock = {a.ingredient.nom.lower() for a in articles if getattr(a, "ingredient", None)}
        if not noms_stock:
            return {"recettes": [], "message": "Inventaire vide."}

        recettes = (
            db.query(Recette)
            .join(RecetteIngredient, RecetteIngredient.recette_id == Recette.id)
            .join(Ingredient, Ingredient.id == RecetteIngredient.ingredient_id)
            .all()
        )

        scores: list[dict[str, Any]] = []
        for recette in recettes:
            ingreds = {ri.ingredient.nom.lower() for ri in recette.ingredients if ri.ingredient}
            if not ingreds:
                continue
            communs = len(ingreds.intersection(noms_stock))
            if communs == 0:
                continue
            couverture = round((communs / max(len(ingreds), 1)) * 100, 1)
            scores.append(
                {
                    "recette_id": recette.id,
                    "nom": recette.nom,
                    "ingredients_couverts": communs,
                    "ingredients_total": len(ingreds),
                    "couverture_stock_pct": couverture,
                }
            )

        scores.sort(key=lambda s: (s["couverture_stock_pct"], s["ingredients_couverts"]), reverse=True)
        return {
            "recettes": scores[:limite],
            "message": f"{len(scores[:limite])} recette(s) priorisee(s) selon le stock.",
        }

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def exclure_articles_surplus_des_courses(
        self,
        *,
        multiplicateur_surplus: float = 1.5,
        db=None,
    ) -> dict[str, Any]:
        """P5-10: identifie les articles de courses deja en surplus dans l'inventaire."""
        from src.core.models import ArticleInventaire, Ingredient
        from src.core.models.courses import ArticleCourses

        liste_courses = (
            db.query(ArticleCourses)
            .join(Ingredient, Ingredient.id == ArticleCourses.ingredient_id)
            .filter(ArticleCourses.achete.is_(False))
            .all()
        )

        exclus = []
        for article in liste_courses:
            inventaire = (
                db.query(ArticleInventaire)
                .filter(ArticleInventaire.ingredient_id == article.ingredient_id)
                .first()
            )
            if not inventaire:
                continue
            seuil = (inventaire.quantite_min or 1.0) * multiplicateur_surplus
            if (inventaire.quantite or 0) >= seuil:
                exclus.append(
                    {
                        "article_courses_id": article.id,
                        "ingredient": article.ingredient.nom if article.ingredient else "",
                        "quantite_stock": float(inventaire.quantite or 0),
                        "seuil_surplus": float(seuil),
                    }
                )

        return {
            "articles_surplus": exclus,
            "message": f"{len(exclus)} article(s) potentiellement exclu(s) pour surplus.",
        }

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def bloquer_jours_batch_dans_planning(
        self,
        *,
        jours_horizon: int = 7,
        db=None,
    ) -> dict[str, Any]:
        """P5-11: marque les jours de batch cooking comme bloques pour le planning."""
        from src.core.models import SessionBatchCooking

        aujourd_hui = date_type.today()
        fin = aujourd_hui + timedelta(days=jours_horizon)

        sessions = (
            db.query(SessionBatchCooking)
            .filter(
                SessionBatchCooking.date_session >= aujourd_hui,
                SessionBatchCooking.date_session <= fin,
            )
            .all()
        )

        jours_bloques = sorted({s.date_session.isoformat() for s in sessions if s.date_session})
        return {
            "jours_bloques": jours_bloques,
            "message": f"{len(jours_bloques)} jour(s) batch a bloquer dans le planning.",
        }

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def analyser_equilibre_nutritionnel_planning(
        self,
        *,
        jours_horizon: int = 7,
        db=None,
    ) -> dict[str, Any]:
        """P5-12: calcule un diagnostic simple d'equilibre nutritionnel de la semaine."""
        from src.core.models import Planning, Repas

        aujourd_hui = date_type.today()
        planning = (
            db.query(Planning)
            .filter(Planning.semaine_debut <= aujourd_hui, Planning.semaine_fin >= aujourd_hui)
            .first()
        )
        if not planning:
            return {"alertes": [], "message": "Aucun planning actif."}

        fin = aujourd_hui + timedelta(days=jours_horizon)
        repas = (
            db.query(Repas)
            .filter(
                Repas.planning_id == planning.id,
                Repas.date_repas >= aujourd_hui,
                Repas.date_repas <= fin,
            )
            .all()
        )

        types_proteines = Counter()
        calories_total = 0
        nb_calories = 0

        for r in repas:
            recette = getattr(r, "recette", None)
            if not recette:
                continue
            tp = (getattr(recette, "type_proteines", "") or "inconnu").lower()
            types_proteines[tp] += 1
            calories = getattr(recette, "calories", None)
            if calories:
                calories_total += calories
                nb_calories += 1

        alertes = []
        if len(types_proteines) <= 1 and sum(types_proteines.values()) >= 4:
            alertes.append("Variete proteique faible sur la semaine.")
        if nb_calories > 0:
            moyenne = calories_total / nb_calories
            if moyenne < 350:
                alertes.append("Apports calories moyens potentiellement faibles.")
            if moyenne > 950:
                alertes.append("Apports calories moyens potentiellement eleves.")

        return {
            "repartition_proteines": dict(types_proteines),
            "alertes": alertes,
            "message": "Diagnostic nutritionnel genere.",
        }

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def filtrer_recettes_mal_notees(
        self,
        *,
        seuil_note: int = 3,
        db=None,
    ) -> dict[str, Any]:
        """P5-13: retourne les recettes a exclure des suggestions (note < seuil)."""
        from src.core.models import RetourRecette

        rows = (
            db.query(
                RetourRecette.recette_id,
                func.avg(RetourRecette.note).label("note_moyenne"),
                func.count(RetourRecette.id).label("nb_retours"),
            )
            .group_by(RetourRecette.recette_id)
            .all()
        )

        exclues = [
            {
                "recette_id": r.recette_id,
                "note_moyenne": round(float(r.note_moyenne or 0), 2),
                "nb_retours": int(r.nb_retours or 0),
            }
            for r in rows
            if float(r.note_moyenne or 0) < seuil_note
        ]

        return {
            "recettes_exclues": exclues,
            "message": f"{len(exclues)} recette(s) sous le seuil {seuil_note}/5.",
        }


@service_factory("inventaire_planning_interaction", tags={"cuisine", "planning", "inventaire"})
def obtenir_service_inventaire_planning_interaction() -> InventairePlanningInteractionService:
    """Factory pour le bridge Inventaire -> Planning."""
    return InventairePlanningInteractionService()
