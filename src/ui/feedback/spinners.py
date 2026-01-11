"""
UI Feedback - Spinners intelligents
"""

from contextlib import contextmanager
from datetime import datetime

import streamlit as st


@contextmanager
def smart_spinner(operation: str, estimated_seconds: int | None = None, show_elapsed: bool = True):
    """
    Spinner avec estimation temps et temps écoulé

    Usage:
        with smart_spinner("Génération recettes", estimated_seconds=5):
            result = await generate_recipes()

    Args:
        operation: Nom de l'opération
        estimated_seconds: Temps estimé (affiche countdown)
        show_elapsed: Afficher temps écoulé après
    """
    start_time = datetime.now()

    # Message initial
    if estimated_seconds:
        message = f"⏳ {operation}... (estimation: {estimated_seconds}s)"
    else:
        message = f"⏳ {operation}..."

    with st.spinner(message):
        try:
            yield
        finally:
            # Calculer temps écoulé
            elapsed = (datetime.now() - start_time).total_seconds()

            if show_elapsed:
                if elapsed < 1:
                    st.caption(f"✅ Terminé en {elapsed*1000:.0f}ms")
                else:
                    st.caption(f"✅ Terminé en {elapsed:.1f}s")


def loading_indicator(message: str = "Chargement..."):
    """
    Indicateur de chargement simple

    Usage:
        loading_indicator("Chargement des données...")
    """
    st.markdown(
        f'<div style="text-align: center; padding: 2rem;">'
        f'<div style="font-size: 2rem;">⏳</div>'
        f'<div style="margin-top: 0.5rem; color: #666;">{message}</div>'
        f"</div>",
        unsafe_allow_html=True,
    )


def skeleton_loader(lines: int = 3):
    """
    Skeleton loader (placeholder animé)

    Usage:
        skeleton_loader(lines=5)
    """
    for _ in range(lines):
        st.markdown(
            '<div style="background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%); '
            "height: 20px; margin: 0.5rem 0; border-radius: 4px; "
            'background-size: 200% 100%; animation: loading 1.5s infinite;"></div>',
            unsafe_allow_html=True,
        )
