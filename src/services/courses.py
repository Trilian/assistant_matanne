"""
Service Courses Unifié (REFACTORING PHASE 2)

✅ Utilise @with_db_session et @with_cache (Phase 1)
✅ Validation Pydantic centralisée
✅ Type hints complets pour meilleur IDE support
✅ Services testables sans Streamlit
"""

import logging
from typing import Any

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session, joinedload

from src.core.ai import obtenir_client_ia
from src.core.cache import Cache
from src.core.database import obtenir_contexte_db
from src.core.decorators import with_db_session, with_cache, with_error_handling
from src.core.models import ArticleCourses
from src.services.base_ai_service import BaseAIService
from src.services.types import BaseService

logger = logging.getLogger(__name__)

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
# SERVICE COURSES UNIFIÉ
# ═══════════════════════════════════════════════════════════


class CoursesService(BaseService[ArticleCourses], BaseAIService):
    """
    Service complet pour la liste de courses.

    ✅ Héritage BaseAIService (rate limiting + cache auto)

    Fonctionnalités:
    - CRUD optimisé avec cache
    - Liste de courses avec filtres
    - Suggestions IA basées sur inventaire
    - Gestion priorités et rayons magasin
    """

    def __init__(self):
        BaseService.__init__(self, ArticleCourses, cache_ttl=1800)
        BaseAIService.__init__(
            self,
            client=obtenir_client_ia(),
            cache_prefix="courses",
            default_ttl=1800,
            default_temperature=0.7,
            service_name="courses",
        )

    # ═══════════════════════════════════════════════════════════
    # SECTION 1: CRUD & LISTE COURSES (REFACTORED)
    # ═══════════════════════════════════════════════════════════

    @with_cache(
        ttl=1800,
        key_func=lambda self, achetes, priorite: f"courses_{achetes}_{priorite}",
    )
    @with_error_handling(default_return=[])
    @with_db_session
    def get_liste_courses(
        self,
        achetes: bool = False,
        priorite: str | None = None,
        db: Session | None = None,
    ) -> list[dict[str, Any]]:
        """Récupère la liste de courses.

        Gets the shopping list, optionally filtered by purchased status and priority.
        Results are cached for 30 minutes.

        Args:
            achetes: Include purchased items
            priorite: Filter by priority (haute, moyenne, basse)
            db: Database session (injected by @with_db_session)

        Returns:
            List of dicts with article data organized by store section
        """
        query = db.query(ArticleCourses).options(
            joinedload(ArticleCourses.ingredient)
        )

        if not achetes:
            query = query.filter(ArticleCourses.achete.is_(False))

        if priorite:
            query = query.filter(ArticleCourses.priorite == priorite)

        articles = query.order_by(ArticleCourses.rayon_magasin).all()

        result = []
        for article in articles:
            result.append(
                {
                    "id": article.id,
                    "ingredient_id": article.ingredient_id,
                    "ingredient_nom": article.ingredient.nom,
                    "quantite_necessaire": article.quantite_necessaire,
                    "unite": article.ingredient.unite,
                    "priorite": article.priorite,
                    "achete": article.achete,
                    "rayon_magasin": article.rayon_magasin,
                    "magasin_cible": article.magasin_cible,
                    "notes": article.notes,
                    "suggere_par_ia": article.suggere_par_ia,
                }
            )

        logger.info(
            f"✅ Retrieved shopping list: {len(result)} items "
            f"(priority={priorite or 'all'}, purchased={achetes})"
        )
        return result

    # ═══════════════════════════════════════════════════════════
    # SECTION 2: SUGGESTIONS IA (REFACTORED)
    # ═══════════════════════════════════════════════════════════

    @with_cache(ttl=3600, key_func=lambda self: "suggestions_courses_ia")
    @with_error_handling(default_return=[])
    def generer_suggestions_ia_depuis_inventaire(self) -> list[SuggestionCourses]:
        """Génère des suggestions de courses depuis l'inventaire via IA.

        Generates shopping suggestions based on inventory status using Mistral AI.
        Results cached for 1 hour.

        Returns:
            List of SuggestionCourses objects, empty list on error
        """
        from .inventaire import inventaire_service

        logger.info("🤖 Generating shopping suggestions from inventory with AI")

        # Récupérer état inventaire
        inventaire = inventaire_service.get_inventaire_complet()

        # Utiliser le Mixin d'inventaire pour contexte
        context = inventaire_service.build_inventory_summary(inventaire)

        # Construire prompt
        prompt = self.build_json_prompt(
            context=context,
            task="Suggest 15 priority shopping items",
            json_schema='[{"nom": str, "quantite": float, "unite": str, "priorite": str, "rayon": str}]',
            constraints=[
                "Priority: haute/moyenne/basse",
                "Focus on critical items first",
                "Realistic quantities",
                "Organize by store section",
                "Budget-aware",
            ],
        )

        # Appel IA avec auto rate limiting & parsing
        suggestions = self.call_with_list_parsing(
            prompt=prompt,
            item_model=SuggestionCourses,
            system_prompt=self.build_system_prompt(
                role="Smart shopping assistant",
                expertise=[
                    "Stock management",
                    "Inventory optimization",
                    "Shopping organization",
                    "Budget management",
                ],
                rules=[
                    "Suggest critical items first",
                    "Group by store section",
                    "Minimize shopping trips",
                    "Quality and value balance",
                ],
            ),
            max_items=15,
        )

        logger.info(f"✅ Generated {len(suggestions)} shopping suggestions")
        return suggestions


# Lazy loading of singleton instance for tests
_courses_service = None

def get_courses_service() -> CoursesService:
    """Get or create the global CoursesService instance."""
    global _courses_service
    if _courses_service is None:
        _courses_service = CoursesService()
    return _courses_service

# Backward compatibility
courses_service = None

__all__ = ["CoursesService", "courses_service", "get_courses_service"]
