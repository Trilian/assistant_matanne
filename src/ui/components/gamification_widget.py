"""
Widget Gamification — Affichage des points, niveau et badges.

Composant UI pour la gamification globale. S'intègre dans le
sidebar, l'accueil ou n'importe quel module.

Usage:
    from src.ui.components.gamification_widget import (
        afficher_gamification_sidebar,
        afficher_badges_complets,
        toast_badge,
    )

    # Dans le sidebar ou l'accueil
    afficher_gamification_sidebar()

    # Vue complète des badges
    afficher_badges_complets()
"""

import logging

import streamlit as st

from src.ui.fragments import ui_fragment
from src.ui.keys import KeyNamespace

logger = logging.getLogger(__name__)

_keys = KeyNamespace("gamif")


# ═══════════════════════════════════════════════════════════
# WIDGETS
# ═══════════════════════════════════════════════════════════


@ui_fragment
def afficher_gamification_sidebar() -> None:
    """Affiche un résumé compact de la gamification dans le sidebar/accueil."""
    try:
        from src.services.core.gamification import (
            SEUILS_NIVEAUX,
            TITRES_NIVEAUX,
            get_gamification_service,
        )

        service = get_gamification_service()
        stats = service.obtenir_stats()
    except Exception as e:
        logger.debug(f"Gamification indisponible: {e}")
        return

    niveau = stats.niveau
    titre = TITRES_NIVEAUX.get(niveau, "Explorateur")
    points = stats.points_total

    # Progression vers le niveau suivant
    seuil_actuel = SEUILS_NIVEAUX[min(niveau - 1, len(SEUILS_NIVEAUX) - 1)]
    seuil_suivant = SEUILS_NIVEAUX[min(niveau, len(SEUILS_NIVEAUX) - 1)]
    if seuil_suivant > seuil_actuel:
        progression = (points - seuil_actuel) / (seuil_suivant - seuil_actuel)
    else:
        progression = 1.0

    nb_badges = len(stats.badges_debloques)

    # Affichage compact
    st.markdown(
        f"**🏅 Niveau {niveau}** · {titre}  \n"
        f"⭐ {points} pts · 🎖️ {nb_badges} badge{'s' if nb_badges != 1 else ''}"
    )
    st.progress(min(progression, 1.0), text=f"Prochain niveau: {seuil_suivant} pts")


@ui_fragment
def afficher_badges_complets() -> None:
    """Affiche la vue complète des badges avec progression."""
    try:
        from src.services.core.gamification import get_gamification_service

        service = get_gamification_service()
        badges = service.obtenir_badges()
        stats = service.obtenir_stats()
    except Exception as e:
        st.warning(f"Service gamification indisponible: {e}")
        return

    st.subheader("🏅 Badges & Progression")

    # Stats globales
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("⭐ Points", stats.points_total)
    with col2:
        st.metric("🏅 Niveau", stats.niveau)
    with col3:
        debloques = len([b for b in badges if b["debloque"]])
        st.metric("🎖️ Badges", f"{debloques}/{len(badges)}")
    with col4:
        st.metric(
            "🔥 Streak max",
            max(
                stats.streak_cuisine,
                stats.streak_entretien,
                stats.streak_routines,
            ),
        )

    st.markdown("---")

    # Grouper badges par catégorie
    categories: dict[str, list[dict]] = {}
    for b in badges:
        cat = b["badge"].categorie
        categories.setdefault(cat, []).append(b)

    _LABELS_CATEGORIES = {
        "cuisine": "🍳 Cuisine",
        "famille": "👨‍👩‍👦 Famille",
        "maison": "🏠 Maison",
        "global": "🌍 Global",
    }

    for cat_key, cat_badges in categories.items():
        st.markdown(f"### {_LABELS_CATEGORIES.get(cat_key, cat_key)}")

        cols = st.columns(3)
        for i, b_info in enumerate(cat_badges):
            badge_def = b_info["badge"]
            debloque = b_info["debloque"]
            progression = b_info["progression"]

            with cols[i % 3]:
                if debloque:
                    st.markdown(
                        f"<div style='text-align:center;padding:10px;background:"
                        f"var(--st-primary-bg,#e3f2fd);border-radius:10px;margin:4px;'>"
                        f"<div style='font-size:2rem;'>{badge_def.emoji}</div>"
                        f"<strong>{badge_def.nom}</strong><br>"
                        f"<small style='color:var(--st-success,#4caf50);'>✅ Débloqué</small>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f"<div style='text-align:center;padding:10px;background:"
                        f"var(--st-surface-alt,#f5f5f5);border-radius:10px;margin:4px;"
                        f"opacity:0.7;'>"
                        f"<div style='font-size:2rem;filter:grayscale(80%);'>"
                        f"{badge_def.emoji}</div>"
                        f"<strong>{badge_def.nom}</strong><br>"
                        f"<small>{badge_def.description}</small><br>"
                        f"<small>{progression}%</small>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )
                    st.progress(progression / 100)


def toast_badge(badge_nom: str, badge_emoji: str) -> None:
    """Affiche un toast de félicitations pour un badge débloqué."""
    st.toast(f"{badge_emoji} Badge débloqué: {badge_nom} !", icon="🏅")


__all__ = [
    "afficher_gamification_sidebar",
    "afficher_badges_complets",
    "toast_badge",
]
