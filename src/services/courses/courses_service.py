"""
Service Courses ULTRA-OPTIMISÉ v2.0
Utilise 100% EnhancedCRUDService + unified helpers
"""
from typing import List, Dict, Optional
from datetime import datetime, timedelta

from src.services.base_enhanced_service import EnhancedCRUDService, StatusTrackingMixin
from src.services.unified_service_helpers import (
    find_or_create_ingredient,
    enrich_with_ingredient_info,
    batch_find_or_create_ingredients
)
from src.core.cache import Cache
from src.core.errors import handle_errors, ValidationError
from src.core.models import ArticleCourses
import logging

logger = logging.getLogger(__name__)

# Constantes
MAGASINS_CONFIG = {
    "Grand Frais": {
        "rayons": ["Fruits & Légumes", "Boucherie", "Poissonnerie", "Fromage", "Traiteur", "Boulangerie", "Epicerie"],
        "couleur": "#4CAF50",
    },
    "Thiriet": {
        "rayons": ["Entrées", "Poissons", "Viandes", "Plats Cuisinés", "Légumes", "Desserts", "Pain"],
        "couleur": "#2196F3",
    },
    "Cora": {
        "rayons": ["Fruits & Légumes", "Boucherie", "Poissonnerie", "Crèmerie", "Epicerie", "Surgelés", "Boissons"],
        "couleur": "#FF5722",
    },
}


class CoursesService(EnhancedCRUDService[ArticleCourses], StatusTrackingMixin):
    """Service courses optimisé - utilise 100% la base"""

    def __init__(self):
        super().__init__(ArticleCourses)

    # ═══════════════════════════════════════════════════════════════
    # LECTURE (Cache + EnhancedCRUD)
    # ═══════════════════════════════════════════════════════════════

    @Cache.cached(ttl=30)
    @handle_errors(show_in_ui=False)
    def get_liste_active(self, filters: Optional[Dict] = None) -> List[Dict]:
        """Liste active avec enrichissement - Cache 30s"""
        items = self.advanced_search(
            filters={**filters, "achete": False} if filters else {"achete": False},
            sort_by="priorite",
            sort_desc=True,
            limit=1000
        )
        return enrich_with_ingredient_info(items, "ingredient_id")

    @handle_errors(show_in_ui=False)
    def get_organisation_par_rayons(self, magasin: str) -> Dict[str, List[Dict]]:
        """Organise par rayons (1 lecture)"""
        items = self.get_liste_active()
        rayons = MAGASINS_CONFIG.get(magasin, {}).get("rayons", ["Autre"])

        organisation = {rayon: [] for rayon in rayons}
        organisation["Autre"] = []

        for item in items:
            rayon = item.get("rayon_magasin") or "Autre"
            organisation.get(rayon, organisation["Autre"]).append(item)

        return {k: v for k, v in organisation.items() if v}

    # ═══════════════════════════════════════════════════════════════
    # CRÉATION (bulk_create_with_merge)
    # ═══════════════════════════════════════════════════════════════

    @handle_errors(show_in_ui=True)
    def ajouter(self, nom: str, quantite: float, unite: str,
                priorite: str = "moyenne", **kwargs) -> int:
        """Ajoute avec fusion intelligente"""

        ingredient_id = find_or_create_ingredient(nom, unite)

        # Stratégie fusion : max quantité + max priorité
        def merge_strategy(existing: Dict, new: Dict) -> Dict:
            priorites = {"basse": 1, "moyenne": 2, "haute": 3}
            return {
                **existing,
                "quantite_necessaire": max(
                    existing.get("quantite_necessaire", 0),
                    new.get("quantite_necessaire", 0)
                ),
                "priorite": (
                    new["priorite"] if priorites.get(new.get("priorite"), 2) >
                                       priorites.get(existing.get("priorite"), 2) else existing["priorite"]
                )
            }

        created, merged = self.bulk_create_with_merge(
            items_data=[{
                "ingredient_id": ingredient_id,
                "quantite_necessaire": quantite,
                "priorite": priorite,
                "suggere_par_ia": kwargs.get("ia_suggere", False),
                "rayon_magasin": kwargs.get("rayon"),
                "magasin_cible": kwargs.get("magasin"),
                "notes": kwargs.get("notes"),
                "achete": False
            }],
            merge_key="ingredient_id",
            merge_strategy=merge_strategy
        )

        Cache.invalidate("courses")

        # Retourner ID
        from src.core.database import get_db_context
        with get_db_context() as db:
            article = db.query(ArticleCourses).filter(
                ArticleCourses.ingredient_id == ingredient_id,
                ArticleCourses.achete == False
            ).first()
            return article.id if article else None

    @handle_errors(show_in_ui=True)
    def ajouter_batch(self, articles: List[Dict]) -> int:
        """Ajout batch optimisé"""
        from src.core.database import get_db_context

        with get_db_context() as db:
            # Batch ingrédients (1 query)
            ing_map = batch_find_or_create_ingredients(
                [{"nom": a["nom"], "unite": a["unite"]} for a in articles],
                db=db
            )

            items_data = [
                {
                    "ingredient_id": ing_map[art["nom"]],
                    "quantite_necessaire": art["quantite"],
                    "priorite": art.get("priorite", "moyenne"),
                    "suggere_par_ia": art.get("ia", False),
                    "rayon_magasin": art.get("rayon"),
                    "magasin_cible": art.get("magasin"),
                    "achete": False
                }
                for art in articles
            ]

            def merge_strategy(existing: Dict, new: Dict) -> Dict:
                priorites = {"basse": 1, "moyenne": 2, "haute": 3}
                return {
                    **existing,
                    "quantite_necessaire": max(
                        existing.get("quantite_necessaire", 0),
                        new.get("quantite_necessaire", 0)
                    ),
                    "priorite": (
                        new["priorite"] if priorites.get(new.get("priorite"), 2) >
                                           priorites.get(existing.get("priorite"), 2) else existing["priorite"]
                    )
                }

            created, merged = self.bulk_create_with_merge(
                items_data=items_data,
                merge_key="ingredient_id",
                merge_strategy=merge_strategy,
                db=db
            )

            Cache.invalidate("courses")
            return created + merged

    # ═══════════════════════════════════════════════════════════════
    # ACHAT (StatusTrackingMixin)
    # ═══════════════════════════════════════════════════════════════

    @handle_errors(show_in_ui=True)
    def marquer_achete(self, article_id: int, ajouter_au_stock: bool = False) -> bool:
        """Marque acheté + stock"""
        from src.core.database import get_db_context
        from src.core.models import ArticleInventaire

        with get_db_context() as db:
            article = self.get_by_id(article_id, db)
            if not article:
                return False

            # Update article (utilise StatusTrackingMixin)
            self.mark_as(article_id, "achete", True, db=db)
            self.update(article_id, {"achete_le": datetime.now()}, db=db)

            # Ajout stock
            if ajouter_au_stock:
                stock = db.query(ArticleInventaire).filter(
                    ArticleInventaire.ingredient_id == article.ingredient_id
                ).first()

                if stock:
                    stock.quantite += article.quantite_necessaire
                    stock.derniere_maj = datetime.now()
                else:
                    stock = ArticleInventaire(
                        ingredient_id=article.ingredient_id,
                        quantite=article.quantite_necessaire,
                        quantite_min=1.0
                    )
                    db.add(stock)

                db.commit()

            Cache.invalidate("courses")
            return True

    # ═══════════════════════════════════════════════════════════════
    # STATS (get_generic_stats)
    # ═══════════════════════════════════════════════════════════════

    @Cache.cached(ttl=60)
    @handle_errors(show_in_ui=False)
    def get_stats(self, jours: int = 30) -> Dict:
        """Stats complètes (cache 1min)"""
        liste = self.get_liste_active()

        stats = {
            "total_actifs": len(liste),
            "prioritaires": len([i for i in liste if i.get("priorite") == "haute"]),
            "part_ia": len([i for i in liste if i.get("suggere_par_ia")]),
        }

        # Utilise get_generic_stats de la base
        generic_stats = self.get_generic_stats(
            count_filters={"achetes": {"achete": True}},
            date_field="cree_le",
            days_back=jours
        )

        stats["total_achetes"] = generic_stats.get("achetes", 0)
        stats["moyenne_semaine"] = stats["total_achetes"] / max(jours // 7, 1)

        return stats

    # ═══════════════════════════════════════════════════════════════
    # GÉNÉRATION AUTOMATIQUE
    # ═══════════════════════════════════════════════════════════════

    def generer_depuis_stock_bas(self) -> List[Dict]:
        """Génère depuis stock bas"""
        from src.core.database import get_db_context
        from src.core.models import Ingredient, ArticleInventaire

        with get_db_context() as db:
            items = db.query(
                Ingredient.nom, Ingredient.unite,
                ArticleInventaire.quantite, ArticleInventaire.quantite_min
            ).join(
                ArticleInventaire, Ingredient.id == ArticleInventaire.ingredient_id
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

    def generer_depuis_repas_planifies(self, jours: int = 7) -> List[Dict]:
        """Génère depuis planning"""
        from src.core.models import Recette, RepasPlanning, RecetteIngredient, Ingredient, ArticleInventaire
        from src.core.database import get_db_context

        with get_db_context() as db:
            today = datetime.now().date()
            date_fin = today + timedelta(days=jours)

            repas = db.query(Recette.id).join(
                RepasPlanning, Recette.id == RepasPlanning.recette_id
            ).filter(
                RepasPlanning.date.between(today, date_fin),
                RepasPlanning.statut != "terminé"
            ).all()

            consolidated = {}
            for (recette_id,) in repas:
                ingredients = db.query(
                    Ingredient.nom, RecetteIngredient.quantite, Ingredient.unite
                ).join(
                    RecetteIngredient, Ingredient.id == RecetteIngredient.ingredient_id
                ).filter(RecetteIngredient.recette_id == recette_id).all()

                for nom, qty, unite in ingredients:
                    stock = db.query(ArticleInventaire).join(Ingredient).filter(
                        Ingredient.nom == nom
                    ).first()

                    manque = max(qty - (stock.quantite if stock else 0), 0)
                    if manque > 0:
                        key = f"{nom}_{unite}"
                        if key in consolidated:
                            consolidated[key]["quantite"] += manque
                        else:
                            consolidated[key] = {
                                "nom": nom, "quantite": manque,
                                "unite": unite, "priorite": "moyenne"
                            }

            return list(consolidated.values())

    def nettoyer_achetes(self, jours: int = 7) -> int:
        """Nettoie achats anciens (auto_cleanup)"""
        result = self.auto_cleanup(
            date_field="achete_le",
            days_old=jours,
            additional_filters={"achete": True}
        )
        Cache.invalidate("courses")
        return result["count"]


# Instance globale
courses_service = CoursesService()