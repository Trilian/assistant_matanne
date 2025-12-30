"""
Service Inventaire ULTRA-OPTIMISÉ v2.0
Utilise 100% EnhancedCRUDService + unified helpers
"""
from src.core.models import ArticleInventaire

CATEGORIES = ["Légumes", "Fruits", "Féculents", "Protéines", "Laitier"]
EMPLACEMENTS = ["Frigo", "Congélateur", "Placard", "Cave"]


class InventaireService(
    BaseServiceOptimized[ArticleInventaire],
    StatusTrackingMixin,
    IngredientManagementMixin,
    ThresholdAlertingMixin,
    ExportImportMixin
):
    """
    Service Inventaire Ultra-Optimisé

    Fonctionnalités héritées:
    - CRUD complet
    - Gestion seuils (ThresholdAlertingMixin)
    - Gestion ingrédients
    - Export/Import
    """

    def __init__(self):
        super().__init__(ArticleInventaire, cache_ttl=30)

    @Cache.cached(ttl=30)
    @handle_errors(show_in_ui=False, fallback_value=[])
    def get_inventaire_complet(self, filters: Optional[Dict] = None) -> List[Dict]:
        """
        Inventaire enrichi avec statuts

        ✅ Enrichissement via mixin
        ✅ Calcul statuts en Python (plus rapide)
        """
        items = self.advanced_search(
            filters=filters,
            sort_by="ingredient_id",
            limit=1000
        )

        # ✅ Enrichissement mixin (ZÉRO duplication)
        enriched = self.enrich_with_ingredient_info(items, "ingredient_id")

        # Ajouter statuts (logique métier)
        for item in enriched:
            item["statut"], item["icone"] = self._calculer_statut(item)

        return enriched

    @staticmethod
    def _calculer_statut(article: Dict) -> tuple:
        """Calcule statut article (pure function)"""
        sous_seuil = article["quantite"] < article.get("quantite_min", 1.0)

        peremption_proche = False
        if article.get("date_peremption"):
            from datetime import date
            jours = (article["date_peremption"] - date.today()).days
            peremption_proche = 0 <= jours <= 7

        if sous_seuil and peremption_proche:
            return "critique", "🔴"
        elif peremption_proche:
            return "peremption_proche", "⏳"
        elif sous_seuil:
            return "sous_seuil", "⚠️"
        else:
            return "ok", "✅"

    @handle_errors(show_in_ui=False, fallback_value={})
    def get_alertes(self) -> Dict:
        """
        Alertes critiques

        ✅ Utilise ThresholdAlertingMixin
        """
        inventaire = self.get_inventaire_complet()

        return {
            "stock_bas": [i for i in inventaire if i["statut"] == "sous_seuil"],
            "peremption_proche": [i for i in inventaire if i["statut"] == "peremption_proche"],
            "critiques": [i for i in inventaire if i["statut"] == "critique"]
        }

    @handle_errors(show_in_ui=True)
    def ajuster_quantite(self, article_id: int, delta: float) -> Optional[float]:
        """
        Ajuste quantité

        ✅ Utilise update() hérité
        """
        article = self.get_by_id(article_id)

        if not article:
            return None

        nouvelle_quantite = max(0, article.quantite + delta)

        updated = self.update(
            article_id,
            {"quantite": nouvelle_quantite, "derniere_maj": datetime.now()}
        )

        return nouvelle_quantite if updated else None


# Instance globale
inventaire_service = InventaireService()