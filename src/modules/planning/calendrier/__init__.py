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

# Import Google Calendar UI
from src.ui.integrations import render_google_calendar_config

from ._common import construire_semaine_calendrier, date, get_debut_semaine, st
from .analytics import (
    render_actions_prioritaires,
    render_formulaire_optimisation_ia,
    render_graphique_charge_semaine,
    render_graphique_repartition,
    render_metriques_detaillees,
    render_observations,
    render_reequilibrage,
    render_suggestions,
)
from .components import (
    render_actions_rapides,
    render_cellule_jour,
    render_formulaire_ajout_event,
    render_jour_calendrier,
    render_legende,
    render_modal_impression,
    render_navigation_semaine,
    render_stats_semaine,
    render_vue_semaine_grille,
    render_vue_semaine_liste,
)

# Import des fonctions pour exposer l'API publique
from .data import charger_donnees_semaine


def app():
    """Point d'entrée du module Calendrier Familial Unifié."""

    st.title("📅 Calendrier Familial")
    st.caption("Vue unifiée de toute votre semaine: repas, batch, courses, activités, ménage, RDV")

    # Navigation
    render_navigation_semaine()

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
        render_stats_semaine(semaine)

        st.divider()

        # Actions rapides
        render_actions_rapides(semaine)

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
            render_vue_semaine_liste(semaine)
        else:
            render_vue_semaine_grille(semaine)

        # Modals
        render_modal_impression(semaine)
        render_formulaire_ajout_event()

        # Légende
        render_legende()

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
        render_metriques_detaillees(stats, charge_globale)

        st.divider()

        # Graphiques côte à côte
        col1, col2 = st.columns(2)

        with col1:
            render_graphique_charge_semaine(semaine.jours)

        with col2:
            render_graphique_repartition(stats)

        st.divider()

        # Observations et suggestions
        col_obs, col_sug = st.columns(2)

        with col_obs:
            st.markdown("#### 🔍 Observations")
            render_observations(semaine.jours)

        with col_sug:
            st.markdown("#### 💡 Suggestions")
            render_suggestions(stats)

    # ═══════════════════════════════════════════════════════════
    # ONGLET IA
    # ═══════════════════════════════════════════════════════════
    with tab_ia:
        st.subheader("🤖 Optimisation Intelligente")

        # Formulaire d'optimisation IA
        render_formulaire_optimisation_ia(st.session_state.cal_semaine_debut)

        st.divider()

        # Rééquilibrage
        st.markdown("#### 🔄 Rééquilibrage des jours chargés")
        render_reequilibrage(semaine.jours)

    # ═══════════════════════════════════════════════════════════
    # ONGLET GOOGLE CALENDAR
    # ═══════════════════════════════════════════════════════════
    with tab_google:
        st.subheader("🔗 Synchronisation Google Calendar")
        st.caption("Connectez votre Google Calendar pour synchroniser vos événements")
        render_google_calendar_config()


__all__ = [
    # Entry point
    "app",
    # Data
    "charger_donnees_semaine",
    # UI Components
    "render_navigation_semaine",
    "render_jour_calendrier",
    "render_vue_semaine_grille",
    "render_cellule_jour",
    "render_vue_semaine_liste",
    "render_stats_semaine",
    "render_actions_rapides",
    "render_modal_impression",
    "render_formulaire_ajout_event",
    "render_legende",
    # Analytics
    "render_graphique_charge_semaine",
    "render_graphique_repartition",
    "render_actions_prioritaires",
    "render_metriques_detaillees",
    "render_suggestions",
    "render_observations",
    "render_formulaire_optimisation_ia",
    "render_reequilibrage",
]
