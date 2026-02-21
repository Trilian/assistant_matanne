"""Mixin: méthodes fluides pour ajouter des champs au formulaire."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, Any, Callable

from .types import ChampConfig, TypeChamp

if TYPE_CHECKING:
    from .builder import FormBuilder


class FormFieldsMixin:
    """Fournit les 12 méthodes de construction fluide + _add_field et section.

    Attend sur ``self``: _fields (list[ChampConfig]), _current_section.
    """

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
        return self  # type: ignore[return-value]

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
        return self  # type: ignore[return-value]

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
        return self  # type: ignore[return-value]

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
        return self  # type: ignore[return-value]

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
        return self  # type: ignore[return-value]

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
        return self  # type: ignore[return-value]

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
        return self  # type: ignore[return-value]

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
        config.height = height  # type: ignore[attr-defined]
        self._add_field(config)
        return self  # type: ignore[return-value]

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
        return self  # type: ignore[return-value]

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
        return self  # type: ignore[return-value]

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
        return self  # type: ignore[return-value]

    def section(self, title: str) -> FormBuilder:
        """Démarre une nouvelle section dans le formulaire."""
        self._current_section = title
        return self  # type: ignore[return-value]

    def _add_field(self, config: ChampConfig) -> None:
        """Ajoute un champ à la liste."""
        self._fields.append(config)
