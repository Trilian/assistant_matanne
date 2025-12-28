"""
Layouts Complexes
Grilles, listes, cartes avec actions
"""
import streamlit as st
from typing import List, Dict, Optional, Callable, Any


# ═══════════════════════════════════════════════════════════════
# GRILLES
# ═══════════════════════════════════════════════════════════════

def grid_layout(
        items: List[Dict],
        cols_per_row: int = 3,
        card_renderer: Callable[[Dict, str], None] = None,
        key: str = "grid"
):
    """
    Layout en grille

    Args:
        items: Liste d'items à afficher
        cols_per_row: Nombre de colonnes par ligne
        card_renderer: Fonction(item, key) pour rendre chaque carte
        key: Clé unique
    """
    if not items:
        st.info("Aucun élément")
        return

    # Découper en lignes
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


def masonry_layout(
        items: List[Dict],
        cols: int = 3,
        card_renderer: Callable[[Dict, str], None] = None,
        key: str = "masonry"
):
    """
    Layout type "masonry" (hauteurs variables)

    Note: Approximation avec Streamlit (pas de vrai masonry)
    """
    columns = st.columns(cols)

    for idx, item in enumerate(items):
        col_idx = idx % cols

        with columns[col_idx]:
            if card_renderer:
                card_renderer(item, f"{key}_{idx}")
            else:
                st.write(item)


# ═══════════════════════════════════════════════════════════════
# LISTES AVEC ACTIONS
# ═══════════════════════════════════════════════════════════════

def action_list(
        items: List[Dict],
        item_renderer: Callable[[Dict, int], None],
        actions: List[Dict],
        key: str = "actionlist"
):
    """
    Liste avec actions par item

    Args:
        items: Items à afficher
        item_renderer: Fonction(item, idx) pour afficher l'item
        actions: [{
            "label": str,
            "icon": str,
            "callback": Callable(item),
            "type": "primary|secondary"
        }]
        key: Clé unique
    """
    if not items:
        st.info("Aucun élément")
        return

    for idx, item in enumerate(items):
        col1, *action_cols = st.columns([4] + [1] * len(actions))

        # Contenu de l'item
        with col1:
            item_renderer(item, idx)

        # Actions
        for action_idx, action in enumerate(actions):
            with action_cols[action_idx]:
                icon = action.get("icon", "")
                label = f"{icon}" if icon else action["label"]

                if st.button(
                        label,
                        key=f"{key}_action_{idx}_{action_idx}",
                        help=action.get("label", ""),
                        type=action.get("type", "secondary")
                ):
                    action["callback"](item)

        st.markdown("---")


def card_list(
        items: List[Dict],
        card_config: Dict,
        key: str = "cardlist"
):
    """
    Liste de cartes standardisées

    Args:
        items: Items à afficher
        card_config: {
            "title_field": str,
            "subtitle_fields": List[str],
            "image_field": str (optionnel),
            "tags_field": str (optionnel),
            "actions": List[Dict]
        }
        key: Clé unique
    """
    if not items:
        st.info("Aucun élément")
        return

    for idx, item in enumerate(items):
        # Image + Contenu
        if card_config.get("image_field") and item.get(card_config["image_field"]):
            col_img, col_content = st.columns([1, 3])

            with col_img:
                st.image(item[card_config["image_field"]], use_container_width=True)

            content_col = col_content
        else:
            content_col = st.container()

        with content_col:
            # Titre
            title_field = card_config.get("title_field", "nom")
            st.markdown(f"### {item.get(title_field, 'Sans titre')}")

            # Sous-titres
            subtitle_fields = card_config.get("subtitle_fields", [])
            if subtitle_fields:
                subtitles = [str(item.get(f, "")) for f in subtitle_fields if item.get(f)]
                st.caption(" • ".join(subtitles))

            # Tags
            tags_field = card_config.get("tags_field")
            if tags_field and item.get(tags_field):
                tags = item[tags_field]
                if isinstance(tags, list):
                    tag_html = " ".join([
                        f'<span style="background: #e7f3ff; padding: 0.25rem 0.5rem; '
                        f'border-radius: 12px; font-size: 0.875rem;">{tag}</span>'
                        for tag in tags
                    ])
                    st.markdown(tag_html, unsafe_allow_html=True)

        # Actions
        actions = card_config.get("actions", [])
        if actions:
            cols = st.columns(len(actions))
            for action_idx, action in enumerate(actions):
                with cols[action_idx]:
                    if st.button(
                            action["label"],
                            key=f"{key}_action_{idx}_{action_idx}",
                            use_container_width=True
                    ):
                        action["callback"](item)

        st.markdown("---")


# ═══════════════════════════════════════════════════════════════
# CARTES ITEM UNIVERSELLES
# ═══════════════════════════════════════════════════════════════

def item_card(
        title: str,
        metadata: List[str],
        status: Optional[str] = None,
        status_color: Optional[str] = None,
        tags: Optional[List[str]] = None,
        image_url: Optional[str] = None,
        actions: Optional[List[tuple]] = None,  # (label, callback)
        expandable_content: Optional[Callable] = None,
        alert: Optional[str] = None,
        key: str = "item"
):
    """
    Carte item universelle

    Utilisable pour recettes, articles inventaire, courses, etc.

    Args:
        title: Titre de la carte
        metadata: Liste de métadonnées à afficher
        status: Statut (optionnel)
        status_color: Couleur du statut
        tags: Tags à afficher
        image_url: URL image (optionnel)
        actions: [(label, callback)]
        expandable_content: Fonction pour contenu extensible
        alert: Message d'alerte
        key: Clé unique
    """
    border_color = status_color or "#e2e8e5"

    with st.container():
        st.markdown(
            f'<div style="border-left: 4px solid {border_color}; padding: 1rem; '
            f'background: #f8f9fa; border-radius: 8px; margin-bottom: 0.5rem;"></div>',
            unsafe_allow_html=True
        )

        # Layout avec ou sans image
        if image_url:
            col_img, col_content = st.columns([1, 4])
            with col_img:
                st.image(image_url, use_container_width=True)
            content_col = col_content
        else:
            content_col = st.container()

        with content_col:
            # Titre + Statut
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

            # Alert
            if alert:
                st.warning(alert)

            # Métadonnées
            if metadata:
                st.caption(" • ".join(metadata))

            # Tags
            if tags:
                tag_html = " ".join([
                    f'<span style="background: #e7f3ff; padding: 0.25rem 0.5rem; '
                    f'border-radius: 12px; font-size: 0.875rem;">{tag}</span>'
                    for tag in tags
                ])
                st.markdown(tag_html, unsafe_allow_html=True)

        # Actions
        if actions:
            cols = st.columns(len(actions))
            for idx, (label, callback) in enumerate(actions):
                with cols[idx]:
                    if st.button(label, key=f"{key}_action_{idx}", use_container_width=True):
                        callback()

        # Contenu extensible
        if expandable_content:
            with st.expander("👁️ Détails"):
                expandable_content()


# ═══════════════════════════════════════════════════════════════
# TIMELINE
# ═══════════════════════════════════════════════════════════════

def timeline(
        events: List[Dict],
        key: str = "timeline"
):
    """
    Timeline verticale

    Args:
        events: [{
            "title": str,
            "date": str,
            "description": str,
            "icon": str,
            "status": "completed|current|pending"
        }]
        key: Clé unique
    """
    for idx, event in enumerate(events):
        status = event.get("status", "pending")

        # Couleur selon statut
        color_map = {
            "completed": "#4CAF50",
            "current": "#2196F3",
            "pending": "#9e9e9e"
        }
        color = color_map.get(status, "#9e9e9e")

        # Icône
        icon = event.get("icon", "•")

        col1, col2 = st.columns([1, 10])

        with col1:
            st.markdown(
                f'<div style="text-align: center; font-size: 1.5rem; color: {color};">'
                f'{icon}</div>',
                unsafe_allow_html=True
            )

        with col2:
            st.markdown(f"**{event['title']}**")
            if event.get("date"):
                st.caption(event["date"])
            if event.get("description"):
                st.write(event["description"])

        # Ligne de connexion (sauf dernier)
        if idx < len(events) - 1:
            st.markdown(
                f'<div style="margin-left: 1.5rem; border-left: 2px solid {color}; '
                f'height: 2rem;"></div>',
                unsafe_allow_html=True
            )


# ═══════════════════════════════════════════════════════════════
# QUICK ACTIONS
# ═══════════════════════════════════════════════════════════════

def quick_actions(
        actions: List[tuple],
        layout: str = "horizontal",
        key: str = "actions"
):
    """
    Barre d'actions rapides

    Args:
        actions: [(label, callback)]
        layout: "horizontal" | "vertical"
        key: Clé unique
    """
    if layout == "horizontal":
        cols = st.columns(len(actions))
        for idx, (label, callback) in enumerate(actions):
            with cols[idx]:
                if st.button(label, key=f"{key}_{idx}", use_container_width=True):
                    callback()
    else:
        for idx, (label, callback) in enumerate(actions):
            if st.button(label, key=f"{key}_{idx}", use_container_width=True):
                callback()