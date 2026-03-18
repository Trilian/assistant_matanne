"""
Service Courses Intelligentes.

Generation de liste de courses depuis le planning repas avec comparaison inventaire.
"""

import logging
from collections import defaultdict
from datetime import date

from sqlalchemy.orm import Session, selectinload

from src.core.ai import obtenir_client_ia
from src.core.decorators import avec_gestion_erreurs, avec_session_db
from src.core.models import (
    ArticleCourses,
    ArticleInventaire,
    Ingredient,
    ListeCourses,
    Planning,
    Recette,
    RecetteIngredient,
    Repas,
)
from src.services.core.base import BaseAIService
from src.services.core.event_bus_mixin import emettre_evenement_simple

from .constantes import MAPPING_RAYONS, PRIORITES
from .types import ArticleCourse, ListeCoursesIntelligente, SuggestionSubstitution

logger = logging.getLogger(__name__)


class ServiceCoursesIntelligentes(BaseAIService):
    """Service pour generer des listes de courses intelligentes depuis le planning."""

    def __init__(self):
        client = obtenir_client_ia()
        if client is None:
            raise RuntimeError("Client IA non disponible")
        super().__init__(
            client=client,
            cache_prefix="courses_intel",
            default_ttl=1800,
            service_name="courses_intelligentes",
        )

    def _determiner_rayon(self, nom_ingredient: str) -> str:
        """Determine le rayon d'un ingredient."""
        nom_lower = nom_ingredient.lower()
        for mot_cle, rayon in MAPPING_RAYONS.items():
            if mot_cle in nom_lower:
                return rayon
        return "Autre"

    def _determiner_priorite(self, rayon: str) -> int:
        """Determine la priorite basee sur le rayon."""
        return PRIORITES.get(rayon, 3)

    @avec_gestion_erreurs(default_return=None)
    @avec_session_db
    def obtenir_planning_actif(self, db: Session | None = None) -> Planning | None:
        """Recupere le planning actif avec ses repas et recettes."""
        planning = (
            db.query(Planning)
            .options(
                selectinload(Planning.repas)
                .selectinload(Repas.recette)
                .selectinload(Recette.ingredients)
                .selectinload(RecetteIngredient.ingredient),
                # Charger aussi les recettes liées aux entrées/desserts
                selectinload(Planning.repas)
                .selectinload(Repas.entree_recette)
                .selectinload(Recette.ingredients)
                .selectinload(RecetteIngredient.ingredient),
                selectinload(Planning.repas)
                .selectinload(Repas.dessert_recette)
                .selectinload(Recette.ingredients)
                .selectinload(RecetteIngredient.ingredient),
                selectinload(Planning.repas)
                .selectinload(Repas.dessert_jules_recette)
                .selectinload(Recette.ingredients)
                .selectinload(RecetteIngredient.ingredient),
            )
            .filter(Planning.actif == True)
            .first()
        )
        return planning

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def obtenir_stock_actuel(self, db: Session | None = None) -> dict[str, float]:
        """Recupere le stock actuel sous forme de dictionnaire {nom: quantite}."""
        stocks = (
            db.query(ArticleInventaire)
            .options(selectinload(ArticleInventaire.ingredient))
            .filter(ArticleInventaire.quantite > 0)
            .all()
        )
        return {
            stock.ingredient.nom.lower(): stock.quantite for stock in stocks if stock.ingredient
        }

    def extraire_ingredients_planning(self, planning: Planning) -> list[ArticleCourse]:
        """Extrait tous les ingredients des recettes du planning (plat + entrée + desserts)."""
        from typing import Any

        # Agregateur: {nom_ingredient: {quantite, unite, recettes}}
        agregat: dict[str, dict[str, Any]] = defaultdict(
            lambda: {"quantite": 0.0, "unite": "", "recettes": set()}
        )

        recettes_traitees: set[str] = set()

        def _ajouter_ingredients_recette(recette) -> None:
            """Ajoute les ingrédients d'une recette à l'agrégat."""
            if not recette or recette.nom in recettes_traitees:
                return
            recettes_traitees.add(recette.nom)
            for ing_recette in recette.ingredients:
                if not ing_recette.ingredient:
                    continue
                nom = ing_recette.ingredient.nom.lower()
                agregat[nom]["quantite"] += float(ing_recette.quantite or 1)
                agregat[nom]["unite"] = ing_recette.unite or ""
                agregat[nom]["recettes"].add(recette.nom)

        for repas in planning.repas:
            # Sauter les recettes réchauffées (nom commence par "Réchauffé:")
            recette = repas.recette
            if recette and recette.nom and recette.nom.lower().startswith("réchauffé"):
                continue
            # Plat principal
            _ajouter_ingredients_recette(recette)
            # Entrée (si liée à une recette)
            _ajouter_ingredients_recette(getattr(repas, "entree_recette", None))
            # Dessert (si lié à une recette)
            _ajouter_ingredients_recette(getattr(repas, "dessert_recette", None))
            # Dessert Jules (si lié à une recette)
            _ajouter_ingredients_recette(getattr(repas, "dessert_jules_recette", None))

            # Entrées/desserts texte (non liées à une recette) → article direct
            for champ, label in [
                ("entree", "Entrée"),
                ("dessert", "Dessert"),
                ("dessert_jules", "Dessert Jules"),
            ]:
                texte = getattr(repas, champ, None)
                fk = getattr(repas, f"{champ}_recette_id", None) if champ != "dessert_jules" else getattr(repas, "dessert_jules_recette_id", None)
                if texte and not fk:
                    nom = texte.strip().lower()
                    agregat[nom]["quantite"] += 1
                    agregat[nom]["unite"] = ""
                    agregat[nom]["recettes"].add(f"{label}: {texte.strip()}")

        # Construire la liste d'articles
        articles: list[ArticleCourse] = []
        for nom, data in agregat.items():
            rayon = self._determiner_rayon(nom)
            recettes_set: set[str] = data["recettes"]
            articles.append(
                ArticleCourse(
                    nom=nom.capitalize(),
                    quantite=float(data["quantite"]),
                    unite=str(data["unite"]),
                    rayon=rayon,
                    recettes_source=list(recettes_set),
                    priorite=self._determiner_priorite(rayon),
                )
            )

        return articles

    def comparer_avec_stock(
        self, articles: list[ArticleCourse], stock: dict[str, float]
    ) -> list[ArticleCourse]:
        """Compare les besoins avec le stock et calcule ce qu'il faut acheter."""
        articles_ajustes: list[ArticleCourse] = []

        for article in articles:
            nom_lower = article.nom.lower()
            en_stock = stock.get(nom_lower, 0.0)

            article.en_stock = en_stock
            article.a_acheter = max(0.0, article.quantite - en_stock)

            # Ne garder que les articles a acheter
            if article.a_acheter > 0:
                articles_ajustes.append(article)

        return articles_ajustes

    def generer_liste_courses(self) -> ListeCoursesIntelligente:
        """
        Genere une liste de courses complete depuis le planning actif.

        Returns:
            ListeCoursesIntelligente avec les articles optimises
        """
        alertes: list[str] = []

        # 1. Recuperer planning actif
        planning = self.obtenir_planning_actif()
        if not planning:
            return ListeCoursesIntelligente(
                alertes=["Aucun planning actif trouve. Creez d'abord un planning de repas."]
            )

        # 2. Extraire les ingredients
        articles = self.extraire_ingredients_planning(planning)
        if not articles:
            return ListeCoursesIntelligente(
                alertes=["Aucune recette avec ingredients dans le planning."]
            )

        # 3. Comparer avec stock
        stock = self.obtenir_stock_actuel()
        articles_a_acheter = self.comparer_avec_stock(articles, stock)

        # 4. Trier par rayon puis priorite
        articles_a_acheter.sort(key=lambda a: (a.rayon, a.priorite, a.nom))

        # 5. Recuperer les recettes couvertes
        recettes_couvertes: set[str] = set()
        for article in articles:
            recettes_couvertes.update(article.recettes_source)

        # 6. Generer alertes
        if len(articles_a_acheter) == 0:
            alertes.append("Tous les ingredients sont en stock!")
        elif len(stock) == 0:
            alertes.append("Inventaire vide - liste complete generee")

        return ListeCoursesIntelligente(
            articles=articles_a_acheter,
            total_articles=len(articles_a_acheter),
            recettes_couvertes=list(recettes_couvertes),
            alertes=alertes,
        )

    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def ajouter_a_liste_courses(
        self, articles: list[ArticleCourse], db: Session | None = None
    ) -> list[int]:
        """
        Ajoute les articles generes a la liste de courses.

        Args:
            articles: Articles a ajouter
            db: Session DB

        Returns:
            Liste des IDs crees
        """
        ids_crees: list[int] = []

        # 0. Récupérer ou créer la liste de courses active
        # On suppose qu'il y a une liste active "principale"
        liste_active = (
            db.query(ListeCourses)
            .filter(ListeCourses.archivee == False)
            .order_by(ListeCourses.cree_le.desc())
            .first()
        )

        if not liste_active:
            liste_active = ListeCourses(nom="Ma liste de courses")
            db.add(liste_active)
            db.flush()

        liste_id = liste_active.id

        for article in articles:
            # Chercher ou creer l'ingredient
            ingredient = (
                db.query(Ingredient).filter(Ingredient.nom.ilike(f"%{article.nom}%")).first()
            )

            if not ingredient:
                # Vérifier contrainte d'unicité exacte avant création
                existing_exact = db.query(Ingredient).filter(Ingredient.nom == article.nom).first()
                if existing_exact:
                    ingredient = existing_exact
                else:
                    ingredient = Ingredient(
                        nom=article.nom, categorie=article.rayon, unite=article.unite or "pcs"
                    )
                    db.add(ingredient)
                    db.flush()

            # Verifier si deja dans la liste de courses
            existant = (
                db.query(ArticleCourses)
                .filter(
                    ArticleCourses.liste_id == liste_id,
                    ArticleCourses.ingredient_id == ingredient.id,
                    ArticleCourses.achete == False,
                )
                .first()
            )

            if existant:
                # Mettre a jour quantite
                existant.quantite_necessaire = (
                    existant.quantite_necessaire or 0
                ) + article.a_acheter
                notes_actuelles = existant.notes or ""
                if "planning" not in notes_actuelles:
                    existant.notes = f"{notes_actuelles} + planning".strip()
                ids_crees.append(existant.id)
            else:
                # Creer nouvel article courses
                item = ArticleCourses(
                    liste_id=liste_id,
                    ingredient_id=ingredient.id,
                    quantite_necessaire=article.a_acheter,
                    priorite={1: "haute", 2: "moyenne", 3: "basse"}.get(
                        article.priorite, "moyenne"
                    ),
                    rayon_magasin=article.rayon,
                    notes=f"Depuis planning: {', '.join(article.recettes_source[:2])}",
                    achete=False,
                    suggere_par_ia=True,
                )
                db.add(item)
                db.flush()
                ids_crees.append(item.id)

        db.commit()

        emettre_evenement_simple(
            "courses.modifiees",
            {"nb_articles": len(ids_crees), "action": "articles_ajoutes", "source": "planning"},
            source="courses_suggestion",
        )
        logger.info(f"{len(ids_crees)} articles ajoutes a la liste de courses")
        return ids_crees

    async def suggerer_substitutions(
        self, articles: list[ArticleCourse]
    ) -> list[SuggestionSubstitution]:
        """
        Suggere des substitutions economiques ou de saison.

        Args:
            articles: Liste d'articles

        Returns:
            Suggestions de substitutions
        """
        # Filtrer articles couteux ou hors saison
        articles_a_evaluer = [a for a in articles if a.priorite <= 2][:5]

        if not articles_a_evaluer:
            return []

        noms = ", ".join([a.nom for a in articles_a_evaluer])

        prompt = f"""Pour ces ingredients de liste de courses: {noms}

Suggere des substitutions economiques ou de saison (max 3).
Format JSON:
[
    {{"ingredient_original": "...", "suggestion": "...", "raison": "..."}}
]

Criteres:
- Moins cher en ce moment
- De saison (nous sommes en {date.today().strftime("%B")})
- Equivalent nutritionnel

Reponds UNIQUEMENT avec le JSON."""

        try:
            response = await self.client.appeler(prompt)
            import json

            data = json.loads(response.strip().replace("```json", "").replace("```", ""))
            return [SuggestionSubstitution(**item) for item in data]
        except Exception as e:
            logger.error(f"Erreur suggestions: {e}")
            return []


# ═══════════════════════════════════════════════════════════
# FACTORY FUNCTION
# ═══════════════════════════════════════════════════════════

from src.services.core.registry import service_factory


@service_factory("courses_intelligentes", tags={"cuisine", "ia"})
def obtenir_service_courses_intelligentes() -> ServiceCoursesIntelligentes:
    """Factory pour le service courses intelligentes (thread-safe via registre)."""
    return ServiceCoursesIntelligentes()


def get_smart_shopping_service() -> ServiceCoursesIntelligentes:
    """Factory for smart shopping service (English alias)."""
    return obtenir_service_courses_intelligentes()


__all__ = [
    "ServiceCoursesIntelligentes",
    "obtenir_service_courses_intelligentes",
    "get_smart_shopping_service",
]
