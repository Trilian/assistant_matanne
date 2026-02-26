"""
Service IA Soirée Couple - Suggestions de soirées romantiques.

Suggestions basées sur:
- Budget, durée disponible
- Type de soirée souhaitée
- Disponibilité de la garde
"""

from src.core.ai import obtenir_client_ia
from src.services.core.base import BaseAIService
from src.services.core.registry import service_factory


class SoireeAIService(BaseAIService):
    """Service IA pour suggestions de soirées en couple."""

    def __init__(self):
        super().__init__(
            client=obtenir_client_ia(),
            cache_prefix="soiree_couple",
            default_ttl=7200,
            service_name="soiree_ai",
        )

    async def suggerer_soirees(
        self,
        *,
        budget: int = 80,
        duree_heures: float = 4.0,
        type_soiree: str = "variee",
        region: str = "Île-de-France",
        nb_suggestions: int = 3,
    ) -> str:
        """Suggère des idées de soirée en couple."""
        prompt = f"""Suggère {nb_suggestions} idées de soirée en amoureux:
- Budget max: {budget}€ pour deux
- Durée disponible: {duree_heures}h
- Ambiance souhaitée: {type_soiree}
- Région: {region}

Pour chaque suggestion:
❤️ [Nom / Thème de la soirée]
📍 Lieu ou activité
💰 Budget estimé: X€
⏱️ Durée: Xh
🎯 Pourquoi c'est top: 1-2 phrases
💡 Conseil pratique: 1 phrase

Types possibles: restaurant gastronomique, cinéma, spectacle, escape game,
spa/bien-être, balade nocturne, dîner maison amélioré, atelier cuisine,
dégustation vin, concert...

Varier les idées du plus simple au plus élaboré."""

        return await self.call_with_cache(
            prompt=prompt,
            system_prompt=(
                "Tu es un expert en organisation de soirées romantiques. "
                "Réponds en français avec des suggestions créatives et réalisables."
            ),
            max_tokens=700,
        )

    async def planifier_soiree_maison(
        self,
        *,
        theme: str = "romantique",
        budget: int = 40,
    ) -> str:
        """Planifie une soirée romantique à la maison."""
        prompt = f"""Planifie une soirée romantique à la maison (thème: {theme}, budget: {budget}€):

📋 Programme de la soirée:
1. Préparation (ambiance, déco)
2. Menu complet (entrée, plat, dessert) — recettes simples
3. Activité(s) à faire ensemble
4. Playlist / ambiance musicale conseillée
5. Petites attentions qui font la différence

Budget max {budget}€ tout compris (courses + éventuels achats déco).
Recettes réalisables en 1h max de préparation.
L'enfant (bébé) dort ou est gardé."""

        return await self.call_with_cache(
            prompt=prompt,
            system_prompt=(
                "Tu es expert en art de vivre et organisation d'événements intimes. "
                "Réponds en français, ton chaleureux et pratique."
            ),
            max_tokens=900,
        )

    def stream_suggestions(
        self,
        *,
        budget: int = 80,
        duree_heures: float = 4.0,
        type_soiree: str = "variee",
    ):
        """Version streaming des suggestions de soirée."""
        prompt = f"""Suggère 3 idées de soirée en amoureux:
- Budget: {budget}€
- Durée: {duree_heures}h
- Ambiance: {type_soiree}

Format: ❤️ Nom | 💰 Budget | ⏱️ Durée | Description courte"""

        return self.stream_response(
            prompt=prompt,
            system_prompt="Expert soirées romantiques. Français, concis.",
            max_tokens=500,
        )


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


@service_factory("soiree_ai", tags={"famille", "ia", "couple"})
def obtenir_service_soiree_ai() -> SoireeAIService:
    """Factory pour le service IA soirée couple (singleton via ServiceRegistry)."""
    return SoireeAIService()


# Alias anglais
get_soiree_ai_service = obtenir_service_soiree_ai
