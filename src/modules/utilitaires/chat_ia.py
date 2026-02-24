"""
Module Chat IA — Assistant conversationnel familial.

Interface de chat contextuel utilisant st.chat_input() + st.chat_message()
avec streaming IA via st.write_stream().

Fonctionnalités:
- Historique de conversation persistant en session
- Streaming des réponses IA (st.write_stream)
- Contexte familial automatique (Jules, planning, inventaire)
- Suggestions rapides prédéfinies
"""

import logging

import streamlit as st

from src.core.ai import obtenir_client_ia
from src.core.monitoring import profiler_rerun
from src.modules._framework import error_boundary
from src.services.core.base import BaseAIService
from src.services.core.registry import service_factory
from src.ui.keys import KeyNamespace

logger = logging.getLogger(__name__)

_keys = KeyNamespace("chat_ia")

# ═══════════════════════════════════════════════════════════
# SERVICE CHAT IA
# ═══════════════════════════════════════════════════════════

_SYSTEM_PROMPT = """Tu es Matanne, l'assistant IA familial intelligent.
Tu aides une famille française avec un enfant, Jules (environ 20 mois).

Tu peux aider avec:
- 🍽️ Recettes et planification des repas
- 🛒 Listes de courses et inventaire
- 👶 Conseils pour Jules (développement, activités, alimentation)
- 📅 Organisation du planning familial
- 🏠 Entretien de la maison et jardin
- 💰 Gestion du budget et des dépenses

Réponds de manière concise et pratique en français.
Utilise des emojis pour les rubriques.
Si tu proposes des recettes, donne les ingrédients et étapes.
"""

_SUGGESTIONS_RAPIDES = [
    "Suggère un menu pour la semaine",
    "Quelles activités pour Jules aujourd'hui ?",
    "Idée de recette rapide pour ce soir",
    "Conseils pour le sommeil de Jules",
    "Ma liste de courses essentielle",
]


class ChatIAService(BaseAIService):
    """Service Chat IA avec streaming."""

    def __init__(self):
        super().__init__(
            client=obtenir_client_ia(),
            cache_prefix="chat",
            default_ttl=0,  # Pas de cache pour le chat
            service_name="chat_ia",
        )

    def streamer_reponse(self, messages: list[dict]):
        """Génère une réponse streaming à partir de l'historique.

        Args:
            messages: Historique de conversation [{role, content}, ...]

        Yields:
            str: Chunks de texte pour st.write_stream()
        """
        # Construire le prompt complet avec historique
        historique = ""
        for msg in messages[:-1]:  # Tous sauf le dernier
            role = "Utilisateur" if msg["role"] == "user" else "Assistant"
            historique += f"{role}: {msg['content']}\n\n"

        dernier_message = messages[-1]["content"]

        prompt = f"""Historique de la conversation:
{historique}

Question actuelle de l'utilisateur:
{dernier_message}

Réponds de manière utile et concise."""

        return self.call_with_streaming_sync(
            prompt=prompt,
            system_prompt=_SYSTEM_PROMPT,
            temperature=0.7,
            max_tokens=1500,
        )


@service_factory("chat_ia", tags={"ia", "chat"})
def obtenir_chat_ia_service() -> ChatIAService:
    """Factory singleton pour ChatIAService."""
    return ChatIAService()


# ═══════════════════════════════════════════════════════════
# MODULE UI
# ═══════════════════════════════════════════════════════════

_SK_MESSAGES = "chat_ia_messages"


@profiler_rerun("chat_ia")
def app():
    """Point d'entrée module Chat IA."""

    st.title("💬 Chat IA — Assistant Matanne")
    st.caption("Pose tes questions sur les recettes, le planning, Jules, ou la maison !")

    with error_boundary("chat_ia"):
        # Initialiser l'historique
        if _SK_MESSAGES not in st.session_state:
            st.session_state[_SK_MESSAGES] = []

        messages: list[dict] = st.session_state[_SK_MESSAGES]

        # Suggestions rapides (si conversation vide)
        if not messages:
            st.markdown("##### 💡 Suggestions")
            cols = st.columns(len(_SUGGESTIONS_RAPIDES))
            for i, suggestion in enumerate(_SUGGESTIONS_RAPIDES):
                with cols[i]:
                    if st.button(
                        suggestion[:25] + "..." if len(suggestion) > 25 else suggestion,
                        key=_keys("suggest", str(i)),
                        use_container_width=True,
                        help=suggestion,
                    ):
                        messages.append({"role": "user", "content": suggestion})
                        st.rerun()

        # Afficher l'historique
        for msg in messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Input utilisateur
        if prompt := st.chat_input("Pose ta question à Matanne..."):
            # Ajouter le message utilisateur
            messages.append({"role": "user", "content": prompt})

            with st.chat_message("user"):
                st.markdown(prompt)

            # Générer la réponse en streaming
            with st.chat_message("assistant"):
                try:
                    service = obtenir_chat_ia_service()
                    response = st.write_stream(service.streamer_reponse(messages))

                    # Sauvegarder la réponse
                    messages.append({"role": "assistant", "content": response})

                except Exception as e:
                    error_msg = f"Désolé, je n'ai pas pu répondre. Erreur: {e}"
                    st.error(error_msg)
                    messages.append({"role": "assistant", "content": error_msg})
                    logger.error(f"Chat IA erreur: {e}")

        # Actions en bas
        st.markdown("---")
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("🗑️ Effacer", key=_keys("clear"), use_container_width=True):
                st.session_state[_SK_MESSAGES] = []
                st.rerun()
    with col2:
        st.caption(f"💬 {len(messages)} message(s) dans la conversation")
