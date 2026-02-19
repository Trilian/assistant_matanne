"""
Widgets UI optimisés pour interfaces tactiles.

Fournit des composants avec:
- Zones tactiles agrandies
- Gestion des gestes
- Feedback visuel adapté au touch
"""

from collections.abc import Callable
from typing import Any

import streamlit as st


def bouton_tablette(
    label: str,
    key: str | None = None,
    icon: str = "",
    type_bouton: str = "secondary",
    on_click: Callable | None = None,
    **kwargs,
) -> bool:
    """
    Bouton optimisé pour tablette.

    Args:
        label: Texte du bouton
        key: Clé unique
        icon: Emoji/icône à afficher
        type_bouton: "primary", "secondary", "danger"
        on_click: Callback au clic

    Returns:
        True si cliqué
    """
    # Rétrocompatibilité: accepter l'ancien paramètre 'type'
    if "type" in kwargs:
        type_bouton = kwargs.pop("type")
    full_label = f"{icon} {label}" if icon else label

    # Styles selon le type
    if type_bouton == "primary":
        kwargs["type"] = "primary"
    elif type_bouton == "danger":
        kwargs["help"] = "⚠️ Action irréversible"

    return st.button(full_label, key=key, on_click=on_click, **kwargs)


def grille_selection_tablette(
    options: list[dict[str, Any]],
    key: str,
    columns: int = 3,
) -> str | None:
    """
    Grille de sélection tactile.

    Args:
        options: Liste de {"value": str, "label": str, "icon": str}
        key: Clé unique
        columns: Nombre de colonnes

    Returns:
        Valeur sélectionnée ou None
    """
    selected = st.session_state.get(f"{key}_selected")

    cols = st.columns(columns)

    for i, opt in enumerate(options):
        with cols[i % columns]:
            is_selected = selected == opt.get("value")

            btn_label = f"{opt.get('icon', '')} {opt.get('label', opt.get('value', ''))}"

            if st.button(
                btn_label,
                key=f"{key}_{i}",
                use_container_width=True,
                type="primary" if is_selected else "secondary",
            ):
                st.session_state[f"{key}_selected"] = opt.get("value")
                st.rerun()

    return selected


def saisie_nombre_tablette(
    label: str,
    key: str,
    min_value: int = 0,
    max_value: int = 100,
    default: int = 1,
    step: int = 1,
) -> int:
    """
    Input numérique avec boutons +/- tactiles.

    Args:
        label: Label du champ
        key: Clé unique
        min_value: Valeur minimale
        max_value: Valeur maximale
        default: Valeur par défaut
        step: Incrément

    Returns:
        Valeur actuelle
    """
    if f"{key}_value" not in st.session_state:
        st.session_state[f"{key}_value"] = default

    current = st.session_state[f"{key}_value"]

    st.write(f"**{label}**")

    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if st.button("➖", key=f"{key}_minus", use_container_width=True):
            new_val = max(min_value, current - step)
            st.session_state[f"{key}_value"] = new_val
            st.rerun()

    with col2:
        st.markdown(
            f"<div style='text-align: center; font-size: 2rem; font-weight: bold;'>{current}</div>",
            unsafe_allow_html=True,
        )

    with col3:
        if st.button("➕", key=f"{key}_plus", use_container_width=True):
            new_val = min(max_value, current + step)
            st.session_state[f"{key}_value"] = new_val
            st.rerun()

    return current


def liste_cases_tablette(
    items: list[str],
    key: str,
    on_check: Callable[[str, bool], None] | None = None,
) -> dict[str, bool]:
    """
    Liste de cases à cocher tactile.

    Args:
        items: Liste des éléments
        key: Clé unique
        on_check: Callback (item, checked)

    Returns:
        Dict {item: checked}
    """
    if f"{key}_checked" not in st.session_state:
        st.session_state[f"{key}_checked"] = dict.fromkeys(items, False)

    checked = st.session_state[f"{key}_checked"]

    for item in items:
        is_checked = checked.get(item, False)
        icon = "✅" if is_checked else "⬜"

        if st.button(
            f"{icon} {item}",
            key=f"{key}_{item}",
            use_container_width=True,
        ):
            new_state = not is_checked
            st.session_state[f"{key}_checked"][item] = new_state

            if on_check:
                on_check(item, new_state)

            st.rerun()

    return checked
