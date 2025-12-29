"""
Service Inventaire ULTRA-OPTIMISÉ v2.0
Utilise 100% EnhancedCRUDService + unified helpers
"""
from typing import List, Dict, Optional, Tuple
from datetime import datetime, date, timedelta

from src.services.base_enhanced_service import EnhancedCRUDService, StatusTrackingMixin
from src.services.unified_service_helpers import (
    find_or_create_ingredient,
    enrich_with_ingredient_info,
    validate_quantity
)
from src.core.cache import Cache
from src.core.errors import handle_errors, ValidationError, NotFoundError
from src.core.models import ArticleInventaire, ArticleCourses
import logging

logger = logging.getLogger(__name__)

# Constantes
CATEGORIES = ["Légumes", "Fruits", "Féculents", "Protéines", "Laitier", "Épices", "Huiles", "Conserves", "Autre"]
EMPLACEMENTS = ["Frigo", "Congélateur", "Placard", "Cave", "Autre"]
JOURS_ALERTE_PEREMPTION = 7


# ═══════════════════════════════════════════════════════════════
# HELPERS STATUT (Pure Functions)
# ═══════════════════════════════════════════════════════════════

def calculer_statut_article(quantite: float, seuil: float, date_peremption: Optional[date]) -> Tuple[str, str]:
    """Calcule statut (pure function)"""
    sous_seuil = quantite < seuil
    peremption_proche = False

    if date_peremption:
        jours = (date_peremption - date.today()).days
        peremption_proche = 0 <= jours <= JOURS_ALERTE_PEREMPTION

    if sous_seuil and peremption_proche:
        return "critique", "🔴"
    elif peremption_proche:
        return "peremption_proche", "⏳"
    elif sous_seuil:
        return "sous_seuil", "⚠️"
    else:
        return "ok", "✅"


def get_jours_avant_peremption(date_peremption: Optional[date]) -> Optional[int]:
    """Calcule jours restants"""
    if not date_peremption:
        return None
    return max((date_peremption - date.today()).days, 0)


# ═══════════════════════════════════════════════════════════════
# SERVICE OPTIMISÉ
# ═══════════════════════════════════════════════════════════════

class InventaireService(EnhancedCRUDService[ArticleInventaire], StatusTrackingMixin):
    """Service inventaire optimisé - utilise 100% la base"""

    def __init__(self):
        super().__init__(ArticleInventaire)

    # ═══════════════════════════════════════════════════════════════
    # LECTURE (Cache + advanced_search)
    # ═══════════════════════════════════════════════════════════════

    @Cache.cached(ttl=30)
    @handle_errors(show_in_ui=False)
    def get_inventaire_complet(self, filters: Optional[Dict] = None) -> List[Dict]:
        """Inventaire avec enrichissement - Cache 30s"""
        items = self.advanced_search(
            search_term=None,
            filters=filters,
            sort_by="ingredient_id",
            limit=1000
        )

        # Enrichissement (1 query)
        enriched = enrich_with_ingredient_info(items, "ingredient_id")

        # Ajouter statuts
        for item in enriched:
            statut, icone = calculer_statut_article(
                item["quantite"],
                item.get("quantite_min", 1.0),
                item.get("date_peremption")
            )
            item["statut"] = statut
            item["icone"] = icone
            item["jours_peremption"] = get_jours_avant_peremption(item.get("date_peremption"))
            item["seuil"] = item.get("quantite_min", 1.0)

        return enriched

    @handle_errors(show_in_ui=False)
    def get_alertes(self) -> Dict[str, List[Dict]]:
        """Alertes critiques"""
        inventaire = self.get_inventaire_complet()
        return {
            "stock_bas": [i for i in inventaire if i["statut"] == "sous_seuil"],
            "peremption_proche": [i for i in inventaire if i["statut"] == "peremption_proche"],
            "critiques": [i for i in inventaire if i["statut"] == "critique"]
        }

    # ═══════════════════════════════════════════════════════════════
    # CRÉATION/MODIFICATION (find_or_create + update)
    # ═══════════════════════════════════════════════════════════════

    @handle_errors(show_in_ui=True)
    def ajouter_ou_modifier(self, nom: str, categorie: str, quantite: float,
                            unite: str, seuil: float, emplacement: Optional[str] = None,
                            date_peremption: Optional[date] = None,
                            article_id: Optional[int] = None) -> int:
        """Ajoute/modifie article"""
        validate_quantity(quantite, "quantité")
        validate_quantity(seuil, "seuil")

        from src.core.database import get_db_context
        with get_db_context() as db:
            ingredient_id = find_or_create_ingredient(nom, unite, categorie, db)

            if article_id:
                # Modification
                updated = self.update(
                    article_id,
                    {
                        "quantite": quantite,
                        "quantite_min": seuil,
                        "emplacement": emplacement,
                        "date_peremption": date_peremption,
                        "derniere_maj": datetime.now()
                    },
                    db=db
                )
                Cache.invalidate("inventaire")
                return article_id if updated else None

            # Vérifier existant
            existant = db.query(ArticleInventaire).filter(
                ArticleInventaire.ingredient_id == ingredient_id
            ).first()

            if existant:
                existant.quantite += quantite
                existant.quantite_min = seuil
                existant.derniere_maj = datetime.now()
                db.commit()
                Cache.invalidate("inventaire")
                return existant.id

            # Création
            article = self.create({
                "ingredient_id": ingredient_id,
                "quantite": quantite,
                "quantite_min": seuil,
                "emplacement": emplacement,
                "date_peremption": date_peremption
            }, db=db)

            Cache.invalidate("inventaire")
            return article.id

    # ═══════════════════════════════════════════════════════════════
    # AJUSTEMENTS
    # ═══════════════════════════════════════════════════════════════

    @handle_errors(show_in_ui=True)
    def ajuster_quantite(self, article_id: int, delta: float,
                         raison: Optional[str] = None) -> Optional[float]:
        """Ajuste quantité"""
        article = self.get_by_id(article_id)
        if not article:
            raise NotFoundError(
                f"Article {article_id} non trouvé",
                user_message="Article introuvable"
            )

        nouvelle_quantite = max(0, article.quantite + delta)
        updated = self.update(
            article_id,
            {"quantite": nouvelle_quantite, "derniere_maj": datetime.now()}
        )

        if updated:
            Cache.invalidate("inventaire")

        return nouvelle_quantite if updated else None

    # ═══════════════════════════════════════════════════════════════
    # STATS (get_generic_stats)
    # ═══════════════════════════════════════════════════════════════

    @Cache.cached(ttl=60)
    def get_stats(self, jours: int = 30) -> Dict:
        """Stats (cache 1min) - 1 lecture via cache"""
        inventaire = self.get_inventaire_complet()

        stats = {
            "total_articles": len(inventaire),
            "total_critiques": len([i for i in inventaire if i["statut"] == "critique"]),
            "total_stock_bas": len([i for i in inventaire if i["statut"] == "sous_seuil"]),
            "total_peremption": len([i for i in inventaire if i["statut"] == "peremption_proche"]),
        }

        # Par catégorie/emplacement
        from collections import defaultdict
        categories = defaultdict(int)
        emplacements = defaultdict(int)

        for item in inventaire:
            categories[item["categorie"]] += 1
            emplacements[item.get("emplacement", "—")] += 1

        stats["categories"] = dict(categories)
        stats["emplacements"] = dict(emplacements)

        return stats

    # ═══════════════════════════════════════════════════════════════
    # INTÉGRATION COURSES
    # ═══════════════════════════════════════════════════════════════

    @handle_errors(show_in_ui=True)
    def ajouter_a_courses(self, article_id: int, quantite: Optional[float] = None) -> bool:
        """Ajoute à liste courses"""
        from src.core.database import get_db_context

        with get_db_context() as db:
            article = self.get_by_id(article_id, db)
            if not article:
                return False

            # Quantité = manque
            quantite_calculee = quantite or max(
                article.quantite_min - article.quantite,
                article.quantite_min
            )

            # Vérifier si déjà dans courses
            existant = db.query(ArticleCourses).filter(
                ArticleCourses.ingredient_id == article.ingredient_id,
                ArticleCourses.achete == False
            ).first()

            if existant:
                existant.quantite_necessaire = max(
                    existant.quantite_necessaire,
                    quantite_calculee
                )
            else:
                course = ArticleCourses(
                    ingredient_id=article.ingredient_id,
                    quantite_necessaire=quantite_calculee,
                    priorite="haute",
                    suggere_par_ia=False
                )
                db.add(course)

            db.commit()
            return True


# Instance globale
inventaire_service = InventaireService()