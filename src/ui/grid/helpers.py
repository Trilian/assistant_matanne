"""
Helpers raccourcis pour les layouts courants.

Fonctions utilitaires construites au-dessus de Row, Grid, Stack.
"""

from __future__ import annotations

from typing import Any, Callable

import streamlit as st

from .grid_layout import Grid
from .types import Gap


def two_columns(
    ratio: tuple[int, int] = (1, 1),
    gap: Gap | str = Gap.MD,
) -> tuple[Any, Any]:
    """Shortcut pour 2 colonnes.

    Args:
        ratio: Tuple des poids (ex: (2, 1) pour 2/3 + 1/3)
        gap: Espacement entre colonnes

    Returns:
        Tuple de 2 containers de colonnes

    Usage:
        left, right = two_columns((2, 1))
        with left:
            st.write("Contenu principal")
        with right:
            st.write("Sidebar")
    """
    gap_value = gap if isinstance(gap, str) else gap.value
    cols = st.columns(list(ratio), gap=gap_value)
    return cols[0], cols[1]


def three_columns(
    ratio: tuple[int, int, int] = (1, 1, 1),
    gap: Gap | str = Gap.MD,
) -> tuple[Any, Any, Any]:
    """Shortcut pour 3 colonnes.

    Args:
        ratio: Tuple des poids
        gap: Espacement

    Returns:
        Tuple de 3 containers
    """
    gap_value = gap if isinstance(gap, str) else gap.value
    cols = st.columns(list(ratio), gap=gap_value)
    return cols[0], cols[1], cols[2]


def four_columns(
    ratio: tuple[int, int, int, int] = (1, 1, 1, 1),
    gap: Gap | str = Gap.MD,
) -> tuple[Any, Any, Any, Any]:
    """Shortcut pour 4 colonnes.

    Args:
        ratio: Tuple des poids
        gap: Espacement

    Returns:
        Tuple de 4 containers
    """
    gap_value = gap if isinstance(gap, str) else gap.value
    cols = st.columns(list(ratio), gap=gap_value)
    return cols[0], cols[1], cols[2], cols[3]


def metrics_row(
    metrics: list[tuple[str, Any, str | None]],
    columns: int | None = None,
    gap: Gap | str = Gap.MD,
) -> None:
    """Affiche une row de métriques.

    Args:
        metrics: Liste de tuples (label, value, delta)
        columns: Nombre de colonnes (auto si None)
        gap: Espacement entre métriques

    Usage:
        metrics_row([
            ("Ventes", 1234, "+12%"),
            ("Clients", 567, None),
            ("Revenue", "45k€", "-3%"),
        ])
    """
    n_cols = columns or len(metrics)
    gap_value = gap if isinstance(gap, str) else gap.value
    cols = st.columns(n_cols, gap=gap_value)

    for i, metric_data in enumerate(metrics):
        label, value, delta = metric_data
        with cols[i % n_cols]:
            st.metric(label, value, delta)


def card_grid(
    items: list[Any],
    cols: int = 3,
    card_renderer: Callable[[Any], None] | None = None,
    gap: Gap | str = Gap.MD,
    bordered: bool = True,
) -> None:
    """Affiche une grille de cartes.

    Args:
        items: Liste d'items à afficher
        cols: Nombre de colonnes
        card_renderer: Fonction de rendu pour chaque carte
        gap: Espacement entre cartes
        bordered: Ajouter une bordure aux cartes

    Usage:
        def render_recipe(recipe):
            st.image(recipe.image)
            st.subheader(recipe.name)
            st.caption(f"{recipe.time} min")

        card_grid(recipes, cols=4, card_renderer=render_recipe)
    """

    def default_renderer(item: Any) -> None:
        st.write(item)

    renderer = card_renderer or default_renderer

    with Grid(cols=cols, gap=gap) as g:
        for item in items:
            with g.cell():
                if bordered:
                    with st.container(border=True):
                        renderer(item)
                else:
                    renderer(item)


def sidebar_layout(
    sidebar_width: int = 1,
    main_width: int = 3,
    gap: Gap | str = Gap.LG,
) -> tuple[Any, Any]:
    """Layout avec sidebar à droite.

    Args:
        sidebar_width: Poids de la sidebar
        main_width: Poids du contenu principal
        gap: Espacement

    Returns:
        (main_container, sidebar_container)

    Usage:
        main, sidebar = sidebar_layout()
        with main:
            st.write("Contenu principal")
        with sidebar:
            st.write("Filtres, actions...")
    """
    return two_columns((main_width, sidebar_width), gap)


def centered_content(max_width: int = 800) -> Any:
    """Container centré avec largeur maximale.

    Args:
        max_width: Largeur maximale en pixels

    Returns:
        Container Streamlit centré

    Usage:
        with centered_content(600):
            st.title("Titre centré")
            st.write("Contenu...")
    """
    # Utiliser des colonnes vides pour centrer
    _, center, _ = st.columns([1, 2, 1])
    return center


def action_bar(
    actions: list[tuple[str, str, Callable[[], Any] | None]],
    align: str = "left",
) -> None:
    """Barre d'actions horizontale.

    Args:
        actions: Liste de (label, icon, callback)
        align: Alignement ('left', 'center', 'right')

    Usage:
        action_bar([
            ("Nouveau", "➕", lambda: create_new()),
            ("Filtrer", "🔍", lambda: show_filters()),
            ("Exporter", "📥", lambda: export_data()),
        ])
    """
    cols = st.columns(len(actions))

    for i, (label, icon, callback) in enumerate(actions):
        with cols[i]:
            display = f"{icon} {label}" if icon else label
            if st.button(display, key=f"action_{i}_{label}", use_container_width=True):
                if callback:
                    callback()


__all__ = [
    "two_columns",
    "three_columns",
    "four_columns",
    "metrics_row",
    "card_grid",
    "sidebar_layout",
    "centered_content",
    "action_bar",
]
