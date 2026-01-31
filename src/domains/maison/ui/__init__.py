"""
Module Maison - Hub de gestion domestique

Structure:
- jardin.py: Gestion du jardin, plantes, récoltes avec conseils IA
- projets.py: Projets maison (rénovation, aménagement) avec priorisation IA
- entretien.py: Routines ménagères et tâches quotidiennes avec optimisation IA
- helpers.py: Fonctions partagées pour les 3 modules

Hub principal affichant:
- Alertes urgentes (projets en retard, plantes à arroser, tâches ménage)
- Statistiques clés
- Raccourcis vers chaque sous-module
"""

import streamlit as st
from datetime import date

from src.domains.maison.logic.helpers import (
    get_projets_urgents,
    get_plantes_a_arroser,
    get_stats_projets,
    get_stats_jardin,
    get_stats_entretien
)


def app():
    """Point d'entrée principal du module Maison"""
    st.title("🎯 Maison")
    st.caption("Gestion complète : Projets, Jardin, Entretien")
    
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # ALERTES PRIORITAIRES
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    
    col1, col2, col3 = st.columns(3)
    
    # Projets urgents
    urgents = get_projets_urgents()
    with col1:
        if urgents:
            st.error(f"❌ {len(urgents)} projet(s) urgent(s)")
        else:
            st.success("✅ Projets OK")
    
    # Plantes à arroser
    plantes = get_plantes_a_arroser()
    with col2:
        if plantes:
            st.warning(f"🍽️ {len(plantes)} plante(s) à arroser")
        else:
            st.success("✅ Jardin OK")
    
    # Tâches ménage
    stats_entretien = get_stats_entretien()
    with col3:
        if stats_entretien["completion_today"] < 100:
            st.info(f"⏳ {100 - stats_entretien['completion_today']:.0f}% tâches restantes")
        else:
            st.success("✅ Ménage complet!")
    
    st.markdown("---")
    
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # STATISTIQUES
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    
    st.subheader("📊 Tableau de bord")
    
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    
    # Projets
    with col_stat1:
        stats_proj = get_stats_projets()
        st.metric(
            "💡 Projets",
            stats_proj["en_cours"],
            f"{stats_proj['avg_progress']:.0f}% progression"
        )
    
    # Jardin
    with col_stat2:
        stats_jard = get_stats_jardin()
        st.metric(
            "👶 Jardin",
            stats_jard["total_plantes"],
            f"{stats_jard['a_arroser']} à arroser"
        )
    
    # Entretien
    with col_stat3:
        st.metric(
            "🧹 Entretien",
            stats_entretien["routines_actives"],
            f"{stats_entretien['taches_today']} faites aujourd'hui"
        )
    
    st.markdown("---")
    
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # NAVIGATION
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    
    st.subheader("📅 Accès rapide")
    
    col_nav1, col_nav2, col_nav3 = st.columns(3)
    
    with col_nav1:
        if st.button("💡 Projets", use_container_width=True, key="nav_projets"):
            st.session_state.current_page = "Projets"
            st.rerun()
    
    with col_nav2:
        if st.button("👶 Jardin", use_container_width=True, key="nav_jardin"):
            st.session_state.current_page = "Jardin"
            st.rerun()
    
    with col_nav3:
        if st.button("🧹 Entretien", use_container_width=True, key="nav_entretien"):
            st.session_state.current_page = "Entretien"
            st.rerun()
    
    st.markdown("---")
    
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # ALERTES DÉTAILLÉES
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    
    if urgents:
        st.markdown("### âš ï¸ Projets nécessitant attention")
        for urgent in urgents[:5]:
            if urgent["type"] == "RETARD":
                st.error(f"❌ **{urgent['projet']}** - {urgent['message']}")
            else:
                st.warning(f"🧹 **{urgent['projet']}** - {urgent['message']}")
        st.markdown("---")
    
    if plantes:
        st.markdown("### 🍽️ Plantes à arroser aujourd'hui")
        for p in plantes[:5]:
            st.caption(f"• {p['nom']} 🗑️ {p['location']}")
        st.markdown("---")
    
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # CONSEILS IA
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    
    st.info("""
    💰 **Besoin d'aide?**
    
    Chaque module (Projets, Jardin, Entretien) intègre l'IA pour:
    - Générateurs de tâches & routines
    - Estimations de durée & planning
    - Conseils & astuces d'optimisation
    - Priorisation intelligente
    
    Explorez les onglets – "Assistant IA" dans chaque module!
    """)

