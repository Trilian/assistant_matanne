"""
Module Calendrier Familial Unifié - Vue centrale de TOUT

Affiche dans une seule vue:
- 🍽️ Repas (midi, soir, goûters)
- 🍳 Sessions batch cooking
- 🛒 Courses planifiées
- 🎨 Activités famille
- 🏥 RDV médicaux
- 📅 Événements divers

Fonctionnalités:
- Vue semaine avec impression
- Ajout rapide d'événements
- Navigation semaine par semaine
- Export pour le frigo
"""

from datetime import date

import streamlit as st

# Import Google Calendar UI
from src.ui.integrations import afficher_config_google_calendar

from .analytics import (
    afficher_actions_prioritaires,
    afficher_formulaire_optimisation_ia,
    afficher_graphique_charge_semaine,
    afficher_graphique_repartition,
    afficher_metriques_detaillees,
    afficher_observations,
    afficher_reequilibrage,
    afficher_suggestions,
)
from .components import (
    afficher_actions_rapides,
    afficher_cellule_jour,
    afficher_formulaire_ajout_event,
    afficher_jour_calendrier,
    afficher_legende,
    afficher_modal_impression,
    afficher_navigation_semaine,
    afficher_stats_semaine,
    afficher_vue_semaine_grille,
    afficher_vue_semaine_liste,
)

# Import des fonctions pour exposer l'API publique
from .data import charger_donnees_semaine
from .utils import construire_semaine_calendrier, get_debut_semaine


def app():
    """Point d'entrée du module Calendrier Familial Unifié."""

    st.title("📅 Calendrier Familial")
    st.caption("Vue unifiée de toute votre semaine: repas, batch, courses, activités, ménage, RDV")

    # Navigation
    afficher_navigation_semaine()

    st.divider()

    # Init state
    if "cal_semaine_debut" not in st.session_state:
        st.session_state.cal_semaine_debut = get_debut_semaine(date.today())

    # Charger les données
    with st.spinner("Chargement..."):
        donnees = charger_donnees_semaine(st.session_state.cal_semaine_debut)

        semaine = construire_semaine_calendrier(
            date_debut=st.session_state.cal_semaine_debut,
            repas=donnees["repas"],
            sessions_batch=donnees["sessions_batch"],
            activites=donnees["activites"],
            events=donnees["events"],
            courses_planifiees=donnees["courses_planifiees"],
            taches_menage=donnees["taches_menage"],  # Intégration ménage
        )

    # Onglets principaux
    tab_calendrier, tab_analyse, tab_ia, tab_google = st.tabs(
        ["📅 Calendrier", "📊 Analyse", "🤖 IA", "🔗 Google"]
    )

    # ═══════════════════════════════════════════════════════════
    # ONGLET CALENDRIER
    # ═══════════════════════════════════════════════════════════
    with tab_calendrier:
        # Stats en haut
        afficher_stats_semaine(semaine)

        st.divider()

        # Actions rapides
        afficher_actions_rapides(semaine)

        st.divider()

        # Mode d'affichage
        mode = st.radio(
            "Vue",
            ["📋 Liste détaillée", "📊 Grille"],
            horizontal=True,
            label_visibility="collapsed",
        )

        # Affichage principal
        if mode == "📋 Liste détaillée":
            afficher_vue_semaine_liste(semaine)
        else:
            afficher_vue_semaine_grille(semaine)

        # Modals
        afficher_modal_impression(semaine)
        afficher_formulaire_ajout_event()

        # Légende
        afficher_legende()

    # ═══════════════════════════════════════════════════════════
    # ONGLET ANALYSE
    # ═══════════════════════════════════════════════════════════
    with tab_analyse:
        st.subheader("📊 Analyse de la semaine")

        # Calculer les stats pour l'analyse
        stats = {
            "total_repas": semaine.stats.get("repas", 0),
            "total_activites": semaine.stats.get("activites", 0),
            "total_events": semaine.stats.get("events", 0),
            "total_projets": semaine.stats.get("projets", 0),
            "activites_jules": semaine.stats.get("activites_jules", 0),
            "budget_total": semaine.stats.get("budget", 0),
            "charge_moyenne": semaine.stats.get("charge_moyenne", 50),
        }
        charge_globale = semaine.stats.get("charge_globale", "normal")

        # Métriques détaillées
        afficher_metriques_detaillees(stats, charge_globale)

        st.divider()

        # Graphiques côte à côte
        col1, col2 = st.columns(2)

        with col1:
            afficher_graphique_charge_semaine(semaine.jours)

        with col2:
            afficher_graphique_repartition(stats)

        st.divider()

        # Observations et suggestions
        col_obs, col_sug = st.columns(2)

        with col_obs:
            st.markdown("#### 🔍 Observations")
            afficher_observations(semaine.jours)

        with col_sug:
            st.markdown("#### 💡 Suggestions")
            afficher_suggestions(stats)

    # ═══════════════════════════════════════════════════════════
    # ONGLET IA
    # ═══════════════════════════════════════════════════════════
    with tab_ia:
        st.subheader("🤖 Optimisation Intelligente")

        # Formulaire d'optimisation IA
        afficher_formulaire_optimisation_ia(st.session_state.cal_semaine_debut)

        st.divider()

        # Rééquilibrage
        st.markdown("#### 🔄 Rééquilibrage des jours chargés")
        afficher_reequilibrage(semaine.jours)

    # ═══════════════════════════════════════════════════════════
    # ONGLET GOOGLE CALENDAR
    # ═══════════════════════════════════════════════════════════
    with tab_google:
        st.subheader("🔗 Synchronisation Google Calendar")
        st.caption("Connectez votre Google Calendar pour synchroniser vos événements")
        afficher_config_google_calendar()


__all__ = [
    # Entry point
    "app",
    # Data
    "charger_donnees_semaine",
    # UI Components
    "afficher_navigation_semaine",
    "afficher_jour_calendrier",
    "afficher_vue_semaine_grille",
    "afficher_cellule_jour",
    "afficher_vue_semaine_liste",
    "afficher_stats_semaine",
    "afficher_actions_rapides",
    "afficher_modal_impression",
    "afficher_formulaire_ajout_event",
    "afficher_legende",
    # Analytics
    "afficher_graphique_charge_semaine",
    "afficher_graphique_repartition",
    "afficher_actions_prioritaires",
    "afficher_metriques_detaillees",
    "afficher_suggestions",
    "afficher_observations",
    "afficher_formulaire_optimisation_ia",
    "afficher_reequilibrage",
]
