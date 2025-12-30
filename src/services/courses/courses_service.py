from src.services.base_service import BaseService
from src.core.models import ArticleCourses
from typing import List, Dict

MAGASINS_CONFIG = {
    "Grand Frais": {"rayons": ["Fruits & Légumes", "Boucherie", "Fromage"], "couleur": "#4CAF50"},
    "Thiriet": {"rayons": ["Entrées", "Plats Cuisinés", "Desserts"], "couleur": "#2196F3"},
    "Cora": {"rayons": ["Fruits & Légumes", "Boucherie", "Crèmerie"], "couleur": "#FF5722"},
}

class CoursesService(BaseService[ArticleCourses]):
    def __init__(self):
        super().__init__(ArticleCourses, cache_ttl=30)

    @handle_errors(show_in_ui=False, fallback_value=[])
    def get_liste_active(self, filters: Dict = None) -> List[Dict]:
        """Liste active enrichie"""
        base_filters = {"achete": False}
        if filters:
            base_filters.update(filters)

        items = self.advanced_search(filters=base_filters, sort_by="priorite", sort_desc=True, limit=1000)

        return [
            {
                "id": item.id,
                "nom": item.ingredient.nom if item.ingredient else "?",
                "quantite": item.quantite_necessaire,
                "unite": item.ingredient.unite if item.ingredient else "pcs",
                "priorite": item.priorite,
                "magasin": item.magasin_cible,
                "rayon": item.rayon_magasin,
                "suggere_par_ia": item.suggere_par_ia,
                "notes": item.notes
            }
            for item in items
        ]

courses_service = CoursesService()