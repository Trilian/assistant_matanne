"""
Système de layouts composables pour Streamlit.

Abstraction au-dessus de st.columns avec API fluent,
support responsive intégré et design tokens.

Usage:
    from src.ui.layouts import Row, Grid, Stack, Gap

    # Row simple (2 colonnes égales)
    with Row(2) as r:
        with r.col(0):
            st.metric("Ventes", 1234)
        with r.col(1):
            st.metric("Clients", 567)

    # Row pondérée (sidebar)
    with Row([3, 1], gap=Gap.LG) as r:
        with r.col(0):
            st.write("Contenu principal")
        with r.col(1):
            st.write("Sidebar")

    # Grid responsive
    with Grid(cols=3, gap=Gap.MD) as g:
        for item in items:
            with g.cell():
                render_card(item)

    # Stack vertical
    with Stack(gap=Gap.LG):
        st.header("Titre")
        st.write("Contenu")
        st.button("Action")

    # Helpers rapides
    left, right = two_columns((2, 1))
    metrics_row([("Ventes", 1234, "+5%"), ("Clients", 89, None)])
"""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Callable, Generator, Sequence

import streamlit as st


class Gap(StrEnum):
    """Espacements standardisés (mapping vers design tokens).

    Utiliser ces constantes pour un espacement cohérent.
    """

    NONE = "0"
    XS = "small"  # Streamlit gap values
    SM = "small"
    MD = "medium"
    LG = "large"
    XL = "large"


class VerticalAlign(StrEnum):
    """Alignement vertical des colonnes."""

    TOP = "top"
    CENTER = "center"
    BOTTOM = "bottom"


@dataclass
class ColumnSpec:
    """Spécification d'une colonne."""

    weight: float = 1.0
    gap: Gap = Gap.MD


class Row:
    """Row layout avec colonnes flexibles.

    Wrapper ergonomique autour de st.columns avec:
    - API context manager intuitive
    - Accès par index aux colonnes
    - Support des ratios personnalisés
    - Alignement vertical configurable

    Usage:
        # Colonnes égales
        with Row(3) as r:
            with r.col(0): st.write("A")
            with r.col(1): st.write("B")
            with r.col(2): st.write("C")

        # Colonnes pondérées
        with Row([2, 1, 1]) as r:
            with r.col(0): st.write("Large")
            with r.col(1): st.write("Small")
            with r.col(2): st.write("Small")

        # Avec options
        with Row(2, gap=Gap.LG, vertical_align=VerticalAlign.CENTER) as r:
            ...
    """

    def __init__(
        self,
        columns: int | Sequence[float],
        gap: Gap | str = Gap.MD,
        vertical_align: VerticalAlign | str = VerticalAlign.TOP,
    ):
        """
        Args:
            columns: Nombre de colonnes (int) ou liste de poids (ex: [2, 1, 1])
            gap: Espacement entre colonnes
            vertical_align: Alignement vertical ('top', 'center', 'bottom')
        """
        if isinstance(columns, int):
            self._weights = [1.0] * columns
        else:
            self._weights = list(columns)

        self._gap = gap if isinstance(gap, str) else gap.value
        self._vertical_align = (
            vertical_align if isinstance(vertical_align, str) else vertical_align.value
        )
        self._columns: list[Any] = []
        self._entered = False

    def __enter__(self) -> Row:
        self._columns = st.columns(
            self._weights,
            gap=self._gap,
            vertical_alignment=self._vertical_align,
        )
        self._entered = True
        return self

    def __exit__(self, *args: Any) -> None:
        self._entered = False

    @contextmanager
    def col(self, index: int) -> Generator[Any, None, None]:
        """Accède à une colonne par index.

        Args:
            index: Index de la colonne (0-based)

        Raises:
            RuntimeError: Si appelé hors du context manager
            IndexError: Si index hors limites
        """
        if not self._entered:
            raise RuntimeError("Row doit être utilisé comme context manager")
        if index >= len(self._columns):
            raise IndexError(f"Index {index} hors limites (max: {len(self._columns) - 1})")
        with self._columns[index]:
            yield

    @property
    def count(self) -> int:
        """Nombre de colonnes."""
        return len(self._weights)


class Grid:
    """Grid layout responsive.

    Crée une grille avec N colonnes où chaque cellule
    peut contenir du contenu Streamlit. Les lignes sont
    créées automatiquement selon le nombre de cellules.

    Usage:
        with Grid(cols=4, gap=Gap.MD) as g:
            for item in items[:12]:
                with g.cell():
                    st.image(item.image)
                    st.caption(item.name)

        # Grid avec callbacks
        with Grid(cols=3) as g:
            for recipe in recipes:
                with g.cell():
                    if st.button(recipe.name, key=f"btn_{recipe.id}"):
                        show_recipe(recipe)
    """

    def __init__(
        self,
        cols: int = 3,
        gap: Gap | str = Gap.MD,
    ):
        """
        Args:
            cols: Nombre de colonnes par ligne
            gap: Espacement entre cellules
        """
        self._cols = cols
        self._gap = gap if isinstance(gap, str) else gap.value
        self._current_row: list[Any] | None = None
        self._cell_index = 0

    def __enter__(self) -> Grid:
        self._cell_index = 0
        return self

    def __exit__(self, *args: Any) -> None:
        pass

    @contextmanager
    def cell(self) -> Generator[Any, None, None]:
        """Crée une cellule dans la grille.

        Les lignes sont gérées automatiquement - une nouvelle
        ligne est créée quand la précédente est pleine.
        """
        # Nouvelle row si nécessaire
        if self._cell_index % self._cols == 0:
            self._current_row = st.columns(self._cols, gap=self._gap)

        col_index = self._cell_index % self._cols
        self._cell_index += 1

        if self._current_row:
            with self._current_row[col_index]:
                yield

    @property
    def current_row(self) -> int:
        """Numéro de la ligne courante (0-based)."""
        return self._cell_index // self._cols

    @property
    def current_col(self) -> int:
        """Numéro de la colonne courante (0-based)."""
        return self._cell_index % self._cols


class Stack:
    """Stack vertical avec espacement uniforme.

    Simplifie la création de layouts verticaux avec
    espacement cohérent entre les éléments.

    Usage:
        with Stack(gap=Gap.LG):
            st.title("Mon Dashboard")
            st.markdown("Description...")
            with Row(2) as r:
                ...

        # Avec dividers
        with Stack(gap=Gap.MD, dividers=True):
            section_1()
            section_2()
            section_3()
    """

    def __init__(
        self,
        gap: Gap | str = Gap.MD,
        dividers: bool = False,
    ):
        """
        Args:
            gap: Espacement entre éléments
            dividers: Ajouter des séparateurs entre sections
        """
        self._gap = gap if isinstance(gap, str) else gap.value
        self._dividers = dividers
        self._item_count = 0

    def __enter__(self) -> Stack:
        self._item_count = 0
        return self

    def __exit__(self, *args: Any) -> None:
        pass

    def item(self) -> None:
        """Marque un nouvel élément dans le stack.

        Ajoute l'espacement/divider approprié avant l'élément.
        """
        if self._item_count > 0:
            if self._dividers:
                st.divider()
            else:
                # Espacement via container vide
                st.markdown(
                    f"<div style='height: {self._gap_pixels}'></div>", unsafe_allow_html=True
                )
        self._item_count += 1

    @property
    def _gap_pixels(self) -> str:
        """Convertit le gap en pixels."""
        mapping = {
            "small": "0.5rem",
            "medium": "1rem",
            "large": "1.5rem",
        }
        return mapping.get(self._gap, "1rem")


# ═══════════════════════════════════════════════════════════
# HELPERS RACCOURCIS
# ═══════════════════════════════════════════════════════════


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
