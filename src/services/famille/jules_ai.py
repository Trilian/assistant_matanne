"""
Service IA pour suggestions Jules (développement enfant).

Déplacé depuis src/modules/famille/jules/ai_service.py vers la couche services.
"""

from src.core.ai import obtenir_client_ia
from src.services.core.base import BaseAIService
from src.services.core.registry import service_factory


class JulesAIService(BaseAIService):
    """Service IA pour suggestions Jules.

    Note (S12): Hérite de BaseAIService uniquement. Les données DB sont
    gérées côté module, ce service est purement IA/read-heavy.
    """

    def __init__(self):
        super().__init__(
            client=obtenir_client_ia(),
            cache_prefix="jules",
            default_ttl=7200,
            service_name="jules_ai",
        )

    async def suggerer_activites(self, age_mois: int, meteo: str = "intérieur", nb: int = 3) -> str:
        """Suggère des activités adaptées à l'âge"""
        prompt = f"""Pour un enfant de {age_mois} mois, suggère {nb} activités {meteo}.

Format pour chaque activité:
🎯 [Nom de l'activité]
⏱️ Durée: X min
📝 Description: Une phrase
⏰ Bénéfice: Ce que ça développe

Activités adaptées à cet âge, stimulantes et réalisables à la maison."""

        return await self.call_with_cache(
            prompt=prompt,
            system_prompt="Tu es expert en développement de la petite enfance. Réponds en français.",
            max_tokens=600,
        )

    async def conseil_developpement(self, age_mois: int, theme: str) -> str:
        """Donne un conseil sur un thème de développement"""
        themes_detail = {
            "proprete": "l'apprentissage de la propreté et du pot",
            "sommeil": "le sommeil et les routines du coucher",
            "alimentation": "l'alimentation et l'autonomie à table",
            "langage": "le développement du langage et la parole",
            "motricite": "la motricité (marche, coordination, équilibre)",
            "social": "le développement social et la gestion des émotions",
        }

        detail = themes_detail.get(theme, theme)

        prompt = f"""Pour un enfant de {age_mois} mois, donne des conseils pratiques sur {detail}.

Inclure:
1. Ce qui est normal à cet âge
2. 3 conseils pratiques
3. Ce qu'il faut éviter
4. Quand consulter si besoin

Ton bienveillant, rassurant et pratique."""

        return await self.call_with_cache(
            prompt=prompt,
            system_prompt="Tu es pédiatre et expert en développement de l'enfant. Réponds en français de manière concise.",
            max_tokens=700,
        )

    async def suggerer_jouets(self, age_mois: int, budget: int = 30) -> str:
        """Suggère des jouets adaptés à l'âge"""
        prompt = f"""Pour un enfant de {age_mois} mois, suggère 5 jouets éducatifs avec un budget de {budget}€ max par jouet.

Format:
🎁 [Nom du jouet]
💰 Prix estimé: X€
🎯 Développe: [compétence]
📝 Pourquoi: Une phrase

Jouets sûrs, éducatifs et adaptés à cet âge."""

        return await self.call_with_cache(
            prompt=prompt,
            system_prompt="Tu es expert en jouets éducatifs pour enfants. Réponds en français.",
            max_tokens=600,
        )

    # ── Méthodes streaming (pour st.write_stream) ──

    def stream_activites(self, age_mois: int, meteo: str = "intérieur", nb: int = 3):
        """Streaming de suggestions d'activités pour st.write_stream()."""
        prompt = f"""Pour un enfant de {age_mois} mois, suggère {nb} activités {meteo}.

Format pour chaque activité:
🎯 [Nom de l'activité]
⏱️ Durée: X min
📝 Description: Une phrase
⏰ Bénéfice: Ce que ça développe

Activités adaptées à cet âge, stimulantes et réalisables à la maison."""

        return self.call_with_streaming_sync(
            prompt=prompt,
            system_prompt="Tu es expert en développement de la petite enfance. Réponds en français.",
            max_tokens=600,
        )

    def stream_conseil(self, age_mois: int, theme: str):
        """Streaming de conseils développement pour st.write_stream()."""
        themes_detail = {
            "proprete": "l'apprentissage de la propreté et du pot",
            "sommeil": "le sommeil et les routines du coucher",
            "alimentation": "l'alimentation et l'autonomie à table",
            "langage": "le développement du langage et la parole",
            "motricite": "la motricité (marche, coordination, équilibre)",
            "social": "le développement social et la gestion des émotions",
        }
        detail = themes_detail.get(theme, theme)

        prompt = f"""Pour un enfant de {age_mois} mois, donne des conseils pratiques sur {detail}.

Inclure:
1. Ce qui est normal à cet âge
2. 3 conseils pratiques
3. Ce qu'il faut éviter
4. Quand consulter si besoin

Ton bienveillant, rassurant et pratique."""

        return self.call_with_streaming_sync(
            prompt=prompt,
            system_prompt="Tu es pédiatre et expert en développement de l'enfant. Réponds en français de manière concise.",
            max_tokens=700,
        )

    def stream_jouets(self, age_mois: int, budget: int = 30):
        """Streaming de suggestions jouets pour st.write_stream()."""
        prompt = f"""Pour un enfant de {age_mois} mois, suggère 5 jouets éducatifs avec un budget de {budget}€ max par jouet.

Format:
🎁 [Nom du jouet]
💰 Prix estimé: X€
🎯 Développe: [compétence]
📝 Pourquoi: Une phrase

Jouets sûrs, éducatifs et adaptés à cet âge."""

        return self.call_with_streaming_sync(
            prompt=prompt,
            system_prompt="Tu es expert en jouets éducatifs pour enfants. Réponds en français.",
            max_tokens=600,
        )


@service_factory("jules_ai", tags={"famille", "ia", "enfant"})
def obtenir_jules_ai_service() -> JulesAIService:
    """Factory singleton pour JulesAIService."""
    return JulesAIService()


# Alias anglais
def get_jules_ai_service() -> JulesAIService:
    """English alias for obtenir_jules_ai_service."""
    return obtenir_jules_ai_service()
