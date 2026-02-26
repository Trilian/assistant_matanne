"""
Grid layout — grille responsive N colonnes.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Generator

import streamlit as st

from .types import Gap


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


__all__ = ["Grid"]
