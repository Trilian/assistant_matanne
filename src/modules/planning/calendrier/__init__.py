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

# Date utils
from src.core.date_utils import obtenir_debut_semaine as get_debut_semaine
from src.core.monitoring.rerun_profiler import profiler_rerun
from src.modules._framework import error_boundary

# Import Google Calendar UI
from src.ui.integrations import afficher_config_google_calendar
from src.ui.keys import KeyNamespace
from src.ui.state.url import tabs_with_url

# Import des fonctions pour exposer l'API publique
from .aggregation import construire_semaine_calendrier
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
from .components_conflits import (
    afficher_alertes_conflits,
)
from .components_formulaire import (
    afficher_formulaire_ajout_event,
    afficher_legende,
    afficher_navigation_semaine,
)
from .components_jour import (
    afficher_cellule_jour,
    afficher_jour_calendrier,
)
from .components_semaine import (
    afficher_actions_rapides,
    afficher_modal_impression,
    afficher_stats_semaine,
    afficher_vue_semaine_grille,
    afficher_vue_semaine_liste,
)
from .data import charger_donnees_semaine
from .import_ics import afficher_import_ics
from .types import SemaineCalendrier  # noqa: F401
from .vue_mensuelle import afficher_vue_mensuelle

# Session keys scopées
_keys = KeyNamespace("calendrier")


@profiler_rerun("calendrier")
def app():
    """Point d'entrée du module Calendrier Familial Unifié."""

    st.title("📅 Calendrier Familial")
    st.caption("Vue unifiée de toute votre semaine: repas, batch, courses, activités, ménage, RDV")

    with error_boundary("calendrier_principal"):
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

        # Onglets principaux avec deep linking URL
        TAB_LABELS = ["📅 Calendrier", "📊 Analyse", "🤖 IA", "� Import", "🔗 Google"]
        tab_index = tabs_with_url(TAB_LABELS, param="tab")
        tab_calendrier, tab_analyse, tab_ia, tab_import, tab_google = st.tabs(TAB_LABELS)

        # ═══════════════════════════════════════════════════════════
        # ONGLET CALENDRIER
        # ═══════════════════════════════════════════════════════════
        with tab_calendrier:
            # Stats en haut
            afficher_stats_semaine(semaine)

            # Alertes conflits
            afficher_alertes_conflits(st.session_state.cal_semaine_debut)

            st.divider()

            # Actions rapides
            afficher_actions_rapides(semaine)

            st.divider()

            # Mode d'affichage
            mode = st.radio(
                "Vue",
                ["📋 Liste détaillée", "📊 Grille", "📅 Mois"],
                horizontal=True,
                label_visibility="collapsed",
            )

            # Affichage principal
            if mode == "📋 Liste détaillée":
                afficher_vue_semaine_liste(semaine)
            elif mode == "📊 Grille":
                afficher_vue_semaine_grille(semaine)
            else:
                afficher_vue_mensuelle()

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

            # Créneaux libres et suggestions
            _afficher_suggestions_creneaux(semaine)

            st.divider()

            # Formulaire d'optimisation IA
            afficher_formulaire_optimisation_ia(st.session_state.cal_semaine_debut)

            st.divider()

            # Rééquilibrage
            st.markdown("#### 🔄 Rééquilibrage des jours chargés")
            afficher_reequilibrage(semaine.jours)

            st.divider()

            # Chat IA contextuel planning
            st.markdown("#### 💬 Assistant Planning")
            from src.ui.components import afficher_chat_contextuel

            afficher_chat_contextuel("planning")

        # ═══════════════════════════════════════════════════════════
        # ONGLET IMPORT ICS
        # ═══════════════════════════════════════════════════════════
        with tab_import:
            afficher_import_ics()

        # ═══════════════════════════════════════════════════════════
        # ONGLET GOOGLE CALENDAR
        # ═══════════════════════════════════════════════════════════
        with tab_google:
            st.subheader("🔗 Synchronisation Google Calendar")
            st.caption("Connectez votre Google Calendar pour synchroniser vos événements")
            afficher_config_google_calendar()


# ═══════════════════════════════════════════════════════════
# SUGGESTIONS IA — CRÉNEAUX LIBRES
# ═══════════════════════════════════════════════════════════


def _afficher_suggestions_creneaux(semaine):
    """Affiche les créneaux libres et suggestions d'optimisation."""
    try:
        from src.services.planning.suggestions import obtenir_service_suggestions

        service = obtenir_service_suggestions()

        # Suggestions d'optimisation
        suggestions = service.suggestions_planning(semaine.jours)

        if suggestions:
            st.markdown("#### 💡 Suggestions d'optimisation")
            for s in suggestions[:6]:
                if s.priorite >= 4:
                    st.warning(f"{s.icone} **{s.titre}** — {s.description}")
                elif s.priorite >= 3:
                    st.info(f"{s.icone} **{s.titre}** — {s.description}")
                else:
                    st.caption(f"{s.icone} **{s.titre}** — {s.description}")

            st.divider()

        # Créneaux libres
        creneaux = service.creneaux_libres(semaine.jours)

        if creneaux:
            st.markdown("#### 🕐 Meilleurs créneaux libres")
            st.caption("Créneaux disponibles classés par qualité")

            for c in creneaux[:8]:
                from src.core.constants import JOURS_SEMAINE

                jour_nom = JOURS_SEMAINE[c.date_jour.weekday()]
                score_bar = (
                    "🟢" if c.score_qualite >= 70 else "🟡" if c.score_qualite >= 50 else "🔵"
                )

                st.markdown(
                    f"{score_bar} **{jour_nom} {c.date_jour.strftime('%d/%m')}** "
                    f"— {c.horaire_str} ({c.duree_str})" + (f" *— {c.raison}*" if c.raison else "")
                )
        else:
            st.success("✅ Semaine bien remplie — pas de grand créneau libre !")

    except Exception:
        import logging

        logging.getLogger(__name__).debug("Suggestions créneaux indisponibles")


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
