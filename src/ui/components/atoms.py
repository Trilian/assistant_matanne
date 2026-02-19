"""
UI Components - Atoms (composants de base)
badge, etat_vide, carte_metrique, notification, separateur, boite_info

Note: Pour des métriques plus avancées avec icônes et liens,
utilisez carte_metrique_avancee depuis src.ui.components.metrics
"""

import warnings

import streamlit as st

from src.ui.utils import echapper_html


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
        f'font-size: 0.875rem; font-weight: 600;">{echapper_html(texte)}</span>',
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
        f'<div style="font-size: 1rem; margin-top: 0.5rem;">{echapper_html(sous_texte)}</div>'
        if sous_texte
        else ""
    )

    st.markdown(
        f'<div style="text-align: center; padding: 3rem; color: #6c757d;">'
        f'<div style="font-size: 4rem;">{echapper_html(icone)}</div>'
        f'<div style="font-size: 1.5rem; margin-top: 1rem; font-weight: 500;">{echapper_html(message)}</div>'
        f"{html_sous_texte}"
        f"</div>",
        unsafe_allow_html=True,
    )


def carte_metrique(label: str, valeur: str, delta: str | None = None, couleur: str = "#ffffff"):
    """
    Carte métrique simple.

    Pour des métriques plus avancées (avec icône, lien module, gradient),
    préférez `carte_metrique_avancee` de src.ui.components.metrics.

    Args:
        label: Label métrique
        valeur: Valeur
        delta: Variation (optionnel)
        couleur: Couleur fond

    Example:
        carte_metrique("Total", "42", "+5", "#f0f0f0")

    See Also:
        carte_metrique_avancee: Version avancée avec plus d'options
    """
    html_delta = (
        f'<div style="font-size: 0.875rem; color: #4CAF50; margin-top: 0.25rem;">{echapper_html(delta)}</div>'
        if delta
        else ""
    )

    st.markdown(
        f'<div style="background: {couleur}; padding: 1.5rem; '
        f'border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.04);">'
        f'<div style="font-size: 0.875rem; color: #666; font-weight: 500;">{echapper_html(label)}</div>'
        f'<div style="font-size: 2rem; font-weight: 700; margin-top: 0.5rem;">{echapper_html(valeur)}</div>'
        f"{html_delta}"
        f"</div>",
        unsafe_allow_html=True,
    )


def notification(message: str, type_notif: str = "success", **kwargs):
    """
    Notification simple immédiate (wrapper Streamlit).

    .. deprecated::
        Utiliser ``afficher_succes``, ``afficher_erreur``, ``afficher_avertissement``,
        ``afficher_info`` depuis ``src.ui.feedback`` à la place.

    Args:
        message: Message à afficher
        type_notif: "success", "error", "warning", "info"

    Example:
        notification("Sauvegarde réussie", "success")

    See Also:
        src.ui.feedback.afficher_succes: Toast avec expiration automatique
        src.ui.feedback.afficher_erreur: Toast erreur
    """
    # Rétrocompatibilité: accepter l'ancien paramètre 'type'
    if "type" in kwargs:
        type_notif = kwargs.pop("type")
    warnings.warn(
        "notification() est déprécié. Utiliser afficher_succes/afficher_erreur "
        "de src.ui.feedback à la place.",
        DeprecationWarning,
        stacklevel=2,
    )
    if type_notif == "success":
        st.success(message)
    elif type_notif == "error":
        st.error(message)
    elif type_notif == "warning":
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
            f'position: relative; top: -0.75rem;">{echapper_html(texte)}</span>'
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
        f"{echapper_html(icone)} {echapper_html(titre)}</div>"
        f"<div>{echapper_html(contenu)}</div>"
        f"</div>",
        unsafe_allow_html=True,
    )
