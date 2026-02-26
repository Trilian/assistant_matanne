"""
Service Courses Unifie.

Service complet pour la gestion de la liste de courses avec support IA.
"""

import logging
from typing import Any

from sqlalchemy.orm import Session, joinedload

from src.core.ai import obtenir_client_ia
from src.core.decorators import avec_cache, avec_gestion_erreurs, avec_session_db
from src.core.models import ArticleCourses
from src.core.monitoring import chronometre
from src.services.core.base import BaseAIService, BaseService
from src.services.core.events import obtenir_bus

from .types import SuggestionCourses

logger = logging.getLogger(__name__)


class ServiceCourses(BaseService[ArticleCourses], BaseAIService):
    """
    Service complet pour la liste de courses.

    Heritages:
    - BaseService: CRUD generique
    - BaseAIService: Rate limiting + cache auto

    Fonctionnalites:
    - CRUD optimise avec cache
    - Liste de courses avec filtres
    - Suggestions IA basees sur inventaire
    - Gestion priorites et rayons magasin

    Note:
        Utilise MRO cooperatif via super().__init__() pour éviter
        les appels manuels fragiles aux __init__ des classes parentes.
    """

    def __init__(self):
        # MRO coopératif: un seul super() avec tous les paramètres
        super().__init__(
            # BaseService parameters
            model=ArticleCourses,
            cache_ttl=1800,
            # BaseAIService parameters
            client=obtenir_client_ia(),
            cache_prefix="courses",
            default_ttl=1800,
            default_temperature=0.7,
            service_name="courses",
        )

    # ═══════════════════════════════════════════════════════════
    # SECTION 1: CRUD & LISTE COURSES
    # ═══════════════════════════════════════════════════════════

    @chronometre("courses.liste_complete", seuil_alerte_ms=2000)
    @avec_cache(
        ttl=1800,
        key_func=lambda self, achetes, priorite: f"courses_{achetes}_{priorite}",
    )
    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def obtenir_liste_courses(
        self,
        achetes: bool = False,
        priorite: str | None = None,
        db: Session | None = None,
    ) -> list[dict[str, Any]]:
        """Recupere la liste de courses.

        Args:
            achetes: Inclure articles achetes
            priorite: Filtrer par priorite (haute, moyenne, basse)
            db: Session DB (injectee par @avec_session_db)

        Returns:
            Liste de dicts avec donnees articles organisees par rayon
        """
        query = db.query(ArticleCourses).options(joinedload(ArticleCourses.ingredient))

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
            f"Liste courses recuperee: {len(result)} items "
            f"(priorite={priorite or 'toutes'}, achetes={achetes})"
        )
        return result

    # Alias pour compatibilite
    get_liste_courses = obtenir_liste_courses

    @avec_gestion_erreurs(default_return=None)
    @avec_session_db
    def obtenir_ou_creer_ingredient(
        self,
        nom: str,
        unite: str = "pièce",
        db: Session | None = None,
    ) -> int:
        """Trouve ou crée un ingrédient par nom.

        Args:
            nom: Nom de l'ingrédient
            unite: Unité par défaut si création
            db: Session DB (injectée par @avec_session_db)

        Returns:
            ID de l'ingrédient (existant ou créé)
        """
        from src.core.models import Ingredient

        ingredient = db.query(Ingredient).filter(Ingredient.nom == nom).first()
        if not ingredient:
            ingredient = Ingredient(nom=nom, unite=unite)
            db.add(ingredient)
            db.flush()
            db.refresh(ingredient)
            logger.debug(f"Ingredient créé: {nom}")
        return ingredient.id

    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def obtenir_historique_achats(
        self,
        date_debut: Any = None,
        date_fin: Any = None,
        db: Session | None = None,
    ) -> list[dict[str, Any]]:
        """Récupère l'historique des articles achetés dans une période.

        Args:
            date_debut: Date de début (datetime ou date)
            date_fin: Date de fin (datetime ou date)
            db: Session DB (injectée par @avec_session_db)

        Returns:
            Liste de dicts avec données articles achetés
        """
        from datetime import datetime

        query = (
            db.query(ArticleCourses)
            .options(joinedload(ArticleCourses.ingredient))
            .filter(ArticleCourses.achete.is_(True))
        )

        if date_debut:
            if hasattr(date_debut, "hour"):
                dt_debut = date_debut
            else:
                dt_debut = datetime.combine(date_debut, datetime.min.time())
            query = query.filter(ArticleCourses.achete_le >= dt_debut)

        if date_fin:
            if hasattr(date_fin, "hour"):
                dt_fin = date_fin
            else:
                dt_fin = datetime.combine(date_fin, datetime.max.time())
            query = query.filter(ArticleCourses.achete_le <= dt_fin)

        articles = query.all()

        return [
            {
                "id": a.id,
                "ingredient_nom": a.ingredient.nom if a.ingredient else "N/A",
                "quantite_necessaire": a.quantite_necessaire,
                "unite": a.ingredient.unite if a.ingredient else "",
                "priorite": a.priorite,
                "rayon_magasin": a.rayon_magasin,
                "achete_le": a.achete_le,
                "suggere_par_ia": a.suggere_par_ia,
            }
            for a in articles
        ]

    # Alias
    get_historique_achats = obtenir_historique_achats

    @avec_gestion_erreurs(default_return=0)
    def ajouter_suggestions_en_masse(
        self,
        suggestions: list,
    ) -> int:
        """Ajoute des suggestions IA à la liste de courses.

        Pour chaque suggestion, trouve ou crée l'ingrédient puis crée l'article.

        Args:
            suggestions: Liste de SuggestionCourses

        Returns:
            Nombre d'articles ajoutés
        """
        count = 0
        for suggestion in suggestions:
            ingredient_id = self.obtenir_ou_creer_ingredient(
                nom=suggestion.nom,
                unite=suggestion.unite,
            )
            if ingredient_id:
                data = {
                    "ingredient_id": ingredient_id,
                    "quantite_necessaire": suggestion.quantite,
                    "priorite": suggestion.priorite,
                    "rayon_magasin": suggestion.rayon,
                    "suggere_par_ia": True,
                }
                self.create(data)
                count += 1

        # Émettre événement domaine
        if count > 0:
            obtenir_bus().emettre(
                "courses.ingredients_ajoutes",
                {"recette": recette_nom, "nb_articles": count},
                source="courses",
            )

        return count

    @avec_gestion_erreurs(default_return=0)
    def ajouter_ingredients_recette(
        self,
        ingredients_data: list[dict],
        recette_nom: str = "",
    ) -> int:
        """Ajoute les ingrédients d'une recette à la liste de courses.

        Args:
            ingredients_data: Liste de dicts avec nom, quantite, unite
            recette_nom: Nom de la recette pour les notes

        Returns:
            Nombre d'articles ajoutés
        """
        count = 0
        for ing in ingredients_data:
            nom = ing.get("nom", "")
            if not nom:
                continue

            ingredient_id = self.obtenir_ou_creer_ingredient(
                nom=nom,
                unite=ing.get("unite", "pièce"),
            )
            if ingredient_id:
                data = {
                    "ingredient_id": ingredient_id,
                    "quantite_necessaire": ing.get("quantite", 1),
                    "priorite": "moyenne",
                    "rayon_magasin": "Autre",
                    "notes": f"Pour {recette_nom}" if recette_nom else None,
                }
                self.create(data)
                count += 1
        return count

    @avec_gestion_erreurs(default_return=0)
    def importer_articles_csv(
        self,
        articles: list[dict],
    ) -> int:
        """Importe des articles depuis un CSV parsé.

        Args:
            articles: Liste de dicts avec Article, Quantité, Unité, Priorité, Rayon, Notes

        Returns:
            Nombre d'articles importés
        """
        count = 0
        for row in articles:
            nom = row.get("Article", "")
            if not nom:
                continue

            ingredient_id = self.obtenir_ou_creer_ingredient(
                nom=nom,
                unite=row.get("Unité", "pièce"),
            )
            if ingredient_id:
                self.create(
                    {
                        "ingredient_id": ingredient_id,
                        "quantite_necessaire": float(row.get("Quantité", 1)),
                        "priorite": row.get("Priorité", "moyenne"),
                        "rayon_magasin": row.get("Rayon", "Autre"),
                        "notes": row.get("Notes"),
                    }
                )
                count += 1
        return count

    # ═══════════════════════════════════════════════════════════
    # SECTION 2: SUGGESTIONS IA
    # ═══════════════════════════════════════════════════════════

    @avec_gestion_erreurs(default_return=[])
    @avec_cache(ttl=3600, key_func=lambda self: "suggestions_courses_ia")
    def generer_suggestions_ia_depuis_inventaire(self) -> list[SuggestionCourses]:
        """Genere des suggestions de courses depuis l'inventaire via IA.

        Returns:
            Liste de SuggestionCourses, liste vide en cas d'erreur
        """
        from src.services.inventaire import obtenir_service_inventaire

        logger.info("Generation suggestions courses depuis inventaire avec IA")

        try:
            # Recuperer etat inventaire
            inventaire_service = obtenir_service_inventaire()
            if not inventaire_service:
                logger.warning("Service inventaire indisponible")
                return []

            inventaire = inventaire_service.get_inventaire_complet()
            if not inventaire:
                logger.info("Inventaire vide, pas de suggestions")
                return []

            # Utiliser le Mixin d'inventaire pour contexte
            context = inventaire_service.build_inventory_summary(inventaire)

            # Construire prompt avec schema clair
            prompt = self.build_json_prompt(
                context=context,
                task="Generer 15 articles prioritaires a acheter",
                json_schema='[{"nom": str, "quantite": float, "unite": str, "priorite": str, "rayon": str}]',
                constraints=[
                    "Priorite: haute/moyenne/basse",
                    "Articles critiques d'abord",
                    "Quantites realistes",
                    "Grouper par rayon",
                    "Respecter budget",
                ],
            )

            # Appel IA avec auto rate limiting & parsing
            suggestions = self.call_with_list_parsing_sync(
                prompt=prompt,
                item_model=SuggestionCourses,
                system_prompt=self.build_system_prompt(
                    role="Assistant d'achat intelligent",
                    expertise=[
                        "Gestion stock",
                        "Optimisation inventaire",
                        "Organisation achats",
                        "Gestion budget",
                    ],
                    rules=[
                        "Suggerer articles critiques d'abord",
                        "Grouper par rayon magasin",
                        "Minimiser trajets",
                        "Equilibre qualite-prix",
                    ],
                ),
                max_items=15,
            )

            logger.info(f"Genere {len(suggestions)} suggestions courses")
            return suggestions or []

        except KeyError as e:
            logger.error(f"Erreur parsing (champ manquant): {e}")
            return []
        except Exception as e:
            logger.error(f"Erreur generation suggestions: {str(e)}")
            return []

    # ═══════════════════════════════════════════════════════════
    # SECTION 3: MODELES PERSISTANTS
    # ═══════════════════════════════════════════════════════════

    @avec_session_db
    def obtenir_modeles(
        self, utilisateur_id: str | None = None, db: Session | None = None
    ) -> list[dict]:
        """Recuperer tous les modeles sauvegardes."""
        from src.core.models import ModeleCourses

        query = db.query(ModeleCourses).filter(ModeleCourses.actif == True)

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

    # Alias pour compatibilite
    get_modeles = obtenir_modeles

    @avec_session_db
    def creer_modele(
        self,
        nom: str,
        articles: list[dict],
        description: str | None = None,
        utilisateur_id: str | None = None,
        db: Session | None = None,
    ) -> int:
        """Creer un nouveau modele de courses."""
        from src.core.models import ArticleModele, Ingredient, ModeleCourses

        modele = ModeleCourses(
            nom=nom,
            description=description,
            utilisateur_id=utilisateur_id,
        )
        db.add(modele)
        db.flush()

        for ordre, article_data in enumerate(articles):
            ingredient = None
            if "ingredient_id" in article_data:
                ingredient = (
                    db.query(Ingredient).filter_by(id=article_data["ingredient_id"]).first()
                )

            article_modele = ArticleModele(
                modele_id=modele.id,
                ingredient_id=ingredient.id if ingredient else None,
                nom_article=article_data.get("nom", "Article"),
                quantite=float(article_data.get("quantite", 1.0)),
                unite=article_data.get("unite", "piece"),
                rayon_magasin=article_data.get("rayon", "Autre"),
                priorite=article_data.get("priorite", "moyenne"),
                notes=article_data.get("notes"),
                ordre=ordre,
            )
            db.add(article_modele)

        db.commit()
        logger.info(f"Modele '{nom}' cree avec {len(articles)} articles")
        return modele.id

    # Alias pour compatibilite
    create_modele = creer_modele

    @avec_session_db
    def supprimer_modele(self, modele_id: int, db: Session | None = None) -> bool:
        """Supprimer un modele."""
        from src.core.models import ModeleCourses

        modele = db.query(ModeleCourses).filter_by(id=modele_id).first()
        if not modele:
            return False

        db.delete(modele)
        db.commit()
        logger.info(f"Modele {modele_id} supprime")
        return True

    # Alias pour compatibilite
    delete_modele = supprimer_modele

    @avec_session_db
    def appliquer_modele(
        self, modele_id: int, utilisateur_id: str | None = None, db: Session | None = None
    ) -> list[int]:
        """Appliquer un modele a la liste active (cree articles cours)."""
        from sqlalchemy.orm import joinedload

        from src.core.models import ArticleModele, Ingredient, ModeleCourses

        modele = (
            db.query(ModeleCourses)
            .options(joinedload(ModeleCourses.articles).joinedload(ArticleModele.ingredient))
            .filter_by(id=modele_id)
            .first()
        )

        if not modele:
            logger.error(f"Modele {modele_id} non trouve")
            return []

        article_ids = []
        for article_modele in modele.articles:
            logger.debug(f"Traitement article: {article_modele.nom_article}")
            ingredient = article_modele.ingredient
            if not ingredient:
                logger.debug(f"  Recherche ingredient par nom: {article_modele.nom_article}")
                ingredient = db.query(Ingredient).filter_by(nom=article_modele.nom_article).first()
                if not ingredient:
                    logger.debug(f"  Creation nouvel ingredient: {article_modele.nom_article}")
                    ingredient = Ingredient(
                        nom=article_modele.nom_article,
                        unite=article_modele.unite,
                    )
                    db.add(ingredient)
                    db.flush()

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
            logger.debug(f"  Article cree: ID={article_id}")

        logger.info(f"Modele {modele_id} applique ({len(article_ids)} articles)")
        return article_ids


# ═══════════════════════════════════════════════════════════
# SINGLETON SERVICE INSTANCE — Via ServiceRegistry (thread-safe)
# ═══════════════════════════════════════════════════════════

from src.services.core.registry import service_factory


@service_factory("courses", tags={"cuisine", "ia", "crud"})
def obtenir_service_courses() -> ServiceCourses:
    """Obtient ou crée l'instance ServiceCourses (via registre, thread-safe)."""
    return ServiceCourses()


def get_shopping_service() -> ServiceCourses:
    """Factory for shopping service (English alias)."""
    return obtenir_service_courses()


__all__ = [
    "ServiceCourses",
    "obtenir_service_courses",
    "get_shopping_service",
]
