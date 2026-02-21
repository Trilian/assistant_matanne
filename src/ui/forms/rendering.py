"""Mixin: rendu et validation des champs de formulaire."""

from __future__ import annotations

from typing import Any

import streamlit as st

from .types import ChampConfig, TypeChamp


class FormRenderingMixin:
    """Fournit _render_field et _validate.

    Attend sur ``self``: _key (str), _fields (list[ChampConfig]).
    """

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
