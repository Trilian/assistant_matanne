"""
Chat IA Global Flottant — Assistant persistant sur toutes les pages.

Widget flottant (popover) disponible en permanence quel que soit le module.
Détecte automatiquement le contexte du module actuel et adapte
le system prompt en conséquence.

Usage (dans app.py, après page.run()):
    from src.ui.components.chat_global import afficher_chat_global
    afficher_chat_global()
"""

import logging

import streamlit as st

from src.core.state import rerun
from src.ui.keys import KeyNamespace
from src.ui.registry import composant_ui
from src.ui.utils import echapper_html

logger = logging.getLogger(__name__)

_keys = KeyNamespace("chat_global")

# ═══════════════════════════════════════════════════════════
# DÉTECTION DE CONTEXTE AUTOMATIQUE
# ═══════════════════════════════════════════════════════════

_CONTEXTES_PAR_MODULE: dict[str, str] = {
    "accueil": "general",
    "cuisine": "recettes",
    "planning": "planning",
    "famille.jules": "jules",
    "famille.weekend": "weekend",
    "famille": "famille",
    "maison": "maison",
}

_SYSTEM_PROMPTS: dict[str, dict[str, str]] = {
    "general": {
        "system": (
            "Tu es l'assistant IA de Matanne, un hub de gestion familiale.\n"
            "Tu connais tous les modules: recettes, courses, inventaire, planning,\n"
            "famille (Jules ~20 mois), maison, entretien, jardin, budget.\n"
            "Réponds de manière concise et pratique. Propose des actions concrètes."
        ),
        "placeholder": "Pose ta question...",
        "titre": "Assistant Matanne",
    },
    "recettes": {
        "system": (
            "Tu es l'assistant culinaire de Matanne.\n"
            "Tu aides avec les recettes, substitutions, batch cooking, "
            "adaptation bébé (Jules ~20 mois).\n"
            "Réponds de manière concise et pratique."
        ),
        "placeholder": "Question cuisine...",
        "titre": "Assistant Cuisine",
    },
    "planning": {
        "system": (
            "Tu es l'assistant planning de Matanne.\n"
            "Tu aides à organiser les repas de la semaine, les courses, le batch cooking.\n"
            "Réponds de manière structurée et pratique."
        ),
        "placeholder": "Question planning...",
        "titre": "Assistant Planning",
    },
    "jules": {
        "system": (
            "Tu es l'assistant parental, spécialisé dans le développement de Jules (~20 mois).\n"
            "Tu aides avec les activités, l'alimentation, le sommeil, "
            "les étapes de développement.\n"
            "Réponds avec bienveillance et expertise."
        ),
        "placeholder": "Question sur Jules...",
        "titre": "Assistant Jules",
    },
    "weekend": {
        "system": (
            "Tu es l'assistant sorties de Matanne.\n"
            "Tu aides à trouver des activités de weekend adaptées "
            "pour la famille avec Jules (~20 mois)."
        ),
        "placeholder": "Idée de sortie...",
        "titre": "Assistant Weekend",
    },
    "famille": {
        "system": (
            "Tu es l'assistant famille de Matanne.\n"
            "Tu aides avec l'organisation familiale, les activités, "
            "l'équilibre vie pro/perso.\n"
            "Pense toujours à inclure Jules (20 mois) dans tes suggestions."
        ),
        "placeholder": "Question famille...",
        "titre": "Assistant Famille",
    },
    "maison": {
        "system": (
            "Tu es l'assistant maison de Matanne.\n"
            "Tu aides avec l'entretien, le jardin, les charges, les dépenses, l'énergie.\n"
            "Réponds avec des conseils pratiques et économiques."
        ),
        "placeholder": "Question maison...",
        "titre": "Assistant Maison",
    },
}


def _detecter_contexte() -> str:
    """Détecte le contexte IA en fonction du module actuel."""
    try:
        from src.core.state import obtenir_etat

        etat = obtenir_etat()
        module = getattr(etat, "module_actuel", "accueil") or "accueil"

        # Chercher le match le plus spécifique d'abord
        for prefix, contexte in sorted(_CONTEXTES_PAR_MODULE.items(), key=lambda x: -len(x[0])):
            if module.startswith(prefix):
                return contexte

        return "general"
    except Exception:
        return "general"


# ═══════════════════════════════════════════════════════════
# SUGGESTIONS
# ═══════════════════════════════════════════════════════════

_SUGGESTIONS_PAR_CONTEXTE: dict[str, list[str]] = {
    "general": [
        "Que faire à manger ce soir ?",
        "Organiser ma semaine",
        "Idée activité avec Jules",
        "Vérifier mes stocks",
    ],
    "recettes": [
        "Recette rapide ce soir",
        "Que faire avec des restes ?",
        "Idée batch cooking",
        "Dessert facile",
    ],
    "planning": [
        "Planifier les repas de la semaine",
        "Optimiser mes courses",
        "Idées repas équilibrés",
        "Organisation batch cooking",
    ],
    "jules": [
        "Activité calme pour ce soir",
        "Idée jeu moteur",
        "Repas adapté à 20 mois",
        "Étape développement",
    ],
    "weekend": [
        "Sortie ce weekend",
        "Activité par temps de pluie",
        "Idée sortie gratuite",
        "Lieu à découvrir",
    ],
    "famille": [
        "Organiser le weekend",
        "Activité en famille",
        "Équilibre vie pro/perso",
        "Idée cadeau",
    ],
    "maison": [
        "Entretien à faire ce mois",
        "Réduire les charges",
        "Que planter ce mois ?",
        "Faire des économies",
    ],
}


# ═══════════════════════════════════════════════════════════
# COMPOSANT CHAT GLOBAL FLOTTANT
# ═══════════════════════════════════════════════════════════


@composant_ui("chat", tags=("ia", "global", "chat"))
def afficher_chat_global() -> None:
    """Affiche le chat IA global flottant en bas de page.

    Le chat est accessible via un popover Streamlit, persistant
    entre les pages. Le contexte s'adapte automatiquement au module actuel.
    """
    # Session state pour le chat global
    if "chat_global_messages" not in st.session_state:
        st.session_state.chat_global_messages = []

    messages: list[dict[str, str]] = st.session_state.chat_global_messages
    contexte = _detecter_contexte()
    config = _SYSTEM_PROMPTS.get(contexte, _SYSTEM_PROMPTS["general"])

    nb_messages = len([m for m in messages if m["role"] == "user"])
    badge_txt = f" ({nb_messages})" if nb_messages > 0 else ""

    # compteur de messages assistant non lus
    if "chat_global_unread" not in st.session_state:
        st.session_state["chat_global_unread"] = 0

    # Visibilité du chat global (remplace le popover)
    if "chat_global_visible" not in st.session_state:
        st.session_state["chat_global_visible"] = False

    if st.session_state.get("chat_global_visible"):
        _afficher_contenu_chat(messages, contexte, config)

        # Bouton fermer (plein largeur pour éviter le wrapping)
        if st.button("❌ Fermer", key=_keys("close"), use_container_width=True):
            st.session_state["chat_global_visible"] = False
            rerun()
    else:
        # Bouton d'ouverture compact
        # Réinitialiser le compteur de non lus à l'ouverture
        if st.button(
            f"💬 {config['titre']}{badge_txt}",
            key=_keys("open"),
            help="Ouvrir le chat IA",
            use_container_width=False,
        ):
            st.session_state["chat_global_visible"] = True
            st.session_state["chat_global_unread"] = 0
            rerun()


def _afficher_contenu_chat(
    messages: list[dict[str, str]],
    contexte: str,
    config: dict[str, str],
) -> None:
    """Affiche le contenu du chat dans le popover."""
    # Header avec contexte + bouton effacer
    col_titre, col_actions = st.columns([3, 1])
    with col_titre:
        st.markdown(f"**💬 {config['titre']}** · `{contexte}`")
    with col_actions:
        if st.button("🗑️", key=_keys("clear"), help="Effacer la conversation"):
            st.session_state.chat_global_messages = []
            rerun()

    # Suggestions rapides si conversation vide
    if not messages:
        _afficher_suggestions_rapides(contexte)

    # Construire HTML du drawer avec messages
    html_messages = []
    for msg in messages:
        role = msg.get("role", "assistant")
        content = echapper_html(msg.get("content", ""))
        if role == "user":
            html_messages.append(
                f'<div class="chat-msg chat-msg-user"><div class="chat-bubble">{content}</div></div>'
            )
        else:
            html_messages.append(
                f'<div class="chat-msg chat-msg-assistant"><div class="chat-bubble">{content}</div></div>'
            )

    drawer_html = (
        '<div class="chat-drawer chat-card">'
        '<div class="chat-messages">' + "".join(html_messages) + "</div>"
        "</div>"
    )

    st.markdown(drawer_html, unsafe_allow_html=True)

    # Input utilisateur via text_input (Enter pour soumettre)
    input_key = _keys("input")
    last_val_key = _keys("last_input")
    value = st.text_input(config.get("placeholder", "Pose ta question..."), key=input_key)

    # Traiter la soumission (déclenchée par Enter -> nouvelle valeur)
    if value and st.session_state.get(last_val_key) != value:
        st.session_state[last_val_key] = value
        messages.append({"role": "user", "content": value})

        try:
            from src.ui.components.chat_contextuel import ChatContextuelService

            ctx = contexte if contexte != "general" else "recettes"
            service = ChatContextuelService(ctx)
            response = st.write_stream(service.streamer_reponse(messages))
            resp_text = response if isinstance(response, str) else str(response)
            messages.append({"role": "assistant", "content": resp_text})
            # Marquer comme non-lu si le drawer n'est pas visible
            if not st.session_state.get("chat_global_visible"):
                st.session_state["chat_global_unread"] = (
                    st.session_state.get("chat_global_unread", 0) + 1
                )
            else:
                st.session_state["chat_global_unread"] = 0
        except Exception as e:
            error_msg = f"Désolé, une erreur est survenue: {e}"
            st.error(error_msg)
            messages.append({"role": "assistant", "content": error_msg})
            logger.error(f"Chat global erreur: {e}")

        # Clear input and rerun to show the assistant message in the drawer
        try:
            st.session_state[input_key] = ""
        except Exception:
            pass

        rerun()


def _afficher_suggestions_rapides(contexte: str) -> None:
    """Affiche les suggestions contextuelles pour démarrer la conversation."""
    suggestions = _SUGGESTIONS_PAR_CONTEXTE.get(contexte, _SUGGESTIONS_PAR_CONTEXTE["general"])

    st.caption("💡 Suggestions:")
    cols = st.columns(2)
    for i, suggestion in enumerate(suggestions):
        with cols[i % 2]:
            if st.button(
                suggestion,
                key=_keys("suggest", str(i)),
                use_container_width=True,
            ):
                st.session_state.chat_global_messages.append(
                    {"role": "user", "content": suggestion}
                )
                rerun()


__all__ = ["afficher_chat_global"]
