"""
Module Sorties Weekend - Service IA pour suggestions
"""

from .utils import BaseAIService, ClientIA


class WeekendAIService(BaseAIService):
    """Service IA pour suggestions weekend"""
    
    def __init__(self):
        super().__init__(
            client=ClientIA(),
            cache_prefix="weekend",
            default_ttl=3600,
            service_name="weekend_ai"
        )
    
    async def suggerer_activites(
        self, 
        meteo: str = "variable",
        age_enfant_mois: int = 19,
        budget: int = 50,
        region: str = "ÃŽle-de-France",
        nb_suggestions: int = 3
    ) -> str:
        """Suggère des activitÃes weekend"""
        
        prompt = f"""Suggère {nb_suggestions} activitÃes pour un weekend en famille avec:
- Enfant de {age_enfant_mois} mois
- MÃetÃeo prÃevue: {meteo}
- Budget max: {budget}â‚¬
- RÃegion: {region}

Pour chaque activitÃe:
ðŸŽ¯ [Nom de l'activitÃe]
ðŸ“ Type de lieu: [parc/musÃee/piscine/etc.]
â±ï¸ DurÃee recommandÃee: X heures
ðŸ’° Budget estimÃe: Xâ‚¬
ðŸ‘¶ AdaptÃe Ã  l'âge: Oui/Non + explications
ðŸŒ¤ï¸ MÃetÃeo requise: intÃerieur/extÃerieur
ðŸ“ Description: 2-3 phrases sur pourquoi c'est bien

PrivilÃegie les activitÃes:
- AdaptÃees Ã  un enfant de {age_enfant_mois} mois
- Dans le budget
- Selon la mÃetÃeo ({meteo})"""
        
        return await self.call_with_cache(
            prompt=prompt,
            system_prompt="Tu es expert en sorties familiales avec jeunes enfants en France. RÃeponds en français.",
            max_tokens=800
        )
    
    async def details_lieu(self, nom_lieu: str, type_activite: str) -> str:
        """Donne des dÃetails sur un lieu"""
        prompt = f"""Donne des informations pratiques sur {nom_lieu} ({type_activite}):

- Horaires habituels
- Tarifs (adulte, enfant, gratuit?)
- Équipements bÃebÃe (poussette, change, etc.)
- Conseils pour y aller avec un enfant de 18-24 mois
- Meilleur moment pour y aller
- Ce qu'il faut apporter"""
        
        return await self.call_with_cache(
            prompt=prompt,
            system_prompt="Tu es guide touristique spÃecialisÃe familles avec jeunes enfants.",
            max_tokens=500
        )
