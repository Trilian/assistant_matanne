"""
Service IA Inventaire - Analyse & Suggestions

Service IA pour :
- Analyse intelligente de l'inventaire
- Suggestions d'achats
- Détection tendances
- Optimisation stock
"""
import logging
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from src.core import (
    BaseAIService,
    InventoryAIMixin,
    obtenir_client_ia,
    handle_errors,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# SCHÉMAS PYDANTIC
# ═══════════════════════════════════════════════════════════

class AnalyseInventaire(BaseModel):
    """Résultat d'analyse inventaire."""
    articles_prioritaires: List[Dict] = Field(
        default_factory=list,
        description="Articles à commander en priorité"
    )
    alertes_peremption: List[Dict] = Field(
        default_factory=list,
        description="Articles proches de la péremption"
    )
    suggestions: List[str] = Field(
        default_factory=list,
        description="Suggestions d'optimisation"
    )
    tendances: Optional[Dict] = Field(
        None,
        description="Tendances de consommation détectées"
    )


class SuggestionAchat(BaseModel):
    """Suggestion d'article à acheter."""
    nom: str = Field(..., min_length=2)
    categorie: str
    quantite_recommandee: float = Field(..., gt=0)
    unite: str
    priorite: str = Field("moyenne", pattern="^(haute|moyenne|basse)$")
    raison: str = Field("", max_length=500)


# ═══════════════════════════════════════════════════════════
# SERVICE IA INVENTAIRE
# ═══════════════════════════════════════════════════════════

class InventaireAIService(BaseAIService, InventoryAIMixin):
    """
    Service IA pour inventaire.

    Hérite de BaseAIService + InventoryAIMixin pour accès
    aux helpers spécifiques inventaire.
    """

    def __init__(self, client=None):
        """Initialise le service IA inventaire."""
        super().__init__(
            client=client or obtenir_client_ia(),
            cache_prefix="inventaire_ai",
            default_ttl=1800,  # 30min
            default_temperature=0.7
        )

    # ═══════════════════════════════════════════════════════════
    # ANALYSE INVENTAIRE
    # ═══════════════════════════════════════════════════════════

    @handle_errors(show_in_ui=True, fallback_value=None)
    async def analyser_inventaire(
            self,
            inventaire: List[Dict],
            historique_consommation: Optional[List[Dict]] = None
    ) -> Optional[AnalyseInventaire]:
        """
        Analyse intelligente de l'inventaire.

        Args:
            inventaire: Liste complète de l'inventaire
            historique_consommation: Historique optionnel pour tendances

        Returns:
            Analyse complète avec suggestions

        Example:
            >>> analyse = await ai_service.analyser_inventaire(inventaire)
            >>> print(analyse.suggestions)
        """
        logger.info(f"Analyse inventaire: {len(inventaire)} articles")

        # Construire résumé avec mixin
        summary = self.build_inventory_summary(inventaire)

        # Ajouter contexte historique si disponible
        contexte_histo = ""
        if historique_consommation:
            contexte_histo = f"\n\nHISTORIQUE:\n{self._format_historique(historique_consommation)}"

        prompt = f"""{summary}{contexte_histo}

Analyse cet inventaire et fournis:

1. **Articles prioritaires à commander** (stock critique/sous seuil)
2. **Alertes péremption** (articles à consommer rapidement)
3. **Suggestions optimisation** (5 max)
4. **Tendances** (si historique disponible)

FORMAT JSON:
{{
  "articles_prioritaires": [
    {{
      "nom": "Nom article",
      "raison": "Stock critique: 0.5kg restants sur seuil 2kg"
    }}
  ],
  "alertes_peremption": [
    {{
      "nom": "Nom article",
      "jours_restants": 3
    }}
  ],
  "suggestions": [
    "Regrouper les articles du frigo par date de péremption",
    "Prévoir batch cooking pour utiliser tomates avant péremption"
  ],
  "tendances": {{
    "plus_consommes": ["tomates", "pâtes"],
    "peu_utilises": ["épices rares"]
  }}
}}

UNIQUEMENT JSON !"""

        try:
            analyse = await self.call_with_parsing(
                prompt=prompt,
                response_model=AnalyseInventaire,
                temperature=0.7,
                max_tokens=2000,
                use_cache=True
            )

            logger.info(
                f"✅ Analyse terminée: {len(analyse.articles_prioritaires)} prioritaires, "
                f"{len(analyse.alertes_peremption)} alertes péremption"
            )

            return analyse

        except Exception as e:
            logger.error(f"Erreur analyse inventaire: {e}")
            return self._get_fallback_analyse(inventaire)

    # ═══════════════════════════════════════════════════════════
    # SUGGESTIONS ACHATS
    # ═══════════════════════════════════════════════════════════

    @handle_errors(show_in_ui=True, fallback_value=[])
    async def suggerer_achats(
            self,
            inventaire: List[Dict],
            planning_semaine: Optional[Dict] = None
    ) -> List[SuggestionAchat]:
        """
        Suggère des articles à acheter.

        Args:
            inventaire: Inventaire actuel
            planning_semaine: Planning hebdomadaire optionnel

        Returns:
            Liste de suggestions d'achat validées
        """
        logger.info("Génération suggestions d'achats")

        # Construire contexte
        context = self.build_inventory_summary(inventaire)

        if planning_semaine:
            nb_repas = sum(len(j.get("repas", [])) for j in planning_semaine.get("jours", []))
            context += f"\n\nPLANNING: {nb_repas} repas prévus cette semaine"

        prompt = self.build_json_prompt(
            context=context,
            task="Suggère les articles à acheter en priorité",
            json_schema=self._get_schema_suggestions(),
            constraints=[
                "Prioriser articles en stock critique",
                "Tenir compte du planning si fourni",
                "Quantités réalistes pour une semaine",
                "Pas de doublons avec stock existant"
            ]
        )

        try:
            suggestions = await self.call_with_list_parsing(
                prompt=prompt,
                item_model=SuggestionAchat,
                list_key="suggestions",
                temperature=0.7,
                max_tokens=1500,
                use_cache=True,
                max_items=10
            )

            logger.info(f"✅ {len(suggestions)} suggestions générées")
            return suggestions

        except Exception as e:
            logger.error(f"Erreur suggestions achats: {e}")
            return []

    # ═══════════════════════════════════════════════════════════
    # HELPERS PRIVÉS
    # ═══════════════════════════════════════════════════════════

    def _format_historique(self, historique: List[Dict]) -> str:
        """Formate historique consommation."""
        if not historique:
            return ""

        lines = []
        for item in historique[:10]:  # Limiter à 10 derniers
            lines.append(
                f"- {item.get('nom')}: {item.get('quantite_consommee')} "
                f"{item.get('unite')} en {item.get('periode')}"
            )

        return "\n".join(lines)

    def _get_schema_suggestions(self) -> str:
        """Schéma JSON pour suggestions."""
        return """
{
  "suggestions": [
    {
      "nom": "Tomates",
      "categorie": "Légumes",
      "quantite_recommandee": 1.5,
      "unite": "kg",
      "priorite": "haute",
      "raison": "Stock critique + 3 recettes prévues cette semaine"
    }
  ]
}
"""

    def _get_fallback_analyse(self, inventaire: List[Dict]) -> AnalyseInventaire:
        """Analyse fallback basique."""
        # Articles critiques
        prioritaires = [
            {
                "nom": a["nom"],
                "raison": f"Stock bas: {a['quantite']} {a['unite']}"
            }
            for a in inventaire
            if a.get("statut") in ["critique", "sous_seuil"]
        ][:5]

        # Péremption proche
        alertes = [
            {
                "nom": a["nom"],
                "jours_restants": a.get("jours_peremption", 0)
            }
            for a in inventaire
            if a.get("jours_peremption") is not None
               and 0 <= a["jours_peremption"] <= 7
        ][:5]

        # Suggestions génériques
        suggestions = [
            "Vérifier les dates de péremption régulièrement",
            "Organiser le frigo par zones (FIFO: First In First Out)",
            "Prévoir batch cooking pour utiliser les surplus"
        ]

        return AnalyseInventaire(
            articles_prioritaires=prioritaires,
            alertes_peremption=alertes,
            suggestions=suggestions
        )


# ═══════════════════════════════════════════════════════════
# INSTANCE SINGLETON
# ═══════════════════════════════════════════════════════════

inventaire_ai_service = InventaireAIService()