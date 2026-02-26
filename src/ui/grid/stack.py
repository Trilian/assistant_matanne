"""
Stack layout — empilement vertical avec espacement uniforme.
"""

from __future__ import annotations

from typing import Any

import streamlit as st

from .types import Gap


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


__all__ = ["Stack"]
