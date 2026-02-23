"""
Module Suivi Perso - Dashboard santé/sport pour Anne et Mathieu.

Fonctionnalités:
- Switch utilisateur (Anne / Mathieu)
- Dashboard perso (stats Garmin, streak, objectifs)
- Routines sport
- Log alimentation
- Progression (graphiques)
- Sync Garmin
"""

from src.core.monitoring.rerun_profiler import profiler_rerun
from src.modules._framework import error_boundary

from .activities import afficher_activities
from .alimentation import afficher_food_form, afficher_food_log
from .settings import afficher_garmin_settings, afficher_objectifs
from .tableau_bord import afficher_dashboard, afficher_user_switch, afficher_weekly_chart

# Import des fonctions pour exposer l'API publique
from .utils import get_current_user, get_food_logs_today, get_user_data, set_current_user, st


@profiler_rerun("suivi_perso")
def app():
    """Point d'entrée du module Suivi Perso"""
    st.title("💪 Mon Suivi")

    # Switch utilisateur
    afficher_user_switch()

    username = get_current_user()
    display_name = "Anne" if username == "anne" else "Mathieu"
    emoji = "👩" if username == "anne" else "💨"

    st.caption(f"{emoji} {display_name}")

    # Charger les données
    data = get_user_data(username)

    # Tabs
    tabs = st.tabs(["📊 Dashboard", "🏃 Activités", "🥗 Alimentation", "🎯 Objectifs", "⌚ Garmin"])

    with tabs[0]:
        with error_boundary(titre="Erreur dashboard suivi"):
            afficher_dashboard(data)

    with tabs[1]:
        with error_boundary(titre="Erreur activités suivi"):
            afficher_activities(data)

    with tabs[2]:
        with error_boundary(titre="Erreur alimentation"):
            afficher_food_log(username)

    with tabs[3]:
        with error_boundary(titre="Erreur objectifs"):
            afficher_objectifs(data)

    with tabs[4]:
        with error_boundary(titre="Erreur Garmin"):
            afficher_garmin_settings(data)


__all__ = [
    # Entry point
    "app",
    # Helpers
    "get_current_user",
    "set_current_user",
    "get_user_data",
    "get_food_logs_today",
    # UI
    "afficher_user_switch",
    "afficher_dashboard",
    "afficher_weekly_chart",
    "afficher_activities",
    "afficher_food_log",
    "afficher_food_form",
    "afficher_garmin_settings",
    "afficher_objectifs",
]
