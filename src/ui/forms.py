"""
Composants Formulaires
Tous les inputs, forms, listes dynamiques
"""
import streamlit as st
from typing import List, Dict, Optional, Callable, Any
from datetime import date, time, datetime


# ═══════════════════════════════════════════════════════════════
# INPUTS BASIQUES
# ═══════════════════════════════════════════════════════════════

def form_field(field_config: Dict, key_prefix: str) -> Any:
    """
    Champ de formulaire générique

    Args:
        field_config: {
            "type": "text|number|select|checkbox|textarea|date|time",
            "name": str,
            "label": str,
            "default": Any,
            "required": bool,
            "help": str,
            "options": List (pour select),
            "min/max/step": (pour number)
        }
        key_prefix: Préfixe pour clé Streamlit

    Returns:
        Valeur du champ
    """
    field_type = field_config.get("type", "text")
    name = field_config.get("name", "field")
    label = field_config.get("label", name)
    required = field_config.get("required", False)
    help_text = field_config.get("help")
    key = f"{key_prefix}_{name}"

    if required:
        label = f"{label} *"

    # Render selon le type
    if field_type == "text":
        return st.text_input(
            label,
            value=field_config.get("default", ""),
            placeholder=field_config.get("placeholder", ""),
            help=help_text,
            key=key
        )

    elif field_type == "number":
        return st.number_input(
            label,
            value=float(field_config.get("default", 0)),
            min_value=field_config.get("min"),
            max_value=field_config.get("max"),
            step=field_config.get("step", 1),
            help=help_text,
            key=key
        )

    elif field_type == "select":
        options = field_config.get("options", [])
        default_idx = field_config.get("default", 0)
        return st.selectbox(label, options, index=default_idx, help=help_text, key=key)

    elif field_type == "multiselect":
        options = field_config.get("options", [])
        defaults = field_config.get("default", [])
        return st.multiselect(label, options, default=defaults, help=help_text, key=key)

    elif field_type == "checkbox":
        return st.checkbox(label, value=field_config.get("default", False), help=help_text, key=key)

    elif field_type == "textarea":
        return st.text_area(
            label,
            value=field_config.get("default", ""),
            height=field_config.get("height", 100),
            help=help_text,
            key=key
        )

    elif field_type == "date":
        return st.date_input(
            label,
            value=field_config.get("default", date.today()),
            min_value=field_config.get("min"),
            max_value=field_config.get("max"),
            help=help_text,
            key=key
        )

    elif field_type == "time":
        default_time = field_config.get("default")
        if isinstance(default_time, str):
            default_time = datetime.strptime(default_time, "%H:%M").time()
        return st.time_input(label, value=default_time or time(12, 0), help=help_text, key=key)

    elif field_type == "slider":
        return st.slider(
            label,
            min_value=field_config.get("min", 0),
            max_value=field_config.get("max", 100),
            value=field_config.get("default", 50),
            step=field_config.get("step", 1),
            help=help_text,
            key=key
        )

    else:
        return st.text_input(label, help=help_text, key=key)


def search_bar(placeholder: str = "Rechercher...", icon: str = "🔍", key: str = "search") -> str:
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


def filter_panel(filters_config: Dict[str, Dict], key_prefix: str) -> Dict:
    """
    Panneau de filtres dans expander

    Args:
        filters_config: {
            "filter_name": {
                "type": "select|checkbox|slider|...",
                "label": str,
                "options": List,
                "default": Any
            }
        }
        key_prefix: Préfixe pour clés

    Returns:
        Dict des valeurs sélectionnées
    """
    with st.expander("🔍 Filtres", expanded=False):
        results = {}

        for filter_name, config in filters_config.items():
            results[filter_name] = form_field(
                {**config, "name": filter_name},
                key_prefix
            )

        return results


# ═══════════════════════════════════════════════════════════════
# LISTE DYNAMIQUE GÉNÉRIQUE
# ═══════════════════════════════════════════════════════════════

class DynamicList:
    """
    Liste dynamique universelle

    Permet d'ajouter/supprimer/réordonner des items
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
        """
        Args:
            key: Clé unique pour la liste
            fields: Liste des champs (voir form_field)
            initial_items: Items initiaux
            sortable: Permet de réordonner
            add_label: Label du bouton d'ajout
            item_renderer: Fonction custom pour afficher un item
        """
        self.key = key
        self.fields = fields
        self.sortable = sortable
        self.add_label = add_label
        self.item_renderer = item_renderer

        # Init state
        if f"{key}_items" not in st.session_state:
            st.session_state[f"{key}_items"] = initial_items or []

    def render(self) -> List[Dict]:
        """
        Affiche la liste et retourne les items

        Returns:
            Liste des items
        """
        items = st.session_state[f"{self.key}_items"]

        # Formulaire d'ajout
        with st.expander(self.add_label, expanded=len(items) == 0):
            self._render_add_form()

        # Liste des items
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
        """Formulaire d'ajout"""
        cols = st.columns(len(self.fields) + 1)
        form_data = {}

        # Champs
        for i, field in enumerate(self.fields):
            with cols[i]:
                form_data[field["name"]] = form_field(field, f"add_{self.key}")

        # Bouton
        with cols[-1]:
            st.write("")
            st.write("")
            if st.button("➕", key=f"{self.key}_add"):
                if self._validate(form_data):
                    st.session_state[f"{self.key}_items"].append(form_data)
                    st.rerun()

    def _render_item_default(self, item: Dict, idx: int):
        """Affichage par défaut d'un item"""
        col1, col2, col3 = st.columns([5, 1, 1])

        with col1:
            # Afficher les 3 premiers champs
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

    def _validate(self, data: Dict) -> bool:
        """Validation des données"""
        for field in self.fields:
            if field.get("required") and not data.get(field["name"]):
                st.error(f"{field.get('label', field['name'])} est requis")
                return False
        return True


# ═══════════════════════════════════════════════════════════════
# HELPERS SPÉCIFIQUES
# ═══════════════════════════════════════════════════════════════

def date_selector(
        label: str,
        default: Optional[date] = None,
        min_date: Optional[date] = None,
        max_date: Optional[date] = None,
        key: str = "date"
) -> date:
    """
    Sélecteur de date avec contraintes
    """
    return st.date_input(
        label,
        value=default or date.today(),
        min_value=min_date,
        max_value=max_date,
        key=key
    )


def time_range_selector(
        label: str,
        default_start: str = "08:00",
        default_end: str = "18:00",
        key: str = "time"
) -> tuple[str, str]:
    """
    Sélecteur de plage horaire

    Returns:
        (heure_debut, heure_fin)
    """
    st.markdown(f"**{label}**")

    col1, col2 = st.columns(2)

    with col1:
        start = st.time_input(
            "Début",
            value=datetime.strptime(default_start, "%H:%M").time(),
            key=f"{key}_start"
        )

    with col2:
        end = st.time_input(
            "Fin",
            value=datetime.strptime(default_end, "%H:%M").time(),
            key=f"{key}_end"
        )

    return start.strftime("%H:%M"), end.strftime("%H:%M")