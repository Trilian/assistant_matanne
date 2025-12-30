"""
Service Courses ULTRA-OPTIMISÉ v2.0
Utilise 100% EnhancedCRUDService + unified helpers
"""
from typing import List, Dict, Optional
from datetime import datetime, timedelta

from src.services.base_service_optimized import BaseServiceOptimized
from src.services.service_mixins import (
    StatusTrackingMixin,
    IngredientManagementMixin,
    PriorityManagementMixin,
    ExportImportMixin
)
from src.core.models import ArticleCourses, ArticleInventaire
from src.core.database import get_db_context
from src.core.cache import Cache
from src.core.errors import handle_errors
import logging

logger = logging.getLogger(__name__)

# Constantes
MAGASINS_CONFIG = {
    "Grand Frais": {
        "rayons": ["Fruits & Légumes", "Boucherie", "Poissonnerie", "Fromage"],
        "couleur": "#4CAF50",
    },
    "Thiriet": {
        "rayons": ["Entrées", "Poissons", "Viandes", "Plats Cuisinés"],
        "couleur": "#2196F3",
    },
    "Cora": {
        "rayons": ["Fruits & Légumes", "Boucherie", "Poissonnerie", "Crèmerie"],
        "couleur": "#FF5722",
    },
}


class CoursesService(
    BaseServiceOptimized[ArticleCourses],
    StatusTrackingMixin,
    IngredientManagementMixin,
    PriorityManagementMixin,
    ExportImportMixin
):
    """
    Service Courses Ultra-Optimisé

    Fonctionnalités héritées automatiquement:
    - CRUD complet (BaseServiceOptimized)
    - Gestion statuts (StatusTrackingMixin)
    - Gestion ingrédients (IngredientManagementMixin)
    - Gestion priorités (PriorityManagementMixin)
    - Export/Import (ExportImportMixin)
    """

    def __init__(self):
        super().__init__(ArticleCourses, cache_ttl=30)

    # ═══════════════════════════════════════════════════════════
    # MÉTHODES SPÉCIFIQUES COURSES
    # ═══════════════════════════════════════════════════════════

    @Cache.cached(ttl=30)
    @handle_errors(show_in_ui=False, fallback_value=[])
    def get_liste_active(self, filters: Optional[Dict] = None) -> List[Dict]:
        """
        Liste active enrichie

        ✅ Cache 30s
        ✅ Enrichissement automatique via mixin
        """
        items = self.advanced_search(
            filters={**filters, "achete": False} if filters else {"achete": False},
            sort_by="priorite",
            sort_desc=True,
            limit=1000
        )

        # ✅ Utilise le mixin pour enrichir (ZÉRO duplication)
        return self.enrich_with_ingredient_info(items, "ingredient_id")

    @handle_errors(show_in_ui=True)
    def ajouter(
            self,
            nom: str,
            quantite: float,
            unite: str,
            priorite: str = "moyenne",
            **kwargs
    ) -> int:
        """
        Ajoute article avec fusion intelligente

        ✅ Utilise mixin pour ingrédient
        ✅ Utilise bulk_create_with_merge pour fusion
        """
        with get_db_context() as db:
            # ✅ Mixin gère l'ingrédient
            ingredient_id = self.find_or_create_ingredient(nom, unite, db=db)

            # ✅ Stratégie fusion (réutilisable)
            def merge_strategy(existing: Dict, new: Dict) -> Dict:
                priorites = {"basse": 1, "moyenne": 2, "haute": 3}

                return {
                    **existing,
                    "quantite_necessaire": max(
                        existing.get("quantite_necessaire", 0),
                        new.get("quantite_necessaire", 0)
                    ),
                    "priorite": (
                        new["priorite"]
                        if priorites.get(new.get("priorite"), 2) >
                           priorites.get(existing.get("priorite"), 2)
                        else existing["priorite"]
                    )
                }

            # ✅ BaseServiceOptimized gère le bulk
            created, merged = self.bulk_create_with_merge(
                items_data=[{
                    "ingredient_id": ingredient_id,
                    "quantite_necessaire": quantite,
                    "priorite": priorite,
                    **kwargs
                }],
                merge_key="ingredient_id",
                merge_strategy=merge_strategy,
                db=db
            )

            # Retourner ID
            article = db.query(ArticleCourses).filter(
                ArticleCourses.ingredient_id == ingredient_id,
                ArticleCourses.achete == False
            ).first()

            return article.id if article else None

    @handle_errors(show_in_ui=True)
    def marquer_achete(
            self,
            article_id: int,
            ajouter_au_stock: bool = False
    ) -> bool:
        """
        Marque acheté + stock

        ✅ BaseServiceOptimized gère l'update
        """
        with get_db_context() as db:
            article = self.get_by_id(article_id, db)

            if not article:
                return False

            # Update article (méthode héritée)
            self.update(
                article_id,
                {"achete": True, "achete_le": datetime.now()},
                db=db
            )

            # Ajout stock si demandé
            if ajouter_au_stock:
                stock = db.query(ArticleInventaire).filter(
                    ArticleInventaire.ingredient_id == article.ingredient_id
                ).first()

                if stock:
                    stock.quantite += article.quantite_necessaire
                else:
                    stock = ArticleInventaire(
                        ingredient_id=article.ingredient_id,
                        quantite=article.quantite_necessaire,
                        quantite_min=1.0
                    )
                    db.add(stock)

                db.commit()

            return True

    def generer_depuis_stock_bas(self) -> List[Dict]:
        """Génère depuis stock bas"""
        from src.core.models import Ingredient

        with get_db_context() as db:
            items = db.query(
                Ingredient.nom,
                Ingredient.unite,
                ArticleInventaire.quantite,
                ArticleInventaire.quantite_min
            ).join(
                ArticleInventaire
            ).filter(
                ArticleInventaire.quantite < ArticleInventaire.quantite_min
            ).all()

            return [
                {
                    "nom": nom,
                    "quantite": max(seuil - qty, seuil),
                    "unite": unite,
                    "priorite": "haute"
                }
                for nom, unite, qty, seuil in items
            ]


# Instance globale
courses_service = CoursesService()