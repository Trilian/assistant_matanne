"""
Service Chat IA multi-contexte.

Chat conversationnel avec contexte familial:
- Cuisine (recettes, planning, courses)
- Famille (Jules, activités, routines)
- Maison (projets, entretien, jardin)
- Budget (dépenses, analyses)
- Général (tout sujet)
"""

import logging
from typing import Any
from typing import Literal

from src.core.ai import obtenir_client_ia
from src.services.core.base import BaseAIService
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)

ContexteChat = Literal["cuisine", "famille", "maison", "budget", "general", "nutrition"]

SYSTEM_PROMPTS: dict[str, str] = {
    "cuisine": """Tu es un assistant culinaire expert pour une famille française.
Tu aides avec: recettes, planification des repas, courses, conseils nutritionnels, batch cooking.
Tu connais bien la cuisine française, méditerranéenne et les plats familiaux.
Sois concret, donne des quantités et temps précis.""",
    "nutrition": """Tu es un(e) nutritionniste diététicien(ne) expert(e) en nutrition française.
Tu aides à analyser les repas, évaluer l'équilibre nutritionnel et proposer des améliorations concrètes.
Tu maîtrises: macronutriments, micronutriments, alimentation de la petite enfance, allergies alimentaires.
Tu connais les recommandations PNNS (Programme National Nutrition Santé) et ANSES française.
Tu peux analyser un planning de repas, calculer des apports caloriques approximatifs,
identifier les carences ou excès, et proposer des alternatives saines sans sacrifier le plaisir.
Sois bienveillant(e), pratique et basé(e) sur des données scientifiques.
Précise toujours qu'il faut consulter un professionnel de santé pour un suivi personnalisé.""",
    "famille": """Tu es un assistant familial bienveillant.
Tu aides avec: activités pour enfants (Jules, ~3 ans), développement, routines, sorties weekend.
Tu connais les étapes de développement de la petite enfance et les activités Montessori.
Sois rassurant et pratique dans tes conseils.""",
    "maison": """Tu es un assistant maison et bricolage.
Tu aides avec: projets d'aménagement, entretien, jardin, réparations, décoration.
Tu donnes des conseils pratiques adaptés à des non-professionnels.
Indique le niveau de difficulté et si un professionnel est recommandé.""",
    "budget": """Tu es un conseiller en finances familiales.
Tu aides avec: gestion du budget, économies, investissements familiers, dépenses.
Tu donnes des conseils pragmatiques adaptés à une famille française.
Sois concret sur les montants et les actions possibles.""",
    "general": """Tu es un assistant familial polyvalent nommé 'Assistant Matanne'.
Tu aides une famille française avec tous les aspects de la vie quotidienne:
cuisine, enfants, maison, budget, organisation, loisirs.
Sois chaleureux, concret et utile. Réponds en français.""",
}

ACTIONS_RAPIDES: dict[str, list[dict[str, str]]] = {
    "cuisine": [
        {"label": "Idées repas semaine", "message": "Suggère un menu pour la semaine"},
        {"label": "Que faire avec mes restes ?", "message": "Comment utiliser les restes du frigo ?"},
        {"label": "Recette rapide ce soir", "message": "Propose une recette rapide pour ce soir (30 min max)"},
    ],
    "famille": [
        {"label": "Activités pour Jules", "message": "Suggère des activités adaptées pour un enfant de 3 ans"},
        {"label": "Idées week-end", "message": "Que faire en famille ce week-end ?"},
        {"label": "Routine du soir", "message": "Aide-moi à créer une routine du coucher efficace"},
    ],
    "maison": [
        {"label": "Entretien saisonnier", "message": "Quelles tâches d'entretien faire ce mois-ci ?"},
        {"label": "Projets DIY faciles", "message": "Propose un projet bricolage facile pour le week-end"},
        {"label": "Conseils jardin", "message": "Que planter dans le jardin en ce moment ?"},
    ],
    "budget": [
        {"label": "Astuces économies", "message": "Donne-moi 5 astuces pour économiser au quotidien"},
        {"label": "Budget courses", "message": "Comment réduire le budget courses alimentaires ?"},
        {"label": "Analyser mes dépenses", "message": "Comment mieux organiser mon budget familial ?"},
    ],
    "general": [
        {"label": "Organiser ma semaine", "message": "Aide-moi à organiser ma semaine efficacement"},
        {"label": "Idées sortie famille", "message": "Propose des sorties en famille pas chères"},
        {"label": "Conseils quotidien", "message": "Donne un conseil du jour pour une famille épanouie"},
    ],
    "nutrition": [
        {"label": "Analyser mon repas", "message": "Analyse la valeur nutritionnelle de ce repas pour moi"},
        {"label": "Équilibre de la semaine", "message": "Comment équilibrer mon planning repas cette semaine ?"},
        {"label": "Astuces pour Jules", "message": "Conseils nutrition pour un enfant de 3 ans qui refuse les légumes"},
        {"label": "Réduire sucre ajouté", "message": "Comment réduire le sucre dans mes recettes familiales ?"},
    ],
}


class ChatAIService(BaseAIService):
    """Service de chat IA multi-contexte."""

    def __init__(self):
        super().__init__(
            client=obtenir_client_ia(),
            cache_prefix="chat_ia",
            default_ttl=300,
            service_name="chat_ia",
        )

    def envoyer_message(
        self,
        message: str,
        contexte: ContexteChat = "general",
        historique: list[dict[str, str]] | None = None,
    ) -> str | None:
        """
        Envoie un message au chat IA et retourne la réponse.

        Args:
            message: Message de l'utilisateur
            contexte: Contexte du chat (cuisine, famille, etc.)
            historique: Messages précédents [{role: "user"|"assistant", contenu: "..."}]

        Returns:
            Réponse de l'IA ou None si échec
        """
        system_prompt = SYSTEM_PROMPTS.get(contexte, SYSTEM_PROMPTS["general"])

        # Construire le prompt avec historique
        if historique:
            conversation = "\n".join(
                f"{'Utilisateur' if m['role'] == 'user' else 'Assistant'}: {m['contenu']}"
                for m in historique[-5:]  # Memoire conversationnelle courte (IA4)
            )
            prompt = f"""Historique de la conversation:
{conversation}

Utilisateur: {message}

Réponds de manière cohérente avec la conversation précédente."""
        else:
            prompt = message

        return self.call_with_cache_sync(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=1000,
            use_cache=False,  # Pas de cache pour les messages conversationnels
        )

    def envoyer_message_contextualise(
        self,
        message: str,
        contexte_metier: dict[str, Any] | None = None,
        contexte: ContexteChat = "general",
        historique: list[dict[str, str]] | None = None,
    ) -> str | None:
        """Envoie un message IA avec contexte cross-modules injecte (IA4)."""
        system_prompt = SYSTEM_PROMPTS.get(contexte, SYSTEM_PROMPTS["general"])
        contexte_txt = (
            f"Contexte metier disponible (JSON): {contexte_metier}\n\n"
            if contexte_metier
            else ""
        )

        prompt = f"{contexte_txt}Utilisateur: {message}"

        if historique:
            conversation = "\n".join(
                f"{'Utilisateur' if m.get('role') == 'user' else 'Assistant'}: {m.get('contenu', '')}"
                for m in historique[-5:]
            )
            prompt = (
                "Historique recent (5 derniers echanges max):\n"
                f"{conversation}\n\n"
                f"{contexte_txt}Utilisateur: {message}"
            )

        return self.call_with_cache_sync(
            prompt=prompt,
            system_prompt=(
                f"{system_prompt}\n"
                "Utilise explicitement le contexte metier s'il est fourni (planning, inventaire, budget, score Jules, evenements). "
                "Si une donnee manque, dis-le clairement sans l'inventer."
            ),
            max_tokens=1200,
            use_cache=False,
        )

    def obtenir_actions_rapides(self, contexte: ContexteChat = "general") -> list[dict[str, str]]:
        """Retourne les actions rapides pour un contexte donné."""
        return ACTIONS_RAPIDES.get(contexte, ACTIONS_RAPIDES["general"])


@service_factory("chat_ia", tags={"outils", "ia", "chat"})
def obtenir_chat_ai_service() -> ChatAIService:
    """Factory singleton pour ChatAIService."""
    return ChatAIService()


# ─── Aliases rétrocompatibilité (Sprint 12 A3) ───────────────────────────────
get_chat_ai_service = obtenir_chat_ai_service  # alias rétrocompatibilité Sprint 12 A3
