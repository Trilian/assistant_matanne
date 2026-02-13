"""
UI Feedback - Spinners intelligents
"""

from contextlib import contextmanager
from datetime import datetime

import streamlit as st


@contextmanager
def spinner_intelligent(
    operation: str, secondes_estimees: int | None = None, afficher_temps_ecoule: bool = True
):
    """
    Spinner avec estimation temps et temps écoulé

    Usage:
        with spinner_intelligent("Génération recettes", secondes_estimees=5):
            result = await generate_recipes()

    Args:
        operation: Nom de l'opération
        secondes_estimees: Temps estimé (affiche countdown)
        afficher_temps_ecoule: Afficher temps écoulé après
    """
    debut = datetime.now()

    # Message initial
    if secondes_estimees:
        message = f"⏳ {operation}... (estimation: {secondes_estimees}s)"
    else:
        message = f"⏳ {operation}..."

    with st.spinner(message):
        try:
            yield
        finally:
            # Calculer temps écoulé
            temps_ecoule = (datetime.now() - debut).total_seconds()

            if afficher_temps_ecoule:
                if temps_ecoule < 1:
                    st.caption(f"✅ Terminé en {temps_ecoule*1000:.0f}ms")
                else:
                    st.caption(f"✅ Terminé en {temps_ecoule:.1f}s")


def indicateur_chargement(message: str = "Chargement..."):
    """
    Indicateur de chargement simple

    Usage:
        indicateur_chargement("Chargement des données...")
    """
    st.markdown(
        f'<div style="text-align: center; padding: 2rem;">'
        f'<div style="font-size: 2rem;">⏳</div>'
        f'<div style="margin-top: 0.5rem; color: #666;">{message}</div>'
        f"</div>",
        unsafe_allow_html=True,
    )


def chargeur_squelette(lignes: int = 3):
    """
    Chargeur squelette (placeholder animé)

    Usage:
        chargeur_squelette(lignes=5)
    """
    for _ in range(lignes):
        st.markdown(
            '<div style="background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%); '
            "height: 20px; margin: 0.5rem 0; border-radius: 4px; "
            'background-size: 200% 100%; animation: loading 1.5s infinite;"></div>',
            unsafe_allow_html=True,
        )
