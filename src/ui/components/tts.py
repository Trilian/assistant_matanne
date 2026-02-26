"""
Composant TTS (Text-to-Speech) — Lecture vocale des étapes de recette.

Utilise la Web Speech API du navigateur pour lire les instructions
de cuisine à voix haute, avec contrôle pause/reprise/stop.
"""

from __future__ import annotations

import logging

import streamlit as st

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# HTML/JS pour Web Speech API
# ═══════════════════════════════════════════════════════════

_TTS_COMPONENT_HTML = """
<div id="tts-container-{key}" style="
    display: flex; gap: 8px; align-items: center;
    padding: 8px 12px; background: #f0f2f6; border-radius: 8px;
    font-family: sans-serif; font-size: 14px;
">
    <button id="tts-play-{key}" onclick="ttsPlay_{key}()" style="
        background: #4CAF50; color: white; border: none; border-radius: 50%;
        width: 36px; height: 36px; cursor: pointer; font-size: 16px;
    ">▶️</button>
    <button id="tts-pause-{key}" onclick="ttsPause_{key}()" style="
        background: #FF9800; color: white; border: none; border-radius: 50%;
        width: 36px; height: 36px; cursor: pointer; font-size: 16px; display: none;
    ">⏸️</button>
    <button id="tts-stop-{key}" onclick="ttsStop_{key}()" style="
        background: #f44336; color: white; border: none; border-radius: 50%;
        width: 36px; height: 36px; cursor: pointer; font-size: 16px;
    ">⏹️</button>
    <span id="tts-status-{key}" style="margin-left: 8px; color: #666;">
        🎙️ Prêt à lire
    </span>
    <select id="tts-speed-{key}" onchange="ttsSetSpeed_{key}()" style="
        margin-left: auto; padding: 4px 8px; border-radius: 4px;
        border: 1px solid #ccc; font-size: 12px;
    ">
        <option value="0.7">Lent</option>
        <option value="1.0" selected>Normal</option>
        <option value="1.3">Rapide</option>
    </select>
</div>

<script>
(function() {{
    const KEY = "{key}";
    let utterance = null;
    let paused = false;
    const textes = {textes_json};
    let currentStep = 0;

    function getVoice() {{
        const voices = speechSynthesis.getVoices();
        // Chercher une voix française
        const fr = voices.find(v => v.lang.startsWith('fr'));
        return fr || voices[0];
    }}

    // S'assurer que les voix sont chargées
    if (speechSynthesis.getVoices().length === 0) {{
        speechSynthesis.addEventListener('voiceschanged', function() {{}});
    }}

    window['ttsPlay_' + KEY] = function() {{
        if (paused && utterance) {{
            speechSynthesis.resume();
            paused = false;
            updateButtons(true);
            return;
        }}

        speechSynthesis.cancel();
        readStep(currentStep);
    }};

    window['ttsPause_' + KEY] = function() {{
        speechSynthesis.pause();
        paused = true;
        updateButtons(false);
    }};

    window['ttsStop_' + KEY] = function() {{
        speechSynthesis.cancel();
        paused = false;
        currentStep = 0;
        updateButtons(false);
        document.getElementById('tts-status-' + KEY).textContent = '🎙️ Prêt à lire';
    }};

    window['ttsSetSpeed_' + KEY] = function() {{}};

    function readStep(index) {{
        if (index >= textes.length) {{
            updateButtons(false);
            document.getElementById('tts-status-' + KEY).textContent = '✅ Lecture terminée';
            currentStep = 0;
            return;
        }}

        const speed = parseFloat(document.getElementById('tts-speed-' + KEY).value);
        utterance = new SpeechSynthesisUtterance(textes[index]);
        utterance.lang = 'fr-FR';
        utterance.rate = speed;
        utterance.voice = getVoice();

        utterance.onstart = function() {{
            document.getElementById('tts-status-' + KEY).textContent =
                '🔊 Étape ' + (index + 1) + '/' + textes.length;
            updateButtons(true);
        }};

        utterance.onend = function() {{
            currentStep = index + 1;
            if (!paused) {{
                // Pause de 1s entre les étapes
                setTimeout(function() {{ readStep(currentStep); }}, 1000);
            }}
        }};

        utterance.onerror = function(e) {{
            console.error('TTS error:', e);
            document.getElementById('tts-status-' + KEY).textContent = '❌ Erreur TTS';
        }};

        speechSynthesis.speak(utterance);
    }}

    function updateButtons(playing) {{
        const playBtn = document.getElementById('tts-play-' + KEY);
        const pauseBtn = document.getElementById('tts-pause-' + KEY);

        if (playing) {{
            playBtn.style.display = 'none';
            pauseBtn.style.display = 'inline-block';
        }} else {{
            playBtn.style.display = 'inline-block';
            pauseBtn.style.display = 'none';
        }}
    }}
}})();
</script>
"""


# ═══════════════════════════════════════════════════════════
# COMPOSANT STREAMLIT
# ═══════════════════════════════════════════════════════════


def lecteur_vocal_recette(
    etapes: list[str],
    key: str = "tts_recette",
    height: int = 60,
) -> None:
    """
    Affiche un lecteur vocal pour les étapes d'une recette.

    Utilise la Web Speech API (navigateur) — pas de dépendance serveur.

    Args:
        etapes: Liste des étapes textuelles à lire
        key: Clé unique Streamlit
        height: Hauteur du composant en pixels
    """
    if not etapes:
        st.info("Pas d'étapes à lire.")
        return

    # Vérifier support TTS
    import json

    textes_json = json.dumps(etapes, ensure_ascii=False)
    html = _TTS_COMPONENT_HTML.format(key=key, textes_json=textes_json)

    st.components.v1.html(html, height=height)


def preparer_texte_recette(
    nom_recette: str,
    etapes: list[str],
    ingredients: list[str] | None = None,
) -> list[str]:
    """
    Prépare le texte optimisé pour la lecture vocale.

    Ajoute une introduction, formate les quantités en texte lisible,
    et ajoute des pauses naturelles.

    Args:
        nom_recette: Nom de la recette
        etapes: Étapes brutes
        ingredients: Ingrédients (optionnel, lus en premier)

    Returns:
        Liste de textes formatés pour TTS
    """
    textes = [f"Recette : {nom_recette}"]

    if ingredients:
        intro_ing = "Ingrédients nécessaires : " + ", ".join(ingredients[:10])
        if len(ingredients) > 10:
            intro_ing += f", et {len(ingredients) - 10} autres."
        textes.append(intro_ing)

    textes.append("C'est parti ! Commençons la préparation.")

    for i, etape in enumerate(etapes, 1):
        # Nettoyer et formater
        texte = etape.strip()
        # Remplacer les abréviations communes
        texte = texte.replace("°C", " degrés")
        texte = texte.replace("min.", " minutes")
        texte = texte.replace("c.à.s", "cuillère à soupe")
        texte = texte.replace("c.à.c", "cuillère à café")
        texte = texte.replace("cs", "cuillère à soupe")
        texte = texte.replace("cc", "cuillère à café")

        textes.append(f"Étape {i}. {texte}")

    textes.append("Et voilà, c'est prêt ! Bon appétit !")
    return textes


__all__ = [
    "lecteur_vocal_recette",
    "preparer_texte_recette",
]
