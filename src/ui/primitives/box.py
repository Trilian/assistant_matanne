"""
Box - Primitive de conteneur universel.

Box est le bloc de construction fondamental pour composer des layouts.
Il fournit une API props-based pour les styles CSS les plus courants.

Usage:
    from src.ui.primitives import Box
    from src.ui.tokens import Couleur, Espacement, Rayon

    # Style inline
    box = Box(
        display="flex",
        p=Espacement.LG,
        bg=Couleur.BG_SURFACE,
        radius=Rayon.LG,
        shadow="0 2px 4px rgba(0,0,0,0.1)",
    )
    box.child("<span>Contenu</span>")
    box.show()

    # Context manager
    with Box(p="1rem", bg="#f8f9fa") as container:
        container.child("<p>Premier paragraphe</p>")
        container.child("<p>Second paragraphe</p>")
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

import streamlit as st

from src.ui.system.css import StyleSheet
from src.ui.tokens import Espacement, Rayon
from src.ui.utils import echapper_html


@dataclass
class BoxProps:
    """Props du composant Box.

    Toutes les propriétés sont optionnelles et converties en CSS.
    """

    # ── Layout ────────────────────────────────────────────
    display: Literal["block", "flex", "grid", "inline", "inline-flex", "inline-block"] = "block"
    direction: Literal["row", "column", "row-reverse", "column-reverse"] = "row"
    align: Literal["start", "center", "end", "stretch", "baseline"] = "stretch"
    justify: Literal["start", "center", "end", "between", "around", "evenly"] = "start"
    gap: str | None = None
    wrap: bool = False

    # ── Dimensions ────────────────────────────────────────
    w: str | None = None  # width
    h: str | None = None  # height
    min_w: str | None = None
    min_h: str | None = None
    max_w: str | None = None
    max_h: str | None = None

    # ── Spacing ───────────────────────────────────────────
    p: str | None = None  # padding
    px: str | None = None  # padding-x (left/right)
    py: str | None = None  # padding-y (top/bottom)
    pt: str | None = None  # padding-top
    pb: str | None = None  # padding-bottom
    pl: str | None = None  # padding-left
    pr: str | None = None  # padding-right
    m: str | None = None  # margin
    mx: str | None = None
    my: str | None = None
    mt: str | None = None
    mb: str | None = None
    ml: str | None = None
    mr: str | None = None

    # ── Visual ────────────────────────────────────────────
    bg: str | None = None  # background
    color: str | None = None
    border: str | None = None
    radius: str | None = None
    shadow: str | None = None
    opacity: str | None = None

    # ── Position ──────────────────────────────────────────
    position: Literal["static", "relative", "absolute", "fixed", "sticky"] | None = None
    top: str | None = None
    right: str | None = None
    bottom: str | None = None
    left: str | None = None
    z_index: str | None = None

    # ── Animation ─────────────────────────────────────────
    animation: str | None = None
    transition: str | None = None

    # ── Accessibility ─────────────────────────────────────
    role: str | None = None
    aria_label: str | None = None
    aria_hidden: bool | None = None

    # ── Autres ────────────────────────────────────────────
    cursor: str | None = None
    overflow: str | None = None
    text_align: str | None = None

    def to_css(self) -> dict[str, str]:
        """Convertit les props en dict de propriétés CSS."""
        css: dict[str, str] = {}

        # Layout
        css["display"] = self.display
        if "flex" in self.display or "grid" in self.display:
            if "flex" in self.display:
                css["flex-direction"] = self.direction
            css["align-items"] = _ALIGN_MAP.get(self.align, self.align)
            css["justify-content"] = _JUSTIFY_MAP.get(self.justify, self.justify)
            if self.gap:
                css["gap"] = self.gap
            if self.wrap:
                css["flex-wrap"] = "wrap"

        # Dimensions
        if self.w:
            css["width"] = self.w
        if self.h:
            css["height"] = self.h
        if self.min_w:
            css["min-width"] = self.min_w
        if self.min_h:
            css["min-height"] = self.min_h
        if self.max_w:
            css["max-width"] = self.max_w
        if self.max_h:
            css["max-height"] = self.max_h

        # Spacing - Padding
        if self.p:
            css["padding"] = self.p
        if self.px:
            css["padding-left"] = self.px
            css["padding-right"] = self.px
        if self.py:
            css["padding-top"] = self.py
            css["padding-bottom"] = self.py
        if self.pt:
            css["padding-top"] = self.pt
        if self.pb:
            css["padding-bottom"] = self.pb
        if self.pl:
            css["padding-left"] = self.pl
        if self.pr:
            css["padding-right"] = self.pr

        # Spacing - Margin
        if self.m:
            css["margin"] = self.m
        if self.mx:
            css["margin-left"] = self.mx
            css["margin-right"] = self.mx
        if self.my:
            css["margin-top"] = self.my
            css["margin-bottom"] = self.my
        if self.mt:
            css["margin-top"] = self.mt
        if self.mb:
            css["margin-bottom"] = self.mb
        if self.ml:
            css["margin-left"] = self.ml
        if self.mr:
            css["margin-right"] = self.mr

        # Visual
        if self.bg:
            css["background"] = self.bg
        if self.color:
            css["color"] = self.color
        if self.border:
            css["border"] = self.border
        if self.radius:
            css["border-radius"] = self.radius
        if self.shadow:
            css["box-shadow"] = self.shadow
        if self.opacity:
            css["opacity"] = self.opacity

        # Position
        if self.position:
            css["position"] = self.position
        if self.top:
            css["top"] = self.top
        if self.right:
            css["right"] = self.right
        if self.bottom:
            css["bottom"] = self.bottom
        if self.left:
            css["left"] = self.left
        if self.z_index:
            css["z-index"] = self.z_index

        # Animation
        if self.animation:
            css["animation"] = self.animation
        if self.transition:
            css["transition"] = self.transition

        # Autres
        if self.cursor:
            css["cursor"] = self.cursor
        if self.overflow:
            css["overflow"] = self.overflow
        if self.text_align:
            css["text-align"] = self.text_align

        return css

    def to_attrs(self) -> dict[str, str]:
        """Retourne les attributs HTML (ARIA, role, etc.)."""
        attrs: dict[str, str] = {}
        if self.role:
            attrs["role"] = self.role
        if self.aria_label:
            attrs["aria-label"] = self.aria_label
        if self.aria_hidden is not None:
            attrs["aria-hidden"] = "true" if self.aria_hidden else "false"
        return attrs


# Mappings pour valeurs CSS
_ALIGN_MAP = {
    "start": "flex-start",
    "end": "flex-end",
}

_JUSTIFY_MAP = {
    "start": "flex-start",
    "end": "flex-end",
    "between": "space-between",
    "around": "space-around",
    "evenly": "space-evenly",
}


class Box:
    """Composant Box universel.

    Box peut être utilisé de deux façons:

    1. Chaînage fluide:
        html = Box(p="1rem").child("<span>A</span>").child("<span>B</span>").html()

    2. Context manager:
        with Box(p="1rem") as box:
            box.child("<span>A</span>")
            box.child("<span>B</span>")
    """

    __slots__ = ("_props", "_children", "_tag")

    def __init__(self, tag: str = "div", **props):
        """Crée un Box.

        Args:
            tag: Tag HTML (div, section, article, nav, etc.)
            **props: Props de BoxProps (voir BoxProps pour la liste complète)
        """
        self._tag = tag
        self._props = BoxProps(**props)
        self._children: list[str] = []

    def child(self, html: str) -> Box:
        """Ajoute un enfant HTML.

        Args:
            html: HTML brut ou texte (sera échappé si texte simple).

        Returns:
            Self pour chaînage.
        """
        self._children.append(html)
        return self

    def text(self, content: str) -> Box:
        """Ajoute du texte échappé.

        Args:
            content: Texte brut à échapper.

        Returns:
            Self pour chaînage.
        """
        self._children.append(echapper_html(content))
        return self

    def html(self) -> str:
        """Retourne le HTML généré.

        Returns:
            String HTML complet.
        """
        css = self._props.to_css()
        attrs = self._props.to_attrs()

        # Construire la balise ouvrante
        parts = [f"<{self._tag}"]

        if css:
            class_name = StyleSheet.create_class(css)
            parts.append(f'class="{class_name}"')

        for key, value in attrs.items():
            safe_value = str(value).replace('"', "&quot;")
            parts.append(f'{key}="{safe_value}"')

        opening = " ".join(parts) + ">"
        content = "".join(self._children)
        closing = f"</{self._tag}>"

        return f"{opening}{content}{closing}"

    def show(self) -> None:
        """Affiche le Box dans Streamlit."""
        StyleSheet.inject()  # S'assurer que le CSS est injecté
        st.markdown(self.html(), unsafe_allow_html=True)

    def __enter__(self) -> Box:
        """Context manager entry."""
        return self

    def __exit__(self, *_) -> None:
        """Context manager exit - affiche automatiquement."""
        self.show()

    def __str__(self) -> str:
        """Permet d'utiliser Box comme string."""
        return self.html()


__all__ = ["Box", "BoxProps"]
