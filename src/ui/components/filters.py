"""
Composants de filtrage réutilisables.

Élimine la duplication des barres de filtres dans les modules.

Usage:
    from src.ui.components.filters import FilterConfig, afficher_barre_filtres

    filtres = afficher_barre_filtres([
        FilterConfig("categorie", "Catégorie", ["Fruits", "Légumes"]),
        FilterConfig("statut", "Statut", ["ok", "critique"], multiselect=True),
    ])

    data_filtree = appliquer_filtres(data, filtres)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

import streamlit as st

from src.ui.registry import composant_ui


@dataclass
class FilterConfig:
    """Configuration d'un filtre.

    Attributes:
        key: Clé unique du filtre
        label: Label affiché
        options: Liste d'options ou callable qui les retourne
        default: Valeur par défaut
        multiselect: Si True, permet la sélection multiple
        help_text: Texte d'aide optionnel
        icons: Dict optionnel {option: emoji} pour afficher des icônes
    """

    key: str
    label: str
    options: list | Callable[[], list]
    default: Any = None
    multiselect: bool = False
    help_text: str = ""
    icons: dict[str, str] = field(default_factory=dict)
    include_all_option: bool = True
    all_label: str = "Tous"


@composant_ui(
    "filters",
    exemple='afficher_barre_filtres([FilterConfig("cat", "Catégorie", ["A", "B"])])',
    tags=("filtre", "recherche"),
)
def afficher_barre_filtres(
    configs: list[FilterConfig],
    prefix: str = "",
    on_change: Callable[[dict], None] | None = None,
    columns: int | None = None,
) -> dict[str, Any]:
    """Barre de filtres générique et réutilisable.

    Args:
        configs: Liste des configurations de filtres
        prefix: Préfixe pour les clés (évite les collisions)
        on_change: Callback appelé quand un filtre change
        columns: Nombre de colonnes (auto si None)

    Returns:
        Dictionnaire des valeurs de filtres {key: value}

    Usage:
        filtres = afficher_barre_filtres([
            FilterConfig("categorie", "🏷️ Catégorie", ["Fruits", "Légumes"]),
            FilterConfig("statut", "⚠️ Statut", ["ok", "critique"], multiselect=True),
        ])
    """
    if not configs:
        return {}

    num_cols = columns or len(configs)
    cols = st.columns(num_cols)
    result: dict[str, Any] = {}

    for i, conf in enumerate(configs):
        with cols[i % num_cols]:
            # Résoudre les options
            options = conf.options() if callable(conf.options) else conf.options

            # Ajouter les icônes si définies
            if conf.icons:
                display_options = [f"{conf.icons.get(opt, '')} {opt}".strip() for opt in options]
            else:
                display_options = options

            key = f"{prefix}filter_{conf.key}" if prefix else f"filter_{conf.key}"

            if conf.multiselect:
                selected = st.multiselect(
                    conf.label,
                    display_options,
                    default=conf.default or [],
                    key=key,
                    help=conf.help_text or None,
                )
                # Retirer les icônes pour obtenir les valeurs brutes
                if conf.icons:
                    value = [opt.split(" ", 1)[-1] if " " in opt else opt for opt in selected]
                else:
                    value = selected
            else:
                all_options = (
                    [conf.all_label] + list(display_options)
                    if conf.include_all_option
                    else display_options
                )
                selected = st.selectbox(
                    conf.label,
                    all_options,
                    key=key,
                    help=conf.help_text or None,
                )
                if selected == conf.all_label:
                    value = None
                elif conf.icons and " " in selected:
                    value = selected.split(" ", 1)[-1]
                else:
                    value = selected

            result[conf.key] = value

    if on_change:
        on_change(result)

    return result


@composant_ui("filters", exemple='afficher_recherche("Rechercher...")', tags=("recherche",))
def afficher_recherche(
    placeholder: str = "Rechercher...",
    key: str = "search",
    label: str = "🔍 Recherche",
    show_label: bool = False,
) -> str:
    """Champ de recherche avec icône.

    Args:
        placeholder: Texte placeholder
        key: Clé unique
        label: Label du champ
        show_label: Si True, affiche le label

    Returns:
        Texte de recherche
    """
    return st.text_input(
        label,
        placeholder=placeholder,
        key=key,
        label_visibility="visible" if show_label else "collapsed",
    )


@composant_ui(
    "filters",
    exemple='afficher_filtres_rapides("statut", {"Tous": None, "Actif": True})',
    tags=("filtre", "bouton"),
)
def afficher_filtres_rapides(
    options: list[str],
    key: str = "quick_filter",
    default: str | None = None,
    icons: dict[str, str] | None = None,
) -> str | None:
    """Filtres rapides sous forme de boutons radio horizontaux.

    Args:
        options: Liste des options
        key: Clé unique
        default: Option par défaut
        icons: Dict optionnel {option: emoji}

    Returns:
        Option sélectionnée
    """
    display_options = ["Tous"] + [
        f"{icons.get(opt, '')} {opt}".strip() if icons else opt for opt in options
    ]

    selected = st.radio(
        "Filtre rapide",
        display_options,
        horizontal=True,
        key=key,
        label_visibility="collapsed",
    )

    if selected == "Tous":
        return None

    if icons:
        # Retirer l'icône
        for opt in options:
            if opt in selected:
                return opt

    return selected


@composant_ui("filters", exemple='appliquer_filtres(data, {"categorie": "Fruits"})', tags=("filter", "data", "pure"))
def appliquer_filtres(
    data: list[dict],
    filtres: dict[str, Any],
    mappings: dict[str, str] | None = None,
) -> list[dict]:
    """Applique des filtres à une liste de dictionnaires.

    Args:
        data: Données à filtrer
        filtres: Dictionnaire {clé: valeur} des filtres actifs
        mappings: Correspondance {clé_filtre: clé_data} si différent

    Returns:
        Liste filtrée

    Usage:
        data_filtree = appliquer_filtres(
            articles,
            {"categorie": "Fruits", "statut": ["ok", "stock_bas"]},
            mappings={"categorie": "ingredient_categorie"}
        )
    """
    if not filtres or not data:
        return data

    mappings = mappings or {}
    result = data

    for key, value in filtres.items():
        if value is None or value == [] or value == "":
            continue

        data_key = mappings.get(key, key)

        if isinstance(value, list):
            result = [d for d in result if d.get(data_key) in value]
        else:
            result = [d for d in result if d.get(data_key) == value]

    return result


@composant_ui("filters", exemple='appliquer_recherche(data, "tomate", ["nom"])', tags=("search", "filter", "pure"))
def appliquer_recherche(
    data: list[dict],
    terme: str,
    champs: list[str],
) -> list[dict]:
    """Applique une recherche textuelle sur plusieurs champs.

    Args:
        data: Données à filtrer
        terme: Terme de recherche
        champs: Liste des champs à rechercher

    Returns:
        Liste filtrée

    Usage:
        resultats = appliquer_recherche(
            articles,
            "tomate",
            champs=["nom", "description", "categorie"]
        )
    """
    if not terme or not data:
        return data

    terme_lower = terme.lower()

    def match(item: dict) -> bool:
        for champ in champs:
            value = item.get(champ)
            if value and terme_lower in str(value).lower():
                return True
        return False

    return [d for d in data if match(d)]


__all__ = [
    "FilterConfig",
    "afficher_barre_filtres",
    "afficher_recherche",
    "afficher_filtres_rapides",
    "appliquer_filtres",
    "appliquer_recherche",
]
