"""
Service IA Inventaire ULTRA-OPTIMISÉ
"""
import logging
from typing import List, Dict, Optional
from datetime import date, timedelta
from pydantic import BaseModel, Field

from src.core.ai import AIClient, AIParser
from src.core.cache import Cache, RateLimit
from src.core.errors import handle_errors, AIServiceError
from src.utils import format_quantity_with_unit

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════
# SCHÉMAS PYDANTIC
# ═══════════════════════════════════════════════════════════════

class RecetteSuggestion(BaseModel):
    """Recette suggérée par IA"""
    nom: str = Field(..., min_length=2)
    faisabilite: int = Field(..., ge=0, le=100)
    ingredients_utilises: List[str]
    temps_total: int = Field(..., gt=0)
    raison: str


class AnalyseGaspillage(BaseModel):
    """Résultat analyse gaspillage"""
    statut: str = Field(..., pattern="^(OK|ATTENTION|CRITIQUE)$")
    items_risque: int = Field(0, ge=0)
    recettes_urgentes: List[str] = Field(default_factory=list)
    conseils: List[str] = Field(default_factory=list)


class PredictionConsommation(BaseModel):
    """Prédiction consommation"""
    jours_avant_epuisement: int = Field(..., ge=0)
    date_rachat_suggeree: str
    quantite_optimale: float = Field(..., gt=0)
    conseil: str


class AnalyseComplete(BaseModel):
    """Analyse complète inventaire"""
    score_global: int = Field(..., ge=0, le=100)
    statut: str
    problemes: List[Dict] = Field(default_factory=list)
    recommandations: List[str] = Field(default_factory=list)


# ═══════════════════════════════════════════════════════════════
# SERVICE OPTIMISÉ
# ═══════════════════════════════════════════════════════════════

class InventaireAIService:
    """Service IA inventaire ultra-optimisé"""

    def __init__(self, client: AIClient):
        self.client = client

    # ═══════════════════════════════════════════════════════════
    # DÉTECTION GASPILLAGE
    # ═══════════════════════════════════════════════════════════

    @handle_errors(show_in_ui=True)
    @Cache.cached(ttl=1800)
    async def detecter_gaspillage(self, inventaire: List[Dict]) -> AnalyseGaspillage:
        """
        Détecte risques de gaspillage

        ✅ Cache 30min
        ✅ AIJsonParser
        ✅ Fallback automatique
        """
        # Filtrer items à risque
        items_risque = [
            i for i in inventaire
            if i.get("jours_peremption") is not None and i["jours_peremption"] <= 7
        ]

        if not items_risque:
            return AnalyseGaspillage(
                statut="OK",
                message="Aucun risque détecté",
                recettes_urgentes=[],
                conseils=[]
            )

        # Prompt optimisé
        items_str = ", ".join([
            f"{i['nom']} ({i['jours_peremption']}j)"
            for i in items_risque[:10]
        ])

        prompt = f"""Articles périssables: {items_str}

Réponds en JSON:
{{
  "statut": "ATTENTION|CRITIQUE",
  "items_risque": {len(items_risque)},
  "recettes_urgentes": ["Recette 1", "Recette 2"],
  "conseils": ["Conseil 1", "Conseil 2"]
}}"""

        # ✅ Appel IA avec AIJsonParser
        response = await self.client.call(
            prompt=prompt,
            system_prompt="Expert anti-gaspillage. JSON uniquement.",
            temperature=0.7,
            max_tokens=500
        )

        return AIParser.parse(
            response,
            AnalyseGaspillage,
            fallback={
                "statut": "ATTENTION",
                "items_risque": len(items_risque),
                "recettes_urgentes": [f"Utiliser {items_str}"],
                "conseils": ["Consommer rapidement"]
            }
        )

    # ═══════════════════════════════════════════════════════════
    # SUGGESTIONS RECETTES
    # ═══════════════════════════════════════════════════════════

    @handle_errors(show_in_ui=True)
    @Cache.cached(ttl=3600)
    async def suggerer_recettes_stock(
            self,
            inventaire: List[Dict],
            nb: int = 5
    ) -> List[RecetteSuggestion]:
        """
        Suggère recettes depuis stock

        ✅ Cache 1h
        ✅ parse_list_response
        """
        items_dispo = [
            f"{i['nom']} ({format_quantity_with_unit(i['quantite'], i['unite'])})"
            for i in inventaire
            if i["quantite"] > 0
        ][:20]

        if not items_dispo:
            return []

        prompt = f"""Stock: {", ".join(items_dispo)}

{nb} recettes faisables en JSON:
{{
  "recettes": [
    {{
      "nom": "Nom",
      "faisabilite": 100,
      "ingredients_utilises": ["ing1", "ing2"],
      "temps_total": 30,
      "raison": "Pourquoi"
    }}
  ]
}}"""

        response = await self.client.call(
            prompt=prompt,
            system_prompt="Nutritionniste expert. JSON uniquement.",
            temperature=0.7,
            max_tokens=1000
        )

        # ✅ Parse liste avec helper
        from src.core.ai import parse_list_response

        return parse_list_response(
            response,
            RecetteSuggestion,
            list_key="recettes",
            fallback_items=[]
        )[:nb]

    # ═══════════════════════════════════════════════════════════
    # PRÉDICTION CONSOMMATION
    # ═══════════════════════════════════════════════════════════

    @handle_errors(show_in_ui=False)
    async def predire_consommation(
            self,
            article: Dict,
            historique: Optional[List[Dict]] = None
    ) -> PredictionConsommation:
        """
        Prédit consommation

        ✅ Fallback intelligent si IA échoue
        """
        prompt = f"""Article: {article['nom']}
Stock: {article['quantite']:.1f} {article['unite']}
Seuil: {article['seuil']:.1f}

JSON:
{{
  "jours_avant_epuisement": 10,
  "date_rachat_suggeree": "2025-01-15",
  "quantite_optimale": 2.0,
  "conseil": "Racheter dans 7j"
}}"""

        try:
            response = await self.client.call(
                prompt=prompt,
                system_prompt="Expert gestion stocks. JSON.",
                temperature=0.5,
                max_tokens=300
            )

            return AIParser.parse(
                response,
                PredictionConsommation,
                fallback=self._fallback_prediction(article)
            )

        except AIServiceError:
            # Fallback intelligent
            return self._fallback_prediction(article)

    def _fallback_prediction(self, article: Dict) -> Dict:
        """Prédiction de fallback (règle simple)"""
        jours = max(int((article["quantite"] / article["seuil"]) * 7), 1)

        return {
            "jours_avant_epuisement": jours,
            "date_rachat_suggeree": (
                    date.today() + timedelta(days=max(jours - 2, 1))
            ).isoformat(),
            "quantite_optimale": article["seuil"] * 2,
            "conseil": f"Racheter dans ~{max(jours - 2, 1)}j"
        }

    # ═══════════════════════════════════════════════════════════
    # ANALYSE COMPLÈTE
    # ═══════════════════════════════════════════════════════════

    @handle_errors(show_in_ui=True)
    @Cache.cached(ttl=1800)
    async def analyser_inventaire_complet(
            self,
            inventaire: List[Dict]
    ) -> AnalyseComplete:
        """
        Analyse globale

        ✅ Cache 30min
        ✅ Métriques calculées côté Python
        """
        # Calculs Python (plus rapide que IA)
        total = len(inventaire)
        stock_bas = len([i for i in inventaire if i["statut"] in ["sous_seuil", "critique"]])
        peremption = len([i for i in inventaire if i["statut"] in ["peremption_proche", "critique"]])

        prompt = f"""Inventaire: {total} articles
Stock bas: {stock_bas}
Péremption: {peremption}

Analyse JSON:
{{
  "score_global": 75,
  "statut": "correct|attention|critique",
  "problemes": [
    {{"type": "stock_bas", "article": "X", "conseil": "..."}}
  ],
  "recommandations": ["Recommandation 1", "Recommandation 2"]
}}"""

        response = await self.client.call(
            prompt=prompt,
            system_prompt="Expert inventaire. JSON.",
            temperature=0.7,
            max_tokens=800
        )

        return AIParser.parse(
            response,
            AnalyseComplete,
            fallback={
                "score_global": 50,
                "statut": "attention",
                "problemes": [],
                "recommandations": ["Vérifier stock bas", "Surveiller péremptions"]
            }
        )


# ═══════════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════════

def create_inventaire_ai_service(client: AIClient) -> InventaireAIService:
    """Factory pour créer le service"""
    return InventaireAIService(client)