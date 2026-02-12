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

from ._common import st

# Import des fonctions pour exposer l'API publique
from .helpers import (
    get_current_user, set_current_user, get_user_data,
    get_food_logs_today
)
from .dashboard import render_user_switch, render_dashboard, render_weekly_chart
from .activities import render_activities
from .alimentation import render_food_log, render_food_form
from .settings import render_garmin_settings, render_objectifs


def app():
    """Point d'entrée du module Suivi Perso"""
    st.title("💪 Mon Suivi")
    
    # Switch utilisateur
    render_user_switch()
    
    username = get_current_user()
    display_name = "Anne" if username == "anne" else "Mathieu"
    emoji = "👩" if username == "anne" else "👨"
    
    st.caption(f"{emoji} {display_name}")
    
    # Charger les données
    data = get_user_data(username)
    
    # Tabs
    tabs = st.tabs(["📊 Dashboard", "🏃 Activités", "🥗 Alimentation", "🎯 Objectifs", "⌚ Garmin"])
    
    with tabs[0]:
        render_dashboard(data)
    
    with tabs[1]:
        render_activities(data)
    
    with tabs[2]:
        render_food_log(username)
    
    with tabs[3]:
        render_objectifs(data)
    
    with tabs[4]:
        render_garmin_settings(data)


__all__ = [
    # Entry point
    "app",
    # Helpers
    "get_current_user",
    "set_current_user",
    "get_user_data",
    "get_food_logs_today",
    # UI
    "render_user_switch",
    "render_dashboard",
    "render_weekly_chart",
    "render_activities",
    "render_food_log",
    "render_food_form",
    "render_garmin_settings",
    "render_objectifs",
]
