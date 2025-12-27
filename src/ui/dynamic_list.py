"""
DynamicList - Composant liste dynamique réutilisable
Gère ajout/suppression/réordonnancement d'items
"""
import streamlit as st
from typing import List, Dict, Optional, Callable, Any


class DynamicList:
    """
    Composant liste dynamique générique

    Usage:
        ingredients = DynamicList(
            session_key="ingredients_list",
            fields=[
                {"name": "nom", "type": "text", "label": "Nom"},
                {"name": "quantite", "type": "number", "label": "Quantité"},
                {"name": "unite", "type": "select", "label": "Unité", "options": ["g", "kg"]}
            ],
            add_button_label="➕ Ajouter ingrédient"
        )

        items = ingredients.render()
    """

    def __init__(
            self,
            session_key: str,
            fields: List[Dict[str, Any]],
            add_button_label: str = "➕ Ajouter",
            initial_items: Optional[List[Dict]] = None,
            show_order: bool = True,
            allow_reorder: bool = True,
            item_renderer: Optional[Callable[[Dict, int, str], None]] = None
    ):
        """
        Args:
            session_key: Clé session_state unique
            fields: Configuration des champs [
                {
                    "name": "nom",
                    "type": "text/number/select/checkbox/date",
                    "label": "Label",
                    "default": valeur_defaut,
                    "options": [] (pour select),
                    "min": 0 (pour number),
                    "max": 100 (pour number)
                }
            ]
            add_button_label: Label bouton d'ajout
            initial_items: Items initiaux
            show_order: Afficher numéros d'ordre
            allow_reorder: Permettre réordonnancement
            item_renderer: Fonction custom pour afficher un item
        """
        self.session_key = session_key
        self.fields = fields
        self.add_button_label = add_button_label
        self.show_order = show_order
        self.allow_reorder = allow_reorder
        self.item_renderer = item_renderer

        # Initialiser session state
        if self.session_key not in st.session_state:
            st.session_state[self.session_key] = initial_items or []

    def render(self) -> List[Dict]:
        """
        Affiche la liste et retourne les items

        Returns:
            Liste des items
        """
        items = st.session_state[self.session_key]

        # Formulaire d'ajout
        self._render_add_form()

        st.markdown("---")

        # Liste des items
        if items:
            for idx, item in enumerate(items):
                if self.item_renderer:
                    # Renderer custom
                    self.item_renderer(item, idx, self.session_key)
                else:
                    # Renderer par défaut
                    self._render_item_default(item, idx)
        else:
            st.info("Aucun élément ajouté")

        return items

    def _render_add_form(self):
        """Formulaire d'ajout"""
        with st.expander(self.add_button_label, expanded=len(st.session_state[self.session_key]) == 0):
            # Créer colonnes selon nombre de champs
            cols = st.columns(len(self.fields))

            form_data = {}

            # Rendre chaque champ
            for idx, field in enumerate(self.fields):
                with cols[idx]:
                    form_data[field["name"]] = self._render_field(
                        field,
                        f"{self.session_key}_add_{field['name']}"
                    )

            # Bouton d'ajout
            if st.button(
                    "➕ Ajouter",
                    key=f"{self.session_key}_add_btn",
                    use_container_width=True
            ):
                # Valider
                if self._validate_item(form_data):
                    # Ajouter ordre si nécessaire
                    if self.show_order:
                        form_data["ordre"] = len(st.session_state[self.session_key]) + 1

                    st.session_state[self.session_key].append(form_data)
                    st.rerun()

    def _render_field(self, field: Dict, key: str) -> Any:
        """Rend un champ selon son type"""
        field_type = field.get("type", "text")
        label = field.get("label", field["name"])
        default = field.get("default")

        if field_type == "text":
            return st.text_input(
                label,
                value=default or "",
                key=key,
                placeholder=field.get("placeholder", "")
            )

        elif field_type == "number":
            return st.number_input(
                label,
                min_value=field.get("min", 0.0),
                max_value=field.get("max", 10000.0),
                value=float(default) if default else 1.0,
                step=field.get("step", 0.1),
                key=key
            )

        elif field_type == "select":
            options = field.get("options", [])
            default_idx = 0
            if default and default in options:
                default_idx = options.index(default)

            return st.selectbox(
                label,
                options,
                index=default_idx,
                key=key
            )

        elif field_type == "checkbox":
            return st.checkbox(
                label,
                value=bool(default),
                key=key
            )

        elif field_type == "date":
            return st.date_input(
                label,
                value=default,
                key=key
            )

        elif field_type == "textarea":
            return st.text_area(
                label,
                value=default or "",
                height=field.get("height", 100),
                key=key
            )

        else:
            return st.text_input(label, value=default or "", key=key)

    def _render_item_default(self, item: Dict, idx: int):
        """Affiche un item (mode par défaut)"""
        col1, col2, col3 = st.columns([5, 1, 1])

        with col1:
            # Afficher les valeurs
            display_parts = []

            if self.show_order and "ordre" in item:
                display_parts.append(f"**{item['ordre']}.**")

            for field in self.fields:
                name = field["name"]
                if name in item and name != "ordre":
                    value = item[name]
                    label = field.get("short_label", field.get("label", name))

                    if isinstance(value, bool):
                        display_parts.append(f"{'✓' if value else '✗'} {label}")
                    else:
                        display_parts.append(f"{value} {label}")

            st.write(" ".join(display_parts))

        with col2:
            # Réordonnancement
            if self.allow_reorder:
                if idx > 0:
                    if st.button("⬆️", key=f"{self.session_key}_up_{idx}"):
                        self._move_item(idx, -1)
                        st.rerun()

                if idx < len(st.session_state[self.session_key]) - 1:
                    if st.button("⬇️", key=f"{self.session_key}_down_{idx}"):
                        self._move_item(idx, 1)
                        st.rerun()

        with col3:
            # Suppression
            if st.button("🗑️", key=f"{self.session_key}_del_{idx}"):
                self._delete_item(idx)
                st.rerun()

    def _move_item(self, idx: int, direction: int):
        """Déplace un item"""
        items = st.session_state[self.session_key]
        new_idx = idx + direction

        if 0 <= new_idx < len(items):
            items[idx], items[new_idx] = items[new_idx], items[idx]

            # Mettre à jour ordres
            if self.show_order:
                for i, item in enumerate(items):
                    item["ordre"] = i + 1

    def _delete_item(self, idx: int):
        """Supprime un item"""
        items = st.session_state[self.session_key]
        items.pop(idx)

        # Réordonner
        if self.show_order:
            for i, item in enumerate(items):
                item["ordre"] = i + 1

    def _validate_item(self, item: Dict) -> bool:
        """Valide un item"""
        for field in self.fields:
            name = field["name"]
            required = field.get("required", False)

            if required and not item.get(name):
                st.error(f"{field.get('label', name)} est obligatoire")
                return False

        return True

    def clear(self):
        """Vide la liste"""
        st.session_state[self.session_key] = []

    def add_item(self, item: Dict):
        """Ajoute un item programmatiquement"""
        if self.show_order:
            item["ordre"] = len(st.session_state[self.session_key]) + 1

        st.session_state[self.session_key].append(item)

    def get_items(self) -> List[Dict]:
        """Retourne les items"""
        return st.session_state[self.session_key]


# ═══════════════════════════════════════════════════════════════
# EXEMPLES D'USAGE
# ═══════════════════════════════════════════════════════════════

def example_ingredients_list(key: str = "ingredients") -> List[Dict]:
    """Exemple: Liste d'ingrédients"""

    ingredients = DynamicList(
        session_key=key,
        fields=[
            {
                "name": "nom",
                "type": "text",
                "label": "Ingrédient",
                "required": True,
                "placeholder": "Ex: Tomates"
            },
            {
                "name": "quantite",
                "type": "number",
                "label": "Qté",
                "default": 1.0,
                "min": 0.1,
                "step": 0.1
            },
            {
                "name": "unite",
                "type": "select",
                "label": "Unité",
                "options": ["pcs", "kg", "g", "L", "mL"],
                "default": "pcs"
            },
            {
                "name": "optionnel",
                "type": "checkbox",
                "label": "Opt.",
                "default": False
            }
        ],
        add_button_label="➕ Ajouter un ingrédient"
    )

    return ingredients.render()


def example_etapes_list(key: str = "etapes") -> List[Dict]:
    """Exemple: Liste d'étapes"""

    etapes = DynamicList(
        session_key=key,
        fields=[
            {
                "name": "description",
                "type": "textarea",
                "label": "Description",
                "required": True,
                "height": 100
            },
            {
                "name": "duree",
                "type": "number",
                "label": "Durée (min)",
                "default": None,
                "min": 0,
                "max": 300,
                "step": 5
            }
        ],
        add_button_label="➕ Ajouter une étape",
        show_order=True,
        allow_reorder=True
    )

    return etapes.render()


def example_courses_list(key: str = "courses") -> List[Dict]:
    """Exemple: Liste de courses"""

    # Renderer custom pour courses
    def render_course_item(item: Dict, idx: int, session_key: str):
        col1, col2, col3 = st.columns([4, 2, 1])

        with col1:
            priorite_icon = {"haute": "🔴", "moyenne": "🟡", "basse": "🟢"}
            icon = priorite_icon.get(item.get("priorite", "moyenne"), "⚪")

            st.markdown(f"{icon} **{item['nom']}** - {item['quantite']} {item['unite']}")

            if item.get("notes"):
                st.caption(item["notes"])

        with col2:
            if item.get("magasin"):
                st.caption(f"🏬 {item['magasin']}")

        with col3:
            if st.button("🗑️", key=f"{session_key}_del_{idx}"):
                st.session_state[session_key].pop(idx)
                st.rerun()

    courses = DynamicList(
        session_key=key,
        fields=[
            {"name": "nom", "type": "text", "label": "Article", "required": True},
            {"name": "quantite", "type": "number", "label": "Qté", "default": 1.0},
            {"name": "unite", "type": "select", "label": "Unité", "options": ["pcs", "kg", "L"]},
            {
                "name": "priorite",
                "type": "select",
                "label": "Priorité",
                "options": ["haute", "moyenne", "basse"],
                "default": "moyenne"
            },
            {"name": "magasin", "type": "text", "label": "Magasin"},
            {"name": "notes", "type": "text", "label": "Notes"}
        ],
        add_button_label="➕ Ajouter un article",
        show_order=False,
        item_renderer=render_course_item
    )

    return courses.render()