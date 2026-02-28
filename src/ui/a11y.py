"""
Accessibilité (a11y) — Module centralisé WCAG 2.1 / RGAA.

Fournit des utilitaires pour rendre les composants UI accessibles :
- Texte invisible pour screen readers (``sr_only``)
- Régions ARIA live pour les notifications dynamiques
- Rôles et attributs ARIA
- Landmarks ARIA avec context manager (isole ``unsafe_allow_html``)
- Vérification du ratio de contraste WCAG AA/AAA
- CSS utilitaire d'accessibilité injecté globalement

Usage:
    from src.ui.a11y import A11y

    # Texte invisible lu par les screen readers
    A11y.sr_only("42 résultats trouvés")

    # Zone live pour annoncer les changements dynamiques
    A11y.live_region("Sauvegarde réussie", politeness="polite")

    # Landmark via context manager (fermeture garantie)
    with A11y.landmark_region("main", "Contenu principal", html_id="main-content"):
        page.run()

    # Vérifier le contraste
    ratio = A11y.ratio_contraste("#212529", "#ffffff")
    assert ratio >= 4.5  # WCAG AA
"""

from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Generator

import streamlit as st

logger = logging.getLogger(__name__)


# ── Constante CSS a11y (partagée par injecter_css / injecter_css_differe) ──
_A11Y_CSS = """
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
    /* Apparence discrète par défaut (ton neutre) */
    background: var(--sem-surface-alt, #f8f9fa);
    color: var(--sem-on-surface, #212529);
    border: 1px solid var(--sem-border, #ced4da);
    padding: 6px 12px;
    z-index: 10000;
    font-weight: 500;
    text-decoration: none;
    border-radius: 4px;
    transition: top 0.18s ease, background 0.12s ease, color 0.12s ease;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}

.skip-link:focus {
    top: 8px;
    /* Mettre en évidence au focus avec la couleur interactive (accessible) */
    background: var(--sem-interactive, #2E7D32);
    color: var(--sem-on-interactive, #ffffff);
    border-color: transparent;
}

/* ── ARIA live regions ─────────────────────────── */
[aria-live] {
    position: relative;
}
"""


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
        from src.ui.engine import CSSManager

        CSSManager.register(
            "a11y",
            _A11Y_CSS,
        )

    @staticmethod
    def injecter_css_differe() -> None:
        """Enregistre le CSS a11y dans la file CSS différée (non-critique).

        Appelé par ``initialiser_app()`` pour charger le CSS a11y après
        le premier paint critique. Le CSS est injecté via
        ``CSSManager.inject_deferred()``.
        """
        from src.ui.engine import CSSManager

        CSSManager.register_deferred(
            "a11y",
            _A11Y_CSS,
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

        return f'<{tag} role="{role}" aria-label="{echapper_html(label)}">{html_content}</{tag}>'

    # ── Landmark safe rendering (isole unsafe_allow_html) ─

    @staticmethod
    def _safe_html(html: str) -> None:
        """Injecte du HTML brut via st.markdown avec fallback.

        Point unique de dépendance à ``unsafe_allow_html``.
        Si Streamlit retire le support, seule cette méthode doit être adaptée.

        Args:
            html: Fragment HTML à injecter.
        """
        try:
            st.markdown(html, unsafe_allow_html=True)
        except TypeError:
            # Fallback si Streamlit retire unsafe_allow_html dans une future version
            logger.warning(
                "unsafe_allow_html non supporté — HTML ignoré: %.60s…",
                html,
            )

    @staticmethod
    def ouvrir_landmark(
        role: str,
        label: str,
        tag: str = "main",
        html_id: str | None = None,
    ) -> None:
        """Ouvre un landmark ARIA via st.markdown(unsafe_allow_html=True).

        Encapsule la dépendance à ``unsafe_allow_html`` dans un seul
        point de contrôle. Si Streamlit supprime le support, seule
        ``_safe_html`` doit être adaptée.

        Args:
            role: Rôle ARIA (``"main"``, ``"navigation"``, ``"complementary"``…).
            label: Label accessible pour le landmark.
            tag: Balise HTML (``"main"``, ``"nav"``, ``"aside"``, ``"header"``…).
            html_id: Attribut ``id`` optionnel (pour skip-link).
        """
        from src.ui.utils import echapper_html

        id_attr = f' id="{html_id}"' if html_id else ""
        # When an html_id is provided, add tabindex="-1" so the element can
        # receive programmatic focus (used by skip-links for accessibility).
        tabindex_attr = ' tabindex="-1"' if html_id else ""
        html = f'<{tag}{id_attr}{tabindex_attr} role="{role}" aria-label="{echapper_html(label)}">'
        A11y._safe_html(html)

    @staticmethod
    def fermer_landmark(tag: str = "main") -> None:
        """Ferme un landmark ARIA précédemment ouvert.

        Args:
            tag: Balise HTML à fermer (doit correspondre à ``ouvrir_landmark``).
        """
        A11y._safe_html(f"</{tag}>")

    @staticmethod
    @contextmanager
    def landmark_region(
        role: str,
        label: str,
        tag: str = "main",
        html_id: str | None = None,
    ) -> Generator[None, None, None]:
        """Context manager pour un landmark ARIA ouvert/fermé automatiquement.

        Garantit la fermeture même si le contenu lève une exception.
        Isole la dépendance à ``unsafe_allow_html`` de Streamlit dans
        ``_safe_html()`` — un seul point de modification si l'API change.

        Args:
            role: Rôle ARIA du landmark.
            label: Label accessible.
            tag: Balise HTML englobante.
            html_id: ID optionnel pour navigation (skip-link).

        Example::

            with A11y.landmark_region("main", "Contenu principal",
                                      html_id="main-content"):
                page.run()

            with A11y.landmark_region("navigation", "Menu latéral", tag="nav"):
                afficher_sidebar()
        """
        A11y.ouvrir_landmark(role, label, tag, html_id)
        try:
            yield
        finally:
            A11y.fermer_landmark(tag)

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
