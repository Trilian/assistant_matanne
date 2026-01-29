"""
Base Form - Générateur de formulaires universel
"""

from datetime import date
from typing import Callable, Any, Optional

import streamlit as st

# ═══════════════════════════════════════════════════════════
# FORM BUILDER
# ═══════════════════════════════════════════════════════════


class FormBuilder:
    """
    Générateur de formulaires dynamiques

    Usage:
        form = FormBuilder("my_form")
        form.add_text("nom", "Nom", required=True)
        form.add_number("age", "Âge", min_value=0)

        if form.submit():
            data = form.get_data()
    """

    def __init__(self, form_id: str, title: Optional[str] = None):
        self.form_id = form_id
        self.title = title
        self.fields = []
        self.data = {}

    # ═══════════════════════════════════════════════════════
    # AJOUT CHAMPS
    # ═══════════════════════════════════════════════════════

    def add_text(
        self,
        name: str,
        label: str,
        required: bool = False,
        default: str = "",
        max_length: Optional[int] = None,
        help_text: Optional[str] = None,
    ):
        """Ajoute champ texte"""
        self.fields.append(
            {
                "type": "text",
                "name": name,
                "label": label + (" *" if required else ""),
                "required": required,
                "default": default,
                "max_length": max_length,
                "help": help_text,
            }
        )
        return self

    def add_textarea(
        self,
        name: str,
        label: str,
        required: bool = False,
        default: str = "",
        height: int = 100,
        help_text: Optional[str] = None,
    ):
        """Ajoute textarea"""
        self.fields.append(
            {
                "type": "textarea",
                "name": name,
                "label": label + (" *" if required else ""),
                "required": required,
                "default": default,
                "height": height,
                "help": help_text,
            }
        )
        return self

    def add_number(
        self,
        name: str,
        label: str,
        required: bool = False,
        default: float = 0.0,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        step: float = 1.0,
        help_text: Optional[str] = None,
    ):
        """Ajoute champ nombre"""
        self.fields.append(
            {
                "type": "number",
                "name": name,
                "label": label + (" *" if required else ""),
                "required": required,
                "default": default,
                "min_value": min_value,
                "max_value": max_value,
                "step": step,
                "help": help_text,
            }
        )
        return self

    def add_select(
        self,
        name: str,
        label: str,
        options: list[str],
        required: bool = False,
        default: Optional[str] = None,
        help_text: Optional[str] = None,
    ):
        """Ajoute select"""
        self.fields.append(
            {
                "type": "select",
                "name": name,
                "label": label + (" *" if required else ""),
                "required": required,
                "options": options,
                "default": default or (options[0] if options else None),
                "help": help_text,
            }
        )
        return self

    def add_multiselect(
        self,
        name: str,
        label: str,
        options: list[str],
        required: bool = False,
        default: Optional[list[str]] = None,
        help_text: Optional[str] = None,
    ):
        """Ajoute multiselect"""
        self.fields.append(
            {
                "type": "multiselect",
                "name": name,
                "label": label + (" *" if required else ""),
                "required": required,
                "options": options,
                "default": default or [],
                "help": help_text,
            }
        )
        return self

    def add_checkbox(self, name: str, label: str, default: bool = False, help_text: Optional[str] = None):
        """Ajoute checkbox"""
        self.fields.append(
            {
                "type": "checkbox",
                "name": name,
                "label": label,
                "default": default,
                "help": help_text,
            }
        )
        return self

    def add_date(
        self,
        name: str,
        label: str,
        required: bool = False,
        default: Optional[date] = None,
        min_value: Optional[date] = None,
        max_value: Optional[date] = None,
        help_text: Optional[str] = None,
    ):
        """Ajoute date"""
        self.fields.append(
            {
                "type": "date",
                "name": name,
                "label": label + (" *" if required else ""),
                "required": required,
                "default": default or date.today(),
                "min_value": min_value,
                "max_value": max_value,
                "help": help_text,
            }
        )
        return self

    def add_slider(
        self,
        name: str,
        label: str,
        min_value: int = 0,
        max_value: int = 100,
        default: int = 50,
        help_text: Optional[str] = None,
    ):
        """Ajoute slider"""
        self.fields.append(
            {
                "type": "slider",
                "name": name,
                "label": label,
                "min_value": min_value,
                "max_value": max_value,
                "default": default,
                "help": help_text,
            }
        )
        return self

    def add_divider(self):
        """Ajoute séparateur"""
        self.fields.append({"type": "divider"})
        return self

    def add_header(self, text: str):
        """Ajoute header"""
        self.fields.append({"type": "header", "text": text})
        return self

    # ═══════════════════════════════════════════════════════
    # RENDER
    # ═══════════════════════════════════════════════════════

    def render(self, on_submit: Optional[Callable[[dict], Any]] = None, on_cancel: Optional[Callable[[], Any]] = None) -> bool:
        """
        Render formulaire

        Returns:
            True si soumis avec succès
        """
        if self.title:
            st.markdown(f"### {self.title}")

        with st.form(self.form_id):
            # Render champs
            for field in self.fields:
                self._render_field(field)

            # Boutons
            col1, col2 = st.columns(2)

            with col1:
                submitted = st.form_submit_button(
                    "✅ Valider", type="primary", use_container_width=True
                )

            with col2:
                cancelled = st.form_submit_button("❌ Annuler", use_container_width=True)

            if cancelled and on_cancel:
                on_cancel()
                return False

            if submitted:
                # Validation
                if self._validate():
                    if on_submit:
                        on_submit(self.data)
                    return True
                else:
                    st.error("⚠️ Champs requis manquants")
                    return False

        return False

    def _render_field(self, field: dict):
        """Render un champ"""
        field_type = field["type"]

        if field_type == "divider":
            st.markdown("---")

        elif field_type == "header":
            st.markdown(f"#### {field['text']}")

        elif field_type == "text":
            value = st.text_input(
                field["label"],
                value=field["default"],
                max_chars=field.get("max_length"),
                help=field.get("help"),
                key=f"{self.form_id}_{field['name']}",
            )
            self.data[field["name"]] = value

        elif field_type == "textarea":
            value = st.text_area(
                field["label"],
                value=field["default"],
                height=field.get("height", 100),
                help=field.get("help"),
                key=f"{self.form_id}_{field['name']}",
            )
            self.data[field["name"]] = value

        elif field_type == "number":
            value = st.number_input(
                field["label"],
                value=float(field["default"]),
                min_value=field.get("min_value"),
                max_value=field.get("max_value"),
                step=field.get("step", 1.0),
                help=field.get("help"),
                key=f"{self.form_id}_{field['name']}",
            )
            self.data[field["name"]] = value

        elif field_type == "select":
            value = st.selectbox(
                field["label"],
                options=field["options"],
                index=field["options"].index(field["default"]),
                help=field.get("help"),
                key=f"{self.form_id}_{field['name']}",
            )
            self.data[field["name"]] = value

        elif field_type == "multiselect":
            value = st.multiselect(
                field["label"],
                options=field["options"],
                default=field["default"],
                help=field.get("help"),
                key=f"{self.form_id}_{field['name']}",
            )
            self.data[field["name"]] = value

        elif field_type == "checkbox":
            value = st.checkbox(
                field["label"],
                value=field["default"],
                help=field.get("help"),
                key=f"{self.form_id}_{field['name']}",
            )
            self.data[field["name"]] = value

        elif field_type == "date":
            value = st.date_input(
                field["label"],
                value=field["default"],
                min_value=field.get("min_value"),
                max_value=field.get("max_value"),
                help=field.get("help"),
                key=f"{self.form_id}_{field['name']}",
            )
            self.data[field["name"]] = value

        elif field_type == "slider":
            value = st.slider(
                field["label"],
                min_value=field["min_value"],
                max_value=field["max_value"],
                value=field["default"],
                help=field.get("help"),
                key=f"{self.form_id}_{field['name']}",
            )
            self.data[field["name"]] = value

    def _validate(self) -> bool:
        """Valide champs requis"""
        for field in self.fields:
            if field.get("required", False):
                name = field["name"]
                value = self.data.get(name)

                if value is None or value == "" or value == []:
                    return False

        return True

    def get_data(self) -> dict:
        """Récupère données formulaire"""
        return self.data
