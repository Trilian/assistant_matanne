"""
UI Components - Layouts
Grilles, cartes, containers
"""
import streamlit as st
from typing import List, Dict, Optional, Callable


def grid_layout(
        items: List[Dict],
        cols_per_row: int = 3,
        card_renderer: Optional[Callable[[Dict, str], None]] = None,
        key: str = "grid"
):
    """
    Layout en grille

    Args:
        items: Liste d'items
        cols_per_row: Colonnes par ligne
        card_renderer: Fonction render carte (item, key)
        key: Clé unique

    Example:
        grid_layout(
            recipes,
            cols_per_row=3,
            card_renderer=lambda item, k: st.write(item["nom"]),
            key="recipes_grid"
        )
    """
    if not items:
        st.info("Aucun élément")
        return

    for row_idx in range(0, len(items), cols_per_row):
        cols = st.columns(cols_per_row)

        for col_idx in range(cols_per_row):
            item_idx = row_idx + col_idx

            if item_idx < len(items):
                with cols[col_idx]:
                    if card_renderer:
                        card_renderer(items[item_idx], f"{key}_{item_idx}")
                    else:
                        st.write(items[item_idx])


def item_card(
        title: str,
        metadata: List[str],
        status: Optional[str] = None,
        status_color: Optional[str] = None,
        tags: Optional[List[str]] = None,
        image_url: Optional[str] = None,
        actions: Optional[List[tuple]] = None,
        key: str = "item"
):
    """
    Carte item universelle

    Args:
        title: Titre
        metadata: Liste de métadonnées
        status: Statut (optionnel)
        status_color: Couleur statut
        tags: Tags (optionnel)
        image_url: URL image
        actions: Liste (label, callback)
        key: Clé unique

    Example:
        item_card(
            title="Tarte aux pommes",
            metadata=["45min", "6 portions"],
            status="facile",
            status_color="#4CAF50",
            tags=["Dessert", "Automne"],
            actions=[("Voir", lambda: view()), ("Éditer", lambda: edit())]
        )
    """
    border_color = status_color or "#e2e8e5"

    with st.container():
        st.markdown(
            f'<div style="border-left: 4px solid {border_color}; padding: 1rem; '
            f'background: #f8f9fa; border-radius: 8px; margin-bottom: 0.5rem;"></div>',
            unsafe_allow_html=True
        )

        if image_url:
            col_img, col_content = st.columns([1, 4])
            with col_img:
                st.image(image_url, use_container_width=True)
            content_col = col_content
        else:
            content_col = st.container()

        with content_col:
            if status:
                col_title, col_status = st.columns([3, 1])
                with col_title:
                    st.markdown(f"### {title}")
                with col_status:
                    st.markdown(
                        f'<div style="text-align: right; color: {status_color or "#6c757d"}; '
                        f'font-weight: 600;">{status}</div>',
                        unsafe_allow_html=True
                    )
            else:
                st.markdown(f"### {title}")

            if metadata:
                st.caption(" • ".join(metadata))

            if tags:
                tag_html = " ".join([
                    f'<span style="background: #e7f3ff; padding: 0.25rem 0.5rem; '
                    f'border-radius: 12px; font-size: 0.875rem;">{tag}</span>'
                    for tag in tags
                ])
                st.markdown(tag_html, unsafe_allow_html=True)

        if actions:
            cols = st.columns(len(actions))
            for idx, (label, callback) in enumerate(actions):
                with cols[idx]:
                    if st.button(label, key=f"{key}_action_{idx}", use_container_width=True):
                        callback()


def collapsible_section(title: str, content_fn: Callable, expanded: bool = False, key: str = "section"):
    """
    Section pliable

    Args:
        title: Titre
        content_fn: Fonction qui render le contenu
        expanded: Ouvert par défaut
        key: Clé unique

    Example:
        collapsible_section(
            "Détails avancés",
            lambda: st.write("Contenu détaillé"),
            expanded=False,
            key="advanced"
        )
    """
    with st.expander(title, expanded=expanded):
        content_fn()


def tabs_layout(tabs: Dict[str, Callable], key: str = "tabs"):
    """
    Layout tabs

    Args:
        tabs: Dict {label: content_fn}
        key: Clé unique

    Example:
        tabs_layout({
            "Vue 1": lambda: st.write("Contenu 1"),
            "Vue 2": lambda: st.write("Contenu 2")
        }, "views")
    """
    tab_objects = st.tabs(list(tabs.keys()))

    for idx, (label, content_fn) in enumerate(tabs.items()):
        with tab_objects[idx]:
            content_fn()


def card_container(content_fn: Callable, color: str = "#ffffff"):
    """
    Container carte stylé

    Args:
        content_fn: Fonction render contenu
        color: Couleur fond

    Example:
        card_container(
            lambda: st.write("Contenu"),
            color="#f0f0f0"
        )
    """
    st.markdown(
        f'<div style="background: {color}; padding: 1.5rem; '
        f'border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.04);">',
        unsafe_allow_html=True
    )
    content_fn()
    st.markdown('</div>', unsafe_allow_html=True)