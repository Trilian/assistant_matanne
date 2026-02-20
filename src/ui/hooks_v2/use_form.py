"""
use_form - Hook de gestion de formulaires avec validation.

Simplifie la gestion d'état des formulaires complexes avec:
- État des champs centralisé
- Validation synchrone
- Gestion des erreurs par champ
- État dirty/touched tracking
- Submit handling

Usage:
    from src.ui.hooks_v2 import use_form

    form = use_form(
        "recette",
        initial={"nom": "", "temps": 30},
        validators={
            "nom": lambda v: "Nom requis" if not v else None,
            "temps": lambda v: "Min 5 minutes" if v < 5 else None,
        },
    )

    form.field("nom", st.text_input, "Nom de la recette")
    form.field("temps", st.number_input, "Temps (min)", min_value=0)

    if st.button("Soumettre"):
        if form.validate():
            submit_recipe(form.values)
        else:
            st.error("Formulaire invalide")
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Generic, TypeVar

import streamlit as st

T = TypeVar("T")


@dataclass
class FieldState:
    """État d'un champ de formulaire."""

    value: Any
    error: str | None = None
    touched: bool = False
    dirty: bool = False


@dataclass
class FormState(Generic[T]):
    """État complet d'un formulaire.

    Attributes:
        values: Dict des valeurs actuelles.
        errors: Dict des erreurs par champ.
        is_valid: True si aucune erreur.
        is_dirty: True si au moins un champ modifié.
        is_touched: True si au moins un champ touché.
    """

    values: dict[str, Any]
    errors: dict[str, str | None]
    fields: dict[str, FieldState]
    is_valid: bool
    is_dirty: bool
    is_touched: bool

    # Méthodes
    set_value: Callable[[str, Any], None]
    set_error: Callable[[str, str | None], None]
    validate: Callable[[], bool]
    reset: Callable[[], None]
    field: Callable[..., Any]


def use_form(
    key: str,
    initial: dict[str, Any],
    validators: dict[str, Callable[[Any], str | None]] | None = None,
    on_submit: Callable[[dict[str, Any]], None] | None = None,
) -> FormState:
    """Hook de gestion de formulaire.

    Args:
        key: Clé unique du formulaire.
        initial: Valeurs initiales des champs.
        validators: Dict de fonctions de validation par champ.
            Chaque validator retourne None si valide, sinon le message d'erreur.
        on_submit: Callback appelé lors d'un submit valide.

    Returns:
        FormState avec méthodes et état.

    Example:
        form = use_form(
            "new_recipe",
            initial={"nom": "", "categorie": "Plat", "temps": 30},
            validators={
                "nom": lambda v: "Requis" if not v.strip() else None,
                "temps": lambda v: "Min 5" if v < 5 else None,
            },
        )

        # Afficher les champs
        nom = form.field("nom", st.text_input, "Nom *")
        categorie = form.field("categorie", st.selectbox, "Catégorie",
                               options=["Entrée", "Plat", "Dessert"])
        temps = form.field("temps", st.number_input, "Temps (min)",
                          min_value=0, max_value=180)

        # Submit
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Valider", disabled=not form.is_valid):
                save_recipe(form.values)
        with col2:
            if st.button("Réinitialiser"):
                form.reset()
                st.rerun()
    """
    state_key = f"_form_{key}"
    validators = validators or {}

    # Initialiser l'état
    if state_key not in st.session_state:
        st.session_state[state_key] = {
            "values": dict(initial),
            "fields": {name: FieldState(value=value) for name, value in initial.items()},
            "initial": dict(initial),
        }

    state = st.session_state[state_key]

    def set_value(field_name: str, value: Any) -> None:
        """Met à jour la valeur d'un champ."""
        state["values"][field_name] = value
        if field_name in state["fields"]:
            state["fields"][field_name].value = value
            state["fields"][field_name].dirty = value != state["initial"].get(field_name)
            state["fields"][field_name].touched = True

            # Validation immédiate
            if field_name in validators:
                error = validators[field_name](value)
                state["fields"][field_name].error = error

    def set_error(field_name: str, error: str | None) -> None:
        """Définit une erreur pour un champ."""
        if field_name in state["fields"]:
            state["fields"][field_name].error = error

    def validate() -> bool:
        """Valide tous les champs.

        Returns:
            True si tous les champs sont valides.
        """
        all_valid = True

        for field_name, validator in validators.items():
            value = state["values"].get(field_name)
            error = validator(value)
            set_error(field_name, error)

            if error:
                all_valid = False

        return all_valid

    def reset() -> None:
        """Réinitialise le formulaire."""
        state["values"] = dict(state["initial"])
        state["fields"] = {
            name: FieldState(value=value) for name, value in state["initial"].items()
        }

    def render_field(
        field_name: str,
        widget_fn: Callable,
        label: str,
        **widget_kwargs: Any,
    ) -> Any:
        """Rend un champ avec gestion d'état automatique.

        Args:
            field_name: Nom du champ.
            widget_fn: Fonction Streamlit (st.text_input, st.selectbox, etc.).
            label: Label du champ.
            **widget_kwargs: Arguments additionnels pour le widget.

        Returns:
            Valeur du champ.
        """
        field_state = state["fields"].get(field_name, FieldState(value=None))
        current_value = state["values"].get(field_name, "")

        # Créer le widget avec une clé unique
        widget_key = f"{key}_{field_name}"

        # Déterminer le bon paramètre pour la valeur initiale
        if widget_fn in (st.text_input, st.text_area):
            widget_kwargs.setdefault("value", current_value)
        elif widget_fn == st.number_input:
            widget_kwargs.setdefault("value", current_value)
        elif widget_fn in (st.selectbox, st.radio):
            # Pour selectbox, on doit trouver l'index
            options = widget_kwargs.get("options", [])
            if current_value in options:
                widget_kwargs.setdefault("index", options.index(current_value))
        elif widget_fn == st.checkbox:
            widget_kwargs.setdefault("value", bool(current_value))

        # Rendre le widget
        new_value = widget_fn(label, key=widget_key, **widget_kwargs)

        # Mettre à jour si changé
        if new_value != current_value:
            set_value(field_name, new_value)

        # Afficher l'erreur si présente
        if field_state.error and field_state.touched:
            st.caption(f"⚠️ {field_state.error}")

        return new_value

    # Calculer les états dérivés
    errors = {name: fs.error for name, fs in state["fields"].items() if fs.error}
    is_valid = len(errors) == 0
    is_dirty = any(fs.dirty for fs in state["fields"].values())
    is_touched = any(fs.touched for fs in state["fields"].values())

    return FormState(
        values=state["values"],
        errors=errors,
        fields=state["fields"],
        is_valid=is_valid,
        is_dirty=is_dirty,
        is_touched=is_touched,
        set_value=set_value,
        set_error=set_error,
        validate=validate,
        reset=reset,
        field=render_field,
    )


__all__ = ["FormState", "FieldState", "use_form"]
