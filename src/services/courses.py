"""
Service Courses Unifié (REFACTORING v2.2 - PRO)

✅ Héritage de BaseAIService (rate limiting + cache auto)
✅ Fix: Import RateLimitIA depuis src.core.ai
"""

import logging

from sqlalchemy.orm import joinedload

from src.core.ai import obtenir_client_ia
from src.core.cache import Cache
from src.core.database import obtenir_contexte_db
from src.core.errors import gerer_erreurs
from src.core.models import ArticleCourses
from src.services.base_ai_service import BaseAIService
from src.services.types import BaseService

logger = logging.getLogger(__name__)


class CoursesService(BaseService[ArticleCourses], BaseAIService):
    """
    Service complet pour la liste de courses.

    ✅ Héritage BaseAIService (rate limiting + cache auto)
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

    @gerer_erreurs(afficher_dans_ui=False, valeur_fallback=[])
    def get_liste_courses(self, achetes: bool = False, priorite: str | None = None) -> list[dict]:
        """Récupère la liste de courses."""
        cache_key = f"courses_{achetes}_{priorite}"
        cached = Cache.obtenir(cache_key, ttl=self.cache_ttl)
        if cached:
            return cached

        with obtenir_contexte_db() as db:
            query = db.query(ArticleCourses).options(joinedload(ArticleCourses.ingredient))

            if not achetes:
                query = query.filter(ArticleCourses.achete == False)

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

            Cache.definir(cache_key, result, ttl=self.cache_ttl, dependencies=["courses"])
            return result

    @gerer_erreurs(afficher_dans_ui=True, valeur_fallback=[])
    async def generer_suggestions_ia_depuis_inventaire(self) -> list[dict]:
        """
        Génère des suggestions de courses depuis l'inventaire via IA.

        ✅ Rate limiting AUTO
        ✅ Cache AUTO
        """
        from pydantic import BaseModel

        from .inventaire import inventaire_service

        alertes = inventaire_service.get_alertes()
        inventaire = inventaire_service.get_inventaire_complet()

        # Utiliser le Mixin d'inventaire
        context = inventaire_service.build_inventory_summary(inventaire)

        prompt = self.build_json_prompt(
            context=context,
            task="Suggère 15 articles courses prioritaires",
            json_schema='[{"nom": str, "quantite": float, "unite": str, "priorite": str, "rayon": str}]',
        )

        class SuggestionCourses(BaseModel):
            nom: str
            quantite: float
            unite: str
            priorite: str
            rayon: str

        suggestions = await self.call_with_list_parsing(
            prompt=prompt, item_model=SuggestionCourses, max_items=15
        )

        return [s.dict() for s in suggestions]


courses_service = CoursesService()

__all__ = ["CoursesService", "courses_service"]
