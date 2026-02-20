"""
Text - Primitive de typographie.

Composant pour afficher du texte avec styles préfinis.
Supporte les variantes de taille, poids, et couleur.

Usage:
    from src.ui.primitives import Text

    # Texte simple
    Text("Hello World").show()

    # Avec variants
    Text("Titre", size="xl", weight="bold", color=Couleur.TEXT_PRIMARY).show()

    # Inline (retourne HTML)
    html = Text("Label", size="sm", color=Couleur.TEXT_SECONDARY).html()
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import streamlit as st

from src.ui.system.css import StyleSheet
from src.ui.tokens import Couleur, Typographie
from src.ui.utils import echapper_html


@dataclass
class TextProps:
    """Props du composant Text."""

    # Contenu
    content: str = ""

    # Taille
    size: Literal["xs", "sm", "md", "lg", "xl", "2xl", "3xl", "4xl"] = "md"

    # Poids
    weight: Literal["normal", "medium", "semibold", "bold"] = "normal"

    # Couleur
    color: str | None = None

    # Alignement
    align: Literal["left", "center", "right", "justify"] = "left"

    # Style
    italic: bool = False
    underline: bool = False
    truncate: bool = False
    line_clamp: int | None = None

    # Espacement
    mb: str | None = None  # margin-bottom
    mt: str | None = None  # margin-top

    # Tag HTML
    tag: Literal["p", "span", "h1", "h2", "h3", "h4", "h5", "h6", "label", "div"] = "span"


# Mapping taille → font-size
_SIZE_MAP = {
    "xs": Typographie.CAPTION,
    "sm": Typographie.BODY_SM,
    "md": Typographie.BODY,
    "lg": Typographie.BODY_LG,
    "xl": Typographie.H4,
    "2xl": Typographie.H3,
    "3xl": Typographie.H2,
    "4xl": Typographie.H1,
}

# Mapping poids → font-weight
_WEIGHT_MAP = {
    "normal": "400",
    "medium": "500",
    "semibold": "600",
    "bold": "700",
}


class Text:
    """Composant Text pour typographie.

    Usage:
        # Simple
        Text("Hello").show()

        # Avec props
        Text("Titre", size="xl", weight="bold").show()

        # HTML inline
        html = Text("Label", size="sm").html()
    """

    __slots__ = ("_props",)

    def __init__(
        self,
        content: str,
        size: Literal["xs", "sm", "md", "lg", "xl", "2xl", "3xl", "4xl"] = "md",
        weight: Literal["normal", "medium", "semibold", "bold"] = "normal",
        color: str | None = None,
        align: Literal["left", "center", "right", "justify"] = "left",
        italic: bool = False,
        underline: bool = False,
        truncate: bool = False,
        line_clamp: int | None = None,
        mb: str | None = None,
        mt: str | None = None,
        tag: Literal["p", "span", "h1", "h2", "h3", "h4", "h5", "h6", "label", "div"] = "span",
    ):
        """Crée un Text.

        Args:
            content: Texte à afficher.
            size: Taille (xs, sm, md, lg, xl, 2xl, 3xl, 4xl).
            weight: Poids (normal, medium, semibold, bold).
            color: Couleur (hex ou token).
            align: Alignement (left, center, right, justify).
            italic: Style italique.
            underline: Souligné.
            truncate: Tronquer avec ellipsis.
            line_clamp: Nombre de lignes max (avec ellipsis).
            mb: Margin bottom.
            mt: Margin top.
            tag: Tag HTML.
        """
        self._props = TextProps(
            content=content,
            size=size,
            weight=weight,
            color=color,
            align=align,
            italic=italic,
            underline=underline,
            truncate=truncate,
            line_clamp=line_clamp,
            mb=mb,
            mt=mt,
            tag=tag,
        )

    def _to_css(self) -> dict[str, str]:
        """Convertit les props en CSS."""
        css: dict[str, str] = {}

        # Taille
        css["font-size"] = _SIZE_MAP.get(self._props.size, Typographie.BODY)

        # Poids
        css["font-weight"] = _WEIGHT_MAP.get(self._props.weight, "400")

        # Couleur
        if self._props.color:
            css["color"] = self._props.color

        # Alignement
        if self._props.align != "left":
            css["text-align"] = self._props.align

        # Style
        if self._props.italic:
            css["font-style"] = "italic"
        if self._props.underline:
            css["text-decoration"] = "underline"

        # Truncate
        if self._props.truncate:
            css["white-space"] = "nowrap"
            css["overflow"] = "hidden"
            css["text-overflow"] = "ellipsis"

        # Line clamp
        if self._props.line_clamp:
            css["display"] = "-webkit-box"
            css["-webkit-line-clamp"] = str(self._props.line_clamp)
            css["-webkit-box-orient"] = "vertical"
            css["overflow"] = "hidden"

        # Spacing
        if self._props.mb:
            css["margin-bottom"] = self._props.mb
        if self._props.mt:
            css["margin-top"] = self._props.mt

        # Reset margin pour span
        if self._props.tag == "span":
            css["margin"] = css.get("margin", "0")

        return css

    def html(self) -> str:
        """Retourne le HTML généré.

        Returns:
            String HTML.
        """
        css = self._to_css()
        class_name = StyleSheet.create_class(css) if css else ""

        tag = self._props.tag
        content = echapper_html(self._props.content)

        if class_name:
            return f'<{tag} class="{class_name}">{content}</{tag}>'
        return f"<{tag}>{content}</{tag}>"

    def show(self) -> None:
        """Affiche le Text dans Streamlit."""
        StyleSheet.inject()
        st.markdown(self.html(), unsafe_allow_html=True)

    def __str__(self) -> str:
        """Permet d'utiliser Text comme string."""
        return self.html()


# ═══════════════════════════════════════════════════════════
# HELPERS typographiques
# ═══════════════════════════════════════════════════════════


def heading(
    content: str,
    level: Literal[1, 2, 3, 4, 5, 6] = 2,
    color: str | None = None,
    align: Literal["left", "center", "right"] = "left",
    mb: str = "1rem",
) -> str:
    """Helper pour créer un heading.

    Args:
        content: Texte du heading.
        level: Niveau (1-6).
        color: Couleur optionnelle.
        align: Alignement.
        mb: Margin bottom.

    Returns:
        HTML du heading.
    """
    size_map = {1: "4xl", 2: "3xl", 3: "2xl", 4: "xl", 5: "lg", 6: "md"}
    tag_map = {1: "h1", 2: "h2", 3: "h3", 4: "h4", 5: "h5", 6: "h6"}

    return Text(
        content,
        size=size_map.get(level, "2xl"),
        weight="bold",
        color=color,
        align=align,
        mb=mb,
        tag=tag_map.get(level, "h2"),
    ).html()


def paragraph(
    content: str,
    size: Literal["sm", "md", "lg"] = "md",
    color: str | None = None,
    mb: str = "1rem",
) -> str:
    """Helper pour créer un paragraphe.

    Args:
        content: Texte du paragraphe.
        size: Taille.
        color: Couleur optionnelle.
        mb: Margin bottom.

    Returns:
        HTML du paragraphe.
    """
    return Text(content, size=size, color=color or Couleur.TEXT_PRIMARY, mb=mb, tag="p").html()


def caption(content: str, color: str | None = None) -> str:
    """Helper pour du texte secondaire/caption.

    Args:
        content: Texte.
        color: Couleur (défaut: TEXT_SECONDARY).

    Returns:
        HTML du caption.
    """
    return Text(content, size="xs", color=color or Couleur.TEXT_SECONDARY).html()


__all__ = ["Text", "TextProps", "heading", "paragraph", "caption"]
