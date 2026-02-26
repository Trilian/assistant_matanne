"""
Skeleton loading — Placeholders animés pour les transitions de modules.

Affiche des blocs shimmer qui imitent la structure d'une page pendant
le chargement différé. Utilise l'animation ``shimmer`` du système
d'animations centralisé (``src.ui.animations``).

Usage dans la navigation::

    from src.ui.components.skeleton import afficher_skeleton_module

    # Pendant le chargement d'un module
    placeholder = st.empty()
    with placeholder.container():
        afficher_skeleton_module("Recettes", n_lignes=5)

Usage standalone::

    from src.ui.components.skeleton import skeleton_block, skeleton_texte

    skeleton_block(hauteur="200px")       # bloc rectangulaire
    skeleton_texte(n_lignes=3)            # lignes de texte
"""

from __future__ import annotations

from typing import Any

import streamlit as st

from src.ui.engine import CSSManager
from src.ui.tokens import Espacement, Rayon
from src.ui.tokens_semantic import Sem

# ═══════════════════════════════════════════════════════════
# CSS SKELETON (enregistré une seule fois via CSSManager)
# ═══════════════════════════════════════════════════════════

_SKELETON_CSS = """
/* ── Skeleton loading – Assistant Matanne ──────────────── */

@keyframes skeleton-shimmer {
    0%   { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}

.sk-base {
    background: linear-gradient(
        90deg,
        var(--sk-bg, #e0e0e0) 25%,
        var(--sk-shine, #f5f5f5) 50%,
        var(--sk-bg, #e0e0e0) 75%
    );
    background-size: 200% 100%;
    animation: skeleton-shimmer 1.5s ease-in-out infinite;
    border-radius: var(--sk-radius, 6px);
}

@media (prefers-reduced-motion: reduce) {
    .sk-base { animation: none; opacity: 0.6; }
}

/* Variantes de forme */
.sk-block {
    width: 100%;
    min-height: var(--sk-h, 20px);
}
.sk-circle {
    width: var(--sk-size, 40px);
    height: var(--sk-size, 40px);
    border-radius: 50%;
}
.sk-titre {
    width: 45%;
    min-height: 28px;
    margin-bottom: 16px;
}
.sk-ligne {
    width: var(--sk-w, 100%);
    min-height: 14px;
    margin-bottom: 10px;
}
.sk-carte {
    width: 100%;
    min-height: 80px;
    margin-bottom: 12px;
    border-radius: 8px;
}

/* Conteneur avec stagger */
.sk-container {
    display: flex;
    flex-direction: column;
    gap: 8px;
    padding: 16px 0;
}
.sk-row {
    display: flex;
    gap: 12px;
    align-items: center;
}

/* Stagger delays */
.sk-container > *:nth-child(1) { animation-delay: 0s; }
.sk-container > *:nth-child(2) { animation-delay: 0.08s; }
.sk-container > *:nth-child(3) { animation-delay: 0.16s; }
.sk-container > *:nth-child(4) { animation-delay: 0.24s; }
.sk-container > *:nth-child(5) { animation-delay: 0.32s; }
.sk-container > *:nth-child(6) { animation-delay: 0.40s; }
.sk-container > *:nth-child(7) { animation-delay: 0.48s; }
.sk-container > *:nth-child(8) { animation-delay: 0.56s; }
"""

_css_registered = False


def _assurer_css() -> None:
    """Enregistre le CSS skeleton une seule fois par session."""
    global _css_registered  # noqa: PLW0603
    if not _css_registered:
        CSSManager.register("skeleton", _SKELETON_CSS)
        _css_registered = True


# ═══════════════════════════════════════════════════════════
# COMPOSANTS UNITAIRES
# ═══════════════════════════════════════════════════════════


def skeleton_block(
    hauteur: str = "20px",
    largeur: str = "100%",
    rayon: str = "6px",
) -> str:
    """Retourne le HTML d'un bloc skeleton rectangulaire.

    Args:
        hauteur: Hauteur CSS du bloc.
        largeur: Largeur CSS du bloc.
        rayon: Border-radius CSS.

    Returns:
        Chaîne HTML du bloc (non injectée).
    """
    return (
        f'<div class="sk-base sk-block" '
        f'style="--sk-h:{hauteur}; width:{largeur}; --sk-radius:{rayon};">'
        f"</div>"
    )


def skeleton_circle(taille: str = "40px") -> str:
    """Retourne le HTML d'un cercle skeleton (avatar).

    Args:
        taille: Diamètre CSS.

    Returns:
        Chaîne HTML du cercle.
    """
    return f'<div class="sk-base sk-circle" style="--sk-size:{taille};"></div>'


def skeleton_texte(n_lignes: int = 3) -> str:
    """Retourne le HTML de N lignes skeleton simulant du texte.

    La dernière ligne est plus courte pour un rendu réaliste.

    Args:
        n_lignes: Nombre de lignes de texte.

    Returns:
        Chaîne HTML des lignes.
    """
    lignes: list[str] = []
    for i in range(n_lignes):
        # Dernière ligne plus courte
        w = "60%" if i == n_lignes - 1 else "100%"
        lignes.append(f'<div class="sk-base sk-ligne" style="--sk-w:{w};"></div>')
    return "\n".join(lignes)


def skeleton_carte() -> str:
    """Retourne le HTML d'une carte skeleton (titre + 2 lignes).

    Returns:
        Chaîne HTML de la carte.
    """
    return '<div class="sk-base sk-carte"></div>'


# ═══════════════════════════════════════════════════════════
# COMPOSANTS DE HAUT NIVEAU
# ═══════════════════════════════════════════════════════════


def afficher_skeleton_module(
    titre: str = "",
    n_lignes: int = 4,
    n_cartes: int = 2,
    show_header: bool = True,
) -> None:
    """Affiche un skeleton complet imitant la structure d'un module.

    Rendu typique:
    - Barre de titre (si ``show_header``)
    - Lignes de texte (métriques / résumé)
    - Cartes (contenu principal)

    Args:
        titre: Titre indicatif affiché en texte léger au-dessus.
        n_lignes: Nombre de lignes skeleton de texte.
        n_cartes: Nombre de cartes skeleton.
        show_header: Afficher le bloc titre shimmer.
    """
    _assurer_css()

    parts: list[str] = []

    # Titre indicatif léger
    if titre:
        parts.append(
            f'<div style="color:{Sem.ON_SURFACE_SECONDARY}; '
            f'font-size:0.85rem; margin-bottom:{Espacement.SM};">'
            f"Chargement de {titre}…</div>"
        )

    parts.append('<div class="sk-container" role="status" aria-label="Chargement en cours">')

    # Barre titre
    if show_header:
        parts.append('<div class="sk-base sk-titre"></div>')

    # Ligne de métriques (row avec cercle + bloc)
    parts.append('<div class="sk-row">')
    parts.append(skeleton_circle("32px"))
    parts.append(skeleton_block("16px", "50%"))
    parts.append("</div>")

    # Lignes de texte
    parts.append(skeleton_texte(n_lignes))

    # Cartes
    for _ in range(n_cartes):
        parts.append(skeleton_carte())

    parts.append("</div>")

    CSSManager.inject()
    st.markdown("\n".join(parts), unsafe_allow_html=True)


def afficher_skeleton_tableau(
    n_colonnes: int = 4,
    n_rangees: int = 5,
) -> None:
    """Affiche un skeleton imitant un tableau de données.

    Args:
        n_colonnes: Nombre de colonnes.
        n_rangees: Nombre de rangées de données.
    """
    _assurer_css()

    parts: list[str] = [
        '<div class="sk-container" role="status" aria-label="Chargement du tableau">'
    ]

    # Header du tableau
    parts.append('<div class="sk-row">')
    for _ in range(n_colonnes):
        parts.append(skeleton_block("18px", f"{90 // n_colonnes}%", Rayon.SM))
    parts.append("</div>")
    parts.append(f'<hr style="border-color:{Sem.BORDER_SUBTLE}; margin:4px 0;">')

    # Rangées
    for _ in range(n_rangees):
        parts.append('<div class="sk-row">')
        for _ in range(n_colonnes):
            parts.append(skeleton_block("14px", f"{85 // n_colonnes}%"))
        parts.append("</div>")

    parts.append("</div>")

    CSSManager.inject()
    st.markdown("\n".join(parts), unsafe_allow_html=True)


def skeleton_pendant_chargement(
    titre: str = "",
    n_lignes: int = 4,
    n_cartes: int = 2,
) -> Any:
    """Retourne un ``st.empty()`` pré-rempli avec un skeleton module.

    Usage typique dans un module::

        placeholder = skeleton_pendant_chargement("Recettes")
        donnees = service.charger_donnees_lourdes()  # bloquant
        placeholder.empty()                          # efface le skeleton
        afficher_donnees(donnees)                     # contenu réel

    Args:
        titre: Titre indicatif pour le skeleton.
        n_lignes: Nombre de lignes shimmer.
        n_cartes: Nombre de cartes shimmer.

    Returns:
        Le ``st.empty()`` contenant le skeleton (appeler ``.empty()`` pour effacer).
    """
    placeholder = st.empty()
    with placeholder.container():
        afficher_skeleton_module(titre, n_lignes, n_cartes)
    return placeholder


__all__ = [
    "afficher_skeleton_module",
    "afficher_skeleton_tableau",
    "skeleton_block",
    "skeleton_carte",
    "skeleton_circle",
    "skeleton_pendant_chargement",
    "skeleton_texte",
]
