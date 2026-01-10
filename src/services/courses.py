"""
Service Courses Unifié (REFACTORING v2.1)

Service complet pour la liste de courses fusionnant :
- courses_service.py (CRUD)
- courses_ai_service.py (Suggestions IA)
- courses_io_service.py (Import/Export)

Architecture simplifiée : Tout en 1 seul fichier.
"""
import logging
from typing import Dict, List, Optional
from sqlalchemy.orm import joinedload, Session
import csv
import json
from io import StringIO

from src.services.types import BaseService

from src.core.database import obtenir_contexte_db
from src.core.errors import gerer_erreurs as handle_errors
from src.core.cache import Cache
from src.core.models import ArticleCourses, Ingredient
from src.core.ai import get_ai_client

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# SERVICE COURSES UNIFIÉ
# ═══════════════════════════════════════════════════════════

class CoursesService(BaseService[ArticleCourses]):
    """
    Service complet pour la liste de courses.

    Fonctionnalités :
    - CRUD liste de courses
    - Suggestions IA depuis inventaire
    - Organisation par rayon
    - Import/Export
    - Statistiques
    """

    def __init__(self):
        super().__init__(ArticleCourses, cache_ttl=1800)
        self.ai_client = None

    # ═══════════════════════════════════════════════════════════
    # SECTION 1 : CRUD LISTE
    # ═══════════════════════════════════════════════════════════

    @handle_errors(show_in_ui=False, fallback_value=[])
    def get_liste_courses(
        self,
        achetes: bool = False,
        priorite: Optional[str] = None
    ) -> List[Dict]:
        """
        Récupère la liste de courses.

        Args:
            achetes: Inclure articles achetés
            priorite: Filtrer par priorité

        Returns:
            Liste articles enrichis
        """
        cache_key = f"courses_{achetes}_{priorite}"
        cached = Cache.obtenir(cache_key, ttl=self.cache_ttl)
        if cached:
            return cached

        with obtenir_contexte_db() as db:
            query = (
                db.query(ArticleCourses)
                .options(joinedload(ArticleCourses.ingredient))
            )

            if not achetes:
                query = query.filter(ArticleCourses.achete == False)

            if priorite:
                query = query.filter(ArticleCourses.priorite == priorite)

            articles = query.order_by(ArticleCourses.rayon_magasin).all()

            result = []
            for article in articles:
                result.append({
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
                    "suggere_par_ia": article.suggere_par_ia
                })

            Cache.definir(cache_key, result, ttl=self.cache_ttl, dependencies=["courses"])
            return result

    @handle_errors(show_in_ui=True, fallback_value=False)
    def marquer_achete(self, article_id: int, achete: bool = True) -> bool:
        """
        Marque un article comme acheté.

        Args:
            article_id: ID de l'article
            achete: État acheté

        Returns:
            True si succès
        """
        from datetime import datetime

        with obtenir_contexte_db() as db:
            article = db.query(ArticleCourses).get(article_id)
            if not article:
                return False

            article.achete = achete
            if achete:
                article.achete_le = datetime.utcnow()
            else:
                article.achete_le = None

            db.commit()

            # Invalider cache
            Cache.invalider(pattern="courses")

            return True

    @handle_errors(show_in_ui=True)
    def ajouter_article(
        self,
        ingredient_nom: str,
        quantite: float,
        unite: str = "pcs",
        priorite: str = "moyenne",
        rayon: Optional[str] = None
    ) -> Optional[ArticleCourses]:
        """
        Ajoute un article à la liste de courses.

        Args:
            ingredient_nom: Nom de l'ingrédient
            quantite: Quantité nécessaire
            unite: Unité
            priorite: Priorité (basse, moyenne, haute)
            rayon: Rayon magasin

        Returns:
            Article créé
        """
        with obtenir_contexte_db() as db:
            # Trouver ou créer ingrédient
            ingredient = db.query(Ingredient).filter(
                Ingredient.nom == ingredient_nom
            ).first()

            if not ingredient:
                ingredient = Ingredient(nom=ingredient_nom, unite=unite)
                db.add(ingredient)
                db.flush()

            # Créer article courses
            article = ArticleCourses(
                ingredient_id=ingredient.id,
                quantite_necessaire=quantite,
                priorite=priorite,
                rayon_magasin=rayon,
                achete=False,
                suggere_par_ia=False
            )
            db.add(article)
            db.commit()
            db.refresh(article)

            # Invalider cache
            Cache.invalider(pattern="courses")

            logger.info(f"✅ Article ajouté aux courses : {ingredient_nom}")
            return article

    # ═══════════════════════════════════════════════════════════
    # SECTION 2 : SUGGESTIONS IA
    # ═══════════════════════════════════════════════════════════

    def _ensure_ai_client(self):
        """Initialise le client IA si nécessaire"""
        if self.ai_client is None:
            self.ai_client = get_ai_client()

    @handle_errors(show_in_ui=True, fallback_value=[])
    def generer_suggestions_ia_depuis_inventaire(self) -> List[Dict]:
        """
        Génère des suggestions de courses depuis l'inventaire via IA.

        Returns:
            Liste de suggestions
        """
        # Import local pour éviter circular import
        from .inventaire import inventaire_service

        self._ensure_ai_client()

        # Vérifier rate limit
        autorise, msg = Cache.peut_appeler_ia()
        if not autorise:
            logger.warning(msg)
            return []

        # Récupérer alertes inventaire
        alertes = inventaire_service.get_alertes()

        # Construire prompt
        prompt = f"""Analyse ces articles manquants et suggère une liste de courses optimisée :

Articles en stock bas ({len(alertes['stock_bas'])}):
{', '.join([a['ingredient_nom'] for a in alertes['stock_bas'][:15]])}

Articles critiques ({len(alertes['critique'])}):
{', '.join([a['ingredient_nom'] for a in alertes['critique'][:15]])}

Suggère 15 articles prioritaires avec quantités et rayons magasin.
Réponds en JSON : [{"nom": str, "quantite": float, "unite": str, "priorite": str, "rayon": str}]"""

        # Vérifier cache
        cached = Cache.obtenir_ia(prompt)
        if cached:
            return cached

        # Appeler IA
        try:
            response = self.ai_client.chat.complete(
                model="mistral-small-latest",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )

            # Parser réponse
            suggestions = self._parse_ai_suggestions(response.choices[0].message.content)

            # Cacher
            Cache.definir_ia(prompt, suggestions)
            Cache.enregistrer_appel_ia()

            logger.info(f"✅ {len(suggestions)} suggestions courses IA générées")
            return suggestions

        except Exception as e:
            logger.error(f"❌ Erreur suggestions courses IA : {e}")
            return []

    # ═══════════════════════════════════════════════════════════
    # SECTION 3 : IMPORT/EXPORT
    # ═══════════════════════════════════════════════════════════

    def export_to_csv(self, articles: List[Dict]) -> str:
        """
        Exporte la liste de courses en CSV.

        Args:
            articles: Liste articles

        Returns:
            Contenu CSV
        """
        output = StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=["ingredient_nom", "quantite_necessaire", "unite", "priorite",
                       "achete", "rayon_magasin"]
        )

        writer.writeheader()
        for a in articles:
            writer.writerow({
                "ingredient_nom": a["ingredient_nom"],
                "quantite_necessaire": a["quantite_necessaire"],
                "unite": a["unite"],
                "priorite": a["priorite"],
                "achete": "Oui" if a["achete"] else "Non",
                "rayon_magasin": a["rayon_magasin"] or ""
            })

        return output.getvalue()

    def export_to_json(self, articles: List[Dict], indent: int = 2) -> str:
        """
        Exporte la liste de courses en JSON.

        Args:
            articles: Liste articles
            indent: Indentation

        Returns:
            Contenu JSON
        """
        return json.dumps(articles, indent=indent, ensure_ascii=False, default=str)

    # ═══════════════════════════════════════════════════════════
    # HELPERS PRIVÉS
    # ═══════════════════════════════════════════════════════════

    def _parse_ai_suggestions(self, content: str) -> List[Dict]:
        """Parse les suggestions IA"""
        try:
            start = content.find("[")
            end = content.rfind("]") + 1
            if start == -1:
                return []
            json_str = content[start:end]
            return json.loads(json_str)
        except:
            return []


# ═══════════════════════════════════════════════════════════
# INSTANCE SINGLETON
# ═══════════════════════════════════════════════════════════

courses_service = CoursesService()


# ═══════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════

__all__ = [
    "CoursesService",
    "courses_service",
]

