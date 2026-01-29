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
        suggestions = self.call_with_list_parsing_sync(
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

    # ═══════════════════════════════════════════════════════════
    # PHASE 2: MODÈLES PERSISTANTS
    # ═══════════════════════════════════════════════════════════

    @with_db_session
    def get_modeles(self, utilisateur_id: str | None = None, db: Session | None = None) -> list[dict]:
        """Récupérer tous les modèles sauvegardés"""
        from src.core.models import ModeleCourses
        
        query = db.query(ModeleCourses).filter(ModeleCourses.actif == True)
        
        # Phase 2: Filter by user_id if provided
        if utilisateur_id:
            query = query.filter(ModeleCourses.utilisateur_id == utilisateur_id)
        
        modeles = query.order_by(ModeleCourses.nom).all()
        
        return [
            {
                "id": m.id,
                "nom": m.nom,
                "description": m.description,
                "articles": [
                    {
                        "nom": a.nom_article,
                        "quantite": a.quantite,
                        "unite": a.unite,
                        "rayon": a.rayon_magasin,
                        "priorite": a.priorite,
                        "notes": a.notes,
                    }
                    for a in sorted(m.articles, key=lambda x: x.ordre)
                ],
                "cree_le": m.cree_le.isoformat() if m.cree_le else None,
            }
            for m in modeles
        ]

    @with_db_session
    def create_modele(self, nom: str, articles: list[dict], description: str | None = None, 
                     utilisateur_id: str | None = None, db: Session | None = None) -> int:
        """Créer un nouveau modèle de courses"""
        from src.core.models import ModeleCourses, ArticleModele
        from src.core.models import Ingredient
        
        modele = ModeleCourses(
            nom=nom,
            description=description,
            utilisateur_id=utilisateur_id,
        )
        db.add(modele)
        db.flush()  # Get ID
        
        for ordre, article_data in enumerate(articles):
            # Chercher l'ingrédient
            ingredient = None
            if "ingredient_id" in article_data:
                ingredient = db.query(Ingredient).filter_by(id=article_data["ingredient_id"]).first()
            
            article_modele = ArticleModele(
                modele_id=modele.id,
                ingredient_id=ingredient.id if ingredient else None,
                nom_article=article_data.get("nom", "Article"),
                quantite=float(article_data.get("quantite", 1.0)),
                unite=article_data.get("unite", "pièce"),
                rayon_magasin=article_data.get("rayon", "Autre"),
                priorite=article_data.get("priorite", "moyenne"),
                notes=article_data.get("notes"),
                ordre=ordre,
            )
            db.add(article_modele)
        
        db.commit()
        logger.info(f"✅ Modèle '{nom}' créé avec {len(articles)} articles")
        return modele.id

    @with_db_session
    def delete_modele(self, modele_id: int, db: Session | None = None) -> bool:
        """Supprimer un modèle"""
        from src.core.models import ModeleCourses
        
        modele = db.query(ModeleCourses).filter_by(id=modele_id).first()
        if not modele:
            return False
        
        db.delete(modele)
        db.commit()
        logger.info(f"✅ Modèle {modele_id} supprimé")
        return True

    @with_db_session
    def appliquer_modele(self, modele_id: int, utilisateur_id: str | None = None, 
                        db: Session | None = None) -> list[int]:
        """Appliquer un modèle à la liste active (crée articles cours)"""
        from src.core.models import ModeleCourses, Ingredient, ArticleModele
        from sqlalchemy.orm import joinedload
        
        # Load with eager loading to prevent lazy loading issues outside session
        modele = db.query(ModeleCourses).options(
            joinedload(ModeleCourses.articles).joinedload(ArticleModele.ingredient)
        ).filter_by(id=modele_id).first()
        
        if not modele:
            logger.error(f"Modèle {modele_id} non trouvé")
            return []
        
        article_ids = []
        for article_modele in modele.articles:
            logger.debug(f"Processing article: {article_modele.nom_article}")
            # Récupérer ou créer l'ingrédient
            ingredient = article_modele.ingredient
            if not ingredient:
                logger.debug(f"  Cherchant ingrédient par nom: {article_modele.nom_article}")
                ingredient = db.query(Ingredient).filter_by(
                    nom=article_modele.nom_article
                ).first()
                if not ingredient:
                    logger.debug(f"  Créant nouvel ingrédient: {article_modele.nom_article}")
                    ingredient = Ingredient(
                        nom=article_modele.nom_article,
                        unite=article_modele.unite,
                    )
                    db.add(ingredient)
                    db.flush()
            
            # Créer article courses
            data = {
                "ingredient_id": ingredient.id,
                "quantite_necessaire": article_modele.quantite,
                "priorite": article_modele.priorite,
                "rayon_magasin": article_modele.rayon_magasin,
                "notes": article_modele.notes,
                "achete": False,
            }
            
            article_id = self.create(data, db=db)
            article_ids.append(article_id)
            logger.debug(f"  ✓ Article créé: ID={article_id}")
        
        logger.info(f"✅ Modèle {modele_id} appliqué ({len(article_ids)} articles)")
        return article_ids


# ═══════════════════════════════════════════════════════════
# SINGLETON SERVICE INSTANCE
# ═══════════════════════════════════════════════════════════

_courses_service: CoursesService | None = None


def get_courses_service() -> CoursesService:
    """Get or create the global CoursesService instance."""
    global _courses_service
    if _courses_service is None:
        _courses_service = CoursesService()
    return _courses_service

# Backward compatibility
courses_service = None

__all__ = ["CoursesService", "courses_service", "get_courses_service"]
