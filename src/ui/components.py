"""
Composants UI de Base - VERSION NETTOYÉE
Conserve uniquement les fonctions non dupliquées
Les composants avancés sont dans unified_components.py
"""
import streamlit as st
from typing import List, Dict, Optional, Callable, Any
import pandas as pd


# ═══════════════════════════════════════════════════════════════
# AFFICHAGE DE BASE
# ═══════════════════════════════════════════════════════════════

def render_stat_row(stats: List[Dict], cols: int = None):
    """
    Ligne de statistiques avec métriques

    Args:
        stats: [{"label": str, "value": Any, "delta": Any, "delta_color": str}]
        cols: Nombre de colonnes (auto si None)
    """
    if not stats:
        return

    cols_count = cols or len(stats)
    columns = st.columns(cols_count)

    for idx, stat in enumerate(stats):
        if idx >= len(columns):
            break

        with columns[idx]:
            st.metric(
                label=stat.get("label", ""),
                value=stat.get("value", ""),
                delta=stat.get("delta"),
                delta_color=stat.get("delta_color", "normal")
            )


def render_badge(text: str, color: str = "#4CAF50"):
    """
    Badge coloré

    Usage:
        render_badge("✅ Actif", "#28a745")
    """
    st.markdown(
        f'<span style="background: {color}; color: white; '
        f'padding: 0.25rem 0.75rem; border-radius: 12px; '
        f'font-size: 0.875rem; font-weight: 600;">{text}</span>',
        unsafe_allow_html=True
    )


# ═══════════════════════════════════════════════════════════════
# RECHERCHE & FILTRES
# ═══════════════════════════════════════════════════════════════

def render_search_bar(
        placeholder: str = "Rechercher...",
        key: str = "search",
        icon: str = "🔍"
) -> str:
    """
    Barre de recherche simple

    Returns:
        Terme de recherche
    """
    return st.text_input(
        "",
        placeholder=f"{icon} {placeholder}",
        key=key,
        label_visibility="collapsed"
    )


def render_filter_panel(
        filters_config: Dict[str, Dict],
        key_prefix: str
) -> Dict:
    """
    Panneau de filtres dans expander

    Args:
        filters_config: {
            "filter_name": {
                "type": "select|checkbox|slider|text",
                "label": str,
                "options": List (pour select),
                "default": Any,
                "min/max/step": int (pour slider)
            }
        }
        key_prefix: Préfixe pour clés Streamlit

    Returns:
        Dict des valeurs de filtres
    """
    with st.expander("🔍 Filtres", expanded=False):
        results = {}

        for filter_name, config in filters_config.items():
            filter_type = config.get("type", "text")
            label = config.get("label", filter_name)
            key = f"{key_prefix}_filter_{filter_name}"

            if filter_type == "select":
                results[filter_name] = st.selectbox(
                    label,
                    options=config.get("options", []),
                    index=config.get("default", 0),
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
                    step=config.get("step", 1),
                    key=key
                )

            elif filter_type == "text":
                results[filter_name] = st.text_input(
                    label,
                    value=config.get("default", ""),
                    key=key
                )

        return results


# ═══════════════════════════════════════════════════════════════
# PAGINATION
# ═══════════════════════════════════════════════════════════════

def render_pagination(
        total_items: int,
        items_per_page: int = 20,
        key: str = "pagination"
) -> tuple[int, int]:
    """
    Pagination simple

    Returns:
        (page_actuelle, items_per_page)
    """
    if total_items <= items_per_page:
        return 1, items_per_page

    total_pages = (total_items + items_per_page - 1) // items_per_page

    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if st.button("⬅️ Préc", key=f"{key}_prev", disabled=st.session_state.get(f"{key}_page", 1) <= 1):
            st.session_state[f"{key}_page"] = max(1, st.session_state.get(f"{key}_page", 1) - 1)
            st.rerun()

    with col2:
        page = st.selectbox(
            "Page",
            options=list(range(1, total_pages + 1)),
            index=st.session_state.get(f"{key}_page", 1) - 1,
            key=f"{key}_select",
            label_visibility="collapsed"
        )

        if page != st.session_state.get(f"{key}_page", 1):
            st.session_state[f"{key}_page"] = page
            st.rerun()

    with col3:
        if st.button("Suiv ➡️", key=f"{key}_next", disabled=page >= total_pages):
            st.session_state[f"{key}_page"] = min(total_pages, page + 1)
            st.rerun()

    current_page = st.session_state.get(f"{key}_page", 1)
    st.caption(f"Page {current_page}/{total_pages} • {total_items} élément(s)")

    return current_page, items_per_page


# ═══════════════════════════════════════════════════════════════
# ÉTATS VIDES
# ═══════════════════════════════════════════════════════════════

def render_empty_state(
        message: str,
        icon: str = "📭",
        action_label: Optional[str] = None,
        action_callback: Optional[Callable] = None,
        key: str = "empty"
):
    """
    État vide avec action optionnelle

    Usage:
        render_empty_state(
            "Aucune recette",
            "🍽️",
            "➕ Ajouter",
            lambda: navigate("recettes.ajout")
        )
    """
    st.markdown(
        f"""
        <div style="text-align: center; padding: 3rem; color: #6c757d;">
            <div style="font-size: 4rem;">{icon}</div>
            <div style="font-size: 1.5rem; margin-top: 1rem;">{message}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    if action_label and action_callback:
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button(action_label, key=f"{key}_action", type="primary", use_container_width=True):
                action_callback()


# ═══════════════════════════════════════════════════════════════
# NOTIFICATIONS
# ═══════════════════════════════════════════════════════════════

def render_toast(message: str, type: str = "success"):
    """
    Toast notification simple

    Args:
        message: Message à afficher
        type: success|error|warning|info
    """
    if type == "success":
        st.success(message)
    elif type == "error":
        st.error(message)
    elif type == "warning":
        st.warning(message)
    else:
        st.info(message)


# ═══════════════════════════════════════════════════════════════
# ACTIONS RAPIDES
# ═══════════════════════════════════════════════════════════════

def quick_action_bar(actions: List[tuple[str, Callable]], key_prefix: str = "action"):
    """
    Barre d'actions horizontale

    Args:
        actions: [(label, callback)]
        key_prefix: Préfixe pour clés

    Usage:
        quick_action_bar([
            ("🗑️ Nettoyer", cleanup),
            ("📤 Exporter", export)
        ])
    """
    if not actions:
        return

    cols = st.columns(len(actions))

    for idx, (label, callback) in enumerate(actions):
        with cols[idx]:
            if st.button(label, key=f"{key_prefix}_{idx}", use_container_width=True):
                callback()


# ═══════════════════════════════════════════════════════════════
# HELPERS AFFICHAGE
# ═══════════════════════════════════════════════════════════════

def render_collapsible_section(
        title: str,
        content: Callable,
        icon: str = "📋",
        expanded: bool = False,
        key: Optional[str] = None
):
    """
    Section collapsible standardisée

    Usage:
        render_collapsible_section(
            "Détails",
            lambda: st.write("Contenu..."),
            icon="👁️"
        )
    """
    with st.expander(f"{icon} {title}", expanded=expanded):
        content()