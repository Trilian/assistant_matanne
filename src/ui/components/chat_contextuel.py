"""
Composant Chat IA Contextuel — Chat intégré par module.

Widget réutilisable utilisant st.chat_input() + st.chat_message()
avec contexte automatique selon le module (recettes, jules, etc.).

Usage:
    from src.ui.components.chat_contextuel import afficher_chat_contextuel

    # Dans un module recettes
    afficher_chat_contextuel("recettes", context_extra={"plats_favoris": ["Pasta", "Poulet"]})

    # Dans un module jules
    afficher_chat_contextuel("jules", context_extra={"age_mois": 20})
"""

import logging
from typing import Any

import streamlit as st

from src.core.ai import obtenir_client_ia
from src.core.state import rerun
from src.services.core.base import BaseAIService
from src.services.core.registry import service_factory
from src.ui.fragments import ui_fragment
from src.ui.keys import KeyNamespace
from src.ui.registry import composant_ui

logger = logging.getLogger(__name__)

_keys = KeyNamespace("chat_ctx")

# ═══════════════════════════════════════════════════════════
# PROMPTS CONTEXTUELS PAR MODULE
# ═══════════════════════════════════════════════════════════

_PROMPTS_CONTEXTUELS = {
    "recettes": {
        "system": """Tu es l'assistant culinaire de Matanne, expert en recettes familiales.
Tu aides avec:
- 🍳 Suggestions de recettes selon les ingrédients disponibles
- 🥗 Substitutions d'ingrédients et adaptations
- ⏱️ Conseils de préparation et timing
- 🍼 Adaptation de recettes pour bébé (Jules, ~20 mois)
- 🛒 Estimation des quantités et courses

Réponds de manière concise et pratique. Si tu proposes une recette, donne les étapes clés.""",
        "suggestions": [
            "Que faire avec des courgettes ?",
            "Recette rapide pour ce soir",
            "Adapter cette recette pour bébé",
            "Substitut pour la crème fraîche",
        ],
        "placeholder": "Pose ta question cuisine...",
    },
    "jules": {
        "system": """Tu es l'assistant parental de Matanne, spécialisé dans le développement de Jules (~20 mois).
Tu aides avec:
- 🎨 Activités adaptées à son âge et développement
- 🍼 Conseils alimentation et diversification
- 😴 Sommeil, routines et rituels
- 🧸 Jouets et équipements recommandés
- 📈 Étapes de développement (motricité, langage, propreté)

Réponds avec bienveillance et expertise. Adapte tes conseils à un enfant de ~20 mois.""",
        "suggestions": [
            "Activité calme pour ce soir",
            "À quel âge la propreté ?",
            "Idée de jeu moteur",
            "Que manger à cet âge ?",
        ],
        "placeholder": "Pose ta question sur Jules...",
    },
    "famille": {
        "system": """Tu es l'assistant famille de Matanne, expert en organisation familiale.
Tu aides avec:
- 👨‍👩‍👦 Organisation de la vie familiale quotidienne
- 📅 Planification d'activités en famille
- 🏠 Conseils d'équilibre vie pro/perso
- 🎁 Idées de sorties et activités adaptées à toute la famille
- 💰 Gestion du budget familial

Réponds de manière pratique et bienveillante. Pense toujours à inclure Jules (20 mois) dans tes suggestions.""",
        "suggestions": [
            "Activité en famille ce weekend",
            "Comment organiser notre semaine",
            "Idée sortie adaptée à un bébé",
            "Conseil pour le temps écran",
        ],
        "placeholder": "Pose ta question famille...",
    },
    "planning": {
        "system": """Tu es l'assistant planning de Matanne, expert en organisation du temps.
Tu aides avec:
- 📅 Organisation des repas de la semaine
- 🛒 Planification des courses
- ⏱️ Optimisation du temps en cuisine
- 🍳 Batch cooking et préparation à l'avance
- 🎯 Gestion des priorités familiales

Réponds de manière structurée et pratique. Propose des solutions concrètes et réalistes.""",
        "suggestions": [
            "Organiser mes repas de la semaine",
            "Quand faire mes courses ?",
            "Idées de batch cooking",
            "Optimiser mon temps cuisine",
        ],
        "placeholder": "Pose ta question planning...",
    },
    "weekend": {
        "system": """Tu es l'assistant sorties de Matanne, expert en activités de weekend.
Tu aides avec:
- 🎉 Idées de sorties en famille
- 🌦️ Activités selon la météo
- 👶 Sorties adaptées à Jules (~20 mois)
- 💰 Suggestions selon le budget
- 🗺️ Découverte de nouveaux lieux

Réponds avec enthousiasme et propose des activités variées. Pense toujours à la praticité avec un enfant en bas âge.""",
        "suggestions": [
            "Sortie ce weekend avec bébé",
            "Activité par temps de pluie",
            "Idée sortie gratuite",
            "Nouveau lieu à découvrir",
        ],
        "placeholder": "Pose ta question sorties...",
    },
}


# ═══════════════════════════════════════════════════════════
# SERVICE CHAT CONTEXTUEL
# ═══════════════════════════════════════════════════════════


class ChatContextuelService(BaseAIService):
    """Service Chat contextuel avec streaming."""

    def __init__(self, contexte: str):
        super().__init__(
            client=obtenir_client_ia(),
            cache_prefix=f"chat_{contexte}",
            default_ttl=0,  # Pas de cache pour le chat
            service_name=f"chat_{contexte}",
        )
        self.contexte = contexte
        self.config = _PROMPTS_CONTEXTUELS.get(contexte, _PROMPTS_CONTEXTUELS["recettes"])

    def streamer_reponse(self, messages: list[dict], context_extra: dict | None = None):
        """Génère une réponse streaming à partir de l'historique.

        Args:
            messages: Historique de conversation [{role, content}, ...]
            context_extra: Contexte additionnel (ingrédients, âge, etc.)

        Yields:
            str: Chunks de texte pour st.write_stream()
        """
        # Construire le prompt avec contexte
        historique = ""
        for msg in messages[:-1]:
            role = "Utilisateur" if msg["role"] == "user" else "Assistant"
            historique += f"{role}: {msg['content']}\n\n"

        dernier_message = messages[-1]["content"]

        # Ajouter contexte extra si fourni
        contexte_str = ""
        if context_extra:
            contexte_str = f"\n\nContexte actuel: {context_extra}"

        prompt = f"""Historique de la conversation:
{historique}

Question actuelle:
{dernier_message}{contexte_str}

Réponds de manière utile et concise."""

        return self.call_with_streaming_sync(
            prompt=prompt,
            system_prompt=self.config["system"],
            temperature=0.7,
            max_tokens=1000,
        )


# ═══════════════════════════════════════════════════════════
# COMPOSANT UI
# ═══════════════════════════════════════════════════════════


@composant_ui(
    "data", exemple='afficher_chat_contextuel("recettes")', tags=("chat", "ia", "contextuel")
)
@ui_fragment
def afficher_chat_contextuel(
    contexte: str = "recettes",
    context_extra: dict[str, Any] | None = None,
    hauteur_max: int = 400,
) -> None:
    """Affiche un chat IA contextuel intégré.

    Args:
        contexte: Type de contexte ("recettes", "jules")
        context_extra: Données contextuelles supplémentaires
        hauteur_max: Hauteur max du conteneur de messages (px)
    """
    config = _PROMPTS_CONTEXTUELS.get(contexte, _PROMPTS_CONTEXTUELS["recettes"])

    # Clé unique pour l'historique par contexte
    sk_messages = f"chat_ctx_{contexte}_messages"

    # Initialiser l'historique
    if sk_messages not in st.session_state:
        st.session_state[sk_messages] = []

    messages: list[dict] = st.session_state[sk_messages]

    # Header compact (hidden if the global chat is visible to avoid duplicate titles)
    col1, col2 = st.columns([4, 1])
    with col1:
        if not st.session_state.get("chat_global_visible", False):
            st.markdown(f"**💬 Assistant {contexte.capitalize()}**")
    with col2:
        if st.button("🗑️", key=_keys("clear", contexte), help="Effacer"):
            st.session_state[sk_messages] = []
            rerun()

    # Suggestions rapides (si conversation vide)
    if not messages:
        st.caption("💡 Suggestions:")
        cols = st.columns(2)
        for i, suggestion in enumerate(config["suggestions"]):
            with cols[i % 2]:
                if st.button(
                    suggestion,
                    key=_keys("suggest", contexte, str(i)),
                    use_container_width=True,
                ):
                    messages.append({"role": "user", "content": suggestion})
                    rerun()

    # Conteneur scrollable pour les messages
    with st.container(height=hauteur_max if messages else 100):
        for msg in messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # Input utilisateur
    if prompt := st.chat_input(config["placeholder"], key=_keys("input", contexte)):
        messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                service = ChatContextuelService(contexte)
                response = st.write_stream(service.streamer_reponse(messages, context_extra))
                messages.append({"role": "assistant", "content": response})
            except Exception as e:
                error_msg = f"Désolé, erreur: {e}"
                st.error(error_msg)
                messages.append({"role": "assistant", "content": error_msg})
                logger.error(f"Chat contextuel {contexte} erreur: {e}")


__all__ = ["afficher_chat_contextuel", "ChatContextuelService"]
