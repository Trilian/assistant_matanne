"""
Audio Input — Innovation v11: st.experimental_audio_input() natif.

Composant qui utilise st.audio_input() (Streamlit ≥ 1.33) pour capturer
l'audio du microphone, puis le transcrit via Whisper/Mistral.

Ajoute une couche d'interprétation NLU pour les commandes vocales
permettant l'ajout rapide de recettes, courses, etc.

Usage:
    from src.ui.components.audio_input import (
        capture_audio,
        transcrire_audio,
        commande_vocale_rapide,
    )

    # Capture et transcription simple
    audio_data = capture_audio(key="mon_audio")
    if audio_data:
        texte = transcrire_audio(audio_data)
        st.write(f"Transcription: {texte}")

    # Commande vocale complète avec interprétation IA
    commande_vocale_rapide(
        callback_courses=ajouter_a_liste,
        callback_recettes=rechercher_recette,
    )
"""

from __future__ import annotations

import base64
import io
import logging
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable

import streamlit as st

if TYPE_CHECKING:
    from pydub import AudioSegment

logger = logging.getLogger(__name__)

__all__ = [
    "capture_audio",
    "transcrire_audio",
    "commande_vocale_rapide",
    "AudioInputWidget",
]


# ═══════════════════════════════════════════════════════════
# CAPTURE AUDIO — st.audio_input() natif
# ═══════════════════════════════════════════════════════════


def capture_audio(
    *,
    key: str = "audio_input",
    label: str = "🎙️ Enregistrer un message vocal",
) -> bytes | None:
    """Capture audio via st.audio_input() natif Streamlit.

    Utilise le widget natif Streamlit (disponible depuis v1.33+)
    qui gère automatiquement:
    - Permissions microphone navigateur
    - Encodage WebM/WAV
    - Interface utilisateur native

    Args:
        key: Clé unique du widget
        label: Label affiché

    Returns:
        Bytes audio (WAV/WebM) ou None si pas d'enregistrement
    """
    try:
        # st.audio_input disponible depuis Streamlit 1.33+
        audio_data = st.audio_input(label, key=key)

        if audio_data is not None:
            # audio_data est un UploadedFile-like object
            return audio_data.read()
        return None

    except AttributeError:
        # Fallback pour versions antérieures
        st.warning(
            "⚠️ st.audio_input() nécessite Streamlit ≥ 1.33. Utilisez le bouton vocal classique."
        )
        return None


def _convertir_audio_wav(audio_bytes: bytes) -> bytes:
    """Convertit l'audio en WAV 16kHz mono pour transcription.

    Args:
        audio_bytes: Audio brut (WebM, WAV, MP3, etc.)

    Returns:
        Bytes WAV 16kHz mono
    """
    try:
        from pydub import AudioSegment

        # Charger l'audio
        audio: AudioSegment = AudioSegment.from_file(io.BytesIO(audio_bytes))

        # Convertir en WAV 16kHz mono
        audio = audio.set_frame_rate(16000).set_channels(1)

        # Exporter en WAV
        buffer = io.BytesIO()
        audio.export(buffer, format="wav")
        return buffer.getvalue()

    except ImportError:
        logger.warning("pydub non installé, audio non converti")
        return audio_bytes
    except Exception as e:
        logger.error(f"Erreur conversion audio: {e}")
        return audio_bytes


# ═══════════════════════════════════════════════════════════
# TRANSCRIPTION — Whisper via Mistral ou local
# ═══════════════════════════════════════════════════════════


def transcrire_audio(
    audio_bytes: bytes,
    *,
    methode: str = "mistral",
    langue: str = "fr",
) -> str | None:
    """Transcrit l'audio en texte.

    Supporte plusieurs méthodes:
    - "mistral": Via l'API Mistral (si disponible audio-to-text)
    - "whisper_local": Whisper local (openai-whisper)
    - "whisper_api": Via OpenAI Whisper API

    Args:
        audio_bytes: Audio brut
        methode: Méthode de transcription
        langue: Langue cible (fr, en, etc.)

    Returns:
        Texte transcrit ou None si erreur
    """
    if not audio_bytes:
        return None

    # Convertir en WAV optimisé
    wav_bytes = _convertir_audio_wav(audio_bytes)

    if methode == "whisper_local":
        return _transcrire_whisper_local(wav_bytes, langue)
    elif methode == "whisper_api":
        return _transcrire_whisper_api(wav_bytes, langue)
    else:
        # Default: Mistral avec fallback
        return _transcrire_mistral(wav_bytes, langue)


def _transcrire_whisper_local(audio_bytes: bytes, langue: str) -> str | None:
    """Transcription via Whisper local."""
    try:
        import whisper

        # Sauvegarder temporairement
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(audio_bytes)
            temp_path = f.name

        # Charger modèle (cached)
        model = whisper.load_model("base")

        # Transcrire
        result = model.transcribe(temp_path, language=langue)

        # Nettoyer
        Path(temp_path).unlink(missing_ok=True)

        return result.get("text", "").strip()

    except ImportError:
        logger.warning("whisper non installé")
        return None
    except Exception as e:
        logger.error(f"Erreur Whisper local: {e}")
        return None


def _transcrire_whisper_api(audio_bytes: bytes, langue: str) -> str | None:
    """Transcription via OpenAI Whisper API."""
    try:
        from openai import OpenAI

        client = OpenAI()

        # Créer un fichier-like object
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "audio.wav"

        response = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language=langue,
        )

        return response.text.strip()

    except ImportError:
        logger.warning("openai non installé")
        return None
    except Exception as e:
        logger.error(f"Erreur Whisper API: {e}")
        return None


def _transcrire_mistral(audio_bytes: bytes, langue: str) -> str | None:
    """Transcription via Mistral (si audio supporté) ou fallback Whisper."""
    # Mistral n'a pas encore d'API audio native publique
    # Fallback sur Whisper local
    result = _transcrire_whisper_local(audio_bytes, langue)
    if result:
        return result

    # Dernier recours: Whisper API
    return _transcrire_whisper_api(audio_bytes, langue)


# ═══════════════════════════════════════════════════════════
# NLU — Interprétation des commandes vocales
# ═══════════════════════════════════════════════════════════


def interpreter_commande(texte: str) -> dict[str, Any]:
    """Interprète une commande vocale avec l'IA.

    Extrait:
    - intention: ajouter_course, rechercher_recette, planning, question
    - entites: articles, dates, quantités
    - reponse: confirmation pour l'utilisateur

    Args:
        texte: Texte transcrit

    Returns:
        Dict avec intention, entites, reponse
    """
    if not texte or len(texte.strip()) < 3:
        return {"intention": "vide", "entites": {}, "reponse": ""}

    try:
        from src.core.ai import obtenir_client_ia

        client = obtenir_client_ia()

        system_prompt = """Tu es l'assistant vocal MaTanne. Analyse la commande et retourne un JSON:
{
    "intention": "ajouter_course|retirer_course|rechercher_recette|planning|inventaire|question|autre",
    "entites": {
        "articles": [{"nom": "string", "quantite": 1, "unite": ""}],
        "recette": "nom ou null",
        "date": "YYYY-MM-DD ou null",
        "question": "reformulée ou null"
    },
    "reponse": "Confirmation courte et naturelle",
    "confiance": 0.0 à 1.0
}

Exemples:
- "Ajoute 500g de farine et 3 œufs" → ajouter_course, articles: [farine 500g, œufs x3]
- "Comment faire une quiche" → rechercher_recette, recette: "quiche"
- "Qu'est-ce qu'on mange samedi" → planning, date: samedi prochain

Réponds UNIQUEMENT en JSON valide."""

        result = client.generer_json(
            prompt=f'Commande vocale: "{texte}"',
            system_prompt=system_prompt,
            temperature=0.1,
            max_tokens=500,
        )

        if isinstance(result, dict):
            return result

        return {"intention": "autre", "entites": {}, "reponse": texte}

    except Exception as e:
        logger.error(f"Erreur interprétation: {e}")
        return {"intention": "erreur", "entites": {}, "reponse": str(e)}


# ═══════════════════════════════════════════════════════════
# WIDGET COMPLET — Commande vocale rapide
# ═══════════════════════════════════════════════════════════


class AudioInputWidget:
    """Widget complet de commande vocale avec traitement.

    Encapsule capture → transcription → interprétation → action.

    Usage:
        widget = AudioInputWidget(key="vocal_courses")
        widget.on_course(lambda articles: ajouter_a_liste(articles))
        widget.on_recette(lambda nom: rechercher_recette(nom))
        widget.render()
    """

    def __init__(self, key: str = "audio_widget"):
        self.key = key
        self._callbacks: dict[str, Callable] = {}

    def on_course(self, callback: Callable[[list[dict]], None]) -> AudioInputWidget:
        """Callback quand l'intention est ajouter_course."""
        self._callbacks["ajouter_course"] = callback
        return self

    def on_recette(self, callback: Callable[[str], None]) -> AudioInputWidget:
        """Callback quand l'intention est rechercher_recette."""
        self._callbacks["rechercher_recette"] = callback
        return self

    def on_planning(self, callback: Callable[[str | None], None]) -> AudioInputWidget:
        """Callback quand l'intention est planning."""
        self._callbacks["planning"] = callback
        return self

    def on_inventaire(self, callback: Callable[[str], None]) -> AudioInputWidget:
        """Callback quand l'intention est inventaire."""
        self._callbacks["inventaire"] = callback
        return self

    def render(self) -> dict[str, Any] | None:
        """Affiche le widget et traite les commandes.

        Returns:
            Résultat de l'interprétation ou None
        """
        st.markdown("### 🎙️ Commande vocale rapide")

        col1, col2 = st.columns([1, 2])

        with col1:
            audio_data = capture_audio(key=self.key)

        result = None

        with col2:
            if audio_data:
                with st.status("🔄 Traitement en cours...", expanded=True) as status:
                    st.write("📝 Transcription...")
                    texte = transcrire_audio(audio_data)

                    if texte:
                        st.write(f'🗣️ "{texte}"')
                        st.write("🤔 Interprétation...")
                        result = interpreter_commande(texte)

                        if result.get("intention") != "erreur":
                            status.update(label="✅ Commande reconnue!", state="complete")
                        else:
                            status.update(label="❌ Erreur", state="error")
                    else:
                        status.update(label="⚠️ Transcription échouée", state="error")

                if result and result.get("intention") not in ("erreur", "vide"):
                    self._handle_result(result)

            else:
                st.info(
                    "🎤 Cliquez sur **Enregistrer** et parlez.\n\n"
                    "**Exemples:**\n"
                    '- *"Ajoute du lait et des œufs"*\n'
                    '- *"Comment faire une tarte aux pommes"*\n'
                    "- *\"Qu'est-ce qu'on mange ce soir\"*"
                )

        return result

    def _handle_result(self, result: dict[str, Any]) -> None:
        """Exécute les callbacks selon l'intention."""
        intention = result.get("intention", "")
        entites = result.get("entites", {})
        reponse = result.get("reponse", "")

        if reponse:
            st.success(f"💡 {reponse}")

        # Exécuter callback si défini
        if intention == "ajouter_course" and "ajouter_course" in self._callbacks:
            articles = entites.get("articles", [])
            if articles:
                st.markdown("**Articles à ajouter:**")
                for art in articles:
                    st.markdown(
                        f"- {art.get('quantite', 1)} {art.get('unite', '')} {art.get('nom', '')}"
                    )

                if st.button("✅ Confirmer l'ajout", key=f"{self.key}_confirm"):
                    self._callbacks["ajouter_course"](articles)
                    st.success("✅ Ajouté!")
                    st.rerun()

        elif intention == "rechercher_recette" and "rechercher_recette" in self._callbacks:
            recette = entites.get("recette", "")
            if recette:
                st.markdown(f"🍽️ Recherche: *{recette}*")
                self._callbacks["rechercher_recette"](recette)

        elif intention == "planning" and "planning" in self._callbacks:
            date = entites.get("date")
            self._callbacks["planning"](date)

        elif intention == "inventaire" and "inventaire" in self._callbacks:
            articles = entites.get("articles", [])
            if articles:
                self._callbacks["inventaire"](articles[0].get("nom", ""))


@st.fragment
def commande_vocale_rapide(
    *,
    key: str = "vocal_rapide",
    callback_courses: Callable[[list[dict]], None] | None = None,
    callback_recettes: Callable[[str], None] | None = None,
    callback_planning: Callable[[str | None], None] | None = None,
) -> dict[str, Any] | None:
    """Widget simplifié de commande vocale.

    Version fonctionnelle du AudioInputWidget pour usage rapide.

    Args:
        key: Clé unique
        callback_courses: Fonction appelée pour ajouter des courses
        callback_recettes: Fonction appelée pour rechercher une recette
        callback_planning: Fonction appelée pour le planning

    Returns:
        Résultat de l'interprétation
    """
    widget = AudioInputWidget(key=key)

    if callback_courses:
        widget.on_course(callback_courses)
    if callback_recettes:
        widget.on_recette(callback_recettes)
    if callback_planning:
        widget.on_planning(callback_planning)

    return widget.render()
