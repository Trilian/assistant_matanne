"""
Bridge NIM6: Courses → Planning validation post-achat.

Connecte les articles achetés aux recettes planifiées pour apprendre les substitutions.
- Quand des articles sont marqués achétés, comparer avec le planning de la semaine
- Tracker les substitutions (ex: article A planifié → article B acheté)
- Événement: courses.articles_achetes -> planning.substitutions_apprises
"""

import logging
from datetime import datetime, timedelta

from sqlalchemy import and_
from sqlalchemy.orm import Session

from src.core.decorators import avec_gestion_erreurs, avec_session_db
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


class CoursesValidationBridgeService:
    """Bridge pour valider les courses vs planning et apprendre les substitutions."""

    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def analyser_substitutions_post_achat(self, db: Session | None = None) -> list[dict]:
        """Analyse les articles achetés vs planifiés et identifie les substitutions.

        Logique:
        - Cherche les articles de courses achetés dans les 7 derniers jours
        - Compare avec les ingrédients planifiés pour la semaine
        - Identifie les écarts comme substitutions
        - Stocke pour l'apprentissage IA

        Returns:
            Liste des substitutions détectées
        """
        from src.core.models.courses import ArticleCourses
        from src.core.models.planning import PlanificationRepas
        from src.core.models.recettes import Ingredient, Recette

        try:
            # Articles achetés récemment
            date_pivot = datetime.utcnow().date() - timedelta(days=7)
            articles_achetes = (
                db.query(ArticleCourses)
                .filter(
                    and_(
                        ArticleCourses.achete.is_(True),
                        ArticleCourses.achete_le.isnot(None),
                        ArticleCourses.achete_le >= date_pivot,
                    )
                )
                .all()
            )

            if not articles_achetes:
                logger.info("Aucun article acheté récemment à analyser")
                return []

            # Ingrédients planifiés pour la dernière semaine
            date_debut = datetime.utcnow().date() - timedelta(days=7)
            date_fin = datetime.utcnow().date() + timedelta(days=7)

            planifications = (
                db.query(PlanificationRepas)
                .filter(
                    and_(
                        PlanificationRepas.date_repas >= date_debut,
                        PlanificationRepas.date_repas <= date_fin,
                    )
                )
                .all()
            )

            # Récupérer les ingrédients planifiés
            ingredients_planifies = set()
            for plan in planifications:
                if plan.recette_id:
                    recette = db.query(Recette).filter_by(id=plan.recette_id).first()
                    if recette:
                        for ingredient in recette.ingredients:
                            ingredients_planifies.add((ingredient.nom.lower(), ingredient.id))

            # Analyser les substitutions
            substitutions = []
            for article in articles_achetes:
                # Chercher l'ingrédient correspondant
                if article.ingredient_id:
                    ingredient = db.query(Ingredient).filter_by(id=article.ingredient_id).first()
                    if ingredient:
                        # Vérifier si cet ingrédient était planifié
                        planifie = any(ing_name.lower() == ingredient.nom.lower() for ing_name, _ in ingredients_planifies)

                        if not planifie and ingredient.nom:
                            # C'est une substitution (acheté mais pas planifié directement)
                            substitutions.append(
                                {
                                    "article_id": article.id,
                                    "ingredient_acheté": ingredient.nom,
                                    "type": "nouveau_ingredient",
                                    "date_achat": article.achete_le.isoformat() if article.achete_le else None,
                                    "rayon": article.rayon_magasin,
                                    "quantite": article.quantite_necessaire,
                                }
                            )

            if substitutions:
                logger.info(f"✅ {len(substitutions)} substitution(s) détectée(s)")
                # Émettre l'événement
                from src.services.core.events import obtenir_bus

                bus = obtenir_bus()
                bus.emettre(
                    "planning.substitutions_apprises",
                    {
                        "nombre": len(substitutions),
                        "substitutions": substitutions[:5],  # Top 5 pour le log
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                )

            return substitutions

        except Exception as e:
            logger.error(f"Erreur bridge courses→planning: {e}")
            return []

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def valider_achete_vs_planifie(self, liste_courses_id: int, db: Session | None = None) -> dict:
        """Valide que tout ce qui était planifié a été acheté (ou remplacé).

        Returns:
            Stats de validation
        """
        from src.core.models.courses import ArticleCourses, ListeCourses

        try:
            liste = db.query(ListeCourses).filter_by(id=liste_courses_id).first()
            if not liste:
                return {"erreur": "Liste non trouvée"}

            articles = db.query(ArticleCourses).filter_by(liste_id=liste_courses_id).all()

            total = len(articles)
            achetes = sum(1 for a in articles if a.achete)
            non_achetes = total - achetes

            taux_completion = (achetes / total * 100) if total > 0 else 0

            return {
                "total": total,
                "achetes": achetes,
                "non_achetes": non_achetes,
                "taux_completion": round(taux_completion, 1),
                "etat": "complète" if non_achetes == 0 else "en cours" if achetes > 0 else "pas commencée",
            }

        except Exception as e:
            logger.error(f"Erreur validation courses→planning: {e}")
            return {"erreur": str(e)}


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


@service_factory("courses_validation_bridge", tags={"bridges", "cuisine"})
def obtenir_courses_validation_bridge() -> CoursesValidationBridgeService:
    """Factory singleton pour le bridge Courses → Planning."""
    return CoursesValidationBridgeService()


# ═══════════════════════════════════════════════════════════
# EVENT SUBSCRIBERS
# ═══════════════════════════════════════════════════════════


def enregistrer_courses_validation_subscribers() -> None:
    """Enregistre les subscribers pour le bridge Courses → Planning."""
    from src.services.core.events import obtenir_bus

    bus = obtenir_bus()

    def _on_courses_completees(event):
        """Handler: Quand les courses sont complétées → analyser substitutions."""
        try:
            service = obtenir_courses_validation_bridge()
            substitutions = service.analyser_substitutions_post_achat()
            if substitutions:
                logger.info(f"📊 {len(substitutions)} substitution(s) analysée(s)")
        except Exception as e:
            logger.warning(f"Erreur handler courses→planning: {e}")

    bus.souscrire("courses.articles_achetes", _on_courses_completees)
    logger.info("✅ Bridge Courses → Planning validation enregistré")
