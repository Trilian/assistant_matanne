"""
Système d'animation centralisé — @keyframes et transitions unifiées.

Toutes les animations sont déclarées ici et injectées UNE SEULE FOIS au
démarrage via ``injecter_animations()``. Les composants utilisent les tokens
``Animation`` pour référencer les animations par nom.

Le système respecte automatiquement ``prefers-reduced-motion: reduce`` en
enveloppant les ``@keyframes`` dans une media query.

Usage:
    from src.ui.animations import Animation, animer, injecter_animations

    # Au démarrage (dans initialiser_app()) :
    injecter_animations()

    # Dans un composant :
    html = f'<div class="{Animation.FADE_IN}">Contenu</div>'

    # Ou via le helper :
    html_anime = animer('<div>Contenu</div>', Animation.SLIDE_UP, delay="0.1s")
"""

from __future__ import annotations

from enum import StrEnum

import streamlit as st


class Animation(StrEnum):
    """Noms de classes CSS d'animation.

    Chaque valeur correspond à une classe CSS générée par
    ``injecter_animations()``.
    """

    FADE_IN = "anim-fade-in"
    FADE_OUT = "anim-fade-out"
    SLIDE_UP = "anim-slide-up"
    SLIDE_DOWN = "anim-slide-down"
    SLIDE_LEFT = "anim-slide-left"
    SLIDE_RIGHT = "anim-slide-right"
    SCALE_IN = "anim-scale-in"
    SCALE_OUT = "anim-scale-out"
    PULSE = "anim-pulse"
    SHIMMER = "anim-shimmer"
    BOUNCE_IN = "anim-bounce-in"
    SPIN = "anim-spin"


# ═══════════════════════════════════════════════════════════
# KEYFRAMES + CLASSES CSS
# ═══════════════════════════════════════════════════════════

_ANIMATION_CSS = """
/* ── Animation System — Assistant Matanne ─────────────── */
/* Respecte prefers-reduced-motion automatiquement         */

@media (prefers-reduced-motion: no-preference) {

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

@keyframes fadeOut {
    from { opacity: 1; }
    to { opacity: 0; }
}

@keyframes slideUp {
    from { opacity: 0; transform: translateY(16px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes slideDown {
    from { opacity: 0; transform: translateY(-16px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes slideLeft {
    from { opacity: 0; transform: translateX(16px); }
    to { opacity: 1; transform: translateX(0); }
}

@keyframes slideRight {
    from { opacity: 0; transform: translateX(-16px); }
    to { opacity: 1; transform: translateX(0); }
}

@keyframes scaleIn {
    from { opacity: 0; transform: scale(0.9); }
    to { opacity: 1; transform: scale(1); }
}

@keyframes scaleOut {
    from { opacity: 1; transform: scale(1); }
    to { opacity: 0; transform: scale(0.9); }
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.6; }
}

@keyframes shimmer {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}

@keyframes bounceIn {
    0% { opacity: 0; transform: scale(0.3); }
    50% { opacity: 1; transform: scale(1.05); }
    70% { transform: scale(0.95); }
    100% { transform: scale(1); }
}

@keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

/* ── Animation classes ────────────────────────────────── */

.anim-fade-in { animation: fadeIn 0.3s ease forwards; }
.anim-fade-out { animation: fadeOut 0.3s ease forwards; }
.anim-slide-up { animation: slideUp 0.35s ease forwards; }
.anim-slide-down { animation: slideDown 0.35s ease forwards; }
.anim-slide-left { animation: slideLeft 0.35s ease forwards; }
.anim-slide-right { animation: slideRight 0.35s ease forwards; }
.anim-scale-in { animation: scaleIn 0.25s ease forwards; }
.anim-scale-out { animation: scaleOut 0.25s ease forwards; }
.anim-pulse { animation: pulse 1.5s ease-in-out infinite; }
.anim-shimmer {
    background: linear-gradient(90deg, transparent 25%, rgba(255,255,255,0.3) 50%, transparent 75%);
    background-size: 200% 100%;
    animation: shimmer 1.5s infinite;
}
.anim-bounce-in { animation: bounceIn 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) forwards; }
.anim-spin { animation: spin 1s linear infinite; }

/* ── Staggered children ───────────────────────────────── */
.anim-stagger > *:nth-child(1) { animation-delay: 0s; }
.anim-stagger > *:nth-child(2) { animation-delay: 0.05s; }
.anim-stagger > *:nth-child(3) { animation-delay: 0.1s; }
.anim-stagger > *:nth-child(4) { animation-delay: 0.15s; }
.anim-stagger > *:nth-child(5) { animation-delay: 0.2s; }
.anim-stagger > *:nth-child(6) { animation-delay: 0.25s; }
.anim-stagger > *:nth-child(7) { animation-delay: 0.3s; }
.anim-stagger > *:nth-child(8) { animation-delay: 0.35s; }

/* ── Hover micro-interactions ─────────────────────────── */
.anim-hover-lift {
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.anim-hover-lift:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.anim-hover-glow {
    transition: box-shadow 0.2s ease;
}
.anim-hover-glow:hover {
    box-shadow: 0 0 0 3px var(--sem-interactive, #4CAF50)33;
}

.anim-hover-scale {
    transition: transform 0.15s ease;
}
.anim-hover-scale:hover {
    transform: scale(1.02);
}

} /* fin @media (prefers-reduced-motion: no-preference) */
"""

_INJECTED_KEY = "_animations_css_injected"


def injecter_animations() -> None:
    """Injecte TOUS les @keyframes et classes d'animation une seule fois.

    Appelé automatiquement dans ``initialiser_app()``.
    L'injection est dédupliquée via ``session_state``.
    """
    if st.session_state.get(_INJECTED_KEY):
        return

    st.markdown(f"<style>{_ANIMATION_CSS}</style>", unsafe_allow_html=True)
    st.session_state[_INJECTED_KEY] = True


def animer(
    html: str,
    animation: Animation,
    delay: str = "0s",
    tag: str = "div",
) -> str:
    """Enveloppe du HTML dans un conteneur animé.

    Args:
        html: HTML à animer.
        animation: Classe d'animation à appliquer.
        delay: Délai CSS avant le début (ex: ``"0.1s"``).
        tag: Tag HTML du wrapper.

    Returns:
        HTML enveloppé avec la classe d'animation.

    Example:
        html_anime = animer("<p>Bonjour</p>", Animation.SLIDE_UP, delay="0.1s")
    """
    style = f' style="animation-delay: {delay}"' if delay != "0s" else ""
    return f'<{tag} class="{animation}"{style}>{html}</{tag}>'


__all__ = [
    "Animation",
    "injecter_animations",
    "animer",
]
