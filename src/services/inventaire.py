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
