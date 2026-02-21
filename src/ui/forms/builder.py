"""
FormBuilder - Système de formulaires déclaratifs avec validation.

Compose ``FormFieldsMixin`` (champs fluides) et ``FormRenderingMixin``
(rendu Streamlit + validation) pour une API chainée propre.

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
from typing import Any

import streamlit as st

from .fields import FormFieldsMixin
from .rendering import FormRenderingMixin
from .types import ChampConfig, FormResult, TypeChamp

logger = logging.getLogger(__name__)


class FormBuilder(FormFieldsMixin, FormRenderingMixin):
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
    # RENDU
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
