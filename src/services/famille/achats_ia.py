"""
Service IA Achats Famille - Suggestions d'achats automatiques.

Suggère via Mistral :
- Cadeaux d'anniversaire (basé sur âge, relation, historique)
- Achats saisonniers (vêtements, équipements enfant)
- Achats liés aux jalons OMS (chaussures marche, etc.)
"""

import logging

from src.core.ai import obtenir_client_ia
from src.services.core.base import BaseAIService
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


class AchatsIAService(BaseAIService):
    """Service IA pour suggestions d'achats familiaux automatiques."""

    def __init__(self):
        super().__init__(
            client=obtenir_client_ia(),
            cache_prefix="achats_famille",
            default_ttl=86400,  # 24h
            service_name="achats_ia",
        )

    async def suggerer_cadeaux_anniversaire(
        self,
        nom: str,
        age: int,
        relation: str,
        budget_max: float = 50.0,
        historique_cadeaux: list[str] | None = None,
    ) -> list[dict]:
        """Suggère des idées cadeaux pour un anniversaire."""
        historique_txt = ""
        if historique_cadeaux:
            historique_txt = f"\nCadeaux déjà offerts : {', '.join(historique_cadeaux)}"

        prompt = f"""Suggère 5 idées cadeaux pour {nom}, {age} ans, ({relation}).
Budget max : {budget_max}€.{historique_txt}

Retourne un JSON valide, une liste d'objets avec ces champs :
- titre : nom du cadeau
- description : 1-2 phrases
- fourchette_prix : "X-Y€"
- ou_acheter : suggestion de magasin/site
- pertinence : "haute", "moyenne" ou "basse"

Réponds UNIQUEMENT avec le JSON, pas de texte autour."""

        result = await self.call_with_cache(
            prompt=prompt,
            system_prompt="Tu es expert en cadeaux. Retourne UNIQUEMENT du JSON valide. Français.",
            max_tokens=800,
        )

        return self._parse_suggestions(result)

    async def suggerer_achats_saison(
        self,
        age_enfant_mois: int,
        saison: str,
        tailles: dict | None = None,
    ) -> list[dict]:
        """Suggère des achats saisonniers pour l'enfant."""
        tailles_txt = ""
        if tailles:
            tailles_txt = f"\nTailles actuelles : {tailles}"

        prompt = f"""Jules a {age_enfant_mois} mois. La saison {saison} arrive.{tailles_txt}

Quels vêtements et équipements prévoir ? Suggère 5 achats.

Retourne un JSON valide, une liste d'objets avec ces champs :
- titre : nom de l'article
- description : 1-2 phrases (pourquoi c'est nécessaire)
- fourchette_prix : "X-Y€"
- ou_acheter : suggestion de magasin/site
- pertinence : "haute", "moyenne" ou "basse"

Réponds UNIQUEMENT avec le JSON."""

        result = await self.call_with_cache(
            prompt=prompt,
            system_prompt="Tu es expert en puériculture et vêtements enfants. JSON valide uniquement. Français.",
            max_tokens=800,
        )

        return self._parse_suggestions(result)

    async def suggerer_achats_jalon(
        self,
        age_mois: int,
        prochains_jalons: list[str],
    ) -> list[dict]:
        """Suggère des achats liés aux prochains jalons de développement."""
        jalons_txt = "\n".join(f"- {j}" for j in prochains_jalons)

        prompt = f"""Jules a {age_mois} mois. Prochains jalons de développement attendus :
{jalons_txt}

Quels achats préparer pour accompagner ces étapes ? Suggère 3-5 achats pertinents.

Retourne un JSON valide, une liste d'objets avec ces champs :
- titre : nom de l'article
- description : 1-2 phrases (lien avec le jalon)
- fourchette_prix : "X-Y€"
- ou_acheter : suggestion de magasin/site
- pertinence : "haute", "moyenne" ou "basse"

Réponds UNIQUEMENT avec le JSON."""

        result = await self.call_with_cache(
            prompt=prompt,
            system_prompt="Tu es expert en développement de l'enfant et puériculture. JSON valide uniquement. Français.",
            max_tokens=600,
        )

        return self._parse_suggestions(result)

    def _parse_suggestions(self, raw_result: str) -> list[dict]:
        """Parse le résultat IA en liste de suggestions."""
        import json

        if not raw_result:
            return []

        # Nettoyer le résultat (enlever les blocs markdown)
        text = raw_result.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:])
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()

        try:
            data = json.loads(text)
            if isinstance(data, list):
                return [
                    {
                        "titre": item.get("titre", ""),
                        "description": item.get("description", ""),
                        "fourchette_prix": item.get("fourchette_prix"),
                        "ou_acheter": item.get("ou_acheter"),
                        "pertinence": item.get("pertinence", "moyenne"),
                    }
                    for item in data
                    if isinstance(item, dict) and item.get("titre")
                ]
        except json.JSONDecodeError:
            logger.warning("Impossible de parser les suggestions IA achats")

        return []


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


@service_factory("achats_ia", tags={"famille", "ia", "achats"})
def obtenir_service_achats_ia() -> AchatsIAService:
    """Factory singleton pour AchatsIAService."""
    return AchatsIAService()


# Alias anglais
get_achats_ia_service = obtenir_service_achats_ia
