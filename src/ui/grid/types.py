"""
Types de base pour le système de layout grid.

Enums, dataclasses et constantes partagées.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


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


__all__ = [
    "Gap",
    "VerticalAlign",
    "ColumnSpec",
]
