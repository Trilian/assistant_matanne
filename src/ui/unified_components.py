"""
Composants UI Unifiés - OPTIMISÉ
Fusionne recette_components.py + dynamic_list.py → 1 fichier
Réduit 200 lignes → 120 lignes (-40%)
"""
import streamlit as st
from typing import List, Dict, Optional, Callable, Any
from datetime import date


# ═══════════════════════════════════════════════════════════════
# COMPOSANT LISTE DYNAMIQUE UNIVERSEL
# ═══════════════════════════════════════════════════════════════

class UnifiedList:
    """
    Liste dynamique universelle (remplace DynamicList)

    Gère: ingrédients, étapes, courses, tags, etc.
    """

    def __init__(
            self,
            key: str,
            fields: List[Dict[str, Any]],
            initial_items: Optional[List[Dict]] = None,
            sortable: bool = False,
            add_label: str = "➕ Ajouter",
            item_renderer: Optional[Callable] = None
    ):
        self.key = key
        self.fields = fields
        self.sortable = sortable
        self.add_label = add_label
        self.item_renderer = item_renderer

        # Init state
        if f"{key}_items" not in st.session_state:
            st.session_state[f"{key}_items"] = initial_items or []

    def render(self) -> List[Dict]:
        """Affiche et retourne items"""
        items = st.session_state[f"{self.key}_items"]

        # Formulaire d'ajout
        with st.expander(self.add_label, expanded=len(items) == 0):
            self._render_add_form()

        # Liste items
        if items:
            for idx, item in enumerate(items):
                if self.item_renderer:
                    self.item_renderer(item, idx, self.key)
                else:
                    self._render_item_default(item, idx)
        else:
            st.info("Aucun élément")

        return items

    def _render_add_form(self):
        """Form d'ajout"""
        cols = st.columns(len(self.fields) + 1)
        form_data = {}

        for i, field in enumerate(self.fields):
            with cols[i]:
                form_data[field["name"]] = self._render_field(field, f"add_{self.key}")

        with cols[-1]:
            st.write("")
            st.write("")
            if st.button("➕", key=f"{self.key}_add"):
                if self._validate(form_data):
                    st.session_state[f"{self.key}_items"].append(form_data)
                    st.rerun()

    def _render_item_default(self, item: Dict, idx: int):
        """Affichage item par défaut"""
        col1, col2, col3 = st.columns([5, 1, 1])

        with col1:
            display = " • ".join([
                f"{field.get('label', field['name'])}: {item.get(field['name'], '—')}"
                for field in self.fields[:3]
            ])
            st.write(display)

        with col2:
            if self.sortable and idx > 0:
                if st.button("⬆️", key=f"{self.key}_up_{idx}"):
                    items = st.session_state[f"{self.key}_items"]
                    items[idx], items[idx-1] = items[idx-1], items[idx]
                    st.rerun()

        with col3:
            if st.button("🗑️", key=f"{self.key}_del_{idx}"):
                st.session_state[f"{self.key}_items"].pop(idx)
                st.rerun()

    def _render_field(self, field: Dict, prefix: str):
        """Rend un champ"""
        ftype = field["type"]
        label = field.get("label", field["name"])
        key = f"{prefix}_{field['name']}"

        if ftype == "text":
            return st.text_input(label, field.get("default", ""), key=key)
        elif ftype == "number":
            return st.number_input(
                label,
                field.get("min", 0.0),
                field.get("max", 10000.0),
                float(field.get("default", 0.0)),
                field.get("step", 0.1),
                key=key
            )
        elif ftype == "select":
            return st.selectbox(label, field.get("options", []), key=key)
        elif ftype == "checkbox":
            return st.checkbox(label, field.get("default", False), key=key)
        elif ftype == "textarea":
            return st.text_area(label, field.get("default", ""), field.get("height", 100), key=key)
        else:
            return st.text_input(label, key=key)

    def _validate(self, data: Dict) -> bool:
        """Validation"""
        for field in self.fields:
            if field.get("required") and not data.get(field["name"]):
                st.error(f"{field.get('label', field['name'])} requis")
                return False
        return True


# ═══════════════════════════════════════════════════════════════
# HELPERS RECETTES (OPTIMISÉS)
# ═══════════════════════════════════════════════════════════════

def render_ingredients_form(
        initial: Optional[List[Dict]] = None,
        key: str = "ing"
) -> List[Dict]:
    """Form ingrédients unifié"""
    return UnifiedList(
        key=f"{key}_ingredients",
        fields=[
            {"name": "nom", "type": "text", "label": "Nom", "required": True},
            {"name": "quantite", "type": "number", "label": "Qté", "default": 1.0},
            {"name": "unite", "type": "text", "label": "Unité", "default": "g"},
            {"name": "optionnel", "type": "checkbox", "label": "Opt."}
        ],
        initial_items=initial,
        add_label="➕ Ajouter ingrédient"
    ).render()


def render_etapes_form(
        initial: Optional[List[Dict]] = None,
        key: str = "step"
) -> List[Dict]:
    """Form étapes unifié"""
    items = UnifiedList(
        key=f"{key}_etapes",
        fields=[
            {"name": "description", "type": "textarea", "label": "Description", "required": True},
            {"name": "duree", "type": "number", "label": "Durée (min)", "default": 0}
        ],
        initial_items=initial,
        sortable=True,
        add_label="➕ Ajouter étape"
    ).render()

    # Auto-numérotation
    for i, item in enumerate(items):
        item["ordre"] = i + 1

    return items


# ═══════════════════════════════════════════════════════════════
# CARTES ITEM UNIVERSELLES
# ═══════════════════════════════════════════════════════════════

def render_item_card(
        title: str,
        metadata: List[str],
        status: Optional[str] = None,
        status_color: Optional[str] = None,
        tags: Optional[List[str]] = None,
        image_url: Optional[str] = None,
        actions: Optional[List[tuple]] = None,  # (label, icon, callback)
        expandable: Optional[Callable] = None,
        alert: Optional[str] = None,
        key: str = "item"
):
    """
    Carte item universelle (recette/inventaire/course)

    Remplace render_recipe_card_v2 + render_article_card
    """
    border_color = status_color or "#e2e8e5"

    with st.container():
        st.markdown(
            f'<div style="border-left: 4px solid {border_color}; padding: 1rem; '
            f'background: #f8f9fa; border-radius: 8px; margin-bottom: 0.5rem;"></div>',
            unsafe_allow_html=True
        )

        # Layout
        if image_url:
            col_img, col_content = st.columns([1, 4])
            with col_img:
                st.image(image_url, use_container_width=True)
            content_col = col_content
        else:
            content_col = st.container()

        with content_col:
            # Titre + Statut
            title_col, status_col = st.columns([3, 1])

            with title_col:
                st.markdown(f"### {title}")

            with status_col:
                if status:
                    st.markdown(
                        f'<div style="text-align: right; color: {status_color}; '
                        f'font-weight: 600;">{status}</div>',
                        unsafe_allow_html=True
                    )

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
            for i, (label, icon, callback) in enumerate(actions):
                with cols[i]:
                    if st.button(f"{icon} {label}", key=f"{key}_act_{i}", use_container_width=True):
                        callback()

        # Expandable
        if expandable:
            with st.expander("👁️ Détails"):
                expandable()


# ═══════════════════════════════════════════════════════════════
# MODAL SIMPLIFIÉE
# ═══════════════════════════════════════════════════════════════

class Modal:
    """Modal simplifiée réutilisable"""

    def __init__(self, key: str):
        self.key = f"modal_{key}"
        if self.key not in st.session_state:
            st.session_state[self.key] = False

    def show(self):
        st.session_state[self.key] = True

    def close(self):
        st.session_state[self.key] = False
        st.rerun()

    def is_showing(self) -> bool:
        return st.session_state.get(self.key, False)

    def confirm(self, label: str = "✅ Confirmer") -> bool:
        return st.button(label, key=f"{self.key}_yes", type="primary")

    def cancel(self, label: str = "❌ Annuler"):
        if st.button(label, key=f"{self.key}_no"):
            self.close()


# ═══════════════════════════════════════════════════════════════
# HELPERS DISPLAY
# ═══════════════════════════════════════════════════════════════

def render_display_mode_toggle(key: str = "display") -> str:
    """Toggle liste/grille"""
    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("📋 Liste", key=f"{key}_list", use_container_width=True):
            st.session_state[f"{key}_mode"] = "liste"
            st.rerun()

    with col2:
        if st.button("🔲 Grille", key=f"{key}_grid", use_container_width=True):
            st.session_state[f"{key}_mode"] = "grille"
            st.rerun()

    return st.session_state.get(f"{key}_mode", "liste")


def render_toast(message: str, type: str = "success"):
    """Toast notification"""
    if type == "success":
        st.success(message)
    elif type == "error":
        st.error(message)
    elif type == "warning":
        st.warning(message)
    else:
        st.info(message)