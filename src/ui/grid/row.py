"""
Row layout — colonnes flexibles au-dessus de st.columns.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Generator, Sequence

import streamlit as st

from .types import Gap, VerticalAlign


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


__all__ = ["Row"]
