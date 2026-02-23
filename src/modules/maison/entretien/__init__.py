"""
Module Entretien - Sous-module de gestion de l'entretien maison.

IA-first: Tâches auto-générées selon équipements et calendrier.
"""

import streamlit as st

from src.core.monitoring.rerun_profiler import profiler_rerun
from src.modules._framework import error_boundary

from .logic import (
    BADGES_ENTRETIEN,
    calculer_score_proprete,
    calculer_stats_globales,
    calculer_streak,
    generer_taches_entretien,
    obtenir_badges_obtenus,
)
from .onglets import (
    onglet_export,
    onglet_graphiques,
    onglet_historique,
    onglet_inventaire,
    onglet_pieces,
    onglet_stats,
    onglet_taches,
)
from .styles import injecter_css_entretien

__all__ = ["app"]


@profiler_rerun("entretien")
def app():
    """Point d'entrée du module Entretien avec gamification."""
    injecter_css_entretien()

    # Initialiser les données en session
    if "mes_objets_entretien" not in st.session_state:
        st.session_state.mes_objets_entretien = []

    if "historique_entretien" not in st.session_state:
        st.session_state.historique_entretien = []

    mes_objets = st.session_state.mes_objets_entretien
    historique = st.session_state.historique_entretien

    # Score et stats gamifiés
    score = calculer_score_proprete(mes_objets, historique)
    streak = calculer_streak(historique)
    stats = calculer_stats_globales(mes_objets, historique)
    badges_obtenus = obtenir_badges_obtenus(stats)

    # Header gamifié
    col_h1, col_h2, col_h3 = st.columns([3, 1, 1])
    with col_h1:
        st.markdown(
            f"""
        <div class="entretien-header">
            <h1>🏠 Entretien Maison</h1>
            <div class="score-badge">
                <span style="font-size: 1.25rem">✨</span>
                <span>Score: <strong>{score["score"]}/100</strong> • {score["niveau"]}</span>
                {f'<span class="streak-mini">🔥 {streak}j</span>' if streak > 2 else ""}
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with col_h2:
        st.metric("🏅 Badges", f"{len(badges_obtenus)}/{len(BADGES_ENTRETIEN)}")
    with col_h3:
        taches = generer_taches_entretien(mes_objets, historique)
        urgentes = len([t for t in taches if t.get("priorite") == "urgente"])
        if urgentes > 0:
            st.metric("⚠️ Urgentes", urgentes, delta=f"-{urgentes}", delta_color="inverse")
        else:
            st.metric("✅ Urgentes", 0, delta="OK", delta_color="normal")

    # Onglets enrichis
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
        [
            "🎯 Tâches",
            "📦 Inventaire",
            "🏠 Par pièce",
            "📜 Historique",
            "🏅 Stats & Badges",
            "📈 Graphiques",
            "📥 Export",
        ]
    )

    with tab1:
        with error_boundary(titre="Erreur tâches entretien"):
            onglet_taches(mes_objets, historique)

    with tab2:
        with error_boundary(titre="Erreur inventaire entretien"):
            onglet_inventaire(mes_objets)

    with tab3:
        with error_boundary(titre="Erreur pièces"):
            onglet_pieces(mes_objets, historique)

    with tab4:
        with error_boundary(titre="Erreur historique entretien"):
            onglet_historique(historique)

    with tab5:
        with error_boundary(titre="Erreur stats entretien"):
            onglet_stats(mes_objets, historique)

    with tab6:
        with error_boundary(titre="Erreur graphiques entretien"):
            onglet_graphiques(mes_objets, historique)

    with tab7:
        with error_boundary(titre="Erreur export entretien"):
            onglet_export(mes_objets, historique)
