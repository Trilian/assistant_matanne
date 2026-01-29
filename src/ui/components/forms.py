"""
UI Components - Forms
Champs formulaire, recherche, filtres
"""

from datetime import date
from typing import Any

import streamlit as st


def form_field(field_config: dict, key_prefix: str) -> Any:
    """
    Champ de formulaire générique

    Args:
        field_config: Configuration du champ
        key_prefix: Préfixe pour clé unique

    Returns:
        Valeur du champ

    Example:
        value = form_field({
            "type": "text",
            "name": "nom",
            "label": "Nom",
            "required": True
        }, "recipe")
    """
    field_type = field_config.get("type", "text")
    name = field_config.get("name", "field")
    label = field_config.get("label", name)
    required = field_config.get("required", False)
    key = f"{key_prefix}_{name}"

    if required:
        label = f"{label} *"

    if field_type == "text":
        return st.text_input(label, value=field_config.get("default", ""), key=key)

    elif field_type == "number":
        return st.number_input(
            label,
            value=float(field_config.get("default", 0)),
            min_value=field_config.get("min"),
            max_value=field_config.get("max"),
            step=field_config.get("step", 1),
            key=key,
        )

    elif field_type == "select":
        return st.selectbox(label, field_config.get("options", []), key=key)

    elif field_type == "multiselect":
        return st.multiselect(label, field_config.get("options", []), key=key)

    elif field_type == "checkbox":
        return st.checkbox(label, value=field_config.get("default", False), key=key)

    elif field_type == "textarea":
        return st.text_area(label, value=field_config.get("default", ""), key=key)

    elif field_type == "date":
        return st.date_input(label, value=field_config.get("default", date.today()), key=key)

    elif field_type == "slider":
        return st.slider(
            label,
            min_value=field_config.get("min", 0),
            max_value=field_config.get("max", 100),
            value=field_config.get("default", 50),
            key=key,
        )

    else:
        return st.text_input(label, key=key)


def search_bar(placeholder: str = "Rechercher...", key: str = "search") -> str:
    """
    Barre de recherche

    Args:
        placeholder: Texte placeholder
        key: Clé unique

    Returns:
        Terme de recherche

    Example:
        term = search_bar("Rechercher recettes...", "recipe_search")
    """
    return st.text_input("", placeholder=f"🔍 {placeholder}", key=key, label_visibility="collapsed")


def filter_panel(filters_config: dict[str, dict], key_prefix: str) -> dict:
    """
    Panneau de filtres

    Args:
        filters_config: Configuration des filtres
        key_prefix: Préfixe clés

    Returns:
        Dict des valeurs filtrées

    Example:
        filters = filter_panel({
            "saison": {
                "type": "select",
                "label": "Saison",
                "options": ["Toutes", "été", "hiver"]
            }
        }, "recipe")
    """
    results = {}

    for filter_name, config in filters_config.items():
        results[filter_name] = form_field({**config, "name": filter_name}, key_prefix)

    return results


def quick_filters(filters: dict[str, list], key_prefix: str = "filter") -> dict[str, str]:
    """
    Filtres rapides (boutons horizontaux)

    Args:
        filters: Dict {label: [options]}
        key_prefix: Préfixe clés

    Returns:
        Dict des sélections

    Example:
        selected = quick_filters({
            "Type": ["Tous", "Entrée", "Plat", "Dessert"]
        })
    """
    results = {}

    for label, options in filters.items():
        cols = st.columns(len(options))

        for idx, option in enumerate(options):
            with cols[idx]:
                if st.button(
                    option, key=f"{key_prefix}_{label}_{option}", use_container_width=True
                ):
                    results[label] = option

    return results
