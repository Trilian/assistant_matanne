"""
Service IA Journal Familial - Génération de résumés et récits.

Génère automatiquement:
- Résumés hebdomadaires de la vie familiale
- Anecdotes mises en forme
- Rétrospectives mensuelles
"""

from src.core.ai import obtenir_client_ia
from src.services.core.base import BaseAIService
from src.services.core.registry import service_factory


class JournalIAService(BaseAIService):
    """Service IA pour le journal familial automatique."""

    def __init__(self):
        super().__init__(
            client=obtenir_client_ia(),
            cache_prefix="journal_familial",
            default_ttl=86400,  # 24h — résumés hebdomadaires
            service_name="journal_ia",
        )

    async def generer_resume_semaine(
        self,
        *,
        evenements: list[str],
        jalons: list[str] | None = None,
        meteo_generale: str = "variable",
        humeur_famille: str = "bonne",
    ) -> str:
        """Génère un résumé narratif de la semaine familiale."""
        evenements_txt = "\n".join(f"- {e}" for e in evenements)
        jalons_txt = ""
        if jalons:
            jalons_txt = "\n\nJalons/Premières fois de Jules cette semaine:\n" + "\n".join(
                f"- {j}" for j in jalons
            )

        prompt = f"""Écris un résumé chaleureux de notre semaine familiale:

Événements de la semaine:
{evenements_txt}
{jalons_txt}

Météo générale: {meteo_generale}
Humeur générale: {humeur_famille}

📝 Format souhaité:
- Un paragraphe narratif de 4-6 phrases (comme un journal intime bienveillant)
- Mentionner les moments marquants
- Ton chaleureux, personnel, pas formel
- Si des jalons/premières fois: mise en avant spéciale
- Finir sur une note positive ou un souhait pour la semaine suivante"""

        return await self.call_with_cache(
            prompt=prompt,
            system_prompt=(
                "Tu es l'auteur du journal de famille Matanne. "
                "Tu écris avec tendresse et humour. La famille: papa, maman, "
                "et Jules (bébé). Réponds en français."
            ),
            max_tokens=500,
        )

    async def generer_retrospective_mensuelle(
        self,
        *,
        mois: str,
        resumes_semaines: list[str],
        nb_evenements: int,
        nb_jalons: int,
    ) -> str:
        """Génère une rétrospective du mois."""
        resumes_txt = "\n\n".join(f"Semaine {i + 1}:\n{r}" for i, r in enumerate(resumes_semaines))

        prompt = f"""Écris la rétrospective du mois de {mois} pour notre famille:

Résumés des semaines:
{resumes_txt}

Stats du mois:
- {nb_evenements} événements
- {nb_jalons} jalons/premières fois de Jules

📝 Format:
- 2-3 paragraphes narratifs
- Les temps forts du mois
- L'évolution de Jules
- Un bilan émotionnel
- Perspective pour le mois prochain"""

        return await self.call_with_cache(
            prompt=prompt,
            system_prompt=(
                "Tu es le chroniqueur de la famille Matanne. "
                "Écris une rétrospective mensuelle chaleureuse. Français."
            ),
            max_tokens=800,
        )

    async def mettre_en_forme_anecdote(
        self,
        *,
        texte_brut: str,
        contexte: str = "",
    ) -> str:
        """Embellit une anecdote familiale brute en texte narratif."""
        prompt = f"""Transforme cette note en une anecdote familiale bien écrite:

Note brute: {texte_brut}
{f"Contexte: {contexte}" if contexte else ""}

📝 Rédige un court texte (3-5 phrases) qui raconte ce moment avec:
- Un début qui plante le décor
- Le moment en lui-même
- Une touche d'émotion ou d'humour
Style: journal de famille, ton chaleureux."""

        return await self.call_with_cache(
            prompt=prompt,
            system_prompt=(
                "Tu es rédacteur de souvenirs de famille. "
                "Style littéraire simple et touchant. Français."
            ),
            max_tokens=300,
        )

    def stream_resume_semaine(
        self,
        *,
        evenements: list[str],
    ):
        """Version streaming du résumé hebdomadaire."""
        evenements_txt = "\n".join(f"- {e}" for e in evenements)
        prompt = f"""Résumé chaleureux de la semaine familiale:
{evenements_txt}

Format: paragraphe narratif court, ton journal intime."""

        return self.stream_response(
            prompt=prompt,
            system_prompt="Chroniqueur famille. Français, chaleureux.",
            max_tokens=400,
        )


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


@service_factory("journal_ia", tags={"famille", "ia", "journal"})
def obtenir_service_journal_ia() -> JournalIAService:
    """Factory pour le service IA journal familial (singleton via ServiceRegistry)."""
    return JournalIAService()


# Alias anglais
get_journal_ia_service = obtenir_service_journal_ia
