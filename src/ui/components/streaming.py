"""
Composants Streamlit pour l'affichage progressif (streaming).

Ces composants permettent d'afficher les réponses IA de manière progressive,
améliorant l'UX en montrant les résultats au fur et à mesure qu'ils arrivent.

Usage:
    from src.ui.components.streaming import StreamingContainer, streaming_response

    # Option 1: Context manager
    with StreamingContainer("Génération en cours...") as container:
        for chunk in service.call_with_streaming_sync(prompt):
            container.append(chunk)

    # Option 2: One-liner helper
    streaming_response(
        generator=service.call_with_streaming_sync(prompt),
        label="Suggestions"
    )

    # Option 3: st.write_stream() natif (Streamlit >= 1.31)
    st.write_stream(service.call_with_streaming_sync(prompt))
"""

from __future__ import annotations

import logging
import time
from collections.abc import Generator, Iterator
from contextlib import contextmanager
from typing import Any

import streamlit as st

from src.ui.registry import composant_ui

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# STREAMING CONTAINER — Affichage progressif manuel
# ═══════════════════════════════════════════════════════════


class StreamingContainer:
    """
    Container pour affichage progressif de texte avec indicateur de statut.

    Gère automatiquement:
    - L'affichage progressif du texte
    - Un spinner pendant la génération
    - Les métriques de timing
    - Le rendu Markdown

    Usage:
        with StreamingContainer("Génération...") as container:
            for chunk in generator:
                container.append(chunk)
        # Le texte final est affiché automatiquement

    Attributes:
        text: Texte accumulé
        duration_ms: Durée de la génération
    """

    def __init__(
        self,
        label: str = "Génération en cours...",
        render_markdown: bool = True,
        show_metrics: bool = True,
        key: str | None = None,
    ):
        """
        Initialise le container de streaming.

        Args:
            label: Message affiché pendant le streaming
            render_markdown: Si True, rend le texte en Markdown
            show_metrics: Si True, affiche le temps et le nombre de caractères
            key: Clé unique pour le container Streamlit
        """
        self.label = label
        self.render_markdown = render_markdown
        self.show_metrics = show_metrics
        self.key = key or f"streaming_{id(self)}"

        self._text: str = ""
        self._start_time: float = 0.0
        self._end_time: float = 0.0
        self._placeholder = None
        self._spinner_placeholder = None
        self._active = False

    @property
    def text(self) -> str:
        """Texte accumulé."""
        return self._text

    @property
    def duration_ms(self) -> float:
        """Durée de génération en millisecondes."""
        if self._end_time and self._start_time:
            return (self._end_time - self._start_time) * 1000
        return 0.0

    def __enter__(self) -> StreamingContainer:
        """Démarre le streaming."""
        self._start_time = time.perf_counter()
        self._text = ""
        self._active = True

        # Créer les placeholders
        self._spinner_placeholder = st.empty()
        self._placeholder = st.empty()

        # Afficher le spinner initial
        self._spinner_placeholder.info(f"⏳ {self.label}")

        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Termine le streaming et affiche le résultat final."""
        self._end_time = time.perf_counter()
        self._active = False

        # Supprimer le spinner
        if self._spinner_placeholder:
            self._spinner_placeholder.empty()

        # Afficher le résultat final
        if self._text:
            if self.render_markdown:
                self._placeholder.markdown(self._text)
            else:
                self._placeholder.text(self._text)

            # Métriques optionnelles
            if self.show_metrics:
                metrics_col1, metrics_col2 = st.columns(2)
                with metrics_col1:
                    st.caption(f"⏱️ {self.duration_ms:.0f}ms")
                with metrics_col2:
                    st.caption(f"📝 {len(self._text)} caractères")
        else:
            self._placeholder.warning("Aucun contenu généré")

    def append(self, chunk: str) -> None:
        """
        Ajoute un chunk de texte et rafraîchit l'affichage.

        Args:
            chunk: Texte à ajouter
        """
        if not self._active:
            logger.warning("StreamingContainer.append() appelé hors contexte")
            return

        self._text += chunk

        # Mettre à jour l'affichage
        if self._placeholder:
            if self.render_markdown:
                self._placeholder.markdown(self._text + "▌")  # Curseur
            else:
                self._placeholder.text(self._text + "▌")

    def clear(self) -> None:
        """Efface le contenu actuel."""
        self._text = ""
        if self._placeholder:
            self._placeholder.empty()


# ═══════════════════════════════════════════════════════════
# HELPERS — Fonctions utilitaires
# ═══════════════════════════════════════════════════════════


@composant_ui(
    "streaming",
    exemple='streaming_response(generator=my_gen, label="Suggestions")',
    tags=("ia", "streaming", "progressif"),
)
def streaming_response(
    generator: Iterator[str] | Generator[str, None, None],
    label: str = "Génération en cours...",
    render_markdown: bool = True,
    show_metrics: bool = True,
) -> str:
    """
    Affiche une réponse streaming dans un container géré automatiquement.

    Args:
        generator: Générateur de chunks de texte
        label: Message pendant le streaming
        render_markdown: Rendre en Markdown
        show_metrics: Afficher les métriques

    Returns:
        Le texte complet généré

    Usage:
        text = streaming_response(
            service.call_with_streaming_sync(prompt),
            label="Suggestions de recettes"
        )
    """
    with StreamingContainer(
        label=label,
        render_markdown=render_markdown,
        show_metrics=show_metrics,
    ) as container:
        for chunk in generator:
            container.append(chunk)

    return container.text


@composant_ui(
    "streaming",
    exemple='with streaming_section("Réponse IA"): st.write("contenu")',
    tags=("ia", "section"),
)
@contextmanager
def streaming_section(
    title: str,
    icon: str = "🤖",
    expanded: bool = True,
):
    """
    Section extensible pour affichage streaming.

    Combine un st.expander avec le streaming.

    Usage:
        with streaming_section("Analyse IA", icon="🔍"):
            st.write_stream(service.call_with_streaming_sync(prompt))
    """
    with st.expander(f"{icon} {title}", expanded=expanded):
        yield


def streaming_placeholder(key: str | None = None) -> tuple:
    """
    Crée un placeholder pour streaming manuel.

    Returns:
        Tuple (placeholder, spinner_placeholder) pour contrôle manuel.

    Usage:
        placeholder, spinner = streaming_placeholder()
        spinner.info("Génération...")
        text = ""
        for chunk in generator:
            text += chunk
            placeholder.markdown(text)
        spinner.empty()
    """
    spinner = st.empty()
    placeholder = st.empty()
    return placeholder, spinner


# ═══════════════════════════════════════════════════════════
# WRITE_STREAM WRAPPER — Pour versions anciennes de Streamlit
# ═══════════════════════════════════════════════════════════


def safe_write_stream(generator: Iterator[str] | Generator[str, None, None]) -> str:
    """
    Wrapper compatible pour st.write_stream().

    Utilise st.write_stream() si disponible (Streamlit >= 1.31),
    sinon utilise un fallback manuel.

    Args:
        generator: Générateur de chunks

    Returns:
        Texte complet
    """
    # Vérifier si st.write_stream existe
    if hasattr(st, "write_stream"):
        return st.write_stream(generator)

    # Fallback pour versions anciennes
    return streaming_response(generator, show_metrics=False)


__all__ = [
    "StreamingContainer",
    "streaming_response",
    "streaming_section",
    "streaming_placeholder",
    "safe_write_stream",
]
