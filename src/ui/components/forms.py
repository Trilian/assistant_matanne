"""
UI Components - Forms
Champs formulaire, recherche, filtres

Fournit un système de formulaires type-safe via ``ConfigChamp`` (dataclass)
tout en conservant la rétrocompatibilité avec les dicts existants.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import StrEnum
from typing import Any

import streamlit as st

from src.ui.registry import composant_ui


class TypeChamp(StrEnum):
    """Types de champs pris en charge."""

    TEXT = "text"
    NUMBER = "number"
    SELECT = "select"
    MULTISELECT = "multiselect"
    CHECKBOX = "checkbox"
    TEXTAREA = "textarea"
    DATE = "date"
    SLIDER = "slider"


@dataclass
class ConfigChamp:
    """Configuration déclarative d'un champ de formulaire.

    Peut être converti en dict via ``asdict()`` pour la rétrocompatibilité.

    Usage::

        champ = ConfigChamp(
            type=TypeChamp.TEXT,
            name="nom",
            label="Nom de la recette",
            required=True,
        )
        valeur = champ_formulaire(champ, "recipe")
    """

    type: TypeChamp = TypeChamp.TEXT
    name: str = "field"
    label: str = ""
    required: bool = False
    default: Any = None
    options: list[str] = field(default_factory=lambda: [])
    min: float | int | None = None
    max: float | int | None = None
    step: float | int = 1

    def __post_init__(self) -> None:
        if not self.label:
            self.label = self.name

    def to_dict(self) -> dict[str, Any]:
        """Convertit en dict (rétrocompatibilité)."""
        result: dict[str, Any] = {
            "type": str(self.type),
            "name": self.name,
            "label": self.label,
            "required": self.required,
        }
        if self.default is not None:
            result["default"] = self.default
        if self.options:
            result["options"] = self.options
        if self.min is not None:
            result["min"] = self.min
        if self.max is not None:
            result["max"] = self.max
        if self.step != 1:
            result["step"] = self.step
        return result


def _normaliser_config(config: dict[str, Any] | ConfigChamp) -> dict[str, Any]:
    """Normalise un ConfigChamp ou un dict en dict."""
    if isinstance(config, ConfigChamp):
        return config.to_dict()
    return config


@composant_ui(
    "forms",
    exemple='champ_formulaire(ConfigChamp(type=TypeChamp.TEXT, name="nom"), "recipe")',
    tags=["form", "input", "field"],
)
def champ_formulaire(config_champ: dict[str, Any] | ConfigChamp, prefixe_cle: str) -> Any:
    """
    Champ de formulaire générique

    Args:
        config_champ: Configuration du champ (dict ou ConfigChamp)
        prefixe_cle: Préfixe pour clé unique

    Returns:
        Valeur du champ

    Example:
        value = champ_formulaire({
            "type": "text",
            "name": "nom",
            "label": "Nom",
            "required": True
        }, "recipe")
    """
    config = _normaliser_config(config_champ)
    field_type = config.get("type", "text")
    name = config.get("name", "field")
    label = config.get("label", name)
    required = config.get("required", False)
    key = f"{prefixe_cle}_{name}"

    if required:
        label = f"{label} *"

    if field_type == "text":
        return st.text_input(label, value=config.get("default", ""), key=key)

    elif field_type == "number":
        return st.number_input(
            label,
            value=float(config.get("default", 0)),
            min_value=config.get("min"),
            max_value=config.get("max"),
            step=config.get("step", 1),
            key=key,
        )

    elif field_type == "select":
        return st.selectbox(label, config.get("options", []), key=key)

    elif field_type == "multiselect":
        return st.multiselect(label, config.get("options", []), key=key)

    elif field_type == "checkbox":
        return st.checkbox(label, value=config.get("default", False), key=key)

    elif field_type == "textarea":
        return st.text_area(label, value=config.get("default", ""), key=key)

    elif field_type == "date":
        return st.date_input(label, value=config.get("default", date.today()), key=key)

    elif field_type == "slider":
        return st.slider(
            label,
            min_value=config.get("min", 0),
            max_value=config.get("max", 100),
            value=config.get("default", 50),
            key=key,
        )

    else:
        return st.text_input(label, key=key)


@composant_ui(
    "forms", exemple='barre_recherche("Rechercher recettes...")', tags=["search", "input"]
)
def barre_recherche(texte_indicatif: str = "Rechercher...", cle: str = "search") -> str:
    """
    Barre de recherche

    Args:
        texte_indicatif: Texte placeholder
        cle: Clé unique

    Returns:
        Terme de recherche

    Example:
        term = barre_recherche("Rechercher recettes...", "recipe_search")
    """
    return st.text_input(
        "", placeholder=f"🔍 {texte_indicatif}", key=cle, label_visibility="collapsed"
    )


@composant_ui(
    "forms",
    exemple='panneau_filtres({"saison": {"type": "select", "label": "Saison"}}, "recipe")',
    tags=["filter", "panel"],
)
def panneau_filtres(config_filtres: dict[str, dict[str, Any]], prefixe_cle: str) -> dict[str, Any]:
    """
    Panneau de filtres

    Args:
        config_filtres: Configuration des filtres
        prefixe_cle: Préfixe clés

    Returns:
        Dict des valeurs filtrées

    Example:
        filters = panneau_filtres({
            "saison": {
                "type": "select",
                "label": "Saison",
                "options": ["Toutes", "été", "hiver"]
            }
        }, "recipe")
    """
    results: dict[str, Any] = {}

    for filter_name, config in config_filtres.items():
        results[filter_name] = champ_formulaire({**config, "name": filter_name}, prefixe_cle)

    return results


@composant_ui(
    "forms",
    exemple='filtres_rapides({"Type": ["Tous", "Entr\u00e9e", "Plat"]})',
    tags=["filter", "buttons"],
)
def filtres_rapides(filtres: dict[str, list[str]], prefixe_cle: str = "filter") -> dict[str, str]:
    """
    Filtres rapides (boutons horizontaux)

    Args:
        filtres: Dict {label: [options]}
        prefixe_cle: Préfixe clés

    Returns:
        Dict des sélections

    Example:
        selected = filtres_rapides({
            "Type": ["Tous", "Entrée", "Plat", "Dessert"]
        })
    """
    results: dict[str, str] = {}

    for label, options in filtres.items():
        cols = st.columns(len(options))

        for idx, option in enumerate(options):
            with cols[idx]:
                if st.button(
                    option, key=f"{prefixe_cle}_{label}_{option}", use_container_width=True
                ):
                    results[label] = option

    return results
