"""
UI Feedback - Spinners intelligents
"""

from contextlib import contextmanager
from datetime import datetime

import streamlit as st

from src.ui.tokens import Couleur, Espacement, Rayon, Typographie
from src.ui.utils import echapper_html


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
                    st.caption(f"✅ Terminé en {temps_ecoule * 1000:.0f}ms")
                else:
                    st.caption(f"✅ Terminé en {temps_ecoule:.1f}s")


def indicateur_chargement(message: str = "Chargement..."):
    """
    Indicateur de chargement simple

    Usage:
        indicateur_chargement("Chargement des données...")
    """
    st.markdown(
        f'<div style="text-align: center; padding: {Espacement.XL};">'
        f'<div style="font-size: {Typographie.ICON_MD};">⏳</div>'
        f'<div style="margin-top: {Espacement.SM}; color: {Couleur.TEXT_SECONDARY};">{echapper_html(message)}</div>'
        f"</div>",
        unsafe_allow_html=True,
    )


def chargeur_squelette(lignes: int = 3):
    """
    Chargeur squelette (placeholder animé)

    Utilise l'animation ``shimmer`` du système centralisé.
    Les @keyframes sont injectés une seule fois via ``injecter_animations()``.

    Usage:
        chargeur_squelette(lignes=5)
    """
    for _ in range(lignes):
        st.markdown(
            f'<div style="background: linear-gradient(90deg, {Couleur.BG_HOVER} 25%, '
            f"{Couleur.BORDER_LIGHT} 50%, {Couleur.BG_HOVER} 75%); "
            f"height: 20px; margin: {Espacement.SM} 0; border-radius: {Rayon.SM}; "
            f'background-size: 200% 100%; animation: shimmer 1.5s infinite;"></div>',
            unsafe_allow_html=True,
        )
