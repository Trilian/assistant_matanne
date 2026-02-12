"""
Module Jules - Service IA pour suggestions
"""

from .utils import BaseAIService, ClientIA


class JulesAIService(BaseAIService):
    """Service IA pour suggestions Jules"""
    
    def __init__(self):
        super().__init__(
            client=ClientIA(),
            cache_prefix="jules",
            default_ttl=7200,
            service_name="jules_ai"
        )
    
    async def suggerer_activites(self, age_mois: int, meteo: str = "intÃerieur", nb: int = 3) -> str:
        """Suggère des activitÃes adaptÃees Ã  l'âge"""
        prompt = f"""Pour un enfant de {age_mois} mois, suggère {nb} activitÃes {meteo}.

Format pour chaque activitÃe:
ðŸŽ¯ [Nom de l'activitÃe]
â±ï¸ DurÃee: X min
ðŸ“ Description: Une phrase
âœ¨ BÃenÃefice: Ce que ça dÃeveloppe

ActivitÃes adaptÃees Ã  cet âge, stimulantes et rÃealisables Ã  la maison."""
        
        return await self.call_with_cache(
            prompt=prompt,
            system_prompt="Tu es expert en dÃeveloppement de la petite enfance. RÃeponds en français.",
            max_tokens=600
        )
    
    async def conseil_developpement(self, age_mois: int, theme: str) -> str:
        """Donne un conseil sur un thème de dÃeveloppement"""
        themes_detail = {
            "proprete": "l'apprentissage de la propretÃe et du pot",
            "sommeil": "le sommeil et les routines du coucher",
            "alimentation": "l'alimentation et l'autonomie Ã  table",
            "langage": "le dÃeveloppement du langage et la parole",
            "motricite": "la motricitÃe (marche, coordination, Ãequilibre)",
            "social": "le dÃeveloppement social et la gestion des Ãemotions",
        }
        
        detail = themes_detail.get(theme, theme)
        
        prompt = f"""Pour un enfant de {age_mois} mois, donne des conseils pratiques sur {detail}.

Inclure:
1. Ce qui est normal Ã  cet âge
2. 3 conseils pratiques
3. Ce qu'il faut Ãeviter
4. Quand consulter si besoin

Ton bienveillant, rassurant et pratique."""
        
        return await self.call_with_cache(
            prompt=prompt,
            system_prompt="Tu es pÃediatre et expert en dÃeveloppement de l'enfant. RÃeponds en français de manière concise.",
            max_tokens=700
        )
    
    async def suggerer_jouets(self, age_mois: int, budget: int = 30) -> str:
        """Suggère des jouets adaptÃes Ã  l'âge"""
        prompt = f"""Pour un enfant de {age_mois} mois, suggère 5 jouets Ãeducatifs avec un budget de {budget}â‚¬ max par jouet.

Format:
ðŸŽ [Nom du jouet]
ðŸ’° Prix estimÃe: Xâ‚¬
ðŸŽ¯ DÃeveloppe: [compÃetence]
ðŸ“ Pourquoi: Une phrase

Jouets sûrs, Ãeducatifs et adaptÃes Ã  cet âge."""
        
        return await self.call_with_cache(
            prompt=prompt,
            system_prompt="Tu es expert en jouets Ãeducatifs pour enfants. RÃeponds en français.",
            max_tokens=600
        )
