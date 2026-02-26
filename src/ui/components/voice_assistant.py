"""
Assistant Vocal Streamlit — Innovation 3.2.

Composant custom utilisant webkitSpeechRecognition pour la dictée vocale,
combiné avec Mistral IA pour le NLU (compréhension langage naturel).

Commandes vocales supportées:
- "Ajoute 3 tomates cerises à la liste"
- "Qu'est-ce qu'on mange ce soir ?"
- "Programme une activité samedi"
- "Combien de tomates dans le frigo ?"

Usage:
    from src.ui.components.voice_assistant import (
        bouton_vocal,
        assistant_vocal_complet,
        transcrire_et_interpreter,
    )

    # Simple bouton de dictée
    texte = bouton_vocal(key="voice_1")
    if texte:
        st.write(f"Vous avez dit: {texte}")

    # Assistant vocal complet avec interprétation IA
    assistant_vocal_complet(key="voice_main")
"""

from __future__ import annotations

import json
import logging
from typing import Any

import streamlit as st
import streamlit.components.v1 as components

logger = logging.getLogger(__name__)

__all__ = [
    "bouton_vocal",
    "assistant_vocal_complet",
    "transcrire_et_interpreter",
]


# ═══════════════════════════════════════════════════════════
# COMPOSANT JS — Speech Recognition
# ═══════════════════════════════════════════════════════════

_VOICE_HTML = """
<div id="voice-container-{key}" style="display: inline-flex; align-items: center; gap: 12px;">
    <button id="voice-btn-{key}"
        onclick="toggleRecording_{key}()"
        style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 50%;
            width: 56px;
            height: 56px;
            cursor: pointer;
            font-size: 24px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
            transition: all 0.3s ease;
            position: relative;
        "
        title="Cliquer pour parler">
        🎤
    </button>
    <div id="voice-status-{key}" style="
        font-size: 14px;
        color: #666;
        min-width: 200px;
    ">Cliquer pour parler</div>
    <div id="voice-transcript-{key}" style="display: none;"></div>
</div>

<style>
    #voice-btn-{key}.recording {{
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%) !important;
        box-shadow: 0 4px 20px rgba(255, 107, 107, 0.6) !important;
        animation: pulse-{key} 1.5s ease-in-out infinite;
    }}
    @keyframes pulse-{key} {{
        0%, 100% {{ transform: scale(1); }}
        50% {{ transform: scale(1.1); }}
    }}
    #voice-btn-{key}:hover {{
        transform: scale(1.05);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
    }}
</style>

<script>
(function() {{
    let recognition_{key} = null;
    let isRecording_{key} = false;
    let finalTranscript_{key} = '';

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {{
        document.getElementById('voice-status-{key}').textContent =
            '⚠️ Reconnaissance vocale non supportée (utilisez Chrome)';
        document.getElementById('voice-btn-{key}').disabled = true;
        document.getElementById('voice-btn-{key}').style.opacity = '0.5';
        return;
    }}

    window.toggleRecording_{key} = function() {{
        if (isRecording_{key}) {{
            stopRecording_{key}();
        }} else {{
            startRecording_{key}();
        }}
    }};

    function startRecording_{key}() {{
        finalTranscript_{key} = '';
        recognition_{key} = new SpeechRecognition();
        recognition_{key}.lang = '{lang}';
        recognition_{key}.continuous = {continuous};
        recognition_{key}.interimResults = true;
        recognition_{key}.maxAlternatives = 1;

        recognition_{key}.onstart = function() {{
            isRecording_{key} = true;
            document.getElementById('voice-btn-{key}').classList.add('recording');
            document.getElementById('voice-btn-{key}').textContent = '⏹️';
            document.getElementById('voice-status-{key}').textContent = '🔴 Écoute en cours...';
        }};

        recognition_{key}.onresult = function(event) {{
            let interim = '';
            for (let i = event.resultIndex; i < event.results.length; i++) {{
                const transcript = event.results[i][0].transcript;
                if (event.results[i].isFinal) {{
                    finalTranscript_{key} += transcript + ' ';
                }} else {{
                    interim += transcript;
                }}
            }}
            const display = finalTranscript_{key} + interim;
            document.getElementById('voice-status-{key}').textContent = display || '🔴 Écoute...';
        }};

        recognition_{key}.onerror = function(event) {{
            console.error('Speech error:', event.error);
            let msg = 'Erreur: ';
            switch(event.error) {{
                case 'no-speech': msg += 'Aucune parole détectée'; break;
                case 'audio-capture': msg += 'Pas de micro'; break;
                case 'not-allowed': msg += 'Accès micro refusé'; break;
                default: msg += event.error;
            }}
            document.getElementById('voice-status-{key}').textContent = '⚠️ ' + msg;
            stopRecording_{key}();
        }};

        recognition_{key}.onend = function() {{
            isRecording_{key} = false;
            document.getElementById('voice-btn-{key}').classList.remove('recording');
            document.getElementById('voice-btn-{key}').textContent = '🎤';

            const text = finalTranscript_{key}.trim();
            if (text) {{
                document.getElementById('voice-status-{key}').textContent = '✅ ' + text;
                // Send to Streamlit via hidden element
                document.getElementById('voice-transcript-{key}').textContent = text;
                document.getElementById('voice-transcript-{key}').style.display = 'block';

                // Send to parent (Streamlit)
                if (window.parent) {{
                    window.parent.postMessage({{
                        type: 'VOICE_TRANSCRIPT',
                        key: '{key}',
                        text: text,
                        confidence: 0.9
                    }}, '*');
                }}

                // Also set in Streamlit session state via experimental_rerun trick
                const streamlitDoc = window.parent.document;
                const hiddenInput = streamlitDoc.querySelector(
                    '[data-testid="stTextInput"] input[aria-label="voice_input_{key}"]'
                );
                if (hiddenInput) {{
                    const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
                        window.HTMLInputElement.prototype, 'value'
                    ).set;
                    nativeInputValueSetter.call(hiddenInput, text);
                    hiddenInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    hiddenInput.dispatchEvent(new Event('change', {{ bubbles: true }}));
                }}
            }} else {{
                document.getElementById('voice-status-{key}').textContent = 'Cliquer pour parler';
            }}
        }};

        try {{
            recognition_{key}.start();
        }} catch(e) {{
            document.getElementById('voice-status-{key}').textContent = '⚠️ Erreur démarrage';
        }}
    }}

    function stopRecording_{key}() {{
        if (recognition_{key}) {{
            recognition_{key}.stop();
        }}
        isRecording_{key} = false;
    }}
}})();
</script>
"""


# ═══════════════════════════════════════════════════════════
# BOUTON VOCAL SIMPLE
# ═══════════════════════════════════════════════════════════


def bouton_vocal(
    *,
    key: str = "voice",
    lang: str = "fr-FR",
    continuous: bool = False,
    height: int = 80,
) -> str | None:
    """Affiche un bouton de dictée vocale.

    Utilise webkitSpeechRecognition (Chrome/Edge) pour transcrire la voix.
    Le texte transcrit est stocké dans st.session_state.

    Args:
        key: Clé unique du composant
        lang: Langue de reconnaissance (défaut: fr-FR)
        continuous: Mode continu (plusieurs phrases)
        height: Hauteur du composant

    Returns:
        Texte transcrit ou None si pas encore de transcription
    """
    # Hidden text input to receive the transcript
    transcript_key = f"voice_input_{key}"
    transcript = st.text_input(
        f"voice_input_{key}",
        key=transcript_key,
        label_visibility="collapsed",
    )

    # Render the voice button component
    html_content = _VOICE_HTML.format(
        key=key,
        lang=lang,
        continuous="true" if continuous else "false",
    )
    components.html(html_content, height=height)

    return transcript if transcript else None


# ═══════════════════════════════════════════════════════════
# INTERPRÉTATION IA DES COMMANDES VOCALES
# ═══════════════════════════════════════════════════════════


def transcrire_et_interpreter(
    texte: str,
) -> dict[str, Any] | None:
    """Interprète une commande vocale avec l'IA Mistral.

    Analyse le texte vocal et extrait:
    - L'intention (ajouter_course, planning, recette, question, etc.)
    - Les entités (articles, quantités, dates, etc.)
    - La réponse suggérée

    Args:
        texte: Texte transcrit par la reconnaissance vocale

    Returns:
        Dict avec intention, entites, reponse ou None si erreur
    """
    if not texte or len(texte.strip()) < 2:
        return None

    try:
        from src.core.ai import obtenir_client_ia

        client = obtenir_client_ia()

        prompt_systeme = """Tu es l'assistant vocal MaTanne. Analyse la commande vocale et retourne
un JSON avec exactement ces champs:
{
    "intention": "ajouter_course|retirer_course|planning|recette|question|inventaire|autre",
    "entites": {
        "articles": [{"nom": "...", "quantite": 1, "unite": ""}],
        "date": null,
        "recette": null,
        "question": null
    },
    "reponse": "Phrase de confirmation courte",
    "confiance": 0.9
}

Exemples:
- "Ajoute 3 tomates cerises" → intention: ajouter_course, articles: [{nom: "tomates cerises", quantite: 3}]
- "Qu'est-ce qu'on mange ce soir" → intention: recette, question: "suggestion repas soir"
- "Combien de lait dans le frigo" → intention: inventaire, articles: [{nom: "lait"}]

Réponds UNIQUEMENT en JSON valide."""

        reponse = client.generer_json(
            prompt=f'Commande vocale: "{texte}"',
            system_prompt=prompt_systeme,
            temperature=0.2,
            max_tokens=500,
        )

        if isinstance(reponse, dict):
            logger.info(f"Commande vocale interprétée: {reponse.get('intention', '?')}")
            return reponse

        logger.warning(f"Réponse IA non-dict pour commande vocale: {type(reponse)}")
        return None

    except Exception as e:
        logger.error(f"Erreur interprétation vocale: {e}")
        return None


# ═══════════════════════════════════════════════════════════
# ASSISTANT VOCAL COMPLET
# ═══════════════════════════════════════════════════════════


@st.fragment
def assistant_vocal_complet(
    *,
    key: str = "voice_assistant",
) -> None:
    """Assistant vocal complet avec bouton + interprétation IA.

    Encapsulé dans @st.fragment pour ne pas rerendre toute la page.

    Args:
        key: Clé unique
    """
    st.markdown("#### 🎤 Assistant Vocal")

    col1, col2 = st.columns([1, 3])

    with col1:
        texte = bouton_vocal(key=key, continuous=True)

    with col2:
        if texte:
            st.info(f'🗣️ "{texte}"')

            # Interpréter avec IA
            with st.spinner("🤔 Analyse en cours..."):
                interpretation = transcrire_et_interpreter(texte)

            if interpretation:
                intention = interpretation.get("intention", "autre")
                reponse = interpretation.get("reponse", "")
                confiance = interpretation.get("confiance", 0)
                entites = interpretation.get("entites", {})

                # Afficher résultat
                st.success(f"💡 {reponse}")

                # Actions selon l'intention
                if intention == "ajouter_course":
                    articles = entites.get("articles", [])
                    if articles:
                        st.markdown("**Articles à ajouter:**")
                        for art in articles:
                            qte = art.get("quantite", 1)
                            unite = art.get("unite", "")
                            nom = art.get("nom", "?")
                            st.markdown(f"- {qte} {unite} {nom}")

                        if st.button(
                            "✅ Ajouter à la liste",
                            key=f"{key}_confirm_add",
                        ):
                            st.session_state[f"{key}_action"] = {
                                "type": "ajouter_course",
                                "articles": articles,
                            }
                            st.success("Ajouté à la liste!")

                elif intention == "recette":
                    question = entites.get("question", texte)
                    st.markdown(f"🍽️ Recherche: *{question}*")
                    # Le module cuisine peut lire st.session_state[f"{key}_action"]
                    st.session_state[f"{key}_action"] = {
                        "type": "recette_search",
                        "query": question,
                    }

                elif intention == "inventaire":
                    articles = entites.get("articles", [])
                    if articles:
                        st.markdown(f"📦 Vérification stock: *{articles[0].get('nom', '?')}*")
                        st.session_state[f"{key}_action"] = {
                            "type": "inventaire_check",
                            "article": articles[0].get("nom", ""),
                        }

                elif intention == "planning":
                    st.markdown("📅 Ouverture du planning...")
                    st.session_state[f"{key}_action"] = {
                        "type": "planning",
                        "date": entites.get("date"),
                    }

                # Confiance
                if confiance < 0.7:
                    st.caption(f"⚠️ Confiance: {confiance:.0%} — reformulez si nécessaire")
            else:
                st.warning("Impossible d'interpréter la commande. Réessayez.")
        else:
            st.caption(
                "Cliquez sur 🎤 et dites votre commande.\n\n"
                "Exemples:\n"
                '- "Ajoute du lait et des œufs"\n'
                "- \"Qu'est-ce qu'on mange ce soir ?\"\n"
                '- "Combien de tomates dans le frigo ?"'
            )
