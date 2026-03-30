"""
Service inter-modules : Batch cooking → Inventaire.

IM-P2-6: Session batch cooking terminée → déduire automatiquement
les ingrédients consommés de l'inventaire.
"""

import logging
from typing import Any

from sqlalchemy.orm import Session

from src.core.decorators import avec_gestion_erreurs, avec_session_db
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


class BatchInventaireInteractionService:
    """Service inter-modules Batch cooking → Inventaire."""

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def deduire_ingredients_session_terminee(
        self,
        session_id: int,
        *,
        db: Session | None = None,
    ) -> dict[str, Any]:
        """Déduit les ingrédients d'une session batch cooking terminée.

        Args:
            session_id: ID de la session batch cooking
            db: Session DB (injectée)

        Returns:
            Dict de synthèse (lignes mises à jour, quantités déduites)
        """
        from src.core.models import ArticleInventaire, HistoriqueInventaire, SessionBatchCooking
        from src.core.models.recettes import RecetteIngredient

        if db is None:
            return {"ok": False, "message": "Session DB indisponible"}

        session = db.query(SessionBatchCooking).filter_by(id=session_id).first()
        if not session:
            return {"ok": False, "message": f"Session {session_id} introuvable"}

        if session.statut != "terminee":
            return {
                "ok": False,
                "message": f"Session {session_id} non terminée (statut={session.statut})",
            }

        recette_ids = session.recettes_selectionnees or []
        if not recette_ids:
            return {"ok": True, "lignes_maj": 0, "message": "Aucune recette sélectionnée"}

        lignes_maj = 0
        quantite_totale_deduite = 0.0
        ingredients_manquants: list[int] = []

        for recette_id in recette_ids:
            ingredients = db.query(RecetteIngredient).filter_by(recette_id=recette_id).all()

            for ing in ingredients:
                article = db.query(ArticleInventaire).filter_by(ingredient_id=ing.ingredient_id).first()
                if not article:
                    ingredients_manquants.append(ing.ingredient_id)
                    continue

                quantite_avant = float(article.quantite or 0)
                quantite_a_deduire = float(ing.quantite or 0)
                nouvelle_quantite = max(0.0, quantite_avant - quantite_a_deduire)

                if nouvelle_quantite == quantite_avant:
                    continue

                article.quantite = nouvelle_quantite
                db.add(
                    HistoriqueInventaire(
                        article_id=article.id,
                        ingredient_id=article.ingredient_id,
                        type_modification="modification",
                        quantite_avant=quantite_avant,
                        quantite_apres=nouvelle_quantite,
                        notes=(
                            f"Déduction batch cooking session #{session_id} "
                            f"(recette #{recette_id})"
                        ),
                    )
                )
                lignes_maj += 1
                quantite_totale_deduite += (quantite_avant - nouvelle_quantite)

        db.commit()

        resume = {
            "ok": True,
            "session_id": session_id,
            "lignes_maj": lignes_maj,
            "quantite_totale_deduite": round(quantite_totale_deduite, 2),
            "ingredients_manquants": sorted(set(ingredients_manquants)),
            "message": f"{lignes_maj} ligne(s) inventaire mise(s) à jour",
        }

        logger.info(
            "✅ Batch→Inventaire session=%s lignes=%s qte=%.2f",
            session_id,
            lignes_maj,
            quantite_totale_deduite,
        )
        return resume


@service_factory("batch_inventaire_interaction", tags={"cuisine", "batch_cooking", "inventaire"})
def obtenir_service_batch_inventaire_interaction() -> BatchInventaireInteractionService:
    """Factory pour le service Batch cooking → Inventaire."""
    return BatchInventaireInteractionService()
