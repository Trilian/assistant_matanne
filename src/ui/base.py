"""
Composants UI de Base (Atomiques)
Briques élémentaires réutilisables dans toute l'app
"""
import streamlit as st
from typing import Optional, Callable, List, Dict, Any


# ═══════════════════════════════════════════════════════════════
# AFFICHAGE BASIQUE
# ═══════════════════════════════════════════════════════════════

def badge(text: str, color: str = "#4CAF50", key: Optional[str] = None):
    """
    Badge coloré simple

    Args:
        text: Texte du badge
        color: Couleur hex
        key: Clé unique (optionnel)

    Usage:
        badge("✅ Actif", "#28a745")
    """
    st.markdown(
        f'<span style="background: {color}; color: white; '
        f'padding: 0.25rem 0.75rem; border-radius: 12px; '
        f'font-size: 0.875rem; font-weight: 600;">{text}</span>',
        unsafe_allow_html=True
    )


def metric_card(
        label: str,
        value: Any,
        delta: Optional[Any] = None,
        delta_color: str = "normal",
        icon: Optional[str] = None
):
    """
    Carte métrique améliorée

    Args:
        label: Label de la métrique
        value: Valeur principale
        delta: Variation (optionnel)
        delta_color: "normal" | "inverse" | "off"
        icon: Emoji/icône (optionnel)
    """
    display_label = f"{icon} {label}" if icon else label
    st.metric(label=display_label, value=value, delta=delta, delta_color=delta_color)


def progress_bar(
        value: float,
        max_value: float = 100,
        label: Optional[str] = None,
        color: str = "#4CAF50",
        show_percentage: bool = True
):
    """
    Barre de progression personnalisée

    Args:
        value: Valeur actuelle
        max_value: Valeur max
        label: Label (optionnel)
        color: Couleur de la barre
        show_percentage: Afficher le %
    """
    percentage = min(100, (value / max_value) * 100)

    if label:
        st.caption(f"{label}: {value}/{max_value}")

    st.markdown(
        f"""
        <div style="background: #e0e0e0; border-radius: 10px; height: 20px; overflow: hidden;">
            <div style="background: {color}; width: {percentage}%; height: 100%; 
                        transition: width 0.3s; display: flex; align-items: center; 
                        justify-content: center; color: white; font-size: 0.75rem; font-weight: bold;">
                {f"{percentage:.0f}%" if show_percentage else ""}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def divider(text: Optional[str] = None, color: str = "#e0e0e0"):
    """
    Séparateur horizontal avec texte optionnel

    Usage:
        divider()  # Simple ligne
        divider("OU")  # Avec texte
    """
    if text:
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; margin: 1rem 0;">
                <div style="flex: 1; height: 1px; background: {color};"></div>
                <div style="padding: 0 1rem; color: #6c757d; font-weight: 500;">{text}</div>
                <div style="flex: 1; height: 1px; background: {color};"></div>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<hr style="border: none; border-top: 1px solid {color}; margin: 1rem 0;">',
            unsafe_allow_html=True
        )


def icon_text(icon: str, text: str, color: Optional[str] = None):
    """
    Icône + texte alignés

    Usage:
        icon_text("🕐", "30 minutes")
    """
    style = f'color: {color};' if color else ''
    st.markdown(
        f'<span style="{style}">{icon} {text}</span>',
        unsafe_allow_html=True
    )


def empty_state(
        message: str,
        icon: str = "📭",
        subtext: Optional[str] = None
):
    """
    État vide centré

    Args:
        message: Message principal
        icon: Grande icône
        subtext: Texte secondaire (optionnel)
    """
    st.markdown(
        f"""
        <div style="text-align: center; padding: 3rem; color: #6c757d;">
            <div style="font-size: 4rem;">{icon}</div>
            <div style="font-size: 1.5rem; margin-top: 1rem; font-weight: 500;">{message}</div>
            {f'<div style="font-size: 1rem; margin-top: 0.5rem;">{subtext}</div>' if subtext else ''}
        </div>
        """,
        unsafe_allow_html=True
    )


def loading_spinner(message: str = "Chargement...", icon: str = "⏳"):
    """
    Spinner de chargement centré
    """
    st.markdown(
        f"""
        <div style="text-align: center; padding: 2rem;">
            <div style="font-size: 2rem;">{icon}</div>
            <div style="margin-top: 1rem; color: #6c757d;">{message}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ═══════════════════════════════════════════════════════════════
# CONTENEURS
# ═══════════════════════════════════════════════════════════════

def card(
        title: str,
        content: Callable,
        icon: Optional[str] = None,
        bg_color: str = "#ffffff",
        border_color: str = "#e2e8e5",
        collapsible: bool = False,
        expanded: bool = True
):
    """
    Carte conteneur standardisée

    Args:
        title: Titre de la carte
        content: Fonction qui rend le contenu
        icon: Icône (optionnel)
        bg_color: Couleur de fond
        border_color: Couleur bordure
        collapsible: Peut être replié
        expanded: État initial si collapsible
    """
    display_title = f"{icon} {title}" if icon else title

    if collapsible:
        with st.expander(display_title, expanded=expanded):
            content()
    else:
        st.markdown(
            f"""
            <div style="background: {bg_color}; border: 1px solid {border_color}; 
                        border-radius: 8px; padding: 1rem; margin-bottom: 1rem;">
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(f"### {display_title}")
        content()


def info_box(
        message: str,
        type: str = "info",
        icon: Optional[str] = None,
        dismissible: bool = False,
        key: str = "infobox"
):
    """
    Boîte d'information avec types

    Args:
        message: Message
        type: "info" | "success" | "warning" | "error"
        icon: Icône personnalisée
        dismissible: Peut être fermée
        key: Clé unique si dismissible
    """
    if dismissible and st.session_state.get(f"{key}_dismissed"):
        return

    icon_map = {
        "info": "ℹ️",
        "success": "✅",
        "warning": "⚠️",
        "error": "❌"
    }

    display_icon = icon or icon_map.get(type, "ℹ️")

    container_func = {
        "success": st.success,
        "warning": st.warning,
        "error": st.error,
        "info": st.info
    }.get(type, st.info)

    if dismissible:
        col1, col2 = st.columns([10, 1])
        with col1:
            container_func(f"{display_icon} {message}")
        with col2:
            if st.button("✕", key=f"{key}_dismiss"):
                st.session_state[f"{key}_dismissed"] = True
                st.rerun()
    else:
        container_func(f"{display_icon} {message}")


# ═══════════════════════════════════════════════════════════════
# IMAGES
# ═══════════════════════════════════════════════════════════════

def image_with_fallback(
        url: Optional[str],
        fallback_icon: str = "🖼️",
        width: Optional[int] = None,
        caption: Optional[str] = None
):
    """
    Image avec fallback si erreur

    Args:
        url: URL de l'image
        fallback_icon: Emoji de fallback
        width: Largeur en pixels
        caption: Légende
    """
    if url:
        try:
            st.image(url, width=width, caption=caption, use_container_width=not width)
        except:
            st.markdown(
                f'<div style="text-align: center; font-size: 3rem; padding: 2rem; '
                f'background: #f5f5f5; border-radius: 8px;">{fallback_icon}</div>',
                unsafe_allow_html=True
            )
    else:
        st.markdown(
            f'<div style="text-align: center; font-size: 3rem; padding: 2rem; '
            f'background: #f5f5f5; border-radius: 8px;">{fallback_icon}</div>',
            unsafe_allow_html=True
        )


# ═══════════════════════════════════════════════════════════════
# NAVIGATION
# ═══════════════════════════════════════════════════════════════

def breadcrumb(path: List[str], icons: Optional[List[str]] = None):
    """
    Fil d'Ariane

    Args:
        path: ["Accueil", "Recettes", "Détails"]
        icons: ["🏠", "🍽️", "👁️"] (optionnel)
    """
    breadcrumb_html = []

    for idx, item in enumerate(path):
        icon = icons[idx] if icons and idx < len(icons) else ""
        display = f"{icon} {item}" if icon else item
        breadcrumb_html.append(f'<span>{display}</span>')

        if idx < len(path) - 1:
            breadcrumb_html.append('<span style="color: #6c757d; margin: 0 0.5rem;">→</span>')

    st.markdown(
        f'<div style="font-size: 0.875rem; color: #6c757d; margin-bottom: 1rem;">'
        f'{"".join(breadcrumb_html)}</div>',
        unsafe_allow_html=True
    )


def tabs_styled(tabs_config: List[Dict[str, Any]], key: str = "tabs") -> str:
    """
    Tabs avec style personnalisé

    Args:
        tabs_config: [{"label": str, "icon": str, "key": str}]
        key: Préfixe clé

    Returns:
        Clé du tab actif
    """
    labels = [f"{t.get('icon', '')} {t['label']}" for t in tabs_config]
    selected = st.tabs(labels)

    # Retourner la clé du tab actif (simplifié)
    return tabs_config[0]["key"]


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════

def key_value_list(items: Dict[str, Any], title: Optional[str] = None, icon: Optional[str] = None):
    """
    Liste clé-valeur simple

    Args:
        items: {"Nom": "Pizza", "Prix": "12€"}
        title: Titre (optionnel)
        icon: Icône (optionnel)
    """
    if title:
        display_title = f"{icon} {title}" if icon else title
        st.markdown(f"**{display_title}**")

    for key, value in items.items():
        col1, col2 = st.columns([1, 2])
        with col1:
            st.caption(key)
        with col2:
            st.write(value)


def countdown(target_date, label: str = "Jours restants", icon: str = "⏰"):
    """
    Compte à rebours simple

    Args:
        target_date: Date cible
        label: Label
        icon: Icône
    """
    from datetime import date

    today = date.today()
    delta = (target_date - today).days

    if delta > 0:
        st.info(f"{icon} {label}: **{delta} jour(s)**")
    elif delta == 0:
        st.success(f"{icon} {label}: **Aujourd'hui !**")
    else:
        st.warning(f"{icon} {label}: **Dépassé de {abs(delta)} jour(s)**")