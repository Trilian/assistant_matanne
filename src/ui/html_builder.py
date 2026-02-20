"""
Générateur HTML sécurisé avec Design Tokens intégrés.

Remplace les f-strings HTML dispersées par un builder fluide et sécurisé.
Échappe automatiquement le contenu texte pour prévenir les injections XSS.

Usage:
    from src.ui.html_builder import HtmlBuilder, render_html

    html = (HtmlBuilder("div")
        .style(background=Couleur.BG_SUBTLE, padding=Espacement.LG)
        .child("span", text="Hello")
        .build())

    render_html(html)
"""

from __future__ import annotations

from src.ui.utils import echapper_html


class HtmlBuilder:
    """Builder fluide pour construire du HTML sécurisé.

    Toutes les valeurs de texte sont échappées automatiquement sauf
    si ``safe=True`` est passé explicitement.

    Example:
        html = (HtmlBuilder("div")
            .style(
                background=Couleur.BG_SUBTLE,
                padding=Espacement.LG,
                border_radius=Rayon.LG,
                box_shadow=Ombre.SM,
            )
            .child("span", text=titre, style={"font-weight": "600"})
            .child("p", text=contenu, style={"color": Couleur.TEXT_SECONDARY})
            .build())
    """

    __slots__ = ("tag", "attrs", "_styles", "_children", "_classes")

    def __init__(self, tag: str = "div", **attrs: str) -> None:
        self.tag = tag
        self.attrs = attrs
        self._styles: dict[str, str] = {}
        self._children: list[str] = []
        self._classes: list[str] = []

    def style(self, **props: str) -> HtmlBuilder:
        """Ajoute des propriétés CSS (underscore -> tiret automatique).

        Args:
            **props: Propriétés CSS. Les underscores dans les noms de clé sont
                convertis en tirets (ex: ``border_radius`` -> ``border-radius``).

        Returns:
            Self pour chaînage.
        """
        for key, val in props.items():
            css_key = key.replace("_", "-")
            self._styles[css_key] = str(val)
        return self

    def cls(self, *classes: str) -> HtmlBuilder:
        """Ajoute des classes CSS.

        Args:
            *classes: Noms de classes à ajouter.

        Returns:
            Self pour chaînage.
        """
        self._classes.extend(classes)
        return self

    def child(
        self,
        tag: str,
        text: str = "",
        safe: bool = False,
        style: dict[str, str] | None = None,
    ) -> HtmlBuilder:
        """Ajoute un élément enfant.

        Args:
            tag: Tag HTML de l'enfant (div, span, p, h2, etc.)
            text: Contenu texte (échappé sauf si ``safe=True``)
            safe: Si True, le texte n'est pas échappé
            style: Dict de propriétés CSS pour l'enfant

        Returns:
            Self pour chaînage.
        """
        style_attr = ""
        if style:
            style_str = "; ".join(f"{k.replace('_', '-')}: {v}" for k, v in style.items())
            style_attr = f' style="{style_str}"'

        content = text if safe else echapper_html(text)
        self._children.append(f"<{tag}{style_attr}>{content}</{tag}>")
        return self

    def child_builder(self, builder: HtmlBuilder) -> HtmlBuilder:
        """Ajoute un sous-builder comme enfant.

        Args:
            builder: Instance HtmlBuilder dont le HTML sera intégré.

        Returns:
            Self pour chaînage.
        """
        self._children.append(builder.build())
        return self

    def raw_child(self, html: str) -> HtmlBuilder:
        """Ajoute du HTML brut pré-construit.

        Le contenu n'est PAS échappé. Utilisez uniquement pour du HTML
        déjà sécurisé (ex: sortie d'un autre HtmlBuilder).

        Args:
            html: HTML brut à insérer.

        Returns:
            Self pour chaînage.
        """
        self._children.append(html)
        return self

    def text(self, content: str) -> HtmlBuilder:
        """Ajoute du texte échappé directement dans l'élément.

        Args:
            content: Texte brut à échapper et insérer.

        Returns:
            Self pour chaînage.
        """
        self._children.append(echapper_html(content))
        return self

    # ── Accessibilité ────────────────────────────────────

    def aria(
        self,
        label: str | None = None,
        role: str | None = None,
        live: str | None = None,
        describedby: str | None = None,
        expanded: bool | None = None,
        hidden: bool | None = None,
        current: str | None = None,
    ) -> HtmlBuilder:
        """Ajoute des attributs ARIA pour l'accessibilité.

        Args:
            label: ``aria-label`` pour l'élément.
            role: Rôle ARIA (``"navigation"``, ``"dialog"``…).
            live: ``aria-live`` (``"polite"``, ``"assertive"``).
            describedby: ID de l'élément descriptif.
            expanded: ``aria-expanded`` pour les accordeons.
            hidden: ``aria-hidden`` pour masquer du contenu.
            current: ``aria-current`` (``"page"``, ``"step"``…).

        Returns:
            Self pour chaînage.
        """
        if role:
            self.attrs["role"] = role
        if label:
            self.attrs["aria-label"] = label
        if live:
            self.attrs["aria-live"] = live
        if describedby:
            self.attrs["aria-describedby"] = describedby
        if expanded is not None:
            self.attrs["aria-expanded"] = "true" if expanded else "false"
        if hidden is not None:
            self.attrs["aria-hidden"] = "true" if hidden else "false"
        if current:
            self.attrs["aria-current"] = current
        return self

    def focusable(self, tabindex: int = 0) -> HtmlBuilder:
        """Rend l'élément focusable au clavier.

        Args:
            tabindex: Ordre dans la navigation clavier (0 = ordre naturel).

        Returns:
            Self pour chaînage.
        """
        self.attrs["tabindex"] = str(tabindex)
        return self

    def conditional(
        self,
        condition: bool,
        tag: str,
        text: str = "",
        style: dict[str, str] | None = None,
    ) -> HtmlBuilder:
        """Ajoute un enfant uniquement si la condition est vraie.

        Args:
            condition: Condition booléenne.
            tag: Tag HTML.
            text: Contenu texte.
            style: Styles CSS.

        Returns:
            Self pour chaînage.
        """
        if condition:
            self.child(tag, text=text, style=style)
        return self

    def build(self) -> str:
        """Génère le HTML final.

        Returns:
            Chaîne HTML complète.
        """
        parts: list[str] = [f"<{self.tag}"]

        if self._classes:
            parts.append(f' class="{" ".join(self._classes)}"')

        all_attrs: list[str] = []

        if self._styles:
            style_str = "; ".join(f"{k}: {v}" for k, v in self._styles.items())
            all_attrs.append(f'style="{style_str}"')

        for key, val in self.attrs.items():
            all_attrs.append(f'{key}="{echapper_html(str(val))}"')

        if all_attrs:
            parts.append(" " + " ".join(all_attrs))

        parts.append(">")
        parts.extend(self._children)
        parts.append(f"</{self.tag}>")

        return "".join(parts)

    def __str__(self) -> str:
        """Permet l'utilisation directe dans les f-strings."""
        return self.build()


def render_html(html: str) -> None:
    """Rend du HTML dans Streamlit via st.markdown.

    Wrapper de commodité pour éviter de répéter
    ``st.markdown(html, unsafe_allow_html=True)`` partout.

    Args:
        html: HTML à afficher (déjà sécurisé via HtmlBuilder).
    """
    import streamlit as st

    st.markdown(html, unsafe_allow_html=True)


__all__ = [
    "HtmlBuilder",
    "render_html",
]
