"""
Stack - Conteneurs Flex simplifiés (HStack, VStack).

Abstraction au-dessus de Box pour créer rapidement des layouts
horizontaux et verticaux avec gap uniforme.

Usage:
    from src.ui.primitives import HStack, VStack
    from src.ui.tokens import Espacement

    # Layout horizontal
    with HStack(gap=Espacement.MD, align="center") as row:
        row.child(badge_html)
        row.child(text_html)
        row.child(button_html)

    # Layout vertical
    with VStack(gap=Espacement.LG) as col:
        col.child(header_html)
        col.child(content_html)
        col.child(footer_html)

    # Imbrication
    with VStack(gap="1rem") as page:
        page.child(HStack(gap="0.5rem").child(a).child(b).html())
        page.child(main_content)
"""

from __future__ import annotations

from typing import Literal

import streamlit as st

from src.ui.primitives.box import Box
from src.ui.system.css import StyleSheet
from src.ui.tokens import Espacement


class Stack(Box):
    """Stack de base - Flex container avec direction configurable.

    Hérite de Box et pré-configure display: flex.
    """

    def __init__(
        self,
        direction: Literal["row", "column"] = "row",
        gap: str = Espacement.MD,
        align: Literal["start", "center", "end", "stretch", "baseline"] = "stretch",
        justify: Literal["start", "center", "end", "between", "around", "evenly"] = "start",
        wrap: bool = False,
        tag: str = "div",
        **props,
    ):
        """Crée un Stack.

        Args:
            direction: Direction du flex (row ou column).
            gap: Espacement entre les éléments.
            align: Alignement sur l'axe croisé (align-items).
            justify: Alignement sur l'axe principal (justify-content).
            wrap: Autoriser le wrap des éléments.
            tag: Tag HTML.
            **props: Props additionnelles de Box.
        """
        super().__init__(
            tag=tag,
            display="flex",
            direction=direction,
            gap=gap,
            align=align,
            justify=justify,
            wrap=wrap,
            **props,
        )


class HStack(Stack):
    """Stack horizontal (direction: row).

    Usage:
        with HStack(gap="1rem", align="center") as row:
            row.child(icon)
            row.child(label)
    """

    def __init__(
        self,
        gap: str = Espacement.MD,
        align: Literal["start", "center", "end", "stretch", "baseline"] = "center",
        justify: Literal["start", "center", "end", "between", "around", "evenly"] = "start",
        wrap: bool = False,
        **props,
    ):
        super().__init__(
            direction="row",
            gap=gap,
            align=align,
            justify=justify,
            wrap=wrap,
            **props,
        )


class VStack(Stack):
    """Stack vertical (direction: column).

    Usage:
        with VStack(gap="1.5rem") as col:
            col.child(header)
            col.child(content)
            col.child(footer)
    """

    def __init__(
        self,
        gap: str = Espacement.MD,
        align: Literal["start", "center", "end", "stretch", "baseline"] = "stretch",
        justify: Literal["start", "center", "end", "between", "around", "evenly"] = "start",
        **props,
    ):
        super().__init__(
            direction="column",
            gap=gap,
            align=align,
            justify=justify,
            **props,
        )


# ═══════════════════════════════════════════════════════════
# HELPERS pour création rapide
# ═══════════════════════════════════════════════════════════


def hstack(*children: str, gap: str = Espacement.MD, **props) -> str:
    """Helper fonctionnel pour HStack.

    Args:
        *children: Éléments HTML enfants.
        gap: Espacement.
        **props: Props additionnelles.

    Returns:
        HTML du HStack.

    Example:
        html = hstack(badge1, badge2, badge3, gap="0.5rem")
    """
    stack = HStack(gap=gap, **props)
    for child in children:
        stack.child(child)
    return stack.html()


def vstack(*children: str, gap: str = Espacement.MD, **props) -> str:
    """Helper fonctionnel pour VStack.

    Args:
        *children: Éléments HTML enfants.
        gap: Espacement.
        **props: Props additionnelles.

    Returns:
        HTML du VStack.

    Example:
        html = vstack(header, content, footer, gap="2rem")
    """
    stack = VStack(gap=gap, **props)
    for child in children:
        stack.child(child)
    return stack.html()


__all__ = ["Stack", "HStack", "VStack", "hstack", "vstack"]
