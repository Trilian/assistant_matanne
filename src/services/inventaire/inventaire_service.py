"""
Service Inventaire - IMPORTS CORRIGÉS
"""
from datetime import date
from typing import List, Dict
from src.services.base_service import BaseService
from src.core.models import ArticleInventaire, Ingredient
from src.core.errors import handle_errors  # ✅ AJOUTÉ
from src.core.database import get_db_context  # ✅ AJOUTÉ

CATEGORIES = ["Légumes", "Fruits", "Féculents", "Protéines", "Laitier"]
EMPLACEMENTS = ["Frigo", "Congélateur", "Placard", "Cave"]


class InventaireService(BaseService[ArticleInventaire]):
    def __init__(self):
        super().__init__(ArticleInventaire, cache_ttl=30)

    @handle_errors(show_in_ui=False, fallback_value=[])
    def get_inventaire_complet(self, filters: Dict = None) -> List[Dict]:
        """Inventaire enrichi avec statuts"""
        items = self.advanced_search(filters=filters, limit=1000)

        result = []
        for item in items:
            enriched = {
                "id": item.id,
                "nom": item.ingredient.nom if item.ingredient else "?",
                "categorie": item.ingredient.categorie or "Autre",
                "quantite": item.quantite,
                "unite": item.ingredient.unite if item.ingredient else "pcs",
                "quantite_min": item.quantite_min,
                "emplacement": item.emplacement,
                "date_peremption": item.date_peremption
            }

            # Calculer statut
            sous_seuil = item.quantite < item.quantite_min
            peremption_proche = False

            if item.date_peremption:
                jours = (item.date_peremption - date.today()).days
                peremption_proche = 0 <= jours <= 7

            if sous_seuil and peremption_proche:
                enriched["statut"] = "critique"
            elif peremption_proche:
                enriched["statut"] = "peremption_proche"
            elif sous_seuil:
                enriched["statut"] = "sous_seuil"
            else:
                enriched["statut"] = "ok"

            result.append(enriched)

        return result


inventaire_service = InventaireService()