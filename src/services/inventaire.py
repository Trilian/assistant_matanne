"""
Service Inventaire Unifié (REFACTORING v2.2 - PRO)

✅ Héritage de BaseAIService (rate limiting + cache auto)
✅ Utilisation de InventoryAIMixin (contextes métier)
✅ Fix: Import RateLimitIA depuis src.core.ai
"""
import logging
from datetime import date
from typing import Dict, List, Optional
from sqlalchemy.orm import joinedload, Session
import csv
import json
from io import StringIO

from src.services.types import BaseService
from src.services.base_ai_service import BaseAIService, InventoryAIMixin

from src.core.database import obtenir_contexte_db
from src.core.errors import gerer_erreurs
from src.core.cache import Cache
from src.core.models import ArticleInventaire, Ingredient
from src.core.ai import obtenir_client_ia

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════

CATEGORIES = ["Légumes", "Fruits", "Féculents", "Protéines", "Laitier",
              "Épices & Condiments", "Conserves", "Surgelés", "Autre"]

EMPLACEMENTS = ["Frigo", "Congélateur", "Placard", "Cave", "Garde-manger"]


# ═══════════════════════════════════════════════════════════
# SERVICE INVENTAIRE UNIFIÉ
# ═══════════════════════════════════════════════════════════

class InventaireService(BaseService[ArticleInventaire], BaseAIService, InventoryAIMixin):
    """
    Service complet pour l'inventaire.
    
    ✅ Héritage multiple :
    - BaseService → CRUD optimisé
    - BaseAIService → IA avec rate limiting auto
    - InventoryAIMixin → Contextes métier inventaire
    """
    
    def __init__(self):
        BaseService.__init__(self, ArticleInventaire, cache_ttl=1800)
        BaseAIService.__init__(
            self,
            client=obtenir_client_ia(),
            cache_prefix="inventaire",
            default_ttl=1800,
            default_temperature=0.7,
            service_name="inventaire"
        )
    
    # ═══════════════════════════════════════════════════════════
    # CRUD (INCHANGÉ)
    # ═══════════════════════════════════════════════════════════
    
    @gerer_erreurs(afficher_dans_ui=False, valeur_fallback=[])
    def get_inventaire_complet(
        self,
        emplacement: Optional[str] = None,
        categorie: Optional[str] = None,
        include_ok: bool = True
    ) -> List[Dict]:
        """Récupère l'inventaire complet avec statuts calculés."""
        cache_key = f"inventaire_{emplacement}_{categorie}_{include_ok}"
        cached = Cache.obtenir(cache_key, ttl=self.cache_ttl)
        if cached:
            return cached
        
        with obtenir_contexte_db() as db:
            query = (
                db.query(ArticleInventaire)
                .options(joinedload(ArticleInventaire.ingredient))
            )
            
            if emplacement:
                query = query.filter(ArticleInventaire.emplacement == emplacement)
            
            articles = query.all()
            
            result = []
            today = date.today()
            
            for article in articles:
                statut = self._calculer_statut(article, today)
                
                if not include_ok and statut == "ok":
                    continue
                
                if categorie and article.ingredient.categorie != categorie:
                    continue
                
                result.append({
                    "id": article.id,
                    "ingredient_id": article.ingredient_id,
                    "ingredient_nom": article.ingredient.nom,
                    "ingredient_categorie": article.ingredient.categorie,
                    "quantite": article.quantite,
                    "quantite_min": article.quantite_min,
                    "unite": article.ingredient.unite,
                    "emplacement": article.emplacement,
                    "date_peremption": article.date_peremption,
                    "statut": statut,
                    "jours_avant_peremption": self._jours_avant_peremption(article, today)
                })
            
            Cache.definir(cache_key, result, ttl=self.cache_ttl, dependencies=["inventaire"])
            return result
    
    @gerer_erreurs(afficher_dans_ui=False, valeur_fallback=[])
    def get_alertes(self) -> Dict[str, List[Dict]]:
        """Récupère toutes les alertes."""
        inventaire = self.get_inventaire_complet(include_ok=False)
        
        alertes = {
            "stock_bas": [],
            "critique": [],
            "peremption_proche": []
        }
        
        for article in inventaire:
            if article["statut"] == "critique":
                alertes["critique"].append(article)
            elif article["statut"] == "stock_bas":
                alertes["stock_bas"].append(article)
            elif article["statut"] == "peremption_proche":
                alertes["peremption_proche"].append(article)
        
        return alertes
    
    # ═══════════════════════════════════════════════════════════
    # SUGGESTIONS IA (SIMPLIFIÉ !)
    # ═══════════════════════════════════════════════════════════
    
    @gerer_erreurs(afficher_dans_ui=True, valeur_fallback=[])
    async def suggerer_courses_ia(self) -> List[Dict]:
        """
        Suggère des articles à ajouter aux courses via IA.
        
        ✅ Rate limiting AUTO
        ✅ Cache AUTO
        Code réduit de 60 lignes → 20 lignes ! 🚀
        """
        # Récupérer alertes
        alertes = self.get_alertes()
        inventaire = self.get_inventaire_complet()
        
        # 🎯 Utilisation du Mixin pour résumé inventaire
        context = self.build_inventory_summary(inventaire)
        
        # Construire prompt
        prompt = self.build_json_prompt(
            context=context,
            task="Suggère 15 articles prioritaires à acheter",
            json_schema='[{"nom": str, "quantite": float, "unite": str, "priorite": str, "rayon": str}]',
            constraints=[
                "Priorité: haute/moyenne/basse",
                "Rayons magasin pour organisation",
                "Quantités réalistes",
                "Focus sur articles critiques en premier"
            ]
        )
        
        # 🚀 Appel automatique (rate limit + cache + parsing)
        from pydantic import BaseModel
        
        class SuggestionCourses(BaseModel):
            nom: str
            quantite: float
            unite: str
            priorite: str
            rayon: str
        
        suggestions = await self.call_with_list_parsing(
            prompt=prompt,
            item_model=SuggestionCourses,
            system_prompt=self.build_system_prompt(
                role="Assistant d'achat intelligent",
                expertise=["Gestion de stock", "Organisation courses"]
            ),
            max_items=15
        )
        
        return [s.dict() for s in suggestions]
    
    # ═══════════════════════════════════════════════════════════
    # HELPERS
    # ═══════════════════════════════════════════════════════════
    
    def _calculer_statut(self, article: ArticleInventaire, today: date) -> str:
        """Calcule le statut d'un article"""
        if article.date_peremption and (article.date_peremption - today).days <= 7:
            return "peremption_proche"
        
        if article.quantite < (article.quantite_min * 0.5):
            return "critique"
        
        if article.quantite < article.quantite_min:
            return "stock_bas"
        
        return "ok"
    
    def _jours_avant_peremption(self, article: ArticleInventaire, today: date) -> Optional[int]:
        """Calcule jours avant péremption"""
        if not article.date_peremption:
            return None
        return (article.date_peremption - today).days


# ═══════════════════════════════════════════════════════════
# INSTANCE SINGLETON
# ═══════════════════════════════════════════════════════════

inventaire_service = InventaireService()

__all__ = ["InventaireService", "inventaire_service", "CATEGORIES", "EMPLACEMENTS"]