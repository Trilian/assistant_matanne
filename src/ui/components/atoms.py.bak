"""
UI Components - Atoms (composants de base)
Badge, empty_state, metric_card
"""

import streamlit as st


def badge(text: str, color: str = "#4CAF50"):
    """
    Badge coloré

    Args:
        text: Texte du badge
        color: Couleur (hex)

    Example:
        badge("Actif", "#4CAF50")
    """
    st.markdown(
        f'<span style="background: {color}; color: white; '
        f"padding: 0.25rem 0.75rem; border-radius: 12px; "
        f'font-size: 0.875rem; font-weight: 600;">{text}</span>',
        unsafe_allow_html=True,
    )


def empty_state(message: str, icon: str = "📭", subtext: str | None = None):
    """
    État vide centré

    Args:
        message: Message principal
        icon: Icône (emoji)
        subtext: Texte secondaire

    Example:
        empty_state("Aucune recette", "🍽️", "Ajoutez-en une")
    """
    sub_html = (
        f'<div style="font-size: 1rem; margin-top: 0.5rem;">{subtext}</div>' if subtext else ""
    )

    st.markdown(
        f'<div style="text-align: center; padding: 3rem; color: #6c757d;">'
        f'<div style="font-size: 4rem;">{icon}</div>'
        f'<div style="font-size: 1.5rem; margin-top: 1rem; font-weight: 500;">{message}</div>'
        f"{sub_html}"
        f"</div>",
        unsafe_allow_html=True,
    )


def metric_card(label: str, value: str, delta: str | None = None, color: str = "#ffffff"):
    """
    Carte métrique stylée

    Args:
        label: Label métrique
        value: Valeur
        delta: Variation (optionnel)
        color: Couleur fond

    Example:
        metric_card("Total", "42", "+5", "#f0f0f0")
    """
    delta_html = (
        f'<div style="font-size: 0.875rem; color: #4CAF50; margin-top: 0.25rem;">{delta}</div>'
        if delta
        else ""
    )

    st.markdown(
        f'<div style="background: {color}; padding: 1.5rem; '
        f'border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.04);">'
        f'<div style="font-size: 0.875rem; color: #666; font-weight: 500;">{label}</div>'
        f'<div style="font-size: 2rem; font-weight: 700; margin-top: 0.5rem;">{value}</div>'
        f"{delta_html}"
        f"</div>",
        unsafe_allow_html=True,
    )


def toast(message: str, type: str = "success"):
    """
    Notification toast simple

    Args:
        message: Message
        type: "success", "error", "warning", "info"

    Example:
        toast("Sauvegarde réussie", "success")
    """
    if type == "success":
        st.success(message)
    elif type == "error":
        st.error(message)
    elif type == "warning":
        st.warning(message)
    else:
        st.info(message)


def divider(text: str | None = None):
    """
    Séparateur avec texte optionnel

    Example:
        divider("OU")
    """
    if text:
        st.markdown(
            f'<div style="text-align: center; margin: 1.5rem 0;">'
            f'<span style="padding: 0 1rem; background: white; '
            f'position: relative; top: -0.75rem;">{text}</span>'
            f'<hr style="margin-top: -1.5rem; border: 1px solid #e0e0e0;">'
            f"</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown("---")


def info_box(title: str, content: str, icon: str = "ℹ️"):
    """
    Boîte d'information

    Example:
        info_box("Astuce", "Utilisez Ctrl+S pour sauvegarder", "💡")
    """
    st.markdown(
        f'<div style="background: #e7f3ff; border-left: 4px solid #2196F3; '
        f'padding: 1rem; border-radius: 4px; margin: 1rem 0;">'
        f'<div style="font-weight: 600; margin-bottom: 0.5rem;">'
        f"{icon} {title}</div>"
        f"<div>{content}</div>"
        f"</div>",
        unsafe_allow_html=True,
    )
