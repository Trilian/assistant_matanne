"""
Service IA pour les suggestions d'entretien saisonnier.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from src.core.ai import obtenir_client_ia
from src.services.core.base import BaseAIService
from src.services.core.registry import service_factory


Saison = Literal["printemps", "été", "automne", "hiver"]


class SuggestionEntretien(BaseModel):
    """Suggestion de tâche d'entretien saisonnière."""

    nom: str = Field(..., description="Nom de la tâche")
    description: str = Field(..., description="Description détaillée")
    duree_minutes: int = Field(..., ge=5, description="Durée estimée en minutes")
    priorite: Literal["haute", "moyenne", "basse"] = Field(..., description="Priorité")
    frequence: str = Field(..., description="Fréquence recommandée (ex: annuel, mensuel)")


def _detecter_saison() -> tuple[Saison, str]:
    """Retourne la saison et l'emoji en fonction du mois courant."""
    mois = datetime.now().month
    if mois in (12, 1, 2):
        return "hiver", "❄️"
    if mois in (3, 4, 5):
        return "printemps", "🌸"
    if mois in (6, 7, 8):
        return "été", "☀️"
    return "automne", "🍂"


class EntretienIAService(BaseAIService):
    """Suggestions d'entretien saisonnier via IA."""

    def __init__(self) -> None:
        super().__init__(
            client=obtenir_client_ia(),
            cache_prefix="entretien_saisonnier",
            default_ttl=86400,  # 24h — les saisons ne changent pas vite
            service_name="entretien_ia",
        )

    def suggestions_saisonieres(self) -> dict:
        """
        Génère 5 à 7 suggestions d'entretien adaptées à la saison actuelle.
        Résultat mis en cache 24h.
        """
        saison, emoji = _detecter_saison()

        prompt = (
            f"Tu es un expert en entretien de maison familiale en France. "
            f"Nous sommes en {saison}. "
            f"Génère 5 à 7 tâches d'entretien ménager/habitat prioritaires pour cette saison. "
            f"Réponds UNIQUEMENT en JSON strict (sans markdown), avec la structure suivante:\n"
            f'{{"suggestions": ['
            f'{{"nom": "...", "description": "...", "duree_minutes": 30, "priorite": "haute|moyenne|basse", "frequence": "annuel|semestriel|mensuel"}}'
            f"]}}"
        )

        suggestions = self.call_with_list_parsing_sync(
            prompt=prompt,
            item_model=SuggestionEntretien,
            system_prompt="Tu es un expert entretien maison. Réponds uniquement en JSON valide.",
            temperature=0.4,
            max_tokens=1500,
            cache_key=f"suggestions_{saison}",
        )

        return {
            "saison": saison,
            "emoji": emoji,
            "suggestions": [s.model_dump() for s in suggestions],
        }


@service_factory("entretien_ia", tags={"maison", "entretien", "ia"})
def obtenir_service_entretien_ia() -> EntretienIAService:
    """Retourne le service IA d'entretien saisonnier."""
    return EntretienIAService()
