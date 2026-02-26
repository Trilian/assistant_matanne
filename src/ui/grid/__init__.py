"""
Système de layouts composables pour Streamlit (PEP 562 lazy imports).

Abstraction au-dessus de st.columns avec API fluent,
support responsive intégré et design tokens.

Usage:
    from src.ui.grid import Row, Grid, Stack, Gap

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

import importlib
from typing import Any

# ═══════════════════════════════════════════════════════════
# Mapping paresseux : nom → (module relatif, attribut)
# ═══════════════════════════════════════════════════════════

_LAZY_IMPORTS: dict[str, tuple[str, str]] = {
    # Types
    "Gap": (".types", "Gap"),
    "VerticalAlign": (".types", "VerticalAlign"),
    "ColumnSpec": (".types", "ColumnSpec"),
    # Row
    "Row": (".row", "Row"),
    # Grid
    "Grid": (".grid_layout", "Grid"),
    # Stack
    "Stack": (".stack", "Stack"),
    # Helpers
    "two_columns": (".helpers", "two_columns"),
    "three_columns": (".helpers", "three_columns"),
    "four_columns": (".helpers", "four_columns"),
    "metrics_row": (".helpers", "metrics_row"),
    "card_grid": (".helpers", "card_grid"),
    "sidebar_layout": (".helpers", "sidebar_layout"),
    "centered_content": (".helpers", "centered_content"),
    "action_bar": (".helpers", "action_bar"),
}


def __getattr__(name: str) -> Any:
    """PEP 562 — import paresseux à la première utilisation."""
    if name in _LAZY_IMPORTS:
        module_path, attr_name = _LAZY_IMPORTS[name]
        module = importlib.import_module(module_path, __package__)
        value = getattr(module, attr_name)
        globals()[name] = value
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = list(_LAZY_IMPORTS.keys())
