"""
Widget IA isolé — st.fragment + st.write_stream() combo.

Combine @st.fragment avec le streaming IA pour des réponses
qui ne déclenchent pas de rerun global. Chaque widget IA
(chat, suggestions, Jules) peut streamer dans son propre fragment.

Innovation 1.1 du rapport d'audit — Impact immédiat.

Usage:
    from src.ui.components.ia_fragment import (
        widget_ia_isole,
        chat_ia_fragment,
        suggestions_ia_fragment,
    )

    # Widget minimaliste
    widget_ia_isole(contexte="recettes")

    # Chat complet avec historique dans un fragment isolé
    chat_ia_fragment("jules", context_extra={"age_mois": 20})

    # Suggestions rapides (genre "Qu'est-ce qu'on mange ?")
    suggestions_ia_fragment(
        prompt="Suggère 3 recettes rapides pour ce soir",
        contexte="recettes",
    )
"""

from __future__ import annotations

import logging
from typing import Any

import streamlit as st

from src.core.state import rerun
from src.ui.fragments import _has_fragment, ui_fragment
from src.ui.keys import KeyNamespace
from src.ui.registry import composant_ui

logger = logging.getLogger(__name__)

_keys = KeyNamespace("ia_frag")

# ═══════════════════════════════════════════════════════════
# FRAGMENT IA ISOLÉ — Chat minimaliste sans rerun global
# ═══════════════════════════════════════════════════════════


def _get_chat_service(contexte: str):
    """Obtient le service chat contextuel (import différé)."""
    from src.ui.components.chat_contextuel import ChatContextuelService

    return ChatContextuelService(contexte)


@composant_ui(
    "ia",
    exemple='widget_ia_isole(contexte="recettes")',
    tags=("ia", "fragment", "streaming", "chat"),
)
def widget_ia_isole(
    contexte: str = "recettes",
    placeholder: str = "Demander à l'IA...",
    system_prompt_override: str | None = None,
    hauteur_messages: int = 300,
    afficher_suggestions: bool = True,
) -> None:
    """Widget IA isolé dans un st.fragment — pas de rerun global.

    Chaque interaction (envoi de message, réponse streaming) reste
    confinée dans le fragment, évitant de recalculer toute la page.

    Args:
        contexte: Contexte IA ("recettes", "jules", "planning", "weekend", etc.)
        placeholder: Placeholder du chat_input
        system_prompt_override: Override du system prompt (optionnel)
        hauteur_messages: Hauteur du conteneur de messages (px)
        afficher_suggestions: Afficher les suggestions rapides
    """
    if _has_fragment():
        # Wrapper dans st.fragment pour isolation complète
        @st.fragment
        def _widget_interne():
            _render_widget_ia(
                contexte=contexte,
                placeholder=placeholder,
                system_prompt_override=system_prompt_override,
                hauteur_messages=hauteur_messages,
                afficher_suggestions=afficher_suggestions,
            )

        _widget_interne()
    else:
        # Fallback sans fragment
        _render_widget_ia(
            contexte=contexte,
            placeholder=placeholder,
            system_prompt_override=system_prompt_override,
            hauteur_messages=hauteur_messages,
            afficher_suggestions=afficher_suggestions,
        )


def _render_widget_ia(
    contexte: str,
    placeholder: str,
    system_prompt_override: str | None,
    hauteur_messages: int,
    afficher_suggestions: bool,
) -> None:
    """Rendu interne du widget IA (appelé dans ou hors fragment)."""
    sk = f"ia_frag_{contexte}_messages"
    if sk not in st.session_state:
        st.session_state[sk] = []

    messages: list[dict[str, str]] = st.session_state[sk]

    # Header compact
    col_t, col_a = st.columns([4, 1])
    with col_t:
        st.markdown(f"**🤖 IA {contexte.capitalize()}** `fragment isolé`")
    with col_a:
        if st.button("🗑️", key=_keys("clear", contexte), help="Effacer"):
            st.session_state[sk] = []
            st.rerun()

    # Suggestions rapides (si vide)
    if afficher_suggestions and not messages:
        _afficher_suggestions_fragment(contexte)

    # Messages existants
    with st.container(height=hauteur_messages if messages else 100):
        for msg in messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # Input utilisateur — le streaming se fait DANS le fragment
    if prompt := st.chat_input(placeholder, key=_keys("input", contexte)):
        messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                service = _get_chat_service(contexte)

                # st.write_stream dans le fragment = pas de rerun global
                response = st.write_stream(
                    service.call_with_streaming_sync(
                        prompt=_build_prompt(messages, contexte),
                        system_prompt=(system_prompt_override or service.config.get("system", "")),
                    )
                )

                resp_text = response if isinstance(response, str) else str(response)
                messages.append({"role": "assistant", "content": resp_text})

            except Exception as e:
                error_msg = f"❌ Erreur: {e}"
                st.error(error_msg)
                messages.append({"role": "assistant", "content": error_msg})
                logger.error(f"Widget IA fragment ({contexte}): {e}")


def _build_prompt(messages: list[dict[str, str]], contexte: str) -> str:
    """Construit le prompt complet à partir de l'historique."""
    historique = ""
    for msg in messages[:-1]:
        role = "Utilisateur" if msg["role"] == "user" else "Assistant"
        historique += f"{role}: {msg['content']}\n\n"

    derniere_question = messages[-1]["content"]

    return f"""Historique:
{historique}

Question: {derniere_question}

Réponds de manière concise et utile."""


# ═══════════════════════════════════════════════════════════
# CHAT IA FRAGMENT — Version complète avec plus de features
# ═══════════════════════════════════════════════════════════


@composant_ui(
    "ia",
    exemple='chat_ia_fragment("jules", context_extra={"age_mois": 20})',
    tags=("ia", "fragment", "chat", "complet"),
)
def chat_ia_fragment(
    contexte: str = "recettes",
    context_extra: dict[str, Any] | None = None,
    titre: str | None = None,
    hauteur: int = 400,
) -> None:
    """Chat IA complet dans un fragment isolé.

    Version enrichie du widget avec :
    - Historique persistant en session
    - Suggestions contextuelles
    - Contexte supplémentaire (ingrédients, âge, etc.)
    - Streaming sans rerun global

    Args:
        contexte: Type de contexte IA
        context_extra: Données contextuelles supplémentaires
        titre: Titre personnalisé (optionnel)
        hauteur: Hauteur du conteneur
    """
    if _has_fragment():

        @st.fragment
        def _chat_interne():
            _render_chat_complet(contexte, context_extra, titre, hauteur)

        _chat_interne()
    else:
        _render_chat_complet(contexte, context_extra, titre, hauteur)


def _render_chat_complet(
    contexte: str,
    context_extra: dict[str, Any] | None,
    titre: str | None,
    hauteur: int,
) -> None:
    """Rendu du chat complet."""
    from src.ui.components.chat_contextuel import _PROMPTS_CONTEXTUELS

    config = _PROMPTS_CONTEXTUELS.get(contexte, _PROMPTS_CONTEXTUELS.get("recettes", {}))
    display_titre = titre or f"💬 Assistant {contexte.capitalize()}"

    sk = f"chat_frag_{contexte}_messages"
    if sk not in st.session_state:
        st.session_state[sk] = []

    messages: list[dict[str, str]] = st.session_state[sk]

    # Header
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.markdown(f"**{display_titre}** `fragment`")
    with col2:
        nb = len([m for m in messages if m["role"] == "user"])
        if nb:
            st.caption(f"💬 {nb} messages")
    with col3:
        if st.button("🗑️", key=_keys("chat_clear", contexte)):
            st.session_state[sk] = []
            st.rerun()

    # Suggestions
    if not messages and config.get("suggestions"):
        st.caption("💡 Suggestions:")
        cols = st.columns(2)
        for i, s in enumerate(config["suggestions"][:4]):
            with cols[i % 2]:
                if st.button(s, key=_keys("s", contexte, str(i)), use_container_width=True):
                    messages.append({"role": "user", "content": s})
                    st.rerun()

    # Messages
    with st.container(height=hauteur if messages else 120):
        for msg in messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # Input
    placeholder = config.get("placeholder", "Pose ta question...")

    if prompt := st.chat_input(placeholder, key=_keys("chat_input", contexte)):
        messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                service = _get_chat_service(contexte)
                response = st.write_stream(service.streamer_reponse(messages, context_extra))
                resp = response if isinstance(response, str) else str(response)
                messages.append({"role": "assistant", "content": resp})
            except Exception as e:
                err = f"Erreur: {e}"
                st.error(err)
                messages.append({"role": "assistant", "content": err})
                logger.error(f"Chat fragment ({contexte}): {e}")


# ═══════════════════════════════════════════════════════════
# SUGGESTIONS IA FRAGMENT — One-shot isolé
# ═══════════════════════════════════════════════════════════


@composant_ui(
    "ia",
    exemple='suggestions_ia_fragment("Suggère 3 recettes rapides")',
    tags=("ia", "fragment", "suggestions"),
)
def suggestions_ia_fragment(
    prompt: str,
    contexte: str = "recettes",
    system_prompt: str = "",
    label: str = "🤖 Suggestions IA",
    temperature: float = 0.7,
    max_tokens: int = 1000,
) -> None:
    """Génère des suggestions IA en streaming dans un fragment isolé.

    Idéal pour les boutons "Qu'est-ce qu'on mange ?" ou
    "Suggère une activité" qui ne doivent pas rerun la page.

    Args:
        prompt: Le prompt à envoyer
        contexte: Contexte IA
        system_prompt: System prompt override
        label: Label affiché pendant le streaming
        temperature: Température IA
        max_tokens: Tokens max
    """
    if _has_fragment():

        @st.fragment
        def _suggestions():
            _render_suggestions(prompt, contexte, system_prompt, label, temperature, max_tokens)

        _suggestions()
    else:
        _render_suggestions(prompt, contexte, system_prompt, label, temperature, max_tokens)


def _render_suggestions(
    prompt: str,
    contexte: str,
    system_prompt: str,
    label: str,
    temperature: float,
    max_tokens: int,
) -> None:
    """Rendu des suggestions."""
    sk_result = f"suggest_frag_{hash(prompt)}"
    sk_loading = f"suggest_frag_loading_{hash(prompt)}"

    # Bouton pour déclencher
    if st.button(f"✨ {label}", key=_keys("suggest_btn", str(hash(prompt)))):
        st.session_state[sk_loading] = True
        st.session_state.pop(sk_result, None)

    # Afficher le résultat précédent
    if sk_result in st.session_state:
        st.markdown(st.session_state[sk_result])

    # Streaming en cours
    if st.session_state.get(sk_loading):
        try:
            service = _get_chat_service(contexte)
            with st.chat_message("assistant"):
                response = st.write_stream(
                    service.call_with_streaming_sync(
                        prompt=prompt,
                        system_prompt=system_prompt,
                        temperature=temperature,
                        max_tokens=max_tokens,
                    )
                )
                resp_text = response if isinstance(response, str) else str(response)
                st.session_state[sk_result] = resp_text
                st.session_state[sk_loading] = False
        except Exception as e:
            st.error(f"Erreur: {e}")
            st.session_state[sk_loading] = False
            logger.error(f"Suggestions fragment: {e}")


# ═══════════════════════════════════════════════════════════
# SUGGESTIONS RAPIDES
# ═══════════════════════════════════════════════════════════

_SUGGESTIONS: dict[str, list[str]] = {
    "recettes": ["Recette rapide ce soir", "Idée batch cooking", "Dessert facile"],
    "jules": ["Activité calme", "Jeu moteur", "Repas adapté 20 mois"],
    "planning": ["Planifier la semaine", "Optimiser les courses"],
    "weekend": ["Sortie ce weekend", "Activité pluie"],
    "famille": ["Organiser le weekend", "Activité en famille"],
    "maison": ["Entretien du mois", "Réduire les charges"],
}


def _afficher_suggestions_fragment(contexte: str) -> None:
    """Affiche les suggestions rapides pour démarrer."""
    suggestions = _SUGGESTIONS.get(contexte, _SUGGESTIONS.get("recettes", []))
    if not suggestions:
        return

    sk = f"ia_frag_{contexte}_messages"
    st.caption("💡 Suggestions:")
    cols = st.columns(min(3, len(suggestions)))
    for i, s in enumerate(suggestions):
        with cols[i % len(cols)]:
            if st.button(s, key=_keys("quick", contexte, str(i)), use_container_width=True):
                if sk in st.session_state:
                    st.session_state[sk].append({"role": "user", "content": s})
                    st.rerun()


__all__ = [
    "widget_ia_isole",
    "chat_ia_fragment",
    "suggestions_ia_fragment",
]
