"""
Service Inventaire Unifié (REFACTORING PHASE 2)

✅ Utilise @with_db_session et @with_cache (Phase 1)
✅ Validation Pydantic centralisée
✅ Type hints complets pour meilleur IDE support
✅ Services testables sans Streamlit
"""

import logging
from datetime import date
from typing import Any

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session, joinedload

from src.core.ai import obtenir_client_ia
from src.core.cache import Cache
from src.core.database import obtenir_contexte_db
from src.core.decorators import with_db_session, with_cache, with_error_handling
from src.core.errors_base import ErreurValidation
from src.core.models import ArticleInventaire
from src.services.base_ai_service import BaseAIService, InventoryAIMixin
from src.services.types import BaseService

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════

CATEGORIES = [
    "Légumes",
    "Fruits",
    "Féculents",
    "Protéines",
    "Laitier",
    "Épices & Condiments",
    "Conserves",
    "Surgelés",
    "Autre",
]

EMPLACEMENTS = ["Frigo", "Congélateur", "Placard", "Cave", "Garde-manger"]

# ═══════════════════════════════════════════════════════════
# SCHÉMAS PYDANTIC
# ═══════════════════════════════════════════════════════════

class SuggestionCourses(BaseModel):
    """Shopping suggestion from IA"""
    nom: str = Field(..., min_length=2)
    quantite: float = Field(..., gt=0)
    unite: str = Field(..., min_length=1)
    priorite: str = Field(..., pattern="^(haute|moyenne|basse)$")
    rayon: str = Field(..., min_length=3)


# ═══════════════════════════════════════════════════════════
# SERVICE INVENTAIRE UNIFIÉ
# ═══════════════════════════════════════════════════════════


class InventaireService(BaseService[ArticleInventaire], BaseAIService, InventoryAIMixin):
    """
    Service complet pour l'inventaire.

    ✅ Héritage multiple :
    - BaseService → CRUD optimisé
    - BaseAIService → IA avec rate limiting auto
    - InventoryAIMixin → Contextes métier inventaire

    Fonctionnalités:
    - CRUD optimisé avec cache
    - Alertes stock et péremption
    - Suggestions IA pour courses
    """

    def __init__(self):
        BaseService.__init__(self, ArticleInventaire, cache_ttl=1800)
        BaseAIService.__init__(
            self,
            client=obtenir_client_ia(),
            cache_prefix="inventaire",
            default_ttl=1800,
            default_temperature=0.7,
            service_name="inventaire",
        )

    # ═══════════════════════════════════════════════════════════
    # SECTION 1: CRUD & INVENTAIRE (REFACTORED)
    # ═══════════════════════════════════════════════════════════

    @with_cache(
        ttl=1800,
        key_func=lambda self, emplacement, categorie, include_ok: (
            f"inventaire_{emplacement}_{categorie}_{include_ok}"
        ),
    )
    @with_error_handling(default_return=[])
    @with_db_session
    def get_inventaire_complet(
        self,
        emplacement: str | None = None,
        categorie: str | None = None,
        include_ok: bool = True,
        db: Session | None = None,
    ) -> list[dict[str, Any]]:
        """Récupère l'inventaire complet avec statuts calculés.

        Retrieves complete inventory with calculated statuses.
        Results are cached for 30 minutes.

        Args:
            emplacement: Optional location filter (Frigo, Congélateur, etc.)
            categorie: Optional category filter
            include_ok: Include items with OK status
            db: Database session (injected by @with_db_session)

        Returns:
            List of dict with article data and calculated status
        """
        query = db.query(ArticleInventaire).options(
            joinedload(ArticleInventaire.ingredient)
        )

        if emplacement:
            query = query.filter(ArticleInventaire.emplacement == emplacement)

        articles = query.all()

        result = []
        today = date.today()

        for article in articles:
            statut = self._calculer_statut(article, today)

            if not include_ok and statut == "ok":
                continue

            if categorie and article.ingredient.categorie != categorie:
                continue

            result.append(
                {
                    "id": article.id,
                    "ingredient_id": article.ingredient_id,
                    "ingredient_nom": article.ingredient.nom,
                    "ingredient_categorie": article.ingredient.categorie,
                    "quantite": article.quantite,
                    "quantite_min": article.quantite_min,
                    "unite": article.ingredient.unite,
                    "emplacement": article.emplacement,
                    "date_peremption": article.date_peremption,
                    "statut": statut,
                    "jours_avant_peremption": self._jours_avant_peremption(article, today),
                }
            )

        logger.info(f"✅ Retrieved complete inventory: {len(result)} items")
        return result

    @with_error_handling(default_return={})
    def get_alertes(self) -> dict[str, list[dict[str, Any]]]:
        """Récupère toutes les alertes d'inventaire.

        Gets all inventory alerts grouped by type.

        Returns:
            Dict with keys: stock_bas, critique, peremption_proche
        """
        inventaire = self.get_inventaire_complet(include_ok=False)

        alertes = {
            "stock_bas": [],
            "critique": [],
            "peremption_proche": [],
        }

        for article in inventaire:
            statut = article["statut"]
            if statut in alertes:
                alertes[statut].append(article)

        logger.info(f"⚠️ Inventory alerts: {sum(len(v) for v in alertes.values())} items")
        return alertes

    # ═══════════════════════════════════════════════════════════
    # SECTION 2: SUGGESTIONS IA (REFACTORED)
    # ═══════════════════════════════════════════════════════════

    @with_cache(ttl=3600, key_func=lambda self: "suggestions_courses_ia")
    @with_error_handling(default_return=[])
    def suggerer_courses_ia(self) -> list[SuggestionCourses]:
        """Suggère des articles à ajouter aux courses via IA.

        Uses Mistral AI to suggest shopping items based on inventory status.
        Results cached for 1 hour.

        Returns:
            List of SuggestionCourses objects, empty list on error
        """
        # Récupérer alertes et contexte
        alertes = self.get_alertes()
        inventaire = self.get_inventaire_complet()

        # Utilisation du Mixin pour résumé inventaire
        context = self.build_inventory_summary(inventaire)

        # Construire prompt
        prompt = self.build_json_prompt(
            context=context,
            task="Suggest 15 priority items to buy",
            json_schema='[{"nom": str, "quantite": float, "unite": str, "priorite": str, "rayon": str}]',
            constraints=[
                "Priority: haute/moyenne/basse",
                "Store sections for organization",
                "Realistic quantities",
                "Focus on critical items first",
                "Respect budget constraints",
            ],
        )

        logger.info("🤖 Generating shopping suggestions with AI")

        # Appel IA avec auto rate limiting & parsing
        suggestions = self.call_with_list_parsing_sync(
            prompt=prompt,
            item_model=SuggestionCourses,
            system_prompt=self.build_system_prompt(
                role="Smart shopping assistant",
                expertise=[
                    "Stock management",
                    "Inventory optimization",
                    "Budget-aware purchasing",
                    "Seasonal availability",
                ],
                rules=[
                    "Prioritize critical items",
                    "Suggest realistic quantities",
                    "Consider seasonal items",
                    "Group by store section",
                ],
            ),
            max_items=15,
        )

        logger.info(f"✅ Generated {len(suggestions)} shopping suggestions")
        return suggestions

    # ═══════════════════════════════════════════════════════════
    # SECTION 3: HELPERS PRIVÉS (REFACTORED)
    # ═══════════════════════════════════════════════════════════

    def _calculer_statut(self, article: ArticleInventaire, today: date) -> str:
        """Calcule le statut d'un article.
        
        Args:
            article: ArticleInventaire object
            today: Current date for calculations
            
        Returns:
            Status string: 'critique', 'stock_bas', 'peremption_proche', or 'ok'
        """
        if article.date_peremption:
            days_left = (article.date_peremption - today).days
            if days_left <= 7:
                return "peremption_proche"

        if article.quantite < (article.quantite_min * 0.5):
            return "critique"

        if article.quantite < article.quantite_min:
            return "stock_bas"

        return "ok"

    def _jours_avant_peremption(
        self, article: ArticleInventaire, today: date
    ) -> int | None:
        """Calcule jours avant péremption.
        
        Args:
            article: ArticleInventaire object
            today: Current date
            
        Returns:
            Days until expiration or None if no expiration date
        """
        if not article.date_peremption:
            return None
        return (article.date_peremption - today).days

    # ═══════════════════════════════════════════════════════════
    # SECTION 4: GESTION ARTICLES (CREATE/UPDATE/DELETE)
    # ═══════════════════════════════════════════════════════════

    @with_error_handling(default_return=None)
    @with_db_session
    def ajouter_article(
        self,
        ingredient_nom: str,
        quantite: float,
        quantite_min: float = 1.0,
        emplacement: str | None = None,
        date_peremption: date | None = None,
        db: Session | None = None,
    ) -> dict[str, Any] | None:
        """Ajoute un article à l'inventaire.

        Args:
            ingredient_nom: Nom de l'ingrédient
            quantite: Quantité en stock
            quantite_min: Quantité minimum
            emplacement: Lieu de stockage
            date_peremption: Date de péremption
            db: Database session (injected)

        Returns:
            Dict with new article data or None on error
        """
        from src.core.models import Ingredient

        # Trouver ou créer l'ingrédient
        ingredient = db.query(Ingredient).filter(
            Ingredient.nom.ilike(ingredient_nom)
        ).first()

        if not ingredient:
            logger.warning(f"⚠️ Ingrédient '{ingredient_nom}' non trouvé")
            return None

        # Vérifier si existe déjà
        existing = db.query(ArticleInventaire).filter(
            ArticleInventaire.ingredient_id == ingredient.id
        ).first()

        if existing:
            logger.warning(f"⚠️ Article '{ingredient_nom}' existe déjà")
            return None

        # Créer l'article
        article = ArticleInventaire(
            ingredient_id=ingredient.id,
            quantite=quantite,
            quantite_min=quantite_min,
            emplacement=emplacement,
            date_peremption=date_peremption,
        )

        db.add(article)
        db.commit()

        logger.info(f"✅ Article '{ingredient_nom}' ajouté à l'inventaire")
        self.invalidate_cache()

        return {
            "id": article.id,
            "ingredient_nom": ingredient.nom,
            "quantite": quantite,
            "quantite_min": quantite_min,
            "emplacement": emplacement,
            "date_peremption": date_peremption,
        }

    @with_error_handling(default_return=False)
    @with_db_session
    def mettre_a_jour_article(
        self,
        article_id: int,
        quantite: float | None = None,
        quantite_min: float | None = None,
        emplacement: str | None = None,
        date_peremption: date | None = None,
        db: Session | None = None,
    ) -> bool:
        """Met à jour un article de l'inventaire.

        Args:
            article_id: ID de l'article
            quantite: Nouvelle quantité (optionnel)
            quantite_min: Nouveau seuil minimum (optionnel)
            emplacement: Nouvel emplacement (optionnel)
            date_peremption: Nouvelle date de péremption (optionnel)
            db: Database session (injected)

        Returns:
            True if updated, False otherwise
        """
        article = db.query(ArticleInventaire).filter(
            ArticleInventaire.id == article_id
        ).first()

        if not article:
            logger.warning(f"⚠️ Article #{article_id} non trouvé")
            return False

        if quantite is not None:
            article.quantite = quantite
        if quantite_min is not None:
            article.quantite_min = quantite_min
        if emplacement is not None:
            article.emplacement = emplacement
        if date_peremption is not None:
            article.date_peremption = date_peremption

        db.commit()
        logger.info(f"✅ Article #{article_id} mis à jour")
        self.invalidate_cache()

        return True

    @with_error_handling(default_return=False)
    @with_db_session
    def supprimer_article(self, article_id: int, db: Session | None = None) -> bool:
        """Supprime un article de l'inventaire.

        Args:
            article_id: ID de l'article
            db: Database session (injected)

        Returns:
            True if deleted, False otherwise
        """
        article = db.query(ArticleInventaire).filter(
            ArticleInventaire.id == article_id
        ).first()

        if not article:
            logger.warning(f"⚠️ Article #{article_id} non trouvé")
            return False

        db.delete(article)
        db.commit()

        logger.info(f"✅ Article #{article_id} supprimé")
        self.invalidate_cache()

        return True

    # ═══════════════════════════════════════════════════════════
    # SECTION 5: STATISTIQUES & RAPPORTS
    # ═══════════════════════════════════════════════════════════

    @with_error_handling(default_return={})
    def get_statistiques(self) -> dict[str, Any]:
        """Récupère statistiques complètes de l'inventaire.

        Returns:
            Dict with statistics and insights
        """
        inventaire = self.get_inventaire_complet()
        alertes = self.get_alertes()

        if not inventaire:
            return {"total_articles": 0}

        return {
            "total_articles": len(inventaire),
            "total_quantite": sum(a["quantite"] for a in inventaire),
            "emplacements": len(set(a["emplacement"] for a in inventaire if a["emplacement"])),
            "categories": len(set(a["ingredient_categorie"] for a in inventaire)),
            "alertes_totales": sum(len(v) for v in alertes.values()),
            "articles_critiques": len(alertes.get("critique", [])),
            "articles_stock_bas": len(alertes.get("stock_bas", [])),
            "articles_peremption": len(alertes.get("peremption_proche", [])),
            "derniere_maj": max((a.get("derniere_maj") for a in inventaire), default=None),
        }

    @with_error_handling(default_return={})
    def get_stats_par_categorie(self) -> dict[str, dict[str, Any]]:
        """Récupère statistiques par catégorie.

        Returns:
            Dict with per-category statistics
        """
        inventaire = self.get_inventaire_complet()

        categories = {}
        for article in inventaire:
            cat = article["ingredient_categorie"]
            if cat not in categories:
                categories[cat] = {
                    "articles": 0,
                    "quantite_totale": 0,
                    "seuil_moyen": 0,
                    "critiques": 0,
                }

            categories[cat]["articles"] += 1
            categories[cat]["quantite_totale"] += article["quantite"]
            categories[cat]["seuil_moyen"] += article["quantite_min"]
            if article["statut"] == "critique":
                categories[cat]["critiques"] += 1

        # Calculer moyenne des seuils
        for cat in categories:
            if categories[cat]["articles"] > 0:
                categories[cat]["seuil_moyen"] /= categories[cat]["articles"]

        logger.info(f"📊 Statistics for {len(categories)} categories")
        return categories

    @with_error_handling(default_return=[])
    def get_articles_a_prelever(self, date_limite: date | None = None) -> list[dict[str, Any]]:
        """Récupère articles à utiliser en priorité.

        Args:
            date_limite: Date limite de péremption (par défaut aujourd'hui + 3 jours)

        Returns:
            List of articles to use first (FIFO)
        """
        from datetime import timedelta

        if date_limite is None:
            date_limite = date.today() + timedelta(days=3)

        inventaire = self.get_inventaire_complet()

        a_prelever = [
            a for a in inventaire
            if a["date_peremption"] and a["date_peremption"] <= date_limite
        ]

        # Trier par date de péremption (plus ancien d'abord)
        a_prelever.sort(key=lambda x: x["date_peremption"])

        logger.info(f"🔄 {len(a_prelever)} articles to use first")
        return a_prelever


# ═══════════════════════════════════════════════════════════
# INSTANCE SINGLETON - LAZY LOADING
# ═══════════════════════════════════════════════════════════

_inventaire_service = None

def get_inventaire_service() -> InventaireService:
    """Get or create the global InventaireService instance."""
    global _inventaire_service
    if _inventaire_service is None:
        _inventaire_service = InventaireService()
    return _inventaire_service

inventaire_service = None

__all__ = ["InventaireService", "inventaire_service", "CATEGORIES", "EMPLACEMENTS", "get_inventaire_service"]
