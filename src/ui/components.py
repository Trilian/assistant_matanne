"""
Composants UI Réutilisables pour Streamlit
Évite la duplication et standardise l'interface
"""
import streamlit as st
from typing import Callable, Optional, List, Dict, Any, Tuple
from datetime import datetime, date
import pandas as pd


# ===================================
# CARTES & CONTAINERS
# ===================================

def render_card(
        title: str,
        content: str = "",
        icon: str = "📦",
        color: str = "#4CAF50",
        actions: Optional[List[Tuple[str, Callable]]] = None,
        footer: Optional[str] = None,
        image_url: Optional[str] = None
):
    """
    Carte moderne avec titre, contenu, actions

    Args:
        title: Titre de la carte
        content: Contenu texte
        icon: Emoji/icône
        color: Couleur de la bordure
        actions: Liste de (label, callback)
        footer: Texte en bas
        image_url: URL image optionnelle
    """
    with st.container():
        # Bordure colorée
        st.markdown(f"""
        <div style="border-left: 4px solid {color}; 
                    padding: 1rem; 
                    background: #f8f9fa; 
                    border-radius: 8px; 
                    margin-bottom: 1rem;">
        </div>
        """, unsafe_allow_html=True)

        # Header avec image
        if image_url:
            col_img, col_content = st.columns([1, 3])
            with col_img:
                st.image(image_url, use_container_width=True)
            with col_content:
                st.markdown(f"### {icon} {title}")
                if content:
                    st.write(content)
        else:
            st.markdown(f"### {icon} {title}")
            if content:
                st.write(content)

        # Actions
        if actions:
            cols = st.columns(len(actions))
            for i, (label, callback) in enumerate(actions):
                if cols[i].button(label, key=f"card_{title}_{i}", use_container_width=True):
                    callback()

        # Footer
        if footer:
            st.caption(footer)


def render_info_card(
        label: str,
        value: str,
        delta: Optional[str] = None,
        delta_color: str = "normal",
        icon: str = "📊",
        help_text: Optional[str] = None
):
    """
    Carte d'information/métrique stylisée

    Args:
        label: Label de la métrique
        value: Valeur principale
        delta: Changement (optionnel)
        delta_color: Couleur delta (normal/inverse/off)
        icon: Icône
        help_text: Tooltip
    """
    with st.container():
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 1rem;
                    border-radius: 12px;
                    text-align: center;">
            <div style="font-size: 2rem;">{icon}</div>
            <div style="font-size: 0.875rem; opacity: 0.9;">{label}</div>
            <div style="font-size: 2rem; font-weight: bold; margin: 0.5rem 0;">{value}</div>
            {f'<div style="font-size: 0.875rem;">{delta}</div>' if delta else ''}
        </div>
        """, unsafe_allow_html=True)

        if help_text:
            st.caption(help_text)


def render_stat_row(stats: List[Dict[str, Any]], cols: int = 4):
    """
    Ligne de statistiques avec métriques

    Args:
        stats: Liste de dicts {"label": str, "value": str, "delta": str}
        cols: Nombre de colonnes
    """
    columns = st.columns(cols)

    for i, stat in enumerate(stats[:cols]):
        with columns[i]:
            st.metric(
                label=stat.get("label", ""),
                value=stat.get("value", ""),
                delta=stat.get("delta"),
                delta_color=stat.get("delta_color", "normal"),
                help=stat.get("help")
            )


# ===================================
# BADGES & TAGS
# ===================================

def render_badge(
        text: str,
        color: str = "#4CAF50",
        icon: str = ""
):
    """Badge coloré"""
    st.markdown(f"""
    <span style="background-color: {color}; 
                 color: white;
                 padding: 0.25rem 0.75rem; 
                 border-radius: 12px; 
                 font-size: 0.875rem; 
                 font-weight: 600;
                 display: inline-block;
                 margin: 0.25rem;">
        {icon} {text}
    </span>
    """, unsafe_allow_html=True)


def render_tags(tags: List[str], colors: Optional[Dict[str, str]] = None):
    """
    Affiche plusieurs tags

    Args:
        tags: Liste de tags
        colors: Dict optionnel {tag: color}
    """
    colors = colors or {}
    default_color = "#6c757d"

    for tag in tags:
        color = colors.get(tag, default_color)
        render_badge(tag, color)


def render_priority_badge(priority: str):
    """Badge de priorité avec couleurs standard"""
    colors = {
        "haute": "#dc3545",
        "moyenne": "#ffc107",
        "basse": "#28a745"
    }

    icons = {
        "haute": "🔴",
        "moyenne": "🟡",
        "basse": "🟢"
    }

    render_badge(
        priority.capitalize(),
        colors.get(priority, "#6c757d"),
        icons.get(priority, "⚪")
    )


# ===================================
# FORMULAIRES
# ===================================

def render_search_bar(
        placeholder: str = "Rechercher...",
        key: str = "search",
        on_change: Optional[Callable] = None
) -> str:
    """Barre de recherche stylisée"""
    col1, col2 = st.columns([4, 1])

    with col1:
        search_term = st.text_input(
            "🔍",
            placeholder=placeholder,
            key=key,
            label_visibility="collapsed"
        )

    with col2:
        if st.button("🔄", key=f"{key}_refresh", help="Rafraîchir"):
            if on_change:
                on_change()
            st.rerun()

    return search_term


def render_filter_panel(
        filters: Dict[str, Dict],
        key_prefix: str = "filter"
) -> Dict[str, Any]:
    """
    Panel de filtres générique

    Args:
        filters: Dict de configs {
            "nom_filtre": {
                "type": "select/text/checkbox/slider",
                "label": "Label",
                "options": [...],  # Pour select
                "default": valeur
            }
        }
        key_prefix: Préfixe pour les keys

    Returns:
        Dict des valeurs sélectionnées
    """
    results = {}

    with st.expander("🔧 Filtres avancés", expanded=False):
        for filter_name, config in filters.items():
            filter_type = config.get("type", "text")
            label = config.get("label", filter_name)
            key = f"{key_prefix}_{filter_name}"

            if filter_type == "select":
                results[filter_name] = st.selectbox(
                    label,
                    config.get("options", []),
                    index=config.get("default", 0),
                    key=key
                )

            elif filter_type == "multiselect":
                results[filter_name] = st.multiselect(
                    label,
                    config.get("options", []),
                    default=config.get("default", []),
                    key=key
                )

            elif filter_type == "checkbox":
                results[filter_name] = st.checkbox(
                    label,
                    value=config.get("default", False),
                    key=key
                )

            elif filter_type == "slider":
                results[filter_name] = st.slider(
                    label,
                    min_value=config.get("min", 0),
                    max_value=config.get("max", 100),
                    value=config.get("default", 50),
                    key=key
                )

            elif filter_type == "number":
                results[filter_name] = st.number_input(
                    label,
                    min_value=config.get("min", 0),
                    max_value=config.get("max", 1000),
                    value=config.get("default", 0),
                    key=key
                )

            elif filter_type == "date":
                results[filter_name] = st.date_input(
                    label,
                    value=config.get("default", date.today()),
                    key=key
                )

            else:  # text
                results[filter_name] = st.text_input(
                    label,
                    value=config.get("default", ""),
                    key=key
                )

    return results


# ===================================
# LISTES & TABLEAUX
# ===================================

def render_data_table(
        df: pd.DataFrame,
        actions: Optional[List[Tuple[str, Callable]]] = None,
        selectable: bool = False,
        key: str = "table"
) -> Optional[List[int]]:
    """
    Tableau de données avec actions

    Args:
        df: DataFrame à afficher
        actions: Actions par ligne [(label, callback)]
        selectable: Permettre la sélection
        key: Clé unique

    Returns:
        Liste des indices sélectionnés si selectable=True
    """
    if df.empty:
        st.info("📝 Aucune donnée à afficher")
        return None

    # Afficher le tableau
    if selectable:
        selected = st.multiselect(
            "Sélectionner",
            df.index.tolist(),
            key=f"{key}_select"
        )

        st.dataframe(
            df.loc[selected] if selected else df,
            use_container_width=True,
            hide_index=True
        )

        return selected
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)
        return None


def render_list_item(
        title: str,
        subtitle: Optional[str] = None,
        metadata: Optional[List[str]] = None,
        actions: Optional[List[Tuple[str, Callable]]] = None,
        icon: str = "•",
        expandable: bool = False,
        expanded_content: Optional[Callable] = None,
        key: str = "item"
):
    """
    Item de liste avec actions

    Args:
        title: Titre principal
        subtitle: Sous-titre
        metadata: Liste de métadonnées (ex: ["10min", "4 portions"])
        actions: Actions rapides
        icon: Icône/bullet
        expandable: Peut s'étendre
        expanded_content: Callback pour contenu étendu
        key: Clé unique
    """
    if expandable and expanded_content:
        with st.expander(f"{icon} {title}", expanded=False):
            if subtitle:
                st.caption(subtitle)

            if metadata:
                st.caption(" • ".join(metadata))

            expanded_content()

            if actions:
                cols = st.columns(len(actions))
                for i, (label, callback) in enumerate(actions):
                    if cols[i].button(label, key=f"{key}_action_{i}"):
                        callback()
    else:
        col1, col2 = st.columns([3, 1])

        with col1:
            st.markdown(f"**{icon} {title}**")
            if subtitle:
                st.caption(subtitle)
            if metadata:
                st.caption(" • ".join(metadata))

        with col2:
            if actions:
                for i, (label, callback) in enumerate(actions):
                    if st.button(label, key=f"{key}_action_{i}", use_container_width=True):
                        callback()


# ===================================
# NOTIFICATIONS & ALERTES
# ===================================

def render_toast(
        message: str,
        type: str = "info",
        duration: int = 3
):
    """
    Notification toast (utilise st.toast si dispo, sinon message standard)

    Args:
        message: Message
        type: info/success/warning/error
        duration: Durée en secondes
    """
    # Streamlit 1.30+ a st.toast
    if hasattr(st, 'toast'):
        st.toast(message, icon={"info": "ℹ️", "success": "✅", "warning": "⚠️", "error": "❌"}.get(type, "ℹ️"))
    else:
        # Fallback
        if type == "success":
            st.success(message)
        elif type == "warning":
            st.warning(message)
        elif type == "error":
            st.error(message)
        else:
            st.info(message)


def render_alert(
        message: str,
        type: str = "info",
        dismissible: bool = False,
        icon: Optional[str] = None
):
    """
    Alerte stylisée

    Args:
        message: Message
        type: info/success/warning/error
        dismissible: Peut être fermée
        icon: Icône custom
    """
    icons = {
        "info": "ℹ️",
        "success": "✅",
        "warning": "⚠️",
        "error": "❌"
    }

    colors = {
        "info": "#d1ecf1",
        "success": "#d4edda",
        "warning": "#fff3cd",
        "error": "#f8d7da"
    }

    icon_display = icon or icons.get(type, "ℹ️")
    color = colors.get(type, "#d1ecf1")

    if dismissible:
        with st.expander(f"{icon_display} {message}", expanded=True):
            st.markdown(f"""
            <div style="background-color: {color}; 
                        padding: 1rem; 
                        border-radius: 8px;">
            </div>
            """, unsafe_allow_html=True)
    else:
        if type == "success":
            st.success(f"{icon_display} {message}")
        elif type == "warning":
            st.warning(f"{icon_display} {message}")
        elif type == "error":
            st.error(f"{icon_display} {message}")
        else:
            st.info(f"{icon_display} {message}")


# ===================================
# MODALES & CONFIRMATIONS
# ===================================

def render_confirmation_dialog(
        title: str,
        message: str,
        confirm_label: str = "Confirmer",
        cancel_label: str = "Annuler",
        key: str = "confirm"
) -> Optional[bool]:
    """
    Dialog de confirmation

    Returns:
        True si confirmé, False si annulé, None si en attente
    """
    if f"{key}_show" not in st.session_state:
        st.session_state[f"{key}_show"] = True

    if st.session_state[f"{key}_show"]:
        with st.expander(f"⚠️ {title}", expanded=True):
            st.warning(message)

            col1, col2 = st.columns(2)

            with col1:
                if st.button(confirm_label, key=f"{key}_confirm", type="primary", use_container_width=True):
                    st.session_state[f"{key}_show"] = False
                    return True

            with col2:
                if st.button(cancel_label, key=f"{key}_cancel", use_container_width=True):
                    st.session_state[f"{key}_show"] = False
                    return False

    return None


# ===================================
# PAGINATION
# ===================================

def render_pagination(
        total_items: int,
        items_per_page: int = 20,
        key: str = "pagination"
) -> Tuple[int, int]:
    """
    Contrôles de pagination

    Returns:
        (page_actuelle, items_per_page)
    """
    if f"{key}_page" not in st.session_state:
        st.session_state[f"{key}_page"] = 1

    total_pages = (total_items + items_per_page - 1) // items_per_page

    col1, col2, col3, col4 = st.columns([1, 2, 1, 1])

    with col1:
        if st.button("⬅️ Préc", key=f"{key}_prev", disabled=st.session_state[f"{key}_page"] <= 1):
            st.session_state[f"{key}_page"] -= 1
            st.rerun()

    with col2:
        st.markdown(f"**Page {st.session_state[f'{key}_page']} / {total_pages}**")
        st.caption(f"{total_items} élément(s)")

    with col3:
        if st.button("Suiv ➡️", key=f"{key}_next", disabled=st.session_state[f"{key}_page"] >= total_pages):
            st.session_state[f"{key}_page"] += 1
            st.rerun()

    with col4:
        items_per_page = st.selectbox(
            "Par page",
            [10, 20, 50, 100],
            index=1,
            key=f"{key}_size"
        )

    return st.session_state[f"{key}_page"], items_per_page


# ===================================
# LOADING & PROGRESS
# ===================================

def render_loading(message: str = "Chargement...", spinner: bool = True):
    """Indicateur de chargement"""
    if spinner:
        with st.spinner(message):
            pass
    else:
        st.info(f"⏳ {message}")


def render_progress_bar(
        value: int,
        max_value: int = 100,
        label: Optional[str] = None,
        color: str = "#4CAF50"
):
    """Barre de progression stylisée"""
    percentage = (value / max_value) * 100 if max_value > 0 else 0

    if label:
        st.caption(label)

    st.progress(percentage / 100)
    st.caption(f"{value}/{max_value} ({percentage:.0f}%)")


# ===================================
# HELPERS DIVERS
# ===================================

def render_empty_state(
        message: str = "Aucune donnée",
        icon: str = "📭",
        action_label: Optional[str] = None,
        action_callback: Optional[Callable] = None
):
    """État vide avec action optionnelle"""
    st.markdown(f"""
    <div style="text-align: center; padding: 3rem; color: #6c757d;">
        <div style="font-size: 4rem;">{icon}</div>
        <div style="font-size: 1.5rem; margin-top: 1rem;">{message}</div>
    </div>
    """, unsafe_allow_html=True)

    if action_label and action_callback:
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button(action_label, key="empty_action", use_container_width=True, type="primary"):
                action_callback()


def render_divider(text: Optional[str] = None, color: str = "#dee2e6"):
    """Séparateur avec texte optionnel"""
    if text:
        st.markdown(f"""
        <div style="text-align: center; margin: 2rem 0;">
            <span style="background: white; padding: 0 1rem; color: {color};">
                {text}
            </span>
            <hr style="margin-top: -0.75rem; border-color: {color};">
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("---")