"""
Service inter-modules : Inventaire péremption → Suggestions recettes.

Produits expirant sous 48h → proposer automatiquement
des recettes les utilisant pour éviter le gaspillage.
"""

import logging
from datetime import date, timedelta
from typing import Any

from sqlalchemy.orm import Session

from src.core.decorators import avec_gestion_erreurs, avec_session_db
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


class PeremptionRecettesInteractionService:
    """Service inter-modules Inventaire péremption → Recettes suggestions."""

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def suggerer_recettes_peremption(
        self,
        *,
        jours_seuil: int = 2,
        limite: int = 5,
        db: Session | None = None,
    ) -> dict[str, Any]:
        """Récupère les produits expirant bientôt et suggère des recettes.

        Args:
            jours_seuil: nombre de jours avant péremption (défaut: 2)
            limite: nombre max de recettes à suggérer
            db: Session DB (injectée par @avec_session_db)

        Returns:
            Dict avec produits_expirants, recettes_suggerees, message
        """
        from src.core.models import ArticleInventaire

        if db is None:
            return {
                "produits_expirants": [],
                "recettes_suggerees": [],
                "message": "Base indisponible.",
            }

        aujourd_hui = date.today()
        seuil = aujourd_hui + timedelta(days=jours_seuil)

        # Produits expirant bientôt
        expirants = (
            db.query(ArticleInventaire)
            .filter(
                ArticleInventaire.date_peremption.isnot(None),
                ArticleInventaire.date_peremption <= seuil,
                ArticleInventaire.date_peremption >= aujourd_hui,
                ArticleInventaire.quantite > 0,
            )
            .all()
        )

        if not expirants:
            return {
                "produits_expirants": [],
                "recettes_suggerees": [],
                "message": "Aucun produit n'expire dans les prochains jours.",
            }

        noms_expirants = [a.nom.lower() for a in expirants]
        produits_info = [
            {
                "nom": a.nom,
                "quantite": a.quantite,
                "unite": getattr(a, "unite", ""),
                "date_peremption": a.date_peremption.isoformat() if a.date_peremption else None,
                "jours_restants": (a.date_peremption - aujourd_hui).days
                if a.date_peremption
                else None,
            }
            for a in expirants
        ]

        # Chercher des recettes contenant ces ingrédients
        recettes_trouvees = self._chercher_recettes_par_ingredients(db, noms_expirants, limite)

        # Si pas assez de recettes en base, tenter l'IA
        if len(recettes_trouvees) < limite:
            recettes_ia = self._suggerer_via_ia(noms_expirants, limite - len(recettes_trouvees))
            recettes_trouvees.extend(recettes_ia)

        message = (
            f"{len(expirants)} produit(s) expirent sous {jours_seuil} jour(s). "
            f"{len(recettes_trouvees)} recette(s) suggérée(s) pour les utiliser."
        )

        logger.info(f"✅ Péremption→Recettes: {message}")

        return {
            "produits_expirants": produits_info,
            "recettes_suggerees": recettes_trouvees,
            "message": message,
        }

    def _chercher_recettes_par_ingredients(
        self,
        db: Session,
        noms_ingredients: list[str],
        limite: int,
    ) -> list[dict[str, Any]]:
        """Cherche en base des recettes contenant les ingrédients expirants."""
        from sqlalchemy import func

        from src.core.models import Recette
        from src.core.models.recettes import Ingredient, RecetteIngredient

        if not noms_ingredients:
            return []

        try:
            recettes = (
                db.query(Recette)
                .join(RecetteIngredient, RecetteIngredient.recette_id == Recette.id)
                .join(Ingredient, Ingredient.id == RecetteIngredient.ingredient_id)
                .filter(func.lower(Ingredient.nom).in_(noms_ingredients[:10]))
                .group_by(Recette.id)
                .order_by(func.count(RecetteIngredient.ingredient_id).desc())
                .limit(limite)
                .all()
            )
            return [
                {
                    "id": r.id,
                    "nom": r.nom,
                    "source": "base_de_donnees",
                    "temps_preparation": getattr(r, "temps_preparation", None),
                    "difficulte": getattr(r, "difficulte", None),
                }
                for r in recettes
            ]
        except Exception as e:
            logger.warning(f"Recherche recettes par ingrédients échouée: {e}")
            return []

    def _suggerer_via_ia(self, noms_ingredients: list[str], limite: int) -> list[dict[str, Any]]:
        """Utilise l'IA pour suggérer des recettes avec les ingrédients expirants."""
        try:
            from src.services.utilitaires.chat.chat_ai import obtenir_chat_ai_service

            chat = obtenir_chat_ai_service()
            ingredients_str = ", ".join(noms_ingredients[:10])
            prompt = (
                f"Ces ingrédients expirent bientôt : {ingredients_str}. "
                f"Propose {limite} idée(s) de recettes simples et rapides "
                f"pour les utiliser. Pour chaque recette, donne juste le nom "
                f"et le temps de préparation estimé."
            )
            reponse = chat.envoyer_message(prompt, contexte="cuisine")
            if reponse:
                return [
                    {
                        "nom": reponse[:200],
                        "source": "ia",
                        "suggestion_texte": reponse,
                    }
                ]
        except Exception as e:
            logger.warning(f"Suggestion IA anti-gaspi échouée: {e}")
        return []


@service_factory("peremption_recettes_interaction", tags={"cuisine", "inventaire", "anti_gaspi"})
def obtenir_service_peremption_recettes() -> PeremptionRecettesInteractionService:
    """Factory pour le service Péremption → Recettes."""
    return PeremptionRecettesInteractionService()
