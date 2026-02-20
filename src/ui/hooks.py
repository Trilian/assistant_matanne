"""
Hooks Streamlit — Logique d'état réutilisable découplée de l'UI.

Pattern inspiré des React Hooks : chaque ``use_*`` encapsule un
comportement stateful (pagination, recherche, filtres, confirmation,
timer) et retourne un tuple ``(données, render_callable)``.

Le contrat est simple :
    données = résultat de la logique (items filtrés, page courante, etc.)
    render = fonction sans argument qui affiche les contrôles UI

Cela permet de séparer proprement QUAND on récupère les données
et OÙ on affiche les contrôles.

Usage:
    from src.ui.hooks import use_pagination, use_recherche

    # Dans un module :
    visible, show_pagination = use_pagination(all_recipes, per_page=20)
    filtered, show_search = use_recherche(visible, champs=["nom", "categorie"])

    show_search()                  # Affiche la barre de recherche en haut
    for r in filtered:
        display_recipe(r)
    show_pagination()              # Affiche la pagination en bas
"""

from __future__ import annotations

from typing import Any, Callable, Sequence

import streamlit as st


def use_pagination(
    items: Sequence[Any],
    per_page: int = 20,
    cle: str = "pg",
) -> tuple[list[Any], Callable[[], None]]:
    """Hook de pagination.

    Découpe une liste en pages et fournit les contrôles de navigation.

    Args:
        items: Liste complète d'items.
        per_page: Nombre d'items par page.
        cle: Préfixe de clé unique pour ``session_state``.

    Returns:
        Tuple (items_page_courante, render_controls).

    Example:
        visible, show_pg = use_pagination(recipes, per_page=10)
        for r in visible:
            st.write(r)
        show_pg()
    """
    total = len(items)
    if total <= per_page:
        return list(items), lambda: None

    total_pages = (total + per_page - 1) // per_page
    state_key = f"_hook_{cle}_page"

    if state_key not in st.session_state:
        st.session_state[state_key] = 1

    page = st.session_state[state_key]
    page = max(1, min(page, total_pages))
    st.session_state[state_key] = page

    start = (page - 1) * per_page
    page_items = list(items[start : start + per_page])

    def render() -> None:
        col1, col2, col3, col4 = st.columns([1, 1, 2, 1])

        with col1:
            if st.button("⬅️ Préc", key=f"{cle}_prev", disabled=page <= 1, use_container_width=True):
                st.session_state[state_key] = page - 1
                st.rerun()

        with col2:
            if st.button(
                "Suiv ➡️", key=f"{cle}_next", disabled=page >= total_pages, use_container_width=True
            ):
                st.session_state[state_key] = page + 1
                st.rerun()

        with col3:
            st.caption(f"Page {page}/{total_pages} — {total} élément(s)")

        with col4:
            new_page = st.number_input(
                "Aller à",
                min_value=1,
                max_value=total_pages,
                value=page,
                key=f"{cle}_goto",
                label_visibility="collapsed",
            )
            if new_page != page:
                st.session_state[state_key] = new_page
                st.rerun()

    return page_items, render


def use_recherche(
    items: Sequence[dict[str, Any]],
    champs: list[str],
    cle: str = "search",
    placeholder: str = "Rechercher...",
) -> tuple[list[dict[str, Any]], Callable[[], None]]:
    """Hook de recherche textuelle sur une liste de dicts.

    Filtre les items dont au moins un champ contient le terme (insensible à la casse).

    Args:
        items: Liste de dicts à filtrer.
        champs: Noms des clés à chercher.
        cle: Clé unique pour ``session_state``.
        placeholder: Texte indicatif de la barre de recherche.

    Returns:
        Tuple (items_filtrés, render_search_bar).

    Example:
        filtered, show_search = use_recherche(recipes, ["nom", "categorie"])
        show_search()
        for r in filtered:
            st.write(r["nom"])
    """
    state_key = f"_hook_{cle}_term"

    term = st.session_state.get(state_key, "").strip().lower()

    if term:
        filtered = [
            item for item in items if any(term in str(item.get(c, "")).lower() for c in champs)
        ]
    else:
        filtered = list(items)

    def render() -> None:
        st.text_input(
            "",
            placeholder=f"🔍 {placeholder}",
            key=state_key,
            label_visibility="collapsed",
        )

    return filtered, render


def use_filtres(
    options: dict[str, list[str]],
    cle: str = "filters",
) -> tuple[dict[str, str], Callable[[], None]]:
    """Hook de filtres multi-critères.

    Chaque filtre est un selectbox. Le premier élément est considéré
    comme « Tous » (pas de filtrage).

    Args:
        options: Dict ``{label: [option1, option2, ...]}``.
        cle: Clé unique.

    Returns:
        Tuple (filtres_sélectionnés, render_filter_panel).
        Les filtres dont la valeur est le premier élément (« Tous ») sont exclus du dict.

    Example:
        filters, show_filters = use_filtres({
            "Catégorie": ["Toutes", "Entrée", "Plat", "Dessert"],
            "Difficulté": ["Toutes", "Facile", "Moyen", "Difficile"],
        })
        show_filters()
        # filters = {"Catégorie": "Plat"} si l'utilisateur a choisi "Plat"
    """
    active: dict[str, str] = {}

    for label, opts in options.items():
        sk = f"_hook_{cle}_{label}"
        val = st.session_state.get(sk, opts[0] if opts else "")
        if val and opts and val != opts[0]:
            active[label] = val

    def render() -> None:
        cols = st.columns(len(options))
        for idx, (label, opts) in enumerate(options.items()):
            with cols[idx]:
                st.selectbox(
                    label,
                    opts,
                    key=f"_hook_{cle}_{label}",
                )

    return active, render


def use_confirmation(
    message: str = "Êtes-vous sûr ?",
    label_confirmer: str = "✅ Confirmer",
    label_annuler: str = "❌ Annuler",
    cle: str = "confirm",
) -> tuple[bool | None, Callable[[], None]]:
    """Hook de confirmation modale.

    Retourne ``True`` si confirmé, ``False`` si annulé, ``None`` si
    pas encore interagi.

    Args:
        message: Message de confirmation.
        label_confirmer: Texte du bouton confirmer.
        label_annuler: Texte du bouton annuler.
        cle: Clé unique.

    Returns:
        Tuple (résultat, render_dialog).

    Example:
        confirmed, show_dialog = use_confirmation("Supprimer cette recette ?")
        show_dialog()
        if confirmed:
            delete_recipe()
    """
    state_key = f"_hook_{cle}_result"
    result = st.session_state.get(state_key)

    def render() -> None:
        st.warning(message)
        col1, col2 = st.columns(2)
        with col1:
            if st.button(
                label_confirmer, key=f"{cle}_yes", use_container_width=True, type="primary"
            ):
                st.session_state[state_key] = True
                st.rerun()
        with col2:
            if st.button(label_annuler, key=f"{cle}_no", use_container_width=True):
                st.session_state[state_key] = False
                st.rerun()

    return result, render


def use_tri(
    items: Sequence[dict[str, Any]],
    champs_tri: dict[str, str],
    cle: str = "sort",
) -> tuple[list[dict[str, Any]], Callable[[], None]]:
    """Hook de tri sur une liste de dicts.

    Args:
        items: Liste de dicts à trier.
        champs_tri: Dict ``{label_affiché: clé_dict}`` pour les options de tri.
        cle: Clé unique.

    Returns:
        Tuple (items_triés, render_sort_controls).

    Example:
        sorted_items, show_sort = use_tri(
            recipes,
            {"Nom": "nom", "Date": "date_creation", "Durée": "duree"},
        )
        show_sort()
    """
    state_field_key = f"_hook_{cle}_field"
    state_order_key = f"_hook_{cle}_asc"

    labels = list(champs_tri.keys())
    selected_label = st.session_state.get(state_field_key, labels[0] if labels else "")
    ascending = st.session_state.get(state_order_key, True)

    field_key = champs_tri.get(selected_label, "")

    if field_key:
        sorted_items = sorted(
            items,
            key=lambda x: (x.get(field_key) is None, x.get(field_key, "")),
            reverse=not ascending,
        )
    else:
        sorted_items = list(items)

    def render() -> None:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.selectbox("Trier par", labels, key=state_field_key)
        with col2:
            st.checkbox("↑ Croissant", value=True, key=state_order_key)

    return sorted_items, render


def use_onglets(
    onglets: list[str],
    cle: str = "tabs",
) -> tuple[str, Callable[[], None]]:
    """Hook d'onglets avec persistance de l'onglet sélectionné.

    Args:
        onglets: Liste des labels d'onglets.
        cle: Clé unique.

    Returns:
        Tuple (onglet_actif, render_tabs).

    Example:
        tab, show_tabs = use_onglets(["Recettes", "Planning", "Courses"])
        show_tabs()
        if tab == "Recettes":
            show_recipes()
    """
    state_key = f"_hook_{cle}_active"

    if state_key not in st.session_state:
        st.session_state[state_key] = onglets[0] if onglets else ""

    active = st.session_state[state_key]
    if active not in onglets:
        active = onglets[0] if onglets else ""
        st.session_state[state_key] = active

    def render() -> None:
        cols = st.columns(len(onglets))
        for idx, label in enumerate(onglets):
            with cols[idx]:
                btn_type = "primary" if label == active else "secondary"
                if st.button(
                    label, key=f"{cle}_tab_{idx}", type=btn_type, use_container_width=True
                ):
                    st.session_state[state_key] = label
                    st.rerun()

    return active, render


__all__ = [
    "use_pagination",
    "use_recherche",
    "use_filtres",
    "use_confirmation",
    "use_tri",
    "use_onglets",
]
