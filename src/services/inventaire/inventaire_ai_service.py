"""
Service IA Inventaire - Prédictions et Analyses
Détection gaspillage, suggestions recettes, prédictions consommation
"""
import asyncio
import json
import logging
from typing import List, Dict, Optional
from datetime import date, timedelta

from src.core.ai_agent import AgentIA
from src.core.ai_cache import RateLimiter
from src.utils.formatters import format_quantity, format_quantity_with_unit

logger = logging.getLogger(__name__)


# ===================================
# SERVICE
# ===================================

class InventaireAIService:
    """Service IA pour l'inventaire"""

    def __init__(self, agent: AgentIA):
        self.agent = agent

    # ===================================
    # DÉTECTION GASPILLAGE
    # ===================================

    async def detecter_gaspillage(
            self,
            inventaire: List[Dict]
    ) -> Dict:
        """
        Analyse l'inventaire et détecte les risques de gaspillage

        Args:
            inventaire: Liste articles avec dates péremption

        Returns:
            Dict avec alertes et suggestions
        """
        logger.info("Détection gaspillage IA")

        # Filtrer items à risque
        items_risque = [
            i for i in inventaire
            if i.get("jours_peremption") is not None
               and i["jours_peremption"] <= 7
        ]

        if not items_risque:
            return {
                "statut": "OK",
                "message": "Aucun risque de gaspillage détecté",
                "recettes_urgentes": [],
                "conseils": []
            }

        # Construire prompt
        items_str = ", ".join([
            f"{i['nom']} (expire dans {i['jours_peremption']}j)"
            for i in items_risque[:10]
        ])

        prompt = f"""Analyse ces articles proches de la péremption:

ARTICLES À RISQUE:
{items_str}

TÂCHES:
1. Suggère 3 recettes RAPIDES utilisant ces ingrédients
2. Donne 2 conseils anti-gaspillage

FORMAT JSON:
{{
  "statut": "ATTENTION",
  "recettes_urgentes": [
    "Recette 1 avec X et Y",
    "Recette 2 avec X"
  ],
  "conseils": [
    "Conseil 1",
    "Conseil 2"
  ]
}}

JSON uniquement !"""

        try:
            response = await self._call_with_retry(prompt, 600)
            data = self._parse_json(response)
            data["items_risque"] = len(items_risque)
            return data

        except Exception as e:
            logger.error(f"Erreur détection gaspillage: {e}")
            return {
                "statut": "ATTENTION",
                "items_risque": len(items_risque),
                "recettes_urgentes": [f"Utiliser {items_str} rapidement"],
                "conseils": ["Consommer ou congeler rapidement"]
            }

    # ===================================
    # SUGGESTIONS RECETTES
    # ===================================

    async def suggerer_recettes_stock(
            self,
            inventaire: List[Dict],
            nb: int = 5
    ) -> List[Dict]:
        """
        Suggère des recettes faisables avec le stock actuel

        Returns:
            Liste de suggestions avec faisabilité
        """
        logger.info(f"Suggestion {nb} recettes depuis stock")

        # Filtrer items disponibles
        items_dispo = [
            f"{i['nom']} ({format_quantity(i['quantite'])} {i['unite']})"
            for i in inventaire
            if i["quantite"] > 0
        ][:30]  # Limiter pour le prompt

        if not items_dispo:
            return []

        prompt = f"""Suggère {nb} recettes FAISABLES avec ces ingrédients:

STOCK DISPONIBLE:
{chr(10).join(items_dispo)}

CONTRAINTES:
- Recettes ENTIÈREMENT faisables (sauf sel/poivre/huile)
- Varier les types
- Indiquer faisabilité en %

FORMAT JSON:
{{
  "recettes": [
    {{
      "nom": "Nom recette",
      "faisabilite": 100,
      "ingredients_utilises": ["ing1", "ing2"],
      "temps_total": 30,
      "raison": "Pourquoi cette recette"
    }}
  ]
}}

JSON uniquement !"""

        try:
            response = await self._call_with_retry(prompt, 1000)
            data = self._parse_json(response)
            return data.get("recettes", [])[:nb]

        except Exception as e:
            logger.error(f"Erreur suggestions recettes: {e}")
            return []

    # ===================================
    # PRÉDICTION CONSOMMATION
    # ===================================

    async def predire_consommation(
            self,
            article: Dict,
            historique: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Prédit quand un article sera épuisé

        Args:
            article: Article à analyser
            historique: Historique consommation (optionnel)

        Returns:
            Dict avec prédiction et recommandations
        """
        logger.info(f"Prédiction consommation: {article['nom']}")

        hist_str = ""
        if historique:
            hist_str = f"\nHISTORIQUE:\n{json.dumps(historique, indent=2, ensure_ascii=False)}"

        prompt = f"""Prédit la consommation de cet article:

ARTICLE: {article['nom']}
QUANTITÉ ACTUELLE: {article['quantite']:.1f} {article['unite']}
SEUIL: {article['seuil']:.1f}
{hist_str}

ANALYSE:
1. Estime jours avant épuisement
2. Recommande quand racheter
3. Suggère quantité optimale

FORMAT JSON:
{{
  "jours_avant_epuisement": 10,
  "date_rachat_suggeree": "2025-01-15",
  "quantite_optimale": 2.0,
  "conseil": "Racheter dans 7 jours"
}}

JSON uniquement !"""

        try:
            response = await self._call_with_retry(prompt, 500)
            return self._parse_json(response)

        except Exception as e:
            logger.error(f"Erreur prédiction: {e}")
            # Fallback simple
            jours = int((article["quantite"] / article["seuil"]) * 7)
            return {
                "jours_avant_epuisement": max(jours, 1),
                "date_rachat_suggeree": (date.today() + timedelta(days=max(jours - 2, 1))).isoformat(),
                "quantite_optimale": article["seuil"] * 2,
                "conseil": f"Racheter dans ~{max(jours - 2, 1)} jours"
            }

    # ===================================
    # ANALYSE COMPLÈTE
    # ===================================

    async def analyser_inventaire_complet(
            self,
            inventaire: List[Dict]
    ) -> Dict:
        """
        Analyse globale de l'inventaire

        Returns:
            Dict avec score, problèmes, recommandations
        """
        logger.info("Analyse complète inventaire")

        # Calculer métriques
        total = len(inventaire)
        stock_bas = len([i for i in inventaire if i["statut"] in ["sous_seuil", "critique"]])
        peremption = len([i for i in inventaire if i["statut"] in ["peremption_proche", "critique"]])

        top_items = sorted(
            inventaire,
            key=lambda x: x["quantite"] * (1 if x["statut"] == "ok" else 0.5),
            reverse=True
        )[:10]

        prompt = f"""Analyse cet inventaire:

TOTAL ARTICLES: {total}
STOCK BAS: {stock_bas}
PÉREMPTION PROCHE: {peremption}

TOP 10 ARTICLES:
{chr(10).join([f"- {i['nom']}: {format_quantity(i['quantite'])} {i['unite']} ({i['statut']})" for i in top_items])}

FOURNIS:
1. Score global (0-100)
2. 3 problèmes principaux
3. 3 recommandations

FORMAT JSON:
{{
  "score_global": 75,
  "statut": "correct",
  "problemes": [
    {{"type": "stock_bas", "article": "X", "conseil": "..."}},
  ],
  "recommandations": [
    "Recommandation 1",
    "Recommandation 2"
  ]
}}

JSON uniquement !"""

        try:
            response = await self._call_with_retry(prompt, 1000)
            return self._parse_json(response)

        except Exception as e:
            logger.error(f"Erreur analyse complète: {e}")
            return {
                "score_global": 50,
                "statut": "attention",
                "problemes": [],
                "recommandations": ["Analyse IA indisponible"]
            }

    # ===================================
    # HELPERS
    # ===================================

    async def _call_with_retry(
            self,
            prompt: str,
            max_tokens: int,
            max_retries: int = 3
    ) -> str:
        """Appel IA avec retry"""
        for attempt in range(max_retries):
            try:
                response = await self.agent._call_mistral(
                    prompt=prompt,
                    system_prompt="Expert gestion stocks alimentaires. JSON uniquement.",
                    temperature=0.7,
                    max_tokens=max_tokens
                )
                RateLimiter.record_call()
                return response
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)

    def _parse_json(self, response: str) -> Dict:
        """Parse JSON depuis réponse"""
        cleaned = response.strip()

        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]

        return json.loads(cleaned.strip())


# ===================================
# FACTORY
# ===================================

def create_inventaire_ai_service(agent: AgentIA) -> InventaireAIService:
    """Factory"""
    return InventaireAIService(agent)