"""
UI Components - Atoms (composants de base)
badge, etat_vide, carte_metrique
"""

import streamlit as st


def badge(texte: str, couleur: str = "#4CAF50"):
    """
    Badge coloré

    Args:
        texte: Texte du badge
        couleur: Couleur (hex)

    Example:
        badge("Actif", "#4CAF50")
    """
    st.markdown(
        f'<span style="background: {couleur}; color: white; '
        f"padding: 0.25rem 0.75rem; border-radius: 12px; "
        f'font-size: 0.875rem; font-weight: 600;">{texte}</span>',
        unsafe_allow_html=True,
    )


def etat_vide(message: str, icone: str = "📭", sous_texte: str | None = None):
    """
    État vide centré

    Args:
        message: Message principal
        icone: Icône (emoji)
        sous_texte: Texte secondaire

    Example:
        etat_vide("Aucune recette", "🍽️", "Ajoutez-en une")
    """
    html_sous_texte = (
        f'<div style="font-size: 1rem; margin-top: 0.5rem;">{sous_texte}</div>'
        if sous_texte
        else ""
    )

    st.markdown(
        f'<div style="text-align: center; padding: 3rem; color: #6c757d;">'
        f'<div style="font-size: 4rem;">{icone}</div>'
        f'<div style="font-size: 1.5rem; margin-top: 1rem; font-weight: 500;">{message}</div>'
        f"{html_sous_texte}"
        f"</div>",
        unsafe_allow_html=True,
    )


def carte_metrique(label: str, valeur: str, delta: str | None = None, couleur: str = "#ffffff"):
    """
    Carte métrique stylée

    Args:
        label: Label métrique
        valeur: Valeur
        delta: Variation (optionnel)
        couleur: Couleur fond

    Example:
        carte_metrique("Total", "42", "+5", "#f0f0f0")
    """
    html_delta = (
        f'<div style="font-size: 0.875rem; color: #4CAF50; margin-top: 0.25rem;">{delta}</div>'
        if delta
        else ""
    )

    st.markdown(
        f'<div style="background: {couleur}; padding: 1.5rem; '
        f'border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.04);">'
        f'<div style="font-size: 0.875rem; color: #666; font-weight: 500;">{label}</div>'
        f'<div style="font-size: 2rem; font-weight: 700; margin-top: 0.5rem;">{valeur}</div>'
        f"{html_delta}"
        f"</div>",
        unsafe_allow_html=True,
    )


def notification(message: str, type: str = "success"):
    """
    Notification simple

    Args:
        message: Message
        type: "success", "error", "warning", "info"

    Example:
        notification("Sauvegarde réussie", "success")
    """
    if type == "success":
        st.success(message)
    elif type == "error":
        st.error(message)
    elif type == "warning":
        st.warning(message)
    else:
        st.info(message)


def separateur(texte: str | None = None):
    """
    Séparateur avec texte optionnel

    Example:
        separateur("OU")
    """
    if texte:
        st.markdown(
            f'<div style="text-align: center; margin: 1.5rem 0;">'
            f'<span style="padding: 0 1rem; background: white; '
            f'position: relative; top: -0.75rem;">{texte}</span>'
            f'<hr style="margin-top: -1.5rem; border: 1px solid #e0e0e0;">'
            f"</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown("---")


def boite_info(titre: str, contenu: str, icone: str = "ℹ️"):
    """
    Boîte d'information

    Example:
        boite_info("Astuce", "Utilisez Ctrl+S pour sauvegarder", "💡")
    """
    st.markdown(
        f'<div style="background: #e7f3ff; border-left: 4px solid #2196F3; '
        f'padding: 1rem; border-radius: 4px; margin: 1rem 0;">'
        f'<div style="font-weight: 600; margin-bottom: 0.5rem;">'
        f"{icone} {titre}</div>"
        f"<div>{contenu}</div>"
        f"</div>",
        unsafe_allow_html=True,
    )
