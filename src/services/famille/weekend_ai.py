"""
Service IA pour suggestions sorties weekend.

Déplacé depuis src/modules/famille/weekend/ai_service.py vers la couche services.
"""

from src.core.ai import obtenir_client_ia
from src.services.core.base import BaseAIService
from src.services.core.registry import service_factory


class WeekendAIService(BaseAIService):
    """Service IA pour suggestions weekend"""

    def __init__(self):
        super().__init__(
            client=obtenir_client_ia(),
            cache_prefix="weekend",
            default_ttl=3600,
            service_name="weekend_ai",
        )

    async def suggerer_activites(
        self,
        meteo: str = "variable",
        age_enfant_mois: int = 19,
        budget: int = 50,
        region: str = "Île-de-France",
        nb_suggestions: int = 3,
    ) -> str:
        """Suggère des activités weekend"""

        prompt = f"""Suggère {nb_suggestions} activités pour un weekend en famille avec:
- Enfant de {age_enfant_mois} mois
- Météo prévue: {meteo}
- Budget max: {budget}€
- Région: {region}

Pour chaque activité:
🎯 [Nom de l'activité]
📝 Type de lieu: [parc/musée/piscine/etc.]
⏱️ Durée recommandée: X heures
💰 Budget estimé: X€
👶 Adapté à l'âge: Oui/Non + explications
🌤️ Météo requise: intérieur/extérieur
📝 Description: 2-3 phrases sur pourquoi c'est bien

Privilégie les activités:
- Adaptées à un enfant de {age_enfant_mois} mois
- Dans le budget
- Selon la météo ({meteo})"""

        return await self.call_with_cache(
            prompt=prompt,
            system_prompt="Tu es expert en sorties familiales avec jeunes enfants en France. Réponds en français.",
            max_tokens=800,
        )

    async def details_lieu(self, nom_lieu: str, type_activite: str) -> str:
        """Donne des détails sur un lieu"""
        prompt = f"""Donne des informations pratiques sur {nom_lieu} ({type_activite}):

- Horaires habituels
- Tarifs (adulte, enfant, gratuit?)
- Équipements bébé (poussette, change, etc.)
- Conseils pour y aller avec un enfant de 18-24 mois
- Meilleur moment pour y aller
- Ce qu'il faut apporter"""

        return await self.call_with_cache(
            prompt=prompt,
            system_prompt="Tu es guide touristique spécialisé familles avec jeunes enfants.",
            max_tokens=500,
        )

    def stream_suggestions(
        self,
        meteo: str = "variable",
        age_enfant_mois: int = 19,
        budget: int = 50,
        region: str = "Île-de-France",
        nb_suggestions: int = 3,
    ):
        """Version streaming de suggerer_activites pour st.write_stream()."""
        prompt = f"""Suggère {nb_suggestions} activités pour un weekend en famille avec:
- Enfant de {age_enfant_mois} mois
- Météo prévue: {meteo}
- Budget max: {budget}€
- Région: {region}

Pour chaque activité:
🎯 [Nom de l'activité]
📝 Type de lieu: [parc/musée/piscine/etc.]
⏱️ Durée recommandée: X heures
💰 Budget estimé: X€
👶 Adapté à l'âge: Oui/Non + explications
🌤️ Météo requise: intérieur/extérieur
📝 Description: 2-3 phrases sur pourquoi c'est bien

Privilégie les activités:
- Adaptées à un enfant de {age_enfant_mois} mois
- Dans le budget
- Selon la météo ({meteo})"""

        return self.call_with_streaming_sync(
            prompt=prompt,
            system_prompt="Tu es expert en sorties familiales avec jeunes enfants en France. Réponds en français.",
            max_tokens=800,
        )


@service_factory("weekend_ai", tags={"famille", "ia", "weekend"})
def obtenir_weekend_ai_service() -> WeekendAIService:
    """Factory singleton pour WeekendAIService."""
    return WeekendAIService()
