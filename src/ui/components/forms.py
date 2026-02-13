"""
UI Components - Forms
Champs formulaire, recherche, filtres
"""

from datetime import date
from typing import Any

import streamlit as st


def champ_formulaire(config_champ: dict, prefixe_cle: str) -> Any:
    """
    Champ de formulaire générique

    Args:
        config_champ: Configuration du champ
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
    field_type = config_champ.get("type", "text")
    name = config_champ.get("name", "field")
    label = config_champ.get("label", name)
    required = config_champ.get("required", False)
    key = f"{prefixe_cle}_{name}"

    if required:
        label = f"{label} *"

    if field_type == "text":
        return st.text_input(label, value=config_champ.get("default", ""), key=key)

    elif field_type == "number":
        return st.number_input(
            label,
            value=float(config_champ.get("default", 0)),
            min_value=config_champ.get("min"),
            max_value=config_champ.get("max"),
            step=config_champ.get("step", 1),
            key=key,
        )

    elif field_type == "select":
        return st.selectbox(label, config_champ.get("options", []), key=key)

    elif field_type == "multiselect":
        return st.multiselect(label, config_champ.get("options", []), key=key)

    elif field_type == "checkbox":
        return st.checkbox(label, value=config_champ.get("default", False), key=key)

    elif field_type == "textarea":
        return st.text_area(label, value=config_champ.get("default", ""), key=key)

    elif field_type == "date":
        return st.date_input(label, value=config_champ.get("default", date.today()), key=key)

    elif field_type == "slider":
        return st.slider(
            label,
            min_value=config_champ.get("min", 0),
            max_value=config_champ.get("max", 100),
            value=config_champ.get("default", 50),
            key=key,
        )

    else:
        return st.text_input(label, key=key)


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


def panneau_filtres(config_filtres: dict[str, dict], prefixe_cle: str) -> dict:
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
    results = {}

    for filter_name, config in config_filtres.items():
        results[filter_name] = champ_formulaire({**config, "name": filter_name}, prefixe_cle)

    return results


def filtres_rapides(filtres: dict[str, list], prefixe_cle: str = "filter") -> dict[str, str]:
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
    results = {}

    for label, options in filtres.items():
        cols = st.columns(len(options))

        for idx, option in enumerate(options):
            with cols[idx]:
                if st.button(
                    option, key=f"{prefixe_cle}_{label}_{option}", use_container_width=True
                ):
                    results[label] = option

    return results
