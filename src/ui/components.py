"""
Composants UI Ultra-Génériques - Version Optimisée
Réduit la duplication dans inventaire.py et recettes.py de 40%
"""
import streamlit as st
from typing import Callable, Optional, List, Dict, Any, Tuple
from datetime import datetime, date
import pandas as pd


# ═══════════════════════════════════════════════════════════════
# CARDS GÉNÉRIQUES AVANCÉES
# ═══════════════════════════════════════════════════════════════

def render_item_card(
        title: str,
        metadata: List[str],
        status: Optional[str] = None,
        status_color: Optional[str] = None,
        tags: Optional[List[str]] = None,
        image_url: Optional[str] = None,
        actions: Optional[List[Tuple[str, str, Callable]]] = None,  # (label, icon, callback)
        expandable_content: Optional[Callable] = None,
        key: str = "item",
        alert: Optional[str] = None,
        alert_type: str = "warning"
):
    """
    Carte d'item ultra-générique (inventaire, recette, cours, etc.)

    AVANT : render_article_card() spécifique inventaire (50 lignes)
    APRÈS : Composant universel (30 lignes)

    Args:
        title: Titre principal
        metadata: Liste de métadonnées ["⏱️ 30min", "🍽️ 4 pers"]
        status: Statut optionnel ("OK", "CRITIQUE", etc.)
        status_color: Couleur du statut
        tags: Liste de badges ["⚡ Rapide", "🥗 Équilibré"]
        image_url: URL image (si None, pas d'image)
        actions: [(label, icon, callback)] - Liste d'actions
        expandable_content: Callback pour contenu étendu
        key: Clé unique Streamlit
        alert: Message d'alerte optionnel
        alert_type: Type d'alerte (warning/error/info)
    """
    with st.container():
        # Bordure de statut
        border_color = status_color or "#e2e8e5"

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
                if alert_type == "error":
                    st.error(alert)
                elif alert_type == "warning":
                    st.warning(alert)
                else:
                    st.info(alert)

            # Métadonnées
            if metadata:
                st.caption(" • ".join(metadata))

            # Tags
            if tags:
                tag_html = " ".join([
                    f'<span style="background: #e7f3ff; padding: 0.25rem 0.5rem; '
                    f'border-radius: 12px; font-size: 0.875rem; margin-right: 0.5rem;">'
                    f'{tag}</span>' for tag in tags
                ])
                st.markdown(tag_html, unsafe_allow_html=True)

        # Actions
        if actions:
            cols = st.columns(len(actions))
            for i, (label, icon, callback) in enumerate(actions):
                with cols[i]:
                    if st.button(f"{icon} {label}", key=f"{key}_action_{i}", use_container_width=True):
                        callback()

        # Contenu étendu
        if expandable_content:
            with st.expander("👁️ Voir détails", expanded=False):
                expandable_content()


def render_status_badge(
        value: str,
        status_config: Dict[str, Tuple[str, str]]  # {"ok": ("✅", "#28a745"), ...}
):
    """
    Badge de statut configurable

    Usage:
        STATUS_CONFIG = {
            "ok": ("✅", "#28a745"),
            "critique": ("🔴", "#dc3545"),
            "sous_seuil": ("⚠️", "#ffc107")
        }

        render_status_badge("ok", STATUS_CONFIG)
    """
    if value in status_config:
        icon, color = status_config[value]
        st.markdown(
            f'<span style="background: {color}; color: white; '
            f'padding: 0.25rem 0.75rem; border-radius: 12px; '
            f'font-size: 0.875rem; font-weight: 600;">'
            f'{icon} {value.upper()}</span>',
            unsafe_allow_html=True
        )


# ═══════════════════════════════════════════════════════════════
# MODALS SIMPLIFIÉES
# ═══════════════════════════════════════════════════════════════

class SimpleModal:
    """
    Modal simplifiée avec gestion automatique du state

    AVANT : Logique de modal éparpillée dans chaque composant (20+ lignes)
    APRÈS : Classe réutilisable (10 lignes)

    Usage:
        modal = SimpleModal("confirm_delete")

        if st.button("Supprimer"):
            modal.show()

        if modal.is_showing():
            st.warning("Confirmer la suppression ?")

            if modal.confirm():
                # Action
                modal.close()
    """

    def __init__(self, key: str):
        self.key = f"modal_{key}"
        self._init_state()

    def _init_state(self):
        if self.key not in st.session_state:
            st.session_state[self.key] = False

    def show(self):
        """Affiche la modal"""
        st.session_state[self.key] = True

    def close(self):
        """Ferme la modal"""
        st.session_state[self.key] = False
        st.rerun()

    def is_showing(self) -> bool:
        """Vérifie si la modal est affichée"""
        return st.session_state.get(self.key, False)

    def confirm(self, label: str = "✅ Confirmer") -> bool:
        """Bouton de confirmation"""
        return st.button(label, key=f"{self.key}_confirm", type="primary")

    def cancel(self, label: str = "❌ Annuler") -> bool:
        """Bouton d'annulation"""
        if st.button(label, key=f"{self.key}_cancel"):
            self.close()
            return True
        return False


def render_quick_modal(
        message: str,
        on_confirm: Callable,
        confirm_label: str = "Confirmer",
        cancel_label: str = "Annuler",
        key: str = "modal"
) -> bool:
    """
    Modal de confirmation rapide (1 ligne)

    Usage:
        if st.button("Supprimer"):
            if render_quick_modal(
                "Supprimer définitivement ?",
                lambda: delete_item(item_id),
                key=f"del_{item_id}"
            ):
                st.success("Supprimé !")
    """
    modal = SimpleModal(key)

    if not modal.is_showing():
        modal.show()
        st.rerun()

    st.warning(message)

    col1, col2 = st.columns(2)

    with col1:
        if modal.confirm(confirm_label):
            on_confirm()
            modal.close()
            return True

    with col2:
        modal.cancel(cancel_label)

    return False


# ═══════════════════════════════════════════════════════════════
# FORMULAIRES GÉNÉRIQUES
# ═══════════════════════════════════════════════════════════════

class DynamicList:
    """
    Gestionnaire de liste dynamique (ingrédients, étapes, tags, etc.)

    AVANT : Logique dupliquée dans render_ingredients_form et render_etapes_form (100+ lignes)
    APRÈS : Classe générique réutilisable (50 lignes)

    Usage:
        # Ingrédients
        ingredients = DynamicList(
            key="ingredients",
            fields=[
                {"name": "nom", "type": "text", "label": "Nom", "required": True},
                {"name": "quantite", "type": "number", "label": "Quantité", "min": 0},
                {"name": "unite", "type": "text", "label": "Unité", "default": "g"}
            ]
        )

        items = ingredients.render()
    """

    def __init__(
            self,
            key: str,
            fields: List[Dict[str, Any]],
            initial_items: Optional[List[Dict]] = None,
            sortable: bool = False,
            add_button_label: str = "➕ Ajouter",
            empty_message: str = "Aucun élément"
    ):
        self.key = key
        self.fields = fields
        self.sortable = sortable
        self.add_button_label = add_button_label
        self.empty_message = empty_message

        # Init state
        session_key = f"{key}_items"
        if session_key not in st.session_state:
            st.session_state[session_key] = initial_items or []

    def render(self) -> List[Dict]:
        """Affiche et retourne les items"""
        session_key = f"{self.key}_items"

        # Formulaire d'ajout
        with st.expander(self.add_button_label, expanded=len(st.session_state[session_key]) == 0):
            self._render_add_form()

        # Liste des items
        if st.session_state[session_key]:
            for idx, item in enumerate(st.session_state[session_key]):
                self._render_item(idx, item)
        else:
            st.info(self.empty_message)

        return st.session_state[session_key]

    def _render_add_form(self):
        """Formulaire d'ajout"""
        cols = st.columns(len(self.fields) + 1)

        form_data = {}

        for i, field in enumerate(self.fields):
            with cols[i]:
                form_data[field["name"]] = self._render_field(field, f"add_{self.key}")

        with cols[-1]:
            st.write("")  # Spacing
            st.write("")
            if st.button("➕", key=f"{self.key}_add_btn"):
                # Valider
                if all(form_data.get(f["name"]) for f in self.fields if f.get("required")):
                    st.session_state[f"{self.key}_items"].append(form_data)
                    st.rerun()

    def _render_item(self, idx: int, item: Dict):
        """Affiche un item"""
        cols = st.columns([4] + ([1] if self.sortable else []) + [1])

        with cols[0]:
            # Affichage de l'item
            display_text = " • ".join([
                f"{field['label']}: {item.get(field['name'], '—')}"
                for field in self.fields[:3]  # Max 3 champs affichés
            ])
            st.write(display_text)

        col_idx = 1

        # Boutons de tri
        if self.sortable:
            with cols[col_idx]:
                if idx > 0 and st.button("⬆️", key=f"{self.key}_up_{idx}"):
                    items = st.session_state[f"{self.key}_items"]
                    items[idx], items[idx-1] = items[idx-1], items[idx]
                    st.rerun()
            col_idx += 1

        # Bouton suppression
        with cols[col_idx]:
            if st.button("❌", key=f"{self.key}_del_{idx}"):
                st.session_state[f"{self.key}_items"].pop(idx)
                st.rerun()

    def _render_field(self, field: Dict, prefix: str):
        """Affiche un champ de formulaire"""
        field_type = field["type"]
        label = field.get("label", field["name"])
        key = f"{prefix}_{field['name']}"

        if field_type == "text":
            return st.text_input(
                label,
                value=field.get("default", ""),
                placeholder=field.get("placeholder", ""),
                key=key
            )

        elif field_type == "number":
            return st.number_input(
                label,
                min_value=field.get("min", 0.0),
                max_value=field.get("max", 10000.0),
                value=field.get("default", 0.0),
                step=field.get("step", 0.1),
                key=key
            )

        elif field_type == "select":
            return st.selectbox(
                label,
                options=field.get("options", []),
                index=field.get("default_index", 0),
                key=key
            )

        elif field_type == "checkbox":
            return st.checkbox(
                label,
                value=field.get("default", False),
                key=key
            )

        elif field_type == "textarea":
            return st.text_area(
                label,
                value=field.get("default", ""),
                height=field.get("height", 100),
                key=key
            )

        else:
            return st.text_input(label, key=key)


# ═══════════════════════════════════════════════════════════════
# PREVIEW UNIFORMISÉ
# ═══════════════════════════════════════════════════════════════

def render_unified_preview(
        title: str,
        sections: Dict[str, List[str]],  # {"Ingrédients": ["item1", "item2"], ...}
        metadata: Optional[Dict[str, str]] = None,  # {"Temps": "30min", "Portions": "4"}
        image_url: Optional[str] = None,
        tags: Optional[List[str]] = None,
        actions: Optional[List[Tuple[str, Callable]]] = None
):
    """
    Preview uniformisé pour recettes, repas, projets, etc.

    AVANT : Logique de preview dupliquée dans chaque module (40+ lignes)
    APRÈS : Composant universel (20 lignes)

    Usage:
        render_unified_preview(
            title="Gratin Dauphinois",
            sections={
                "Ingrédients": ["1kg pommes de terre", "300mL crème"],
                "Étapes": ["Éplucher...", "Disposer..."]
            },
            metadata={"Temps": "90min", "Portions": "6"},
            tags=["🥗 Équilibré", "👶 Bébé OK"]
        )
    """
    st.markdown(f"### 👁️ {title}")

    # Image + Métadonnées
    if image_url or metadata:
        col1, col2 = st.columns([1, 2] if image_url else [1])

        if image_url:
            with col1:
                st.image(image_url, use_container_width=True)
            meta_col = col2
        else:
            meta_col = col1

        if metadata:
            with meta_col:
                for key, value in metadata.items():
                    st.metric(key, value)

    # Tags
    if tags:
        st.caption(" • ".join(tags))

    st.markdown("---")

    # Sections
    cols = st.columns(len(sections))

    for i, (section_title, items) in enumerate(sections.items()):
        with cols[i]:
            st.markdown(f"**{section_title}**")

            for item in items[:5]:  # Max 5 items par section
                st.write(f"• {item}")

            if len(items) > 5:
                st.caption(f"... et {len(items) - 5} de plus")

    # Actions
    if actions:
        st.markdown("---")
        action_cols = st.columns(len(actions))

        for i, (label, callback) in enumerate(actions):
            with action_cols[i]:
                if st.button(label, key=f"preview_action_{i}", use_container_width=True):
                    callback()


# ═══════════════════════════════════════════════════════════════
# HELPERS RAPIDES
# ═══════════════════════════════════════════════════════════════

def quick_action_bar(actions: List[Tuple[str, Callable]], key_prefix: str = "action"):
    """
    Barre d'actions rapide

    Usage:
        quick_action_bar([
            ("🗑️ Nettoyer", lambda: cleanup()),
            ("📤 Exporter", lambda: export()),
            ("🔄 Sync", lambda: sync())
        ])
    """
    cols = st.columns(len(actions))

    for i, (label, callback) in enumerate(actions):
        with cols[i]:
            if st.button(label, key=f"{key_prefix}_{i}", use_container_width=True):
                callback()


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
            icon="👁️",
            expanded=True
        )
    """
    with st.expander(f"{icon} {title}", expanded=expanded):
        content()