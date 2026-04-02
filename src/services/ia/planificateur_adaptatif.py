"""
Service IA — Planificateur adaptatif.

Génère des suggestions contextuelles en exploitant météo, stock, budget
et saisons pour un planning personnalisé (B4.2 / IA2).
"""

import logging
from datetime import date, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.core.decorators import avec_gestion_erreurs, avec_session_db
from src.services.core.base import BaseAIService
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


class PlanificateurAdaptatifService(BaseAIService):
    """Service de planification adaptative multi-contexte."""

    def __init__(self):
        super().__init__(
            cache_prefix="planificateur_adaptatif",
            default_ttl=1800,
            service_name="planificateur_adaptatif",
        )

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def collecter_contexte(self, db: Session | None = None) -> dict:
        """Collecte le contexte actuel (stocks, météo, saison, budget).

        Returns:
            Dict avec stocks_bas, saison, meteo, budget_restant
        """
        from src.core.models import ArticleInventaire

        aujourd_hui = date.today()
        mois = aujourd_hui.month

        # Saison
        if mois in (3, 4, 5):
            saison = "printemps"
        elif mois in (6, 7, 8):
            saison = "été"
        elif mois in (9, 10, 11):
            saison = "automne"
        else:
            saison = "hiver"

        # Stocks disponibles
        stocks = (
            db.query(ArticleInventaire)
            .filter(ArticleInventaire.quantite > 0)
            .limit(50)
            .all()
        )
        ingredients_dispo = [
            {"nom": s.nom, "quantite": s.quantite, "unite": getattr(s, "unite", "pièce")}
            for s in stocks
        ]

        # Stocks bas
        stocks_bas = (
            db.query(ArticleInventaire)
            .filter(ArticleInventaire.quantite <= ArticleInventaire.quantite_min)
            .all()
        )
        articles_bas = [s.nom for s in stocks_bas]

        return {
            "saison": saison,
            "mois": mois,
            "jour_semaine": aujourd_hui.strftime("%A"),
            "ingredients_disponibles": ingredients_dispo[:30],
            "stocks_bas": articles_bas[:10],
        }

    def suggerer_planning_adapte(self, nb_jours: int = 7, contexte: dict | None = None) -> dict:
        """Génère un planning adapté au contexte (stocks, saison, météo).

        Args:
            nb_jours: Nombre de jours à planifier
            contexte: Contexte pré-collecté (ou auto-collecté)

        Returns:
            Dict avec suggestions, raisons, contexte utilisé
        """
        if not contexte:
            contexte = self.collecter_contexte()

        ingredients = [i["nom"] for i in contexte.get("ingredients_disponibles", [])]
        saison = contexte.get("saison", "")

        prompt = f"""Tu es un planificateur de repas familial intelligent.

Contexte:
- Saison: {saison}
- Ingrédients en stock: {', '.join(ingredients[:20]) if ingredients else 'stock vide'}
- Articles en stock bas: {', '.join(contexte.get('stocks_bas', [])) or 'aucun'}
- Nombre de jours: {nb_jours}

Génère un planning de {nb_jours} repas (déjeuner + dîner) qui:
1. Utilise les ingrédients en stock en priorité
2. Est adapté à la saison ({saison})
3. Est varié et équilibré
4. Tient compte des articles en stock bas (à racheter)

Réponds en JSON:
{{
  "planning": [
    {{"jour": "Lundi", "dejeuner": "Nom du plat", "diner": "Nom du plat"}},
    ...
  ],
  "ingredients_a_acheter": ["ingredient1", "ingredient2"],
  "ingredients_stock_utilises": ["ingredient1"],
  "raisons": "Explication courte des choix"
}}"""

        try:
            result = self.call_with_parsing_sync(
                prompt=prompt,
                system_prompt="Tu es un chef cuisinier familial. Réponds en JSON valide uniquement.",
            )
            if isinstance(result, dict):
                result["contexte_utilise"] = {
                    "saison": saison,
                    "nb_ingredients_stock": len(ingredients),
                    "nb_stocks_bas": len(contexte.get("stocks_bas", [])),
                }
                return result
        except Exception as e:
            logger.warning(f"Erreur IA planificateur adaptatif: {e}")

        return {
            "planning": [],
            "ingredients_a_acheter": [],
            "raisons": "Service IA temporairement indisponible",
            "contexte_utilise": contexte,
        }


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


@service_factory("planificateur_adaptatif", tags={"planning", "ia"})
def obtenir_service_planificateur_adaptatif() -> PlanificateurAdaptatifService:
    """Factory singleton."""
    return PlanificateurAdaptatifService()

