"""
Sous-module Jardin - Gestion intelligente du potager.

Structure:
- styles.py: CSS du module
- data.py: Chargement catalogue plantes
- taches.py: Génération automatique des tâches
- autonomie.py: Calculs d'autonomie alimentaire
- ui.py: Composants UI réutilisables
- onglets.py: Onglets de l'interface
"""

import streamlit as st

from src.core.monitoring.rerun_profiler import profiler_rerun
from src.modules._framework import error_boundary
from src.ui.state.url import tabs_with_url

from .data import obtenir_meteo_jardin
from .logic import (
    BADGES_JARDIN,
    calculer_autonomie,
    calculer_stats_jardin,
    calculer_streak_jardin,
    obtenir_badges_jardin,
)
from .onglets import (
    onglet_autonomie,
    onglet_export,
    onglet_graphiques,
    onglet_mes_plantes,
    onglet_plan,
    onglet_recoltes,
    onglet_taches,
)
from .styles import injecter_css_jardin

__all__ = ["app"]


@profiler_rerun("jardin")
def app():
    """Point d'entrée du module Jardin avec gamification."""
    injecter_css_jardin()

    # Initialiser les données en session
    if "mes_plantes_jardin" not in st.session_state:
        st.session_state.mes_plantes_jardin = []

    if "recoltes_jardin" not in st.session_state:
        st.session_state.recoltes_jardin = []

    mes_plantes = st.session_state.mes_plantes_jardin
    recoltes = st.session_state.recoltes_jardin

    # Météo et stats
    meteo = obtenir_meteo_jardin()
    autonomie = calculer_autonomie(mes_plantes, recoltes)
    stats = calculer_stats_jardin(mes_plantes, recoltes)
    badges_obtenus = obtenir_badges_jardin(stats)
    streak = calculer_streak_jardin(recoltes)

    # Header gamifié
    col_h1, col_h2, col_h3 = st.columns([3, 1, 1])
    with col_h1:
        st.markdown(
            f"""
        <div class="jardin-header">
            <h1>🌱 Mon Potager Intelligent</h1>
            <div class="meteo-badge">
                <span style="font-size: 1.8rem">☀️</span>
                <span><strong>{meteo.get("temperature", 20)}°C</strong></span>
                {f'<span class="streak-badge">🔥 {streak}j</span>' if streak > 2 else ""}
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with col_h2:
        st.metric("🏅 Badges", f"{len(badges_obtenus)}/{len(BADGES_JARDIN)}")
    with col_h3:
        st.metric("🎯 Autonomie", f"{autonomie['pourcentage_prevu']}%")

    # Onglets enrichis avec deep linking
    TAB_LABELS = [
        "🎯 Tâches",
        "🌿 Mes Plantes",
        "🥕 Récoltes",
        "🏅 Autonomie",
        "🗺️ Plan",
        "📈 Graphiques",
        "📥 Export",
    ]
    tabs_with_url(TAB_LABELS, param="tab")
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(TAB_LABELS)

    with tab1:
        with error_boundary(titre="Erreur tâches jardin"):
            onglet_taches(mes_plantes, meteo)

    with tab2:
        with error_boundary(titre="Erreur mes plantes"):
            onglet_mes_plantes(mes_plantes)

    with tab3:
        with error_boundary(titre="Erreur récoltes"):
            onglet_recoltes(mes_plantes, recoltes)

    with tab4:
        with error_boundary(titre="Erreur autonomie"):
            onglet_autonomie(mes_plantes, recoltes)

    with tab5:
        with error_boundary(titre="Erreur plan jardin"):
            onglet_plan(mes_plantes)

    with tab6:
        with error_boundary(titre="Erreur graphiques jardin"):
            onglet_graphiques(mes_plantes, recoltes)

    with tab7:
        with error_boundary(titre="Erreur export jardin"):
            onglet_export(mes_plantes, recoltes)
