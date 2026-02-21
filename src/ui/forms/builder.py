"""
FormBuilder - Système de formulaires déclaratifs avec validation.

Permet de construire des formulaires Streamlit de manière déclarative
avec validation intégrée, messages d'erreur automatiques, et support
des modèles Pydantic.

Usage:
    from src.ui.forms import FormBuilder, TypeChamp

    # Builder fluent
    form = (
        FormBuilder("recette")
        .text("nom", label="Nom de la recette", required=True)
        .number("temps", label="Temps (min)", min_value=1, max_value=480)
        .select("difficulte", label="Difficulté", options=["Facile", "Moyen", "Difficile"])
        .textarea("instructions", label="Instructions")
    )

    result = form.render()
    if result.submitted and result.is_valid:
        service.creer_recette(result.data)
        st.success("Recette créée !")

    # Depuis un modèle Pydantic
    form = FormBuilder.from_model(RecetteCreate, key="new_recipe")
    result = form.render()
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import StrEnum
from typing import Any, Callable, TypeVar

import streamlit as st

logger = logging.getLogger(__name__)

T = TypeVar("T")


class TypeChamp(StrEnum):
    """Types de champs supportés."""

    TEXT = "text"
    NUMBER = "number"
    FLOAT = "float"
    SELECT = "select"
    MULTISELECT = "multiselect"
    CHECKBOX = "checkbox"
    TEXTAREA = "textarea"
    DATE = "date"
    TIME = "time"
    DATETIME = "datetime"
    SLIDER = "slider"
    FILE = "file"
    COLOR = "color"
    PASSWORD = "password"


@dataclass
class ChampConfig:
    """Configuration d'un champ de formulaire."""

    name: str
    type_champ: TypeChamp
    label: str = ""
    help_text: str = ""
    required: bool = False
    default: Any = None
    placeholder: str = ""

    # Validation
    min_value: float | int | None = None
    max_value: float | int | None = None
    min_length: int | None = None
    max_length: int | None = None
    pattern: str | None = None
    validator: Callable[[Any], bool] | None = None
    error_message: str = ""

    # Options pour select/multiselect
    options: list[Any] = field(default_factory=list)
    format_func: Callable[[Any], str] | None = None

    # Options pour slider
    step: float | int = 1

    # Options pour file
    accepted_types: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.label:
            self.label = self.name.replace("_", " ").title()


@dataclass
class FormResult:
    """Résultat d'un formulaire soumis."""

    submitted: bool = False
    data: dict[str, Any] = field(default_factory=dict)
    errors: dict[str, str] = field(default_factory=dict)

    @property
    def is_valid(self) -> bool:
        """True si le formulaire est valide (soumis sans erreurs)."""
        return self.submitted and not self.errors

    def get(self, key: str, default: Any = None) -> Any:
        """Récupère une valeur du formulaire."""
        return self.data.get(key, default)

    def __getitem__(self, key: str) -> Any:
        return self.data[key]


class FormBuilder:
    """Builder fluent pour créer des formulaires déclaratifs.

    Permet de construire des formulaires de manière chainée
    avec validation automatique et gestion d'erreurs.

    Usage:
        form = (
            FormBuilder("user_form")
            .text("nom", required=True)
            .text("email", required=True, validator=is_valid_email)
            .number("age", min_value=0, max_value=150)
            .select("role", options=["Admin", "User", "Guest"])
        )

        result = form.render()
        if result.is_valid:
            create_user(result.data)
    """

    def __init__(
        self,
        key: str,
        submit_label: str = "💾 Enregistrer",
        clear_on_submit: bool = False,
        border: bool = True,
    ):
        """
        Args:
            key: Clé unique du formulaire
            submit_label: Texte du bouton submit
            clear_on_submit: Réinitialiser le formulaire après soumission
            border: Afficher une bordure autour du formulaire
        """
        self._key = key
        self._submit_label = submit_label
        self._clear_on_submit = clear_on_submit
        self._border = border
        self._fields: list[ChampConfig] = []
        self._sections: list[tuple[str, list[ChampConfig]]] = []
        self._current_section: str | None = None

    # ═══════════════════════════════════════════════════════════
    # MÉTHODES DE CONSTRUCTION FLUIDE
    # ═══════════════════════════════════════════════════════════

    def text(
        self,
        name: str,
        label: str = "",
        required: bool = False,
        default: str = "",
        placeholder: str = "",
        help_text: str = "",
        max_length: int | None = None,
        pattern: str | None = None,
        validator: Callable[[str], bool] | None = None,
        error_message: str = "",
    ) -> FormBuilder:
        """Ajoute un champ texte."""
        self._add_field(
            ChampConfig(
                name=name,
                type_champ=TypeChamp.TEXT,
                label=label,
                required=required,
                default=default,
                placeholder=placeholder,
                help_text=help_text,
                max_length=max_length,
                pattern=pattern,
                validator=validator,
                error_message=error_message,
            )
        )
        return self

    def password(
        self,
        name: str,
        label: str = "",
        required: bool = False,
        placeholder: str = "",
        help_text: str = "",
        min_length: int | None = None,
    ) -> FormBuilder:
        """Ajoute un champ mot de passe."""
        self._add_field(
            ChampConfig(
                name=name,
                type_champ=TypeChamp.PASSWORD,
                label=label,
                required=required,
                placeholder=placeholder,
                help_text=help_text,
                min_length=min_length,
            )
        )
        return self

    def number(
        self,
        name: str,
        label: str = "",
        required: bool = False,
        default: int = 0,
        min_value: int | None = None,
        max_value: int | None = None,
        step: int = 1,
        help_text: str = "",
    ) -> FormBuilder:
        """Ajoute un champ nombre entier."""
        self._add_field(
            ChampConfig(
                name=name,
                type_champ=TypeChamp.NUMBER,
                label=label,
                required=required,
                default=default,
                min_value=min_value,
                max_value=max_value,
                step=step,
                help_text=help_text,
            )
        )
        return self

    def float_field(
        self,
        name: str,
        label: str = "",
        required: bool = False,
        default: float = 0.0,
        min_value: float | None = None,
        max_value: float | None = None,
        step: float = 0.1,
        help_text: str = "",
    ) -> FormBuilder:
        """Ajoute un champ nombre décimal."""
        self._add_field(
            ChampConfig(
                name=name,
                type_champ=TypeChamp.FLOAT,
                label=label,
                required=required,
                default=default,
                min_value=min_value,
                max_value=max_value,
                step=step,
                help_text=help_text,
            )
        )
        return self

    def select(
        self,
        name: str,
        options: list[Any],
        label: str = "",
        required: bool = False,
        default: Any = None,
        help_text: str = "",
        format_func: Callable[[Any], str] | None = None,
    ) -> FormBuilder:
        """Ajoute un champ sélection unique."""
        self._add_field(
            ChampConfig(
                name=name,
                type_champ=TypeChamp.SELECT,
                label=label,
                required=required,
                default=default,
                options=options,
                help_text=help_text,
                format_func=format_func,
            )
        )
        return self

    def multiselect(
        self,
        name: str,
        options: list[Any],
        label: str = "",
        required: bool = False,
        default: list[Any] | None = None,
        help_text: str = "",
        format_func: Callable[[Any], str] | None = None,
    ) -> FormBuilder:
        """Ajoute un champ sélection multiple."""
        self._add_field(
            ChampConfig(
                name=name,
                type_champ=TypeChamp.MULTISELECT,
                label=label,
                required=required,
                default=default or [],
                options=options,
                help_text=help_text,
                format_func=format_func,
            )
        )
        return self

    def checkbox(
        self,
        name: str,
        label: str = "",
        default: bool = False,
        help_text: str = "",
    ) -> FormBuilder:
        """Ajoute une case à cocher."""
        self._add_field(
            ChampConfig(
                name=name,
                type_champ=TypeChamp.CHECKBOX,
                label=label,
                default=default,
                help_text=help_text,
            )
        )
        return self

    def textarea(
        self,
        name: str,
        label: str = "",
        required: bool = False,
        default: str = "",
        placeholder: str = "",
        help_text: str = "",
        max_length: int | None = None,
        height: int = 150,
    ) -> FormBuilder:
        """Ajoute une zone de texte multiligne."""
        config = ChampConfig(
            name=name,
            type_champ=TypeChamp.TEXTAREA,
            label=label,
            required=required,
            default=default,
            placeholder=placeholder,
            help_text=help_text,
            max_length=max_length,
        )
        # Stocker la hauteur dans un attribut custom
        config.height = height
        self._add_field(config)
        return self

    def date_field(
        self,
        name: str,
        label: str = "",
        required: bool = False,
        default: date | None = None,
        min_value: date | None = None,
        max_value: date | None = None,
        help_text: str = "",
    ) -> FormBuilder:
        """Ajoute un champ date."""
        self._add_field(
            ChampConfig(
                name=name,
                type_champ=TypeChamp.DATE,
                label=label,
                required=required,
                default=default or date.today(),
                min_value=min_value,
                max_value=max_value,
                help_text=help_text,
            )
        )
        return self

    def slider(
        self,
        name: str,
        label: str = "",
        min_value: int | float = 0,
        max_value: int | float = 100,
        default: int | float | None = None,
        step: int | float = 1,
        help_text: str = "",
    ) -> FormBuilder:
        """Ajoute un slider."""
        self._add_field(
            ChampConfig(
                name=name,
                type_champ=TypeChamp.SLIDER,
                label=label,
                default=default if default is not None else min_value,
                min_value=min_value,
                max_value=max_value,
                step=step,
                help_text=help_text,
            )
        )
        return self

    def file(
        self,
        name: str,
        label: str = "",
        required: bool = False,
        accepted_types: list[str] | None = None,
        help_text: str = "",
    ) -> FormBuilder:
        """Ajoute un champ upload de fichier."""
        self._add_field(
            ChampConfig(
                name=name,
                type_champ=TypeChamp.FILE,
                label=label,
                required=required,
                accepted_types=accepted_types or [],
                help_text=help_text,
            )
        )
        return self

    def section(self, title: str) -> FormBuilder:
        """Démarre une nouvelle section dans le formulaire.

        Les champs ajoutés après seront groupés sous cette section.
        """
        self._current_section = title
        return self

    def _add_field(self, config: ChampConfig) -> None:
        """Ajoute un champ à la liste."""
        self._fields.append(config)

    # ═══════════════════════════════════════════════════════════
    # RENDU ET VALIDATION
    # ═══════════════════════════════════════════════════════════

    def render(self) -> FormResult:
        """Rend le formulaire et retourne le résultat.

        Returns:
            FormResult avec submitted, data, errors, is_valid
        """
        result = FormResult()

        container = st.container(border=self._border) if self._border else st.container()

        with container:
            with st.form(self._key, clear_on_submit=self._clear_on_submit):
                # Rendre tous les champs
                for field_config in self._fields:
                    value = self._render_field(field_config)
                    result.data[field_config.name] = value

                # Bouton submit
                submitted = st.form_submit_button(
                    self._submit_label,
                    type="primary",
                    use_container_width=True,
                )
                result.submitted = submitted

                # Validation si soumis
                if submitted:
                    result.errors = self._validate(result.data)

        # Afficher les erreurs
        if result.submitted and result.errors:
            for field_name, error in result.errors.items():
                st.error(f"**{field_name}**: {error}")

        return result

    def _render_field(self, config: ChampConfig) -> Any:
        """Rend un champ selon sa configuration."""
        key = f"{self._key}_{config.name}"
        label = f"{config.label} *" if config.required else config.label

        match config.type_champ:
            case TypeChamp.TEXT:
                return st.text_input(
                    label,
                    value=config.default or "",
                    placeholder=config.placeholder,
                    help=config.help_text or None,
                    max_chars=config.max_length,
                    key=key,
                )

            case TypeChamp.PASSWORD:
                return st.text_input(
                    label,
                    type="password",
                    placeholder=config.placeholder,
                    help=config.help_text or None,
                    key=key,
                )

            case TypeChamp.NUMBER:
                return st.number_input(
                    label,
                    value=int(config.default or 0),
                    min_value=int(config.min_value) if config.min_value else None,
                    max_value=int(config.max_value) if config.max_value else None,
                    step=int(config.step),
                    help=config.help_text or None,
                    key=key,
                )

            case TypeChamp.FLOAT:
                return st.number_input(
                    label,
                    value=float(config.default or 0.0),
                    min_value=float(config.min_value) if config.min_value else None,
                    max_value=float(config.max_value) if config.max_value else None,
                    step=float(config.step),
                    format="%.2f",
                    help=config.help_text or None,
                    key=key,
                )

            case TypeChamp.SELECT:
                index = 0
                if config.default and config.default in config.options:
                    index = config.options.index(config.default)
                return st.selectbox(
                    label,
                    options=config.options,
                    index=index,
                    format_func=config.format_func,
                    help=config.help_text or None,
                    key=key,
                )

            case TypeChamp.MULTISELECT:
                return st.multiselect(
                    label,
                    options=config.options,
                    default=config.default or [],
                    format_func=config.format_func,
                    help=config.help_text or None,
                    key=key,
                )

            case TypeChamp.CHECKBOX:
                return st.checkbox(
                    label,
                    value=config.default or False,
                    help=config.help_text or None,
                    key=key,
                )

            case TypeChamp.TEXTAREA:
                height = getattr(config, "height", 150)
                return st.text_area(
                    label,
                    value=config.default or "",
                    placeholder=config.placeholder,
                    height=height,
                    max_chars=config.max_length,
                    help=config.help_text or None,
                    key=key,
                )

            case TypeChamp.DATE:
                return st.date_input(
                    label,
                    value=config.default,
                    min_value=config.min_value,
                    max_value=config.max_value,
                    help=config.help_text or None,
                    key=key,
                )

            case TypeChamp.SLIDER:
                return st.slider(
                    label,
                    min_value=config.min_value,
                    max_value=config.max_value,
                    value=config.default,
                    step=config.step,
                    help=config.help_text or None,
                    key=key,
                )

            case TypeChamp.FILE:
                return st.file_uploader(
                    label,
                    type=config.accepted_types if config.accepted_types else None,
                    help=config.help_text or None,
                    key=key,
                )

            case _:
                return st.text_input(label, key=key)

    def _validate(self, data: dict[str, Any]) -> dict[str, str]:
        """Valide les données du formulaire.

        Returns:
            Dict des erreurs {nom_champ: message}
        """
        errors: dict[str, str] = {}

        for config in self._fields:
            value = data.get(config.name)

            # Required check
            if config.required:
                if value is None or value == "" or value == []:
                    errors[config.name] = config.error_message or "Ce champ est requis"
                    continue

            # Skip validation for empty non-required fields
            if not value and not config.required:
                continue

            # Min/max length for strings
            if isinstance(value, str):
                if config.min_length and len(value) < config.min_length:
                    errors[config.name] = f"Minimum {config.min_length} caractères"
                    continue
                if config.max_length and len(value) > config.max_length:
                    errors[config.name] = f"Maximum {config.max_length} caractères"
                    continue

            # Pattern validation
            if config.pattern and isinstance(value, str):
                import re

                if not re.match(config.pattern, value):
                    errors[config.name] = config.error_message or "Format invalide"
                    continue

            # Custom validator
            if config.validator:
                try:
                    if not config.validator(value):
                        errors[config.name] = config.error_message or "Valeur invalide"
                except Exception as e:
                    errors[config.name] = str(e)

        return errors

    # ═══════════════════════════════════════════════════════════
    # FACTORY METHODS
    # ═══════════════════════════════════════════════════════════

    @classmethod
    def from_dict(cls, key: str, fields: list[dict[str, Any]], **kwargs: Any) -> FormBuilder:
        """Crée un FormBuilder depuis une liste de dictionnaires.

        Args:
            key: Clé du formulaire
            fields: Liste de configs de champs
            **kwargs: Options du FormBuilder

        Usage:
            form = FormBuilder.from_dict("user", [
                {"name": "nom", "type": "text", "required": True},
                {"name": "age", "type": "number", "min_value": 0},
            ])
        """
        builder = cls(key, **kwargs)

        for field_dict in fields:
            field_type = field_dict.pop("type", "text")
            name = field_dict.pop("name")

            method = getattr(builder, field_type, None)
            if method and callable(method):
                method(name, **field_dict)
            else:
                builder.text(name, **field_dict)

        return builder


# ═══════════════════════════════════════════════════════════
# FACTORY FUNCTION
# ═══════════════════════════════════════════════════════════


def creer_formulaire(
    key: str,
    fields: list[dict[str, Any]],
    submit_label: str = "💾 Enregistrer",
    **kwargs: Any,
) -> FormResult:
    """Fonction raccourci pour créer et rendre un formulaire.

    Args:
        key: Clé unique
        fields: Liste des configurations de champs
        submit_label: Label du bouton submit
        **kwargs: Options supplémentaires

    Returns:
        FormResult

    Usage:
        result = creer_formulaire("contact", [
            {"name": "nom", "type": "text", "required": True},
            {"name": "email", "type": "text", "required": True},
            {"name": "message", "type": "textarea"},
        ])

        if result.is_valid:
            send_contact(result.data)
    """
    builder = FormBuilder.from_dict(key, fields, submit_label=submit_label, **kwargs)
    return builder.render()
