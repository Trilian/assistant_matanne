"""
🏠 Hub Maison - Dashboard Intelligent

Hub central avec :
- Briefing IA quotidien
- Tâches prioritaires (respect charge mentale)
- Stats visuelles
- Navigation modules

Architecture:
┌──────────────────────────────────────────────────────────────┐
│ 📋 AUJOURD'HUI                                               │
│ "3 tâches • 45 min • Charge: ████░░░░░░ 40%"                │
├──────────────────────────────────────────────────────────────┤
│ 🚨 ALERTES          │ 📊 STATS DU MOIS                      │
└──────────────────────────────────────────────────────────────┘
│ 🌳 Jardin  │ 🏡 Entretien  │ 💡 Charges  │ 💰 Dépenses     │
└──────────────────────────────────────────────────────────────┘
"""

import streamlit as st

from src.core.monitoring.rerun_profiler import profiler_rerun
from src.modules._framework import error_boundary

from .data import calculer_charge, obtenir_alertes, obtenir_stats_globales, obtenir_taches_jour
from .styles import injecter_css_hub
from .ui import (
    afficher_alertes,
    afficher_header,
    afficher_modules,
    afficher_stats_mois,
    afficher_taches,
)


@profiler_rerun("maison_hub")
def app():
    """Point d'entrée du hub maison."""
    with error_boundary(titre="Erreur hub maison"):
        injecter_css_hub()

        # Données
        stats = obtenir_stats_globales()
        taches = obtenir_taches_jour()
        alertes = obtenir_alertes()
        charge = calculer_charge(taches)

        # Rendu
        afficher_header()

        # Layout principal
        col_main, col_side = st.columns([2, 1])

        with col_main:
            afficher_taches(taches, charge)
            afficher_modules(stats)

        with col_side:
            afficher_alertes(alertes)
            afficher_stats_mois(stats)

        # Actions rapides
        st.markdown("---")

        with st.expander("⚡ Actions rapides", expanded=False):
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("➕ Nouvelle tâche", use_container_width=True):
                    st.info("Formulaire nouvelle tâche")
            with col2:
                if st.button("⏱️ Démarrer chrono", use_container_width=True):
                    st.info("Lancer chronomètre")
            with col3:
                if st.button("📊 Stats détaillées", use_container_width=True):
                    st.info("Voir statistiques")


__all__ = ["app"]
