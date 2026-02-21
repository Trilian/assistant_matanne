"""
Accessibilité (a11y) — Module centralisé WCAG 2.1 / RGAA.

Fournit des utilitaires pour rendre les composants UI accessibles :
- Texte invisible pour screen readers (``sr_only``)
- Régions ARIA live pour les notifications dynamiques
- Rôles et attributs ARIA
- Vérification du ratio de contraste WCAG AA/AAA
- CSS utilitaire d'accessibilité injecté globalement

Usage:
    from src.ui.a11y import A11y

    # Texte invisible lu par les screen readers
    A11y.sr_only("42 résultats trouvés")

    # Zone live pour annoncer les changements dynamiques
    A11y.live_region("Sauvegarde réussie", politeness="polite")

    # Vérifier le contraste
    ratio = A11y.ratio_contraste("#212529", "#ffffff")
    assert ratio >= 4.5  # WCAG AA
"""

from __future__ import annotations

import streamlit as st


class A11y:
    """Utilitaires d'accessibilité centralisés.

    Méthodes statiques uniquement — pas d'instanciation nécessaire.
    """

    # ── CSS utilitaire ────────────────────────────────────

    @staticmethod
    def injecter_css() -> None:
        """Enregistre le CSS utilitaire d'accessibilité dans le CSSManager.

        Inclut :
        - ``.sr-only`` : texte invisible visuellement mais lu par les screen readers
        - ``:focus-visible`` : indicateurs de focus clairs
        - ``@media (prefers-reduced-motion)`` : désactive les animations
        """
        from src.ui.css import CSSManager

        CSSManager.register(
            "a11y",
            """
/* ── Screen reader only ────────────────────────── */
.sr-only {
    position: absolute !important;
    width: 1px !important;
    height: 1px !important;
    padding: 0 !important;
    margin: -1px !important;
    overflow: hidden !important;
    clip: rect(0, 0, 0, 0) !important;
    white-space: nowrap !important;
    border: 0 !important;
}

/* ── Skip to content link ──────────────────────── */
.skip-link {
    position: absolute;
    top: -40px;
    left: 0;
    background: var(--sem-interactive, #4CAF50);
    color: var(--sem-on-interactive, #fff);
    padding: 8px 16px;
    z-index: 10000;
    font-weight: 600;
    text-decoration: none;
    border-radius: 0 0 8px 0;
    transition: top 0.2s ease;
}

.skip-link:focus {
    top: 0;
}

/* ── ARIA live regions ─────────────────────────── */
[aria-live] {
    position: relative;
}
""",
        )

    # ── Screen Reader ─────────────────────────────────────

    @staticmethod
    def sr_only(texte: str) -> None:
        """Affiche du texte invisible visuellement, lu par les screen readers.

        Args:
            texte: Texte à communiquer aux technologies d'assistance.
        """
        from src.ui.utils import echapper_html

        st.markdown(
            f'<span class="sr-only">{echapper_html(texte)}</span>',
            unsafe_allow_html=True,
        )

    @staticmethod
    def sr_only_html(texte: str) -> str:
        """Retourne le HTML pour du texte screen-reader-only (pour inclusion dans un builder).

        Args:
            texte: Texte à communiquer.

        Returns:
            Chaîne HTML ``<span class="sr-only">...</span>``.
        """
        from src.ui.utils import echapper_html

        return f'<span class="sr-only">{echapper_html(texte)}</span>'

    # ── ARIA Live Regions ─────────────────────────────────

    @staticmethod
    def live_region(
        message: str,
        politeness: str = "polite",
        role: str | None = None,
    ) -> None:
        """Annonce un message dynamique aux screen readers via ARIA live region.

        Args:
            message: Message à annoncer.
            politeness: ``"polite"`` (attend la fin de la lecture) ou
                ``"assertive"`` (interrompt immédiatement).
            role: Rôle ARIA optionnel (``"status"``, ``"alert"``, ``"log"``).
        """
        from src.ui.utils import echapper_html

        role_attr = f' role="{role}"' if role else ""
        st.markdown(
            f'<div aria-live="{politeness}"{role_attr} class="sr-only">'
            f"{echapper_html(message)}</div>",
            unsafe_allow_html=True,
        )

    # ── ARIA Attributes Helpers ───────────────────────────

    @staticmethod
    def attrs(
        role: str | None = None,
        label: str | None = None,
        describedby: str | None = None,
        live: str | None = None,
        expanded: bool | None = None,
        hidden: bool | None = None,
        current: str | None = None,
    ) -> str:
        """Génère une chaîne d'attributs ARIA pour insertion dans du HTML.

        Args:
            role: Rôle ARIA (``"navigation"``, ``"dialog"``, ``"status"``…)
            label: ``aria-label`` pour l'élément.
            describedby: ID de l'élément décrivant celui-ci.
            live: ``aria-live`` politeness.
            expanded: ``aria-expanded`` pour les accordéons/menus.
            hidden: ``aria-hidden`` pour masquer du contenu.
            current: ``aria-current`` (``"page"``, ``"step"``…).

        Returns:
            Chaîne d'attributs à insérer dans une balise HTML.

        Example:
            attrs = A11y.attrs(role="navigation", label="Menu principal")
            html = f'<nav {attrs}>...</nav>'
        """
        parts: list[str] = []
        if role:
            parts.append(f'role="{role}"')
        if label:
            from src.ui.utils import echapper_html

            parts.append(f'aria-label="{echapper_html(label)}"')
        if describedby:
            parts.append(f'aria-describedby="{describedby}"')
        if live:
            parts.append(f'aria-live="{live}"')
        if expanded is not None:
            parts.append(f'aria-expanded="{"true" if expanded else "false"}"')
        if hidden is not None:
            parts.append(f'aria-hidden="{"true" if hidden else "false"}"')
        if current:
            parts.append(f'aria-current="{current}"')
        return " ".join(parts)

    # ── Landmarks ─────────────────────────────────────────

    @staticmethod
    def landmark(
        html_content: str,
        role: str,
        label: str,
        tag: str = "section",
    ) -> str:
        """Enveloppe du HTML dans un landmark ARIA.

        Args:
            html_content: HTML à envelopper.
            role: Rôle ARIA (``"navigation"``, ``"main"``, ``"complementary"``…).
            label: Label accessible pour le landmark.
            tag: Tag HTML (``"section"``, ``"nav"``, ``"aside"``…).

        Returns:
            HTML enveloppé avec les attributs ARIA.
        """
        from src.ui.utils import echapper_html

        return (
            f'<{tag} role="{role}" aria-label="{echapper_html(label)}">' f"{html_content}</{tag}>"
        )

    # ── Contraste WCAG ────────────────────────────────────

    @staticmethod
    def _luminance_relative(hex_color: str) -> float:
        """Calcule la luminance relative d'une couleur hex (WCAG 2.1).

        Args:
            hex_color: Couleur au format ``#RRGGBB``.

        Returns:
            Luminance relative entre 0 et 1.
        """
        hex_color = hex_color.lstrip("#")
        if len(hex_color) == 3:
            hex_color = "".join(c * 2 for c in hex_color)

        r, g, b = (int(hex_color[i : i + 2], 16) / 255.0 for i in (0, 2, 4))

        def _linearize(c: float) -> float:
            return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

        return 0.2126 * _linearize(r) + 0.7152 * _linearize(g) + 0.0722 * _linearize(b)

    @staticmethod
    def ratio_contraste(couleur_fg: str, couleur_bg: str) -> float:
        """Calcule le ratio de contraste WCAG entre deux couleurs.

        Args:
            couleur_fg: Couleur du premier plan (hex ``#RRGGBB``).
            couleur_bg: Couleur de l'arrière-plan (hex ``#RRGGBB``).

        Returns:
            Ratio de contraste (1.0 à 21.0). WCAG AA requiert ≥ 4.5:1
            pour le texte normal, ≥ 3:1 pour le gros texte.

        Example:
            ratio = A11y.ratio_contraste("#212529", "#ffffff")
            # → ~16.0 (excellent)
        """
        lum1 = A11y._luminance_relative(couleur_fg)
        lum2 = A11y._luminance_relative(couleur_bg)

        lighter = max(lum1, lum2)
        darker = min(lum1, lum2)

        return (lighter + 0.05) / (darker + 0.05)

    @staticmethod
    def est_conforme_aa(couleur_fg: str, couleur_bg: str, gros_texte: bool = False) -> bool:
        """Vérifie la conformité WCAG AA d'une paire de couleurs.

        Args:
            couleur_fg: Couleur premier plan.
            couleur_bg: Couleur arrière-plan.
            gros_texte: True si texte ≥ 18pt ou ≥ 14pt bold.

        Returns:
            True si conforme WCAG AA.
        """
        ratio = A11y.ratio_contraste(couleur_fg, couleur_bg)
        seuil = 3.0 if gros_texte else 4.5
        return ratio >= seuil


__all__ = [
    "A11y",
]
