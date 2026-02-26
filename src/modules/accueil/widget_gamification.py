"""
Widget gamification / streaks pour le dashboard.

Affiche les badges récents, points de la semaine et streaks actifs.
Utilise le ServiceGamification existant.
"""

import logging

import streamlit as st

from src.ui.engine import StyleSheet
from src.ui.fragments import cached_fragment
from src.ui.keys import KeyNamespace
from src.ui.tokens import Couleur, Espacement, Rayon
from src.ui.tokens_semantic import Sem

logger = logging.getLogger(__name__)

_keys = KeyNamespace("gamification_dashboard")


@cached_fragment(ttl=300)  # Cache 5 min
def afficher_widget_gamification():
    """Affiche le widget gamification compact pour le dashboard."""
    try:
        from src.services.core.gamification import get_gamification_service

        service = get_gamification_service()
        stats = service.obtenir_stats()
        badges = service.obtenir_badges()
    except Exception as e:
        logger.debug(f"Service gamification indisponible: {e}")
        return  # Pas d'affichage si le service est absent

    container_cls = StyleSheet.create_class(
        {
            "background": "linear-gradient(135deg, #FFF3E0, #FFE0B2)",
            "border-radius": Rayon.XL,
            "padding": Espacement.LG,
            "border-left": f"4px solid {Couleur.ORANGE}",
            "margin-bottom": Espacement.MD,
        }
    )

    StyleSheet.inject()

    st.markdown(f'<div class="{container_cls}">', unsafe_allow_html=True)

    st.markdown("### 🎮 Gamification")

    # Métriques principales
    col1, col2, col3 = st.columns(3)

    with col1:
        points_semaine = getattr(stats, "points_semaine", 0)
        st.metric("⭐ Points semaine", points_semaine)

    with col2:
        total_badges = len(badges) if badges else 0
        st.metric("🏅 Badges", total_badges)

    with col3:
        streak = getattr(stats, "streak_jours", 0)
        if streak > 0:
            st.metric("🔥 Streak", f"{streak}j")
        else:
            niveau = getattr(stats, "niveau", 1)
            st.metric("📊 Niveau", niveau)

    # Derniers badges obtenus (3 max)
    if badges:
        recent_badges = sorted(
            badges,
            key=lambda b: b.get("date_obtention", ""),
            reverse=True,
        )[:3]

        badges_html = " ".join(
            f'<span title="{b.get("nom", "Badge")}" style="font-size:1.5rem;'
            f'margin:0 4px;cursor:help;">{b.get("icone", "🏅")}</span>'
            for b in recent_badges
        )
        st.markdown(
            f'<div style="text-align:center;margin-top:4px;">'
            f"<small>Derniers badges :</small><br>{badges_html}</div>",
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)


__all__ = ["afficher_widget_gamification"]
